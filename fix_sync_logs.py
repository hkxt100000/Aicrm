"""
强制重建 sync_logs 表
"""
import sqlite3

conn = sqlite3.connect('crm.db')
cursor = conn.cursor()

print('删除旧的 sync_logs 表（如果存在）...')
cursor.execute('DROP TABLE IF EXISTS sync_logs')

print('创建新的 sync_logs 表...')
cursor.execute('''
CREATE TABLE sync_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    created_at INTEGER NOT NULL
)
''')

print('创建索引...')
cursor.execute('CREATE INDEX idx_sync_logs_key ON sync_logs(key)')

conn.commit()
conn.close()

print('✅ sync_logs 表重建完成！')

# 验证
conn = sqlite3.connect('crm.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(sync_logs)')
print('\n表结构验证:')
for row in cursor.fetchall():
    print(f'  {row}')
conn.close()
