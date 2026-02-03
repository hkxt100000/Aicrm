"""
员工管理和权限管理 API 诊断脚本
用于检查 API 是否正常工作，找出 500 错误的根本原因
"""
import sys
import os
import sqlite3
import json
import traceback

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from config import DB_PATH

print("="*80)
print("员工管理和权限管理 API 诊断")
print("="*80)

# ========== 1. 检查数据库连接 ==========
print("\n[1] 检查数据库连接")
print("-" * 80)

try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print(f"✅ 数据库连接成功: {DB_PATH}")
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")
    sys.exit(1)

# ========== 2. 检查必要的表是否存在 ==========
print("\n[2] 检查必要的表")
print("-" * 80)

required_tables = ['employees', 'departments', 'sessions']
for table in required_tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"✅ 表 '{table}' 存在，共 {count} 条记录")
    except Exception as e:
        print(f"❌ 表 '{table}' 不存在或查询失败: {e}")

# ========== 3. 检查 employees 表结构 ==========
print("\n[3] 检查 employees 表结构")
print("-" * 80)

try:
    cursor.execute("PRAGMA table_info(employees)")
    columns = cursor.fetchall()
    print("employees 表字段:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']} (NOT NULL: {col['notnull']}, DEFAULT: {col['dflt_value']})")
    
    # 检查关键字段
    column_names = [col['name'] for col in columns]
    required_fields = ['id', 'account', 'password', 'name', 'status', 'is_super_admin', 'department_id']
    for field in required_fields:
        if field in column_names:
            print(f"✅ 字段 '{field}' 存在")
        else:
            print(f"❌ 字段 '{field}' 不存在")
            
except Exception as e:
    print(f"❌ 检查表结构失败: {e}")
    traceback.print_exc()

# ========== 4. 检查 departments 表结构 ==========
print("\n[4] 检查 departments 表结构")
print("-" * 80)

try:
    cursor.execute("PRAGMA table_info(departments)")
    columns = cursor.fetchall()
    print("departments 表字段:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
    
    column_names = [col['name'] for col in columns]
    required_fields = ['id', 'name', 'description', 'menu_permissions']
    for field in required_fields:
        if field in column_names:
            print(f"✅ 字段 '{field}' 存在")
        else:
            print(f"❌ 字段 '{field}' 不存在")
            
except Exception as e:
    print(f"❌ 检查表结构失败: {e}")
    traceback.print_exc()

# ========== 5. 检查员工数据 ==========
print("\n[5] 检查员工数据")
print("-" * 80)

try:
    cursor.execute("""
        SELECT id, account, name, status, is_super_admin, department_id
        FROM employees
        LIMIT 5
    """)
    employees = cursor.fetchall()
    
    if employees:
        print(f"找到 {len(employees)} 个员工（显示前5个）:")
        for emp in employees:
            print(f"  ID: {emp['id']}")
            print(f"    账号: {emp['account']}")
            print(f"    姓名: {emp['name']}")
            print(f"    状态: {emp['status']} (类型: {type(emp['status'])})")
            print(f"    超级管理员: {emp['is_super_admin']} (类型: {type(emp['is_super_admin'])})")
            print(f"    部门ID: {emp['department_id']}")
            print()
    else:
        print("❌ 没有员工数据")
        
except Exception as e:
    print(f"❌ 查询员工数据失败: {e}")
    traceback.print_exc()

# ========== 6. 检查部门数据 ==========
print("\n[6] 检查部门数据")
print("-" * 80)

try:
    cursor.execute("""
        SELECT id, name, description, menu_permissions
        FROM departments
        LIMIT 5
    """)
    departments = cursor.fetchall()
    
    if departments:
        print(f"找到 {len(departments)} 个部门（显示前5个）:")
        for dept in departments:
            print(f"  ID: {dept['id']}")
            print(f"    名称: {dept['name']}")
            print(f"    描述: {dept['description']}")
            print(f"    权限: {dept['menu_permissions']}")
            print()
    else:
        print("⚠️  没有部门数据（这是正常的，可以在页面上创建）")
        
except Exception as e:
    print(f"❌ 查询部门数据失败: {e}")
    traceback.print_exc()

# ========== 7. 模拟 /api/auth/employees API 查询 ==========
print("\n[7] 模拟 /api/auth/employees API 查询")
print("-" * 80)

try:
    page = 1
    limit = 20
    offset = (page - 1) * limit
    
    # 查询总数
    cursor.execute("SELECT COUNT(*) FROM employees WHERE 1=1")
    total = cursor.fetchone()[0]
    print(f"✅ 员工总数: {total}")
    
    # 查询列表
    cursor.execute("""
        SELECT 
            e.id, e.account, e.name, e.department_id, 
            e.wecom_user_id, e.wecom_name, e.status, 
            e.is_super_admin, e.created_at, e.updated_at,
            d.name as department_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE 1=1
        ORDER BY e.created_at DESC
        LIMIT ? OFFSET ?
    """, [limit, offset])
    
    employees = []
    rows = cursor.fetchall()
    print(f"✅ 查询到 {len(rows)} 条员工记录")
    
    for row in rows:
        emp = {
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
        employees.append(emp)
        print(f"\n  员工: {emp['name']} ({emp['account']})")
        print(f"    状态: {emp['status']}")
        print(f"    超管: {emp['is_super_admin']}")
        print(f"    部门: {emp['department_name'] or '未分配'}")
    
    # 模拟返回的 JSON
    response = {
        "code": 0,
        "data": employees,
        "total": total,
        "page": page,
        "limit": limit
    }
    
    print(f"\n✅ API 返回结构预览:")
    print(f"  code: {response['code']}")
    print(f"  data: 数组，共 {len(response['data'])} 项")
    print(f"  total: {response['total']}")
    print(f"  page: {response['page']}")
    print(f"  limit: {response['limit']}")
    
except Exception as e:
    print(f"❌ 模拟 API 查询失败: {e}")
    traceback.print_exc()

# ========== 8. 模拟 /api/auth/departments API 查询 ==========
print("\n[8] 模拟 /api/auth/departments API 查询")
print("-" * 80)

try:
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
    rows = cursor.fetchall()
    print(f"✅ 查询到 {len(rows)} 个部门")
    
    for row in rows:
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
        
        print(f"\n  部门: {dept['name']}")
        print(f"    员工数: {dept['employee_count']}")
        print(f"    权限数: {len(dept['menu_permissions'])}")
    
    # 模拟返回的 JSON
    response = {
        "code": 0,
        "message": "success",
        "data": departments
    }
    
    print(f"\n✅ API 返回结构预览:")
    print(f"  code: {response['code']}")
    print(f"  message: {response['message']}")
    print(f"  data: 数组，共 {len(response['data'])} 项")
    
except Exception as e:
    print(f"❌ 模拟 API 查询失败: {e}")
    traceback.print_exc()

# ========== 9. 检查 sessions 表（Token 验证相关） ==========
print("\n[9] 检查 sessions 表")
print("-" * 80)

try:
    cursor.execute("SELECT COUNT(*) FROM sessions WHERE expires_at > ?", [int(time.time() * 1000)])
    valid_sessions = cursor.fetchone()[0]
    print(f"✅ 有效会话数: {valid_sessions}")
    
    if valid_sessions > 0:
        cursor.execute("""
            SELECT s.*, e.account, e.name
            FROM sessions s
            JOIN employees e ON s.employee_id = e.id
            WHERE s.expires_at > ?
            LIMIT 5
        """, [int(time.time() * 1000)])
        
        sessions = cursor.fetchall()
        print(f"\n最近的 {len(sessions)} 个有效会话:")
        for sess in sessions:
            print(f"  Token: {sess['token'][:20]}...")
            print(f"    用户: {sess['name']} ({sess['account']})")
            print(f"    过期时间: {sess['expires_at']}")
            print()
    else:
        print("⚠️  没有有效的会话，需要重新登录")
        
except Exception as e:
    print(f"❌ 检查会话失败: {e}")
    # 不影响后续检查

# ========== 10. 检查 auth_api.py 的 get_current_user 函数 ==========
print("\n[10] 检查 get_current_user 函数")
print("-" * 80)

try:
    # 读取 auth_api.py
    auth_api_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'auth_api.py')
    with open(auth_api_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找 get_current_user 函数
    if 'async def get_current_user' in content:
        print("✅ 找到 get_current_user 函数")
        
        # 检查是否抛出 HTTPException
        if 'raise HTTPException' in content:
            print("⚠️  函数中使用了 HTTPException（可能导致 500 错误）")
            
            # 查找具体的错误处理
            import re
            exceptions = re.findall(r'raise HTTPException\(.*?\)', content, re.DOTALL)
            if exceptions:
                print(f"\n  找到 {len(exceptions)} 处 HTTPException:")
                for i, exc in enumerate(exceptions[:3], 1):  # 只显示前3个
                    print(f"\n  [{i}] {exc[:100]}...")
        else:
            print("✅ 没有使用 HTTPException")
    else:
        print("❌ 未找到 get_current_user 函数")
        
except Exception as e:
    print(f"❌ 检查函数失败: {e}")

# ========== 11. 检查 app.py 的异常处理器 ==========
print("\n[11] 检查 app.py 的全局异常处理器")
print("-" * 80)

try:
    app_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app.py')
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有异常处理器
    if '@app.exception_handler(HTTPException)' in content:
        print("✅ 找到全局 HTTPException 处理器")
    else:
        print("❌ 未找到全局 HTTPException 处理器")
        print("   这可能导致 HTTPException 返回 HTML 而不是 JSON")
        
    # 检查是否有其他异常处理
    if 'exception_handler' in content:
        print("✅ 文件中包含异常处理相关代码")
    else:
        print("⚠️  文件中没有异常处理相关代码")
        
except Exception as e:
    print(f"❌ 检查 app.py 失败: {e}")

# ========== 12. 总结诊断结果 ==========
print("\n" + "="*80)
print("诊断总结")
print("="*80)

print("""
根据以上诊断，可能的问题：

1. 如果 employees/departments 表数据正常，但 API 返回 500：
   → 检查 get_current_user 是否正确验证 Token
   → 检查是否有全局异常处理器

2. 如果 sessions 表中没有有效会话：
   → 需要重新登录获取新的 Token

3. 如果 HTTPException 没有被正确处理：
   → 需要在 app.py 中添加全局异常处理器
   → 将 HTML 错误转换为 JSON 格式

4. 如果数据库表结构不完整：
   → 需要运行初始化脚本创建缺失的字段

请根据以上诊断结果进行修复。
""")

conn.close()

print("\n诊断完成！")
print("="*80)
