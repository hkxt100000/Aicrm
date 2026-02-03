#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证和API诊断脚本
用于检查认证系统、权限配置、API 响应等问题
"""
import os
import sys
import sqlite3
import json
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import DB_PATH, API_TOKEN
from auth_middleware import get_current_user

def print_section(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_database():
    """检查数据库连接和表结构"""
    print_section("1. 数据库检查")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return False
    
    print(f"✓ 数据库文件存在: {DB_PATH}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查必要的表
        tables_to_check = ['employees', 'departments', 'sessions', 'customers']
        
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cursor.fetchone():
                # 获取表的记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✓ 表 {table:20s} 存在，记录数: {count}")
            else:
                print(f"❌ 表 {table:20s} 不存在")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False

def check_super_admin():
    """检查超级管理员账号"""
    print_section("2. 超级管理员账号检查")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, account, name, department_id, is_super_admin, status, 
                   wecom_user_id, wecom_name
            FROM employees 
            WHERE account = '19938885888'
        """)
        
        row = cursor.fetchone()
        
        if not row:
            print("❌ 超级管理员账号不存在")
            conn.close()
            return None
        
        print(f"✓ 账号存在")
        print(f"  ID: {row['id']}")
        print(f"  账号: {row['account']}")
        print(f"  姓名: {row['name']}")
        print(f"  部门ID: {row['department_id']}")
        print(f"  超级管理员: {bool(row['is_super_admin'])}")
        print(f"  状态: {'启用' if row['status'] == 1 else '禁用'}")
        print(f"  企微用户ID: {row['wecom_user_id'] or '未绑定'}")
        print(f"  企微姓名: {row['wecom_name'] or '未绑定'}")
        
        if not row['is_super_admin']:
            print("❌ 该账号不是超级管理员！")
        
        if row['status'] != 1:
            print("❌ 该账号已被禁用！")
        
        conn.close()
        return dict(row)
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return None

def check_sessions():
    """检查当前会话"""
    print_section("3. 会话检查")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查询最近的会话
        cursor.execute("""
            SELECT s.id, s.employee_id, s.token, s.expires_at, s.created_at,
                   e.account, e.name
            FROM sessions s
            LEFT JOIN employees e ON s.employee_id = e.id
            ORDER BY s.created_at DESC
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("❌ 没有任何会话记录")
            conn.close()
            return
        
        print(f"✓ 找到 {len(rows)} 条最近的会话记录\n")
        
        import time
        current_time = int(time.time() * 1000)
        
        for i, row in enumerate(rows, 1):
            is_expired = row['expires_at'] < current_time
            status = "❌ 已过期" if is_expired else "✓ 有效"
            
            print(f"会话 {i}:")
            print(f"  ID: {row['id']}")
            print(f"  员工: {row['name']} ({row['account']})")
            print(f"  Token: {row['token'][:20]}...")
            print(f"  创建时间: {row['created_at']}")
            print(f"  过期时间: {row['expires_at']}")
            print(f"  状态: {status}")
            print()
        
        conn.close()
    except Exception as e:
        print(f"❌ 检查失败: {e}")

def test_token_validation():
    """测试 token 验证"""
    print_section("4. Token 验证测试")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取最新的有效 token
        import time
        current_time = int(time.time() * 1000)
        
        cursor.execute("""
            SELECT token, employee_id 
            FROM sessions 
            WHERE expires_at > ?
            ORDER BY created_at DESC 
            LIMIT 1
        """, (current_time,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print("❌ 没有有效的 token")
            return
        
        token = row['token']
        print(f"✓ 找到有效 token: {token[:20]}...")
        
        # 测试 get_current_user
        user = get_current_user(token)
        
        if not user:
            print("❌ Token 验证失败")
            return
        
        print("\n✓ Token 验证成功，用户信息:")
        print(f"  ID: {user['id']}")
        print(f"  姓名: {user['name']}")
        print(f"  账号: {user['account']}")
        print(f"  超级管理员: {user['is_super_admin']}")
        print(f"  企微用户ID: {user.get('wecom_user_id', '未绑定')}")
        print(f"  部门: {user.get('department_name', '无')}")
        print(f"  菜单权限数量: {len(user.get('menu_permissions', []))}")
        
        if user['is_super_admin']:
            print("\n✓ 超级管理员权限列表:")
            permissions = user.get('menu_permissions', [])
            for i, perm in enumerate(permissions, 1):
                print(f"    {i:2d}. {perm}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def check_customers_data():
    """检查客户数据"""
    print_section("5. 客户数据检查")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查客户总数
        cursor.execute("SELECT COUNT(*) FROM customers")
        total = cursor.fetchone()[0]
        print(f"✓ 客户总数: {total}")
        
        if total == 0:
            print("❌ 没有客户数据！请先同步客户数据。")
            conn.close()
            return
        
        # 检查最近添加的客户
        cursor.execute("""
            SELECT id, name, external_userid, owner_userid, add_time 
            FROM customers 
            ORDER BY add_time DESC 
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        print(f"\n最近添加的 {len(rows)} 个客户:")
        for i, row in enumerate(rows, 1):
            print(f"  {i}. {row[1]} (ID: {row[0]}, 所属: {row[3]})")
        
        # 检查 owner_userid 分布
        cursor.execute("""
            SELECT owner_userid, COUNT(*) as count 
            FROM customers 
            GROUP BY owner_userid 
            ORDER BY count DESC 
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        print(f"\n客户所属员工分布（Top 5）:")
        for i, (owner, count) in enumerate(rows, 1):
            print(f"  {i}. {owner}: {count} 个客户")
        
        conn.close()
    except Exception as e:
        print(f"❌ 检查失败: {e}")

def check_api_token():
    """检查 API Token 配置"""
    print_section("6. API Token 检查")
    
    try:
        print(f"✓ API_TOKEN 已配置")
        print(f"  值: {API_TOKEN[:10]}... (长度: {len(API_TOKEN)})")
    except Exception as e:
        print(f"❌ API_TOKEN 未配置: {e}")

def simulate_api_request():
    """模拟 API 请求"""
    print_section("7. 模拟 API 请求")
    
    try:
        import time
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取有效 token
        current_time = int(time.time() * 1000)
        cursor.execute("""
            SELECT token 
            FROM sessions 
            WHERE expires_at > ?
            ORDER BY created_at DESC 
            LIMIT 1
        """, (current_time,))
        
        row = cursor.fetchone()
        if not row:
            print("❌ 没有有效 token，无法模拟")
            conn.close()
            return
        
        token = row['token']
        
        # 模拟验证流程
        print("✓ 模拟请求: GET /api/customers")
        print(f"  Authorization: Bearer {token[:20]}...")
        
        # 验证 token
        user = get_current_user(token)
        if not user:
            print("❌ Token 验证失败")
            conn.close()
            return
        
        print(f"✓ Token 验证通过")
        print(f"  用户: {user['name']} ({user['account']})")
        print(f"  超级管理员: {user['is_super_admin']}")
        
        # 查询客户数据
        if user['is_super_admin']:
            # 超级管理员看所有数据
            cursor.execute("SELECT COUNT(*) FROM customers")
            count = cursor.fetchone()[0]
            print(f"✓ 超级管理员查询结果: {count} 个客户")
        else:
            # 普通员工只看自己的数据
            wecom_user_id = user.get('wecom_user_id')
            if wecom_user_id:
                cursor.execute("SELECT COUNT(*) FROM customers WHERE owner_userid = ?", (wecom_user_id,))
                count = cursor.fetchone()[0]
                print(f"✓ 普通员工查询结果: {count} 个客户 (owner_userid={wecom_user_id})")
            else:
                print("❌ 普通员工未绑定企业微信，无法查询数据")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 模拟失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  认证和API诊断脚本")
    print("="*60)
    print(f"  数据库路径: {DB_PATH}")
    print("="*60)
    
    # 1. 检查数据库
    if not check_database():
        print("\n⚠️ 数据库检查失败，后续检查可能不准确")
    
    # 2. 检查超级管理员
    admin = check_super_admin()
    
    # 3. 检查会话
    check_sessions()
    
    # 4. 测试 token 验证
    test_token_validation()
    
    # 5. 检查客户数据
    check_customers_data()
    
    # 6. 检查 API Token
    check_api_token()
    
    # 7. 模拟 API 请求
    simulate_api_request()
    
    # 总结
    print_section("诊断完成")
    print("\n如果以上检查都通过，但前端仍然无法加载数据，请提供:")
    print("1. 浏览器控制台截图（Console + Network）")
    print("2. 服务器控制台输出")
    print("3. 本脚本的完整输出\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
