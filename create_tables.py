"""
快速创建所有数据库表
"""
import sqlite3
from config import DB_PATH

print('开始创建数据库表...')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. 创建客户表
print('创建 customers 表...')
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    name TEXT,
    avatar TEXT,
    gender INTEGER DEFAULT 0,
    type INTEGER DEFAULT 1,
    unionid TEXT,
    position TEXT,
    corp_name TEXT,
    owner_userid TEXT,
    owner_name TEXT,
    add_time INTEGER,
    tags TEXT,
    remark TEXT,
    description TEXT,
    add_way INTEGER DEFAULT 0,
    im_status TEXT,
    state TEXT,
    remark_mobiles TEXT,
    remark_corp_name TEXT,
    enterprise_tags TEXT,
    personal_tags TEXT,
    rule_tags TEXT,
    created_at INTEGER DEFAULT 0,
    updated_at INTEGER DEFAULT 0
)
''')

# 2. 创建员工表
print('创建 employees 表...')
cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id TEXT PRIMARY KEY,
    name TEXT,
    avatar TEXT,
    mobile TEXT,
    email TEXT,
    department TEXT,
    position TEXT,
    status INTEGER DEFAULT 1,
    customer_count INTEGER DEFAULT 0,
    created_at INTEGER DEFAULT 0,
    updated_at INTEGER DEFAULT 0
)
''')

# 3. 创建同步日志表
print('创建 sync_logs 表...')
cursor.execute('''
CREATE TABLE IF NOT EXISTS sync_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT,
    value TEXT,
    created_at INTEGER
)
''')

# 4. 创建跟进记录表
print('创建 follow_records 表...')
cursor.execute('''
CREATE TABLE IF NOT EXISTS follow_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT,
    employee_id TEXT,
    content TEXT,
    follow_type TEXT,
    follow_time INTEGER,
    created_at INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
''')

# 5. 创建标签表
print('创建 customer_tags 表...')
cursor.execute('''
CREATE TABLE IF NOT EXISTS customer_tags (
    id TEXT PRIMARY KEY,
    name TEXT,
    group_name TEXT,
    order_num INTEGER DEFAULT 0
)
''')

# 6. 创建索引
print('创建索引...')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_owner ON customers(owner_userid)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_updated ON customers(updated_at)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_id ON employees(id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_logs_key ON sync_logs(key)')

conn.commit()
conn.close()

print('✅ 所有表创建完成！')
print('\n已创建的表：')
print('  - customers (客户表)')
print('  - employees (员工表)')
print('  - sync_logs (同步日志表)')
print('  - follow_records (跟进记录表)')
print('  - customer_tags (标签表)')
print('\n可以开始同步数据了！')
