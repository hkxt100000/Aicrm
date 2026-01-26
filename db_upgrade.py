"""
数据库升级脚本 - 添加导出所需的字段
"""
import sqlite3
from pathlib import Path

DB_PATH = "data/crm.db"

def upgrade_database():
    """升级数据库结构"""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("[升级] 开始升级数据库...")
    
    # 1. 为customers表添加新字段
    new_columns = [
        ("description", "TEXT", "描述信息"),
        ("add_way", "INTEGER DEFAULT 0", "添加方式"),
        ("im_status", "INTEGER DEFAULT 0", "会话状态"),
        ("state", "TEXT", "渠道来源"),
        ("remark_mobiles", "TEXT", "备注手机号"),
        ("remark_corp_name", "TEXT", "备注企业名称"),
        ("enterprise_tags", "TEXT", "企业标签(JSON)"),
        ("personal_tags", "TEXT", "个人标签(JSON)"),
        ("rule_tags", "TEXT", "规则组标签(JSON)"),
    ]
    
    for col_name, col_type, description in new_columns:
        try:
            cursor.execute(f"ALTER TABLE customers ADD COLUMN {col_name} {col_type}")
            print(f"[升级] ✅ 添加字段 customers.{col_name} - {description}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"[升级] ⏭️  字段 customers.{col_name} 已存在")
            else:
                print(f"[升级] ❌ 添加字段 customers.{col_name} 失败: {e}")
    
    # 2. 创建跟进记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS follow_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            employee_id TEXT NOT NULL,
            employee_name TEXT,
            content TEXT,
            follow_type TEXT DEFAULT '电话',
            follow_time INTEGER,
            next_follow_time INTEGER,
            created_at INTEGER DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    """)
    print("[升级] ✅ 创建跟进记录表 follow_records")
    
    # 3. 创建索引优化查询
    indexes = [
        ("idx_customers_owner", "customers", "owner_userid"),
        ("idx_customers_add_time", "customers", "add_time"),
        ("idx_follow_records_customer", "follow_records", "customer_id"),
        ("idx_follow_records_time", "follow_records", "follow_time"),
    ]
    
    for idx_name, table_name, column_name in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})")
            print(f"[升级] ✅ 创建索引 {idx_name}")
        except Exception as e:
            print(f"[升级] ❌ 创建索引 {idx_name} 失败: {e}")
    
    # 4. 创建同步日志表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sync_type TEXT NOT NULL,
            sync_time INTEGER NOT NULL,
            success INTEGER DEFAULT 1,
            added_count INTEGER DEFAULT 0,
            updated_count INTEGER DEFAULT 0,
            error_message TEXT,
            duration_seconds REAL,
            trigger_type TEXT DEFAULT 'manual'
        )
    """)
    print("[升级] ✅ 创建同步日志表 sync_logs")
    
    conn.commit()
    conn.close()
    
    print("[升级] 数据库升级完成！")

if __name__ == "__main__":
    upgrade_database()
