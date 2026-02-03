"""
初始化员工和权限管理数据库
解决外键约束问题
"""
import sqlite3
import bcrypt
import time
from pathlib import Path

DB_PATH = 'data/crm.db'

def init_auth_database():
    """初始化认证相关的数据库表"""
    
    # 确保 data 目录存在
    Path('data').mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("   初始化员工和权限管理数据库")
    print("=" * 60)
    print(f"数据库路径: {Path(DB_PATH).absolute()}\n")
    
    # 检查旧表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
    old_employees_exists = cursor.fetchone() is not None
    
    if old_employees_exists:
        print("⚠️  检测到旧的 employees 表，准备删除...")
        
        # 检查列结构
        cursor.execute("PRAGMA table_info(employees)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"   现有列: {', '.join(columns)}")
        
        if 'account' not in columns:
            print("   ❌ 表结构不正确，需要重建\n")
            
            # 删除相关表（注意顺序，先删除有外键的表）
            print("🔧 删除旧表...")
            for table in ['sessions', 'login_logs', 'employees', 'departments']:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    print(f"   ✓ 删除表 {table}")
                except Exception as e:
                    print(f"   ⚠️  删除表 {table} 失败: {e}")
            
            conn.commit()
            print("   ✅ 旧表删除完成\n")
        else:
            print("   ✅ 表结构正确，保留现有数据\n")
    
    print("[1/3] 创建表结构...\n")
    
    # 不使用外键约束，直接创建表
    
    # 1. 创建 departments 表
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                menu_permissions TEXT,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )
        """)
        print("  ✓ departments 表创建成功")
    except Exception as e:
        print(f"  ❌ departments 表创建失败: {e}")
    
    # 2. 创建 employees 表
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                account TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                department_id TEXT,
                wecom_user_id TEXT,
                wecom_name TEXT,
                status TEXT DEFAULT 'active',
                is_super_admin BOOLEAN DEFAULT 0,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )
        """)
        print("  ✓ employees 表创建成功")
    except Exception as e:
        print(f"  ❌ employees 表创建失败: {e}")
    
    # 3. 创建 login_logs 表
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_logs (
                id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                login_time INTEGER NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                status TEXT NOT NULL,
                fail_reason TEXT
            )
        """)
        print("  ✓ login_logs 表创建成功")
    except Exception as e:
        print(f"  ❌ login_logs 表创建失败: {e}")
    
    # 4. 创建 sessions 表
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at INTEGER NOT NULL,
                created_at INTEGER NOT NULL
            )
        """)
        print("  ✓ sessions 表创建成功")
    except Exception as e:
        print(f"  ❌ sessions 表创建失败: {e}")
    
    # 5. 创建索引
    print("\n  创建索引...")
    indexes = [
        ("idx_employees_account", "employees", "account"),
        ("idx_employees_wecom_user_id", "employees", "wecom_user_id"),
        ("idx_employees_department", "employees", "department_id"),
        ("idx_employees_status", "employees", "status"),
        ("idx_departments_name", "departments", "name"),
        ("idx_login_logs_employee", "login_logs", "employee_id"),
        ("idx_login_logs_time", "login_logs", "login_time"),
        ("idx_login_logs_status", "login_logs", "status"),
        ("idx_sessions_token", "sessions", "token"),
        ("idx_sessions_employee", "sessions", "employee_id"),
        ("idx_sessions_expires", "sessions", "expires_at"),
    ]
    
    for idx_name, table_name, column_name in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})")
        except:
            pass
    
    print("  ✓ 索引创建完成")
    
    conn.commit()
    
    # 验证表结构
    cursor.execute("PRAGMA table_info(employees)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'account' not in columns:
        print("\n  ❌ employees 表结构验证失败")
        conn.close()
        return
    
    # 检查超级管理员是否已存在
    print("\n[2/3] 初始化超级管理员账号...\n")
    
    cursor.execute("SELECT COUNT(*) FROM employees WHERE account = ?", ('19938885888',))
    exists = cursor.fetchone()[0] > 0
    
    if exists:
        print("  ⚠️  超级管理员已存在，跳过创建")
    else:
        # 生成密码哈希
        password = '8471439'
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        current_time = int(time.time() * 1000)
        
        try:
            cursor.execute("""
                INSERT INTO employees (
                    id, account, password, name, 
                    wecom_user_id, wecom_name,
                    department_id, is_super_admin, status, 
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'emp_super_admin',
                '19938885888',
                password_hash,
                '超级管理员',
                None,
                None,
                None,
                1,
                'active',
                current_time,
                current_time
            ))
            
            conn.commit()
            print("  ✓ 账号: 19938885888")
            print("  ✓ 密码: 8471439")
            print("  ✓ 姓名: 超级管理员")
            
        except Exception as e:
            print(f"  ❌ 创建失败: {e}")
    
    # 验证数据
    print("\n[3/3] 验证初始化结果...\n")
    
    cursor.execute("SELECT COUNT(*) FROM employees")
    emp_count = cursor.fetchone()[0]
    print(f"  ✓ employees 表记录数: {emp_count}")
    
    cursor.execute("SELECT COUNT(*) FROM departments")
    dept_count = cursor.fetchone()[0]
    print(f"  ✓ departments 表记录数: {dept_count}")
    
    # 显示员工列表
    if emp_count > 0:
        print("\n  员工列表:")
        cursor.execute("SELECT id, account, name, is_super_admin FROM employees")
        for row in cursor.fetchall():
            role = "超管" if row[3] else "员工"
            print(f"    - {row[2]} ({row[1]}) [{role}]")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 初始化完成！")
    print("=" * 60)
    print("\n超级管理员账号信息：")
    print("  账号: 19938885888")
    print("  密码: 8471439")
    print("\n现在可以启动服务并登录系统：")
    print("  python start.py")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    init_auth_database()
