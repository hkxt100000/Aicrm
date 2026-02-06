"""
认证中间件
用于验证 token 和保护 API
"""
import sqlite3
import jwt
from datetime import datetime
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse

from config import DB_PATH

# JWT 密钥（生产环境应该从环境变量读取）
JWT_SECRET = "thc_crm_secret_key_2025"
JWT_ALGORITHM = "HS256"


def verify_token(token: str) -> Optional[dict]:
    """
    验证 JWT token
    返回用户信息，如果无效则返回 None
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # 检查是否过期
        if payload.get('exp', 0) < datetime.now().timestamp():
            return None
        
        return payload
    except:
        return None


def get_current_user(token: str) -> Optional[dict]:
    """
    根据 token 获取当前用户信息
    使用数据库 sessions 表验证（与 auth_api.py 一致）
    """
    import time
    
    # 从数据库查询 token
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    current_time = int(time.time() * 1000)
    
    # 查询会话
    cursor.execute("""
        SELECT 
            e.id, e.account, e.name, e.department_id, 
            e.status, e.is_super_admin, e.wecom_user_id, e.wecom_name,
            d.name as department_name, d.menu_permissions
        FROM sessions s
        JOIN employees e ON s.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE s.token = ? AND s.expires_at > ? AND (e.status = 1 OR e.status = '1')
    """, (token, current_time))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    # 转换为字典
    user = {
        'id': row['id'],
        'account': row['account'],
        'name': row['name'],
        'department_id': row['department_id'],
        'department_name': row['department_name'] if row['department_name'] else None,
        'is_super_admin': bool(row['is_super_admin']),
        'wecom_user_id': row['wecom_user_id'],
        'wecom_name': row['wecom_name'],
        'menu_permissions': []
    }
    
    # 解析菜单权限
    if row['menu_permissions']:
        try:
            import json
            user['menu_permissions'] = json.loads(row['menu_permissions'])
        except:
            user['menu_permissions'] = []
    
    # 超级管理员拥有所有权限
    if user['is_super_admin']:
        user['menu_permissions'] = [
            'dashboard',                    # 工作台
            'customers',                    # 客户列表
            'customer-profile',             # 客户画像
            'enterprise-tags',              # 企业标签
            'enterprise-contacts',          # 企业通讯录
            'customer-groups',              # 客户群列表
            'group-tags',                   # 客户群标签
            'welcome-msg',                  # 欢迎语设置
            'customer-broadcast',           # 客户群发
            'moments-publish',              # 发朋友圈
            'moments-record',               # 朋友圈记录
            'group-welcome',                # 进群欢迎语
            'group-broadcast',              # 客户群群发
            'supplier-notify',              # 供应商通知群
            'agent-notify',                 # 代理商通知群
            'data-sources',                 # 源数据管理（父级）
            'data-sources-internal',        # 内部数据源
            'data-sources-external',        # 外部数据源
            'spreadsheet',                  # 企微智能表格（父级）
            'spreadsheet-internal',         # 对内智能表格
            'spreadsheet-external',         # 对外智能表
            'order-data',                   # 订单数据
            'supplier-data',                # 供应商数据
            'product-data',                 # 产品数据
            'agent-data',                   # 代理商数据
            'finance-data',                 # 财务数据
            'business-data',                # 商务数据
            'promoter',                     # 推客管理
            'system-manage',                # 系统管理（父级）
            'system-config',                # 系统配置
            'employee-manage',              # 员工管理
            'permission-manage'             # 权限管理
        ]
    
    return user


async def auth_middleware(request: Request, call_next):
    """
    认证中间件
    检查所有需要认证的请求
    """
    path = request.url.path
    
    # 白名单：不需要认证的路径
    whitelist = [
        '/api/auth/login',
        '/api/auth/logout',
        '/api/auth/current',  # 验证 token 的接口也要放行
        '/static/',
        '/login.html',
        '/favicon.ico'
    ]
    
    # 检查是否在白名单中
    if any(path.startswith(w) for w in whitelist):
        return await call_next(request)
    
    # API 请求需要验证 token（除了白名单）
    if path.startswith('/api/'):
        # 检查是否有旧的 api_token 参数（兼容旧 API）
        query_params = dict(request.query_params)
        api_token = query_params.get('api_token')
        
        # 如果有 api_token 参数，说明是旧 API，放行（由各 API 自己的 check_token 处理）
        if api_token:
            return await call_next(request)
        
        # 新认证系统：从 Header 获取 Bearer token
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"code": 1, "message": "未登录或登录已过期"}
            )
        
        token = auth_header[7:]  # 去掉 "Bearer "
        user = get_current_user(token)
        
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"code": 1, "message": "登录已过期，请重新登录"}
            )
        
        # 将用户信息附加到 request.state
        request.state.user = user
    
    # HTML 页面请求不拦截（由前端 JS 检查）
    
    return await call_next(request)
