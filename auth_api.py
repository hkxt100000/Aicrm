"""
认证和授权 API
"""
import uuid
import time
import secrets
import sqlite3
import bcrypt
import json
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel

router = APIRouter(tags=["认证"])

DB_PATH = 'data/crm.db'

# ========== 数据模型 ==========

class LoginRequest(BaseModel):
    """登录请求"""
    account: str
    password: str
    remember: bool = False

class EmployeeCreate(BaseModel):
    """创建员工"""
    account: str
    password: str
    name: str
    department_id: Optional[str] = None
    wecom_user_id: Optional[str] = None
    wecom_name: Optional[str] = None

class EmployeeUpdate(BaseModel):
    """更新员工"""
    name: Optional[str] = None
    password: Optional[str] = None
    department_id: Optional[str] = None
    wecom_user_id: Optional[str] = None
    wecom_name: Optional[str] = None
    status: Optional[str] = None

class DepartmentCreate(BaseModel):
    """创建部门"""
    name: str
    description: Optional[str] = None

class DepartmentUpdate(BaseModel):
    """更新部门"""
    name: Optional[str] = None
    description: Optional[str] = None
    menu_permissions: Optional[list] = None

# ========== 工具函数 ==========

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """密码加密"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token() -> str:
    """生成访问令牌"""
    return secrets.token_urlsafe(32)

def create_session(employee_id: str, remember: bool = False) -> str:
    """创建会话"""
    conn = get_db()
    cursor = conn.cursor()
    
    token = generate_token()
    current_time = int(time.time() * 1000)
    
    # 过期时间：记住密码7天，否则1天
    expires_days = 7 if remember else 1
    expires_at = current_time + (expires_days * 24 * 60 * 60 * 1000)
    
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    
    cursor.execute("""
        INSERT INTO sessions (id, employee_id, token, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, employee_id, token, expires_at, current_time))
    
    conn.commit()
    conn.close()
    
    return token

def verify_token(token: str):
    """验证令牌并返回员工信息"""
    conn = get_db()
    cursor = conn.cursor()
    
    current_time = int(time.time() * 1000)
    
    # 查询会话
    cursor.execute("""
        SELECT s.*, e.* 
        FROM sessions s
        JOIN employees e ON s.employee_id = e.id
        WHERE s.token = ? AND s.expires_at > ? AND (e.status = 1 OR e.status = '1')
    """, (token, current_time))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return dict(row)

async def get_current_user(authorization: str = Header(None)):
    """依赖项：获取当前登录用户"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="未登录")
    
    token = authorization.replace('Bearer ', '')
    user = verify_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="登录已过期")
    
    return user

# ========== 认证 API ==========

@router.post("/login")
def login(data: LoginRequest):
    """登录"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询员工（兼容 status 字段类型）
        cursor.execute("""
            SELECT * FROM employees 
            WHERE account = ? AND (status = 1 OR status = '1')
        """, (data.account,))
        
        employee = cursor.fetchone()
        
        if not employee:
            # 记录失败日志
            log_id = f"log_{uuid.uuid4().hex[:12]}"
            current_time = int(time.time() * 1000)
            
            cursor.execute("""
                INSERT INTO login_logs (
                    id, employee_id, login_time, status, fail_reason
                ) VALUES (?, ?, ?, ?, ?)
            """, (log_id, '', current_time, 'failed', '账号不存在'))
            
            conn.commit()
            conn.close()
            
            return {"code": 1, "message": "账号或密码错误"}
        
        employee_dict = dict(employee)
        
        # 验证密码
        if not verify_password(data.password, employee_dict['password']):
            # 记录失败日志
            log_id = f"log_{uuid.uuid4().hex[:12]}"
            current_time = int(time.time() * 1000)
            
            cursor.execute("""
                INSERT INTO login_logs (
                    id, employee_id, login_time, status, fail_reason
                ) VALUES (?, ?, ?, ?, ?)
            """, (log_id, employee_dict['id'], current_time, 'failed', '密码错误'))
            
            conn.commit()
            conn.close()
            
            return {"code": 1, "message": "账号或密码错误"}
        
        # 创建会话
        token = create_session(employee_dict['id'], data.remember)
        
        # 记录成功日志
        log_id = f"log_{uuid.uuid4().hex[:12]}"
        current_time = int(time.time() * 1000)
        
        cursor.execute("""
            INSERT INTO login_logs (
                id, employee_id, login_time, status
            ) VALUES (?, ?, ?, ?)
        """, (log_id, employee_dict['id'], current_time, 'success'))
        
        conn.commit()
        
        # 获取部门信息和权限
        department_name = None
        menu_permissions = []
        
        if employee_dict['department_id']:
            cursor.execute("""
                SELECT name, menu_permissions FROM departments 
                WHERE id = ?
            """, (employee_dict['department_id'],))
            
            dept = cursor.fetchone()
            if dept:
                department_name = dept['name']
                if dept['menu_permissions']:
                    import json
                    menu_permissions = json.loads(dept['menu_permissions'])
        
        conn.close()
        
        # 返回用户信息
        user_info = {
            "id": employee_dict['id'],
            "account": employee_dict['account'],
            "name": employee_dict['name'],
            "wecom_user_id": employee_dict['wecom_user_id'],
            "wecom_name": employee_dict['wecom_name'],
            "department_id": employee_dict['department_id'],
            "department_name": department_name,
            "is_super_admin": bool(employee_dict['is_super_admin']),
            "menu_permissions": menu_permissions
        }
        
        return {
            "code": 0,
            "message": "登录成功",
            "data": {
                "token": token,
                "user": user_info
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"code": 1, "message": f"登录失败：{str(e)}"}

@router.post("/logout")
def logout(authorization: str = Header(None)):
    """退出登录"""
    try:
        if not authorization or not authorization.startswith('Bearer '):
            return {"code": 0, "message": "已退出"}
        
        token = authorization.replace('Bearer ', '')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 删除会话
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        
        return {"code": 0, "message": "退出成功"}
        
    except Exception as e:
        return {"code": 1, "message": f"退出失败：{str(e)}"}

@router.get("/current")
def get_current(user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 获取部门信息和权限
        department_name = None
        menu_permissions = []
        
        if user['department_id']:
            cursor.execute("""
                SELECT name, menu_permissions FROM departments 
                WHERE id = ?
            """, (user['department_id'],))
            
            dept = cursor.fetchone()
            if dept:
                department_name = dept['name']
                if dept['menu_permissions']:
                    import json
                    menu_permissions = json.loads(dept['menu_permissions'])
        
        conn.close()
        
        # 返回用户信息
        user_info = {
            "id": user['id'],
            "account": user['account'],
            "name": user['name'],
            "wecom_user_id": user['wecom_user_id'],
            "wecom_name": user['wecom_name'],
            "department_id": user['department_id'],
            "department_name": department_name,
            "is_super_admin": bool(user['is_super_admin']),
            "menu_permissions": menu_permissions
        }
        
        return {"code": 0, "data": user_info}
        
    except Exception as e:
        return {"code": 1, "message": f"获取用户信息失败：{str(e)}"}


# ========== 员工管理 API ==========

@router.get("/employees")
def get_employees(
    page: int = 1,
    limit: int = 20,
    search: str = None,
    status: str = None,
    current_user: dict = Depends(get_current_user)
):
    """获取员工列表"""
    try:
        # 只有超级管理员可以查看员工列表
        if not current_user.get('is_super_admin'):
            return {"code": 1, "message": "权限不足"}
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 构建查询条件
        where_clauses = []
        params = []
        
        if search:
            where_clauses.append("(account LIKE ? OR name LIKE ?)")
            params.extend([f'%{search}%', f'%{search}%'])
        
        if status:
            where_clauses.append("status = ?")
            params.append(status)
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # 查询总数
        cursor.execute(f"""
            SELECT COUNT(*) FROM employees 
            WHERE {where_sql}
        """, params)
        total = cursor.fetchone()[0]
        
        # 查询列表
        offset = (page - 1) * limit
        cursor.execute(f"""
            SELECT 
                e.id, e.account, e.name, e.department_id, 
                e.wecom_user_id, e.wecom_name, e.status, 
                e.is_super_admin, e.created_at, e.updated_at,
                d.name as department_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE {where_sql}
            ORDER BY e.created_at DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset])
        
        employees = []
        for row in cursor.fetchall():
            employees.append({
                "id": row['id'],
                "account": row['account'],
                "name": row['name'],
                "department_id": row['department_id'],
                "department_name": row['department_name'],
                "wecom_user_id": row['wecom_user_id'],
                "wecom_name": row['wecom_name'],
                "status": row['status'],
                "is_super_admin": bool(row['is_super_admin']),
                "created_at": row['created_at'],
                "updated_at": row['updated_at']
            })
        
        conn.close()
        
        return {
            "code": 0,
            "data": employees,
            "total": total,
            "page": page,
            "limit": limit
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"code": 1, "message": f"获取员工列表失败：{str(e)}"}


@router.post("/employees")
def create_employee(data: EmployeeCreate, current_user: dict = Depends(get_current_user)):
    """新增员工"""
    try:
        # 只有超级管理员可以新增员工
        if not current_user.get('is_super_admin'):
            return {"code": 1, "message": "权限不足"}
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查账号是否已存在
        cursor.execute("SELECT COUNT(*) FROM employees WHERE account = ?", (data.account,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return {"code": 1, "message": "账号已存在"}
        
        # 生成员工 ID
        employee_id = f"emp_{uuid.uuid4().hex[:12]}"
        
        # 加密密码
        password_hash = hash_password(data.password)
        
        current_time = int(time.time() * 1000)
        
        # 插入员工
        cursor.execute("""
            INSERT INTO employees (
                id, account, password, name, 
                department_id, wecom_user_id, wecom_name,
                status, is_super_admin, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            employee_id,
            data.account,
            password_hash,
            data.name,
            data.department_id,
            data.wecom_user_id,
            data.wecom_name,
            'active',
            0,
            current_time,
            current_time
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "code": 0,
            "message": "员工创建成功",
            "data": {"id": employee_id}
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"code": 1, "message": f"创建员工失败：{str(e)}"}


@router.get("/employees/{employee_id}")
def get_employee(employee_id: str, current_user: dict = Depends(get_current_user)):
    """获取员工详情"""
    try:
        # 只有超级管理员可以查看员工详情
        if not current_user.get('is_super_admin'):
            return {"code": 1, "message": "权限不足"}
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                e.id, e.account, e.name, e.department_id, 
                e.wecom_user_id, e.wecom_name, e.status, 
                e.is_super_admin, e.created_at, e.updated_at,
                d.name as department_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.id = ?
        """, (employee_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"code": 1, "message": "员工不存在"}
        
        employee = {
            "id": row['id'],
            "account": row['account'],
            "name": row['name'],
            "department_id": row['department_id'],
            "department_name": row['department_name'],
            "wecom_user_id": row['wecom_user_id'],
            "wecom_name": row['wecom_name'],
            "status": row['status'],
            "is_super_admin": bool(row['is_super_admin']),
            "created_at": row['created_at'],
            "updated_at": row['updated_at']
        }
        
        return {"code": 0, "data": employee}
        
    except Exception as e:
        return {"code": 1, "message": f"获取员工详情失败：{str(e)}"}


@router.put("/employees/{employee_id}")
def update_employee(
    employee_id: str, 
    data: EmployeeUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """更新员工信息"""
    try:
        # 只有超级管理员可以更新员工
        if not current_user.get('is_super_admin'):
            return {"code": 1, "message": "权限不足"}
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查员工是否存在
        cursor.execute("SELECT COUNT(*) FROM employees WHERE id = ?", (employee_id,))
        if cursor.fetchone()[0] == 0:
            conn.close()
            return {"code": 1, "message": "员工不存在"}
        
        # 构建更新字段
        update_fields = []
        params = []
        
        if data.name is not None:
            update_fields.append("name = ?")
            params.append(data.name)
        
        if data.password is not None:
            update_fields.append("password = ?")
            params.append(hash_password(data.password))
        
        if data.department_id is not None:
            update_fields.append("department_id = ?")
            params.append(data.department_id)
        
        if data.wecom_user_id is not None:
            update_fields.append("wecom_user_id = ?")
            params.append(data.wecom_user_id)
        
        if data.wecom_name is not None:
            update_fields.append("wecom_name = ?")
            params.append(data.wecom_name)
        
        if data.status is not None:
            update_fields.append("status = ?")
            params.append(data.status)
        
        if not update_fields:
            conn.close()
            return {"code": 1, "message": "没有要更新的字段"}
        
        # 更新时间
        update_fields.append("updated_at = ?")
        params.append(int(time.time() * 1000))
        
        # 执行更新
        params.append(employee_id)
        cursor.execute(f"""
            UPDATE employees 
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, params)
        
        conn.commit()
        conn.close()
        
        return {"code": 0, "message": "更新成功"}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"code": 1, "message": f"更新员工失败：{str(e)}"}


@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: str, current_user: dict = Depends(get_current_user)):
    """删除员工"""
    try:
        # 只有超级管理员可以删除员工
        if not current_user.get('is_super_admin'):
            return {"code": 1, "message": "权限不足"}
        
        # 不能删除超级管理员
        if employee_id == 'emp_super_admin':
            return {"code": 1, "message": "不能删除超级管理员"}
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查员工是否存在
        cursor.execute("SELECT COUNT(*) FROM employees WHERE id = ?", (employee_id,))
        if cursor.fetchone()[0] == 0:
            conn.close()
            return {"code": 1, "message": "员工不存在"}
        
        # 删除员工
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        
        # 删除相关的会话
        cursor.execute("DELETE FROM sessions WHERE employee_id = ?", (employee_id,))
        
        conn.commit()
        conn.close()
        
        return {"code": 0, "message": "删除成功"}
        
    except Exception as e:
        return {"code": 1, "message": f"删除员工失败：{str(e)}"}


@router.put("/employees/{employee_id}/status")
def toggle_employee_status(employee_id: str, current_user: dict = Depends(get_current_user)):
    """切换员工状态（启用/禁用）"""
    try:
        # 只有超级管理员可以切换状态
        if not current_user.get('is_super_admin'):
            return {"code": 1, "message": "权限不足"}
        
        # 不能禁用超级管理员
        if employee_id == 'emp_super_admin':
            return {"code": 1, "message": "不能禁用超级管理员"}
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 获取当前状态
        cursor.execute("SELECT status FROM employees WHERE id = ?", (employee_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"code": 1, "message": "员工不存在"}
        
        # 切换状态
        new_status = 'disabled' if row['status'] == 'active' else 'active'
        
        cursor.execute("""
            UPDATE employees 
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, int(time.time() * 1000), employee_id))
        
        # 如果禁用，清除该员工的所有会话
        if new_status == 'disabled':
            cursor.execute("DELETE FROM sessions WHERE employee_id = ?", (employee_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "code": 0,
            "message": f"已{'启用' if new_status == 'active' else '禁用'}",
            "data": {"status": new_status}
        }
        
    except Exception as e:
        return {"code": 1, "message": f"切换状态失败：{str(e)}"}


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    new_password: str


@router.put("/employees/{employee_id}/reset-password")
def reset_employee_password(
    employee_id: str, 
    data: ResetPasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """重置员工密码"""
    try:
        # 只有超级管理员可以重置密码
        if not current_user.get('is_super_admin'):
            return {"code": 1, "message": "权限不足"}
        
        if not data.new_password or len(data.new_password) < 6:
            return {"code": 1, "message": "密码至少6位"}
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查员工是否存在
        cursor.execute("SELECT COUNT(*) FROM employees WHERE id = ?", (employee_id,))
        if cursor.fetchone()[0] == 0:
            conn.close()
            return {"code": 1, "message": "员工不存在"}
        
        # 更新密码
        password_hash = hash_password(data.new_password)
        
        cursor.execute("""
            UPDATE employees 
            SET password = ?, updated_at = ?
            WHERE id = ?
        """, (password_hash, int(time.time() * 1000), employee_id))
        
        # 清除该员工的所有会话（强制重新登录）
        cursor.execute("DELETE FROM sessions WHERE employee_id = ?", (employee_id,))
        
        conn.commit()
        conn.close()
        
        return {"code": 0, "message": "密码重置成功"}
        
    except Exception as e:
        return {"code": 1, "message": f"重置密码失败：{str(e)}"}


# ========== 部门管理 API ==========

@router.get("/departments")
def get_departments(current_user: dict = Depends(get_current_user)):
    """获取部门列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询所有部门
        cursor.execute("""
            SELECT 
                d.*,
                COUNT(e.id) as employee_count
            FROM departments d
            LEFT JOIN employees e ON d.id = e.department_id AND (e.status = 1 OR e.status = '1')
            GROUP BY d.id
            ORDER BY d.created_at DESC
        """)
        
        departments = []
        for row in cursor.fetchall():
            dept = dict(row)
            # 解析 menu_permissions
            if dept['menu_permissions']:
                try:
                    dept['menu_permissions'] = json.loads(dept['menu_permissions'])
                except:
                    dept['menu_permissions'] = []
            else:
                dept['menu_permissions'] = []
            departments.append(dept)
        
        conn.close()
        
        return {
            "code": 0,
            "message": "success",
            "data": departments
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"code": 1, "message": f"获取部门列表失败：{str(e)}"}


@router.post("/departments")
def create_department(data: DepartmentCreate, current_user: dict = Depends(get_current_user)):
    """创建部门"""
    try:
        # 只有超级管理员可以创建部门
        if not current_user.get('is_super_admin'):
            return {"code": 1, "message": "权限不足"}
        
        if not data.name or not data.name.strip():
            return {"code": 1, "message": "部门名称不能为空"}
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查部门名称是否已存在
        cursor.execute("SELECT COUNT(*) FROM departments WHERE name = ?", (data.name,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return {"code": 1, "message": "部门名称已存在"}
        
        # 创建部门
        dept_id = f"dept_{uuid.uuid4().hex[:12]}"
        current_time = int(time.time() * 1000)
        
        cursor.execute("""
            INSERT INTO departments (id, name, description, menu_permissions, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (dept_id, data.name, data.description, None, current_time, current_time))
        
        conn.commit()
        
        # 返回新创建的部门
        cursor.execute("SELECT * FROM departments WHERE id = ?", (dept_id,))
        department = dict(cursor.fetchone())
        department['menu_permissions'] = []
        
        conn.close()
        
        return {
            "code": 0,
            "message": "创建成功",
            "data": department
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"code": 1, "message": f"创建部门失败：{str(e)}"}


@router.get("/departments/{department_id}")
def get_department(department_id: str, current_user: dict = Depends(get_current_user)):
    """获取部门详情"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM departments WHERE id = ?", (department_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"code": 1, "message": "部门不存在"}
        
        department = dict(row)
        
        # 解析 menu_permissions
        if department['menu_permissions']:
            try:
                department['menu_permissions'] = json.loads(department['menu_permissions'])
            except:
                department['menu_permissions'] = []
        else:
            department['menu_permissions'] = []
        
        # 获取部门员工列表
        cursor.execute("""
            SELECT id, account, name, wecom_name, status
            FROM employees
            WHERE department_id = ?
            ORDER BY created_at DESC
        """, (department_id,))
        
        department['employees'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "code": 0,
            "message": "success",
            "data": department
        }
        
    except Exception as e:
        return {"code": 1, "message": f"获取部门详情失败：{str(e)}"}


@router.put("/departments/{department_id}")
def update_department(
    department_id: str,
    data: DepartmentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新部门信息"""
    try:
        # 只有超级管理员可以更新部门
        if not current_user.get('is_super_admin'):
            return {"code": 1, "message": "权限不足"}
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查部门是否存在
        cursor.execute("SELECT COUNT(*) FROM departments WHERE id = ?", (department_id,))
        if cursor.fetchone()[0] == 0:
            conn.close()
            return {"code": 1, "message": "部门不存在"}
        
        # 如果更新名称，检查是否重复
        if data.name:
            cursor.execute(
                "SELECT COUNT(*) FROM departments WHERE name = ? AND id != ?",
                (data.name, department_id)
            )
            if cursor.fetchone()[0] > 0:
                conn.close()
                return {"code": 1, "message": "部门名称已存在"}
        
        # 构建更新语句
        update_fields = []
        params = []
        
        if data.name is not None:
            update_fields.append("name = ?")
            params.append(data.name)
        
        if data.description is not None:
            update_fields.append("description = ?")
            params.append(data.description)
        
        if data.menu_permissions is not None:
            update_fields.append("menu_permissions = ?")
            params.append(json.dumps(data.menu_permissions, ensure_ascii=False))
        
        if not update_fields:
            conn.close()
            return {"code": 1, "message": "没有要更新的字段"}
        
        # 更新时间
        update_fields.append("updated_at = ?")
        params.append(int(time.time() * 1000))
        
        # 执行更新
        params.append(department_id)
        cursor.execute(f"""
            UPDATE departments 
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, params)
        
        conn.commit()
        conn.close()
        
        return {"code": 0, "message": "更新成功"}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"code": 1, "message": f"更新部门失败：{str(e)}"}


@router.delete("/departments/{department_id}")
def delete_department(department_id: str, current_user: dict = Depends(get_current_user)):
    """删除部门"""
    try:
        # 只有超级管理员可以删除部门
        if not current_user.get('is_super_admin'):
            return {"code": 1, "message": "权限不足"}
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查部门是否存在
        cursor.execute("SELECT COUNT(*) FROM departments WHERE id = ?", (department_id,))
        if cursor.fetchone()[0] == 0:
            conn.close()
            return {"code": 1, "message": "部门不存在"}
        
        # 检查部门下是否有员工
        cursor.execute("SELECT COUNT(*) FROM employees WHERE department_id = ?", (department_id,))
        employee_count = cursor.fetchone()[0]
        
        if employee_count > 0:
            conn.close()
            return {"code": 1, "message": f"该部门下还有 {employee_count} 名员工，无法删除"}
        
        # 删除部门
        cursor.execute("DELETE FROM departments WHERE id = ?", (department_id,))
        
        conn.commit()
        conn.close()
        
        return {"code": 0, "message": "删除成功"}
        
    except Exception as e:
        return {"code": 1, "message": f"删除部门失败：{str(e)}"}


@router.put("/departments/{department_id}/permissions")
def update_department_permissions(
    department_id: str,
    permissions: dict,
    current_user: dict = Depends(get_current_user)
):
    """更新部门权限"""
    try:
        # 只有超级管理员可以配置权限
        if not current_user.get('is_super_admin'):
            return {"code": 1, "message": "权限不足"}
        
        # 从请求体中获取 menu_permissions
        menu_permissions = permissions.get('menu_permissions', [])
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查部门是否存在
        cursor.execute("SELECT COUNT(*) FROM departments WHERE id = ?", (department_id,))
        if cursor.fetchone()[0] == 0:
            conn.close()
            return {"code": 1, "message": "部门不存在"}
        
        # 更新权限
        cursor.execute("""
            UPDATE departments 
            SET menu_permissions = ?, updated_at = ?
            WHERE id = ?
        """, (json.dumps(menu_permissions, ensure_ascii=False), int(time.time() * 1000), department_id))
        
        conn.commit()
        conn.close()
        
        return {"code": 0, "message": "权限更新成功"}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"code": 1, "message": f"更新权限失败：{str(e)}"}

