"""
诊断企业通讯录问题
"""
import sqlite3
import sys

DB_PATH = "data/crm.db"

def check_employees_table():
    """检查employees表数据"""
    print("\n===== 检查 employees 表 =====")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
    if not cursor.fetchone():
        print("❌ employees 表不存在！")
        return
    print("✅ employees 表存在")
    
    # 2. 检查数据量
    cursor.execute("SELECT COUNT(*) as count FROM employees")
    count = cursor.fetchone()['count']
    print(f"✅ employees 表有 {count} 条数据")
    
    if count == 0:
        print("❌ 表是空的，需要同步企微数据")
        conn.close()
        return
    
    # 3. 查看前5条数据
    print("\n前5条员工数据：")
    cursor.execute("SELECT id, name, mobile, status FROM employees LIMIT 5")
    for row in cursor.fetchall():
        print(f"  - ID: {row['id']}, 姓名: {row['name']}, 手机: {row['mobile']}, 状态: {row['status']}")
    
    conn.close()

def check_super_admin():
    """检查超级管理员信息"""
    print("\n===== 检查超级管理员 =====")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 查询超级管理员（系统账号表）
    cursor.execute("""
        SELECT id, account, name, is_super_admin, wecom_user_id, status 
        FROM employees
        WHERE account = '19938885888'
    """)
    admin = cursor.fetchone()
    
    if not admin:
        print("❌ 找不到超级管理员账号（可能在不同的表中）")
        # 尝试查找认证系统的employees表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        print(f"   数据库中的表: {', '.join(tables)}")
    else:
        print(f"✅ 超级管理员信息：")
        print(f"   - ID: {admin['id']}")
        print(f"   - 账号: {admin['account']}")
        print(f"   - 姓名: {admin['name']}")
        print(f"   - 超级管理员: {bool(admin['is_super_admin'])}")
        print(f"   - 绑定企微: {admin['wecom_user_id'] or '未绑定'}")
        print(f"   - 状态: {admin['status']}")
    
    conn.close()

def check_api_logic():
    """模拟API逻辑"""
    print("\n===== 模拟 API 查询逻辑 =====")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 模拟超级管理员查询
    print("\n场景1：超级管理员查询（is_super_admin=True）")
    cursor.execute("SELECT * FROM employees")
    rows = cursor.fetchall()
    print(f"✅ 查询到 {len(rows)} 条员工数据")
    
    if len(rows) > 0:
        print("   前3条数据：")
        for i, row in enumerate(rows[:3]):
            print(f"   {i+1}. ID: {row['id']}, 姓名: {row['name']}")
    
    # 模拟普通员工查询（假设绑定了msYang）
    print("\n场景2：普通员工查询（wecom_user_id='msYang'）")
    cursor.execute("SELECT * FROM employees WHERE id = ?", ('msYang',))
    rows = cursor.fetchall()
    print(f"✅ 查询到 {len(rows)} 条员工数据")
    
    if len(rows) > 0:
        for row in rows:
            print(f"   - ID: {row['id']}, 姓名: {row['name']}")
    else:
        print("   ⚠️ 没有找到 id='msYang' 的员工")
    
    conn.close()

def check_auth_tables():
    """检查认证系统的表"""
    print("\n===== 检查认证系统表 =====")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 列出所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row['name'] for row in cursor.fetchall()]
    print(f"数据库中的所有表：")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()['count']
        print(f"  - {table}: {count} 条数据")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("企业通讯录诊断工具")
    print("=" * 60)
    
    try:
        check_employees_table()
        check_super_admin()
        check_api_logic()
        check_auth_tables()
        
        print("\n" + "=" * 60)
        print("诊断完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 诊断过程中出错: {e}")
        import traceback
        traceback.print_exc()
