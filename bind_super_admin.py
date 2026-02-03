#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
绑定超级管理员到企业微信员工 msYang
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import DB_PATH

def bind_super_admin_to_wecom():
    """绑定超级管理员到 msYang"""
    print("="*60)
    print("  绑定超级管理员到企业微信")
    print("="*60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. 查看当前状态
        print("\n【当前状态】")
        cursor.execute("""
            SELECT account, name, wecom_user_id, wecom_name, status, is_super_admin
            FROM employees
            WHERE account = '19938885888'
        """)
        row = cursor.fetchone()
        
        if not row:
            print("❌ 超级管理员账号不存在")
            conn.close()
            return False
        
        print(f"  账号: {row['account']}")
        print(f"  姓名: {row['name']}")
        print(f"  企微用户ID: {row['wecom_user_id'] or '未绑定'}")
        print(f"  企微姓名: {row['wecom_name'] or '未绑定'}")
        print(f"  状态: {'启用' if str(row['status']) in ('1', 1) else '禁用'}")
        print(f"  超级管理员: {'是' if row['is_super_admin'] else '否'}")
        
        # 2. 绑定到 msYang
        print("\n【绑定到 msYang】")
        cursor.execute("""
            UPDATE employees
            SET wecom_user_id = 'msYang',
                wecom_name = 'msYang',
                status = 1,
                is_super_admin = 1
            WHERE account = '19938885888'
        """)
        
        affected = cursor.rowcount
        print(f"  受影响行数: {affected}")
        
        conn.commit()
        print("  ✓ 已提交事务")
        
        # 3. 验证
        print("\n【绑定后状态】")
        cursor.execute("""
            SELECT account, name, wecom_user_id, wecom_name, status, is_super_admin
            FROM employees
            WHERE account = '19938885888'
        """)
        row = cursor.fetchone()
        
        if row:
            print(f"  账号: {row['account']}")
            print(f"  姓名: {row['name']}")
            print(f"  企微用户ID: {row['wecom_user_id']}")
            print(f"  企微姓名: {row['wecom_name']}")
            print(f"  状态: {'启用' if str(row['status']) in ('1', 1) else '禁用'}")
            print(f"  超级管理员: {'是' if row['is_super_admin'] else '否'}")
            
            if row['wecom_user_id'] == 'msYang':
                print("\n  ✅ 绑定成功！")
            else:
                print(f"\n  ❌ 绑定失败，当前值: {row['wecom_user_id']}")
        
        # 4. 检查数据
        print("\n【检查客户数据】")
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(DISTINCT owner_userid) as owners
            FROM customers
        """)
        row = cursor.fetchone()
        print(f"  客户总数: {row['total']:,}")
        print(f"  所属员工数: {row['owners']}")
        
        # 检查 msYang 的客户数
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM customers
            WHERE owner_userid = 'msYang'
        """)
        row = cursor.fetchone()
        print(f"  msYang 的客户数: {row['count']:,}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ 绑定失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_after_bind():
    """测试绑定后的认证"""
    print("\n" + "="*60)
    print("  测试绑定后的认证")
    print("="*60)
    
    try:
        from auth_middleware import get_current_user
        import time
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取最新 token
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
            print("\n⚠️ 没有有效 token，请重新登录")
            conn.close()
            return
        
        token = row['token']
        print(f"\n✓ 找到 token: {token[:30]}...")
        
        # 验证 token
        user = get_current_user(token)
        
        if not user:
            print("❌ Token 验证失败")
            print("\n请确保:")
            print("  1. 已更新 auth_middleware.py（兼容 status 类型）")
            print("  2. 已重启服务")
            print("  3. 或重新登录")
            conn.close()
            return
        
        print("✅ Token 验证成功！")
        print(f"\n用户信息:")
        print(f"  姓名: {user['name']}")
        print(f"  账号: {user['account']}")
        print(f"  超级管理员: {user['is_super_admin']}")
        print(f"  企微用户ID: {user.get('wecom_user_id', '未绑定')}")
        print(f"  企微姓名: {user.get('wecom_name', '未绑定')}")
        
        if user.get('wecom_user_id') == 'msYang':
            print("\n  ✅ 已绑定到 msYang")
        else:
            print(f"\n  ⚠️ 企微用户ID: {user.get('wecom_user_id')}")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  绑定超级管理员到企业微信脚本")
    print("="*60)
    print(f"  数据库: {DB_PATH}")
    print("="*60)
    
    # 1. 绑定
    success = bind_super_admin_to_wecom()
    
    if not success:
        print("\n❌ 绑定失败，请检查错误信息")
        return
    
    # 2. 测试
    test_after_bind()
    
    # 3. 总结
    print("\n" + "="*60)
    print("  绑定完成")
    print("="*60)
    
    print("\n下一步:")
    print("1. 确保已更新并重启服务:")
    print("   - auth_middleware.py (兼容 status 类型)")
    print("   - python restart_service.py")
    print("\n2. 访问系统:")
    print("   http://127.0.0.1:9999")
    print("\n3. 重新登录:")
    print("   - 退出当前登录")
    print("   - 账号: 19938885888")
    print("   - 密码: 8471439")
    print("\n4. 应该能看到:")
    print("   - 所有 19,629 个客户数据")
    print("   - 客户都属于 msYang")
    print("   - 超级管理员可以看到全部")
    print()

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
