"""
Token 验证诊断脚本
检查 Token 验证流程是否正常
"""
import sys
import os
import time
import sqlite3

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from config import DB_PATH

print("="*80)
print("Token 验证诊断")
print("="*80)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# ========== 1. 检查所有会话 ==========
print("\n[1] 检查 sessions 表中的所有会话")
print("-" * 80)

try:
    cursor.execute("SELECT COUNT(*) FROM sessions")
    total_sessions = cursor.fetchone()[0]
    print(f"✅ 总会话数: {total_sessions}")
    
    current_time = int(time.time() * 1000)
    print(f"   当前时间戳: {current_time}")
    
    cursor.execute("""
        SELECT 
            s.id, s.employee_id, s.token, s.expires_at, s.created_at,
            e.account, e.name, e.is_super_admin
        FROM sessions s
        LEFT JOIN employees e ON s.employee_id = e.id
        ORDER BY s.created_at DESC
        LIMIT 5
    """)
    
    sessions = cursor.fetchall()
    print(f"\n最近的 {len(sessions)} 个会话:")
    
    for sess in sessions:
        is_expired = sess['expires_at'] <= current_time
        status = "❌ 已过期" if is_expired else "✅ 有效"
        
        print(f"\n  Session ID: {sess['id']}")
        print(f"    Token: {sess['token'][:30]}...")
        print(f"    用户: {sess['name']} ({sess['account']})")
        print(f"    超管: {sess['is_super_admin']}")
        print(f"    创建时间: {sess['created_at']}")
        print(f"    过期时间: {sess['expires_at']}")
        print(f"    状态: {status}")
        
        # 计算剩余时间
        if not is_expired:
            remaining_ms = sess['expires_at'] - current_time
            remaining_hours = remaining_ms / (1000 * 60 * 60)
            print(f"    剩余时间: {remaining_hours:.2f} 小时")
            
except Exception as e:
    print(f"❌ 检查会话失败: {e}")
    import traceback
    traceback.print_exc()

# ========== 2. 检查有效会话数量 ==========
print("\n[2] 检查有效会话")
print("-" * 80)

try:
    current_time = int(time.time() * 1000)
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM sessions 
        WHERE expires_at > ?
    """, [current_time])
    
    valid_count = cursor.fetchone()[0]
    print(f"✅ 有效会话数: {valid_count}")
    
    if valid_count == 0:
        print("\n⚠️  警告：没有有效的会话！")
        print("   可能的原因：")
        print("   1. 所有 Token 都已过期")
        print("   2. 用户需要重新登录")
        print("\n   解决方法：")
        print("   1. 在浏览器中重新登录")
        print("   2. 或者运行: python create_test_session.py 创建测试会话")
    else:
        # 显示有效会话详情
        cursor.execute("""
            SELECT 
                s.token, e.account, e.name, e.is_super_admin,
                s.expires_at
            FROM sessions s
            JOIN employees e ON s.employee_id = e.id
            WHERE s.expires_at > ?
            ORDER BY s.created_at DESC
            LIMIT 3
        """, [current_time])
        
        valid_sessions = cursor.fetchall()
        print(f"\n有效会话详情（显示前3个）:")
        for sess in valid_sessions:
            print(f"\n  用户: {sess['name']} ({sess['account']})")
            print(f"    超管: {sess['is_super_admin']}")
            print(f"    Token: {sess['token'][:30]}...")
            remaining_ms = sess['expires_at'] - current_time
            remaining_hours = remaining_ms / (1000 * 60 * 60)
            print(f"    剩余时间: {remaining_hours:.2f} 小时")
            
except Exception as e:
    print(f"❌ 检查有效会话失败: {e}")
    import traceback
    traceback.print_exc()

# ========== 3. 测试 verify_token 函数 ==========
print("\n[3] 测试 verify_token 函数")
print("-" * 80)

try:
    # 获取一个有效的 token
    current_time = int(time.time() * 1000)
    cursor.execute("""
        SELECT token, employee_id
        FROM sessions
        WHERE expires_at > ?
        ORDER BY created_at DESC
        LIMIT 1
    """, [current_time])
    
    session = cursor.fetchone()
    
    if session:
        test_token = session['token']
        print(f"✅ 找到测试 Token: {test_token[:30]}...")
        
        # 模拟 verify_token 的逻辑
        cursor.execute("""
            SELECT s.*, e.* 
            FROM sessions s
            JOIN employees e ON s.employee_id = e.id
            WHERE s.token = ? AND s.expires_at > ? AND (e.status = 1 OR e.status = '1')
        """, (test_token, current_time))
        
        row = cursor.fetchone()
        
        if row:
            print("✅ Token 验证成功！")
            print(f"   用户: {row['name']} ({row['account']})")
            print(f"   超管: {row['is_super_admin']}")
            print(f"   状态: {row['status']}")
        else:
            print("❌ Token 验证失败！")
            print("   可能的原因：")
            print("   1. Token 不存在")
            print("   2. Token 已过期")
            print("   3. 员工状态不是 1 或 '1'")
    else:
        print("❌ 没有找到有效的 Token 进行测试")
        print("   需要重新登录或创建测试会话")
        
except Exception as e:
    print(f"❌ 测试 verify_token 失败: {e}")
    import traceback
    traceback.print_exc()

# ========== 4. 检查员工状态 ==========
print("\n[4] 检查员工状态")
print("-" * 80)

try:
    cursor.execute("""
        SELECT id, account, name, status, is_super_admin
        FROM employees
    """)
    
    employees = cursor.fetchall()
    print(f"✅ 找到 {len(employees)} 个员工:")
    
    for emp in employees:
        status_ok = emp['status'] == 1 or emp['status'] == '1'
        status_icon = "✅" if status_ok else "❌"
        
        print(f"\n  {status_icon} {emp['name']} ({emp['account']})")
        print(f"       状态: {emp['status']} (类型: {type(emp['status']).__name__})")
        print(f"       超管: {emp['is_super_admin']}")
        
        if not status_ok:
            print(f"       ⚠️  警告：状态不是 1 或 '1'，无法登录！")
            
except Exception as e:
    print(f"❌ 检查员工状态失败: {e}")
    import traceback
    traceback.print_exc()

# ========== 5. 模拟完整的认证流程 ==========
print("\n[5] 模拟完整的认证流程")
print("-" * 80)

try:
    # 获取一个有效的 token
    current_time = int(time.time() * 1000)
    cursor.execute("""
        SELECT token
        FROM sessions
        WHERE expires_at > ?
        ORDER BY created_at DESC
        LIMIT 1
    """, [current_time])
    
    session = cursor.fetchone()
    
    if session:
        test_token = session['token']
        print(f"步骤 1: 获取 Token")
        print(f"  Token: {test_token[:30]}...")
        
        print(f"\n步骤 2: 验证 Token（模拟 verify_token 函数）")
        cursor.execute("""
            SELECT s.*, e.* 
            FROM sessions s
            JOIN employees e ON s.employee_id = e.id
            WHERE s.token = ? AND s.expires_at > ? AND (e.status = 1 OR e.status = '1')
        """, (test_token, current_time))
        
        row = cursor.fetchone()
        
        if row:
            print(f"  ✅ Token 验证成功")
            
            user_info = {
                'id': row['id'],
                'account': row['account'],
                'name': row['name'],
                'is_super_admin': bool(row['is_super_admin'])
            }
            
            print(f"\n步骤 3: 构建用户信息")
            print(f"  用户 ID: {user_info['id']}")
            print(f"  账号: {user_info['account']}")
            print(f"  姓名: {user_info['name']}")
            print(f"  超管: {user_info['is_super_admin']}")
            
            print(f"\n步骤 4: 检查权限（员工管理需要超管权限）")
            if user_info['is_super_admin']:
                print(f"  ✅ 有超管权限，可以访问员工管理")
            else:
                print(f"  ❌ 无超管权限，无法访问员工管理")
                
            print(f"\n✅ 完整认证流程模拟成功！")
            print(f"\n结论：后端认证逻辑正常，问题可能在：")
            print(f"  1. 前端没有正确发送 Token")
            print(f"  2. 前端 Token 已过期")
            print(f"  3. 前端 Token 格式错误（缺少 'Bearer ' 前缀）")
        else:
            print(f"  ❌ Token 验证失败")
    else:
        print("❌ 没有有效的 Token，需要重新登录")
        
except Exception as e:
    print(f"❌ 模拟认证流程失败: {e}")
    import traceback
    traceback.print_exc()

# ========== 总结 ==========
print("\n" + "="*80)
print("诊断总结")
print("="*80)

try:
    current_time = int(time.time() * 1000)
    cursor.execute("SELECT COUNT(*) FROM sessions WHERE expires_at > ?", [current_time])
    valid_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 1 OR status = '1'")
    active_employees = cursor.fetchone()[0]
    
    print(f"\n数据库状态:")
    print(f"  ✅ 活跃员工: {active_employees}")
    print(f"  {'✅' if valid_count > 0 else '❌'} 有效会话: {valid_count}")
    
    if valid_count > 0:
        print(f"\n✅ 后端认证系统正常！")
        print(f"\n如果前端仍然出现 500 错误，问题可能是：")
        print(f"  1. 前端 Token 与数据库不匹配（需要重新登录）")
        print(f"  2. 前端 Token 格式错误（检查是否有 'Bearer ' 前缀）")
        print(f"  3. 前端请求头错误（检查 Authorization header）")
        print(f"\n建议操作：")
        print(f"  1. 在浏览器中退出登录")
        print(f"  2. 清除浏览器缓存和 localStorage")
        print(f"  3. 重新登录")
        print(f"  4. 查看浏览器控制台的 Network 标签，检查请求头")
    else:
        print(f"\n❌ 没有有效会话！")
        print(f"\n解决方法：")
        print(f"  1. 在浏览器中重新登录")
        print(f"  2. 或运行测试脚本创建会话")
        
except Exception as e:
    print(f"❌ 生成总结失败: {e}")

conn.close()

print("\n诊断完成！")
print("="*80)
