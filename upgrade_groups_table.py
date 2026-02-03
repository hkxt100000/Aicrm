"""
升级客户群表结构 - 添加新字段
"""
import sqlite3
from config import DB_PATH

def upgrade_customer_groups_table():
    """升级customer_groups表，添加新字段"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("🔧 开始升级客户群表结构...")
        print("=" * 60)
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customer_groups'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ 表已存在，检查字段...")
            
            # 获取当前表结构
            cursor.execute("PRAGMA table_info(customer_groups)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"📋 当前字段: {', '.join(columns)}")
            
            # 检查是否需要添加新字段
            new_fields = [
                ('external_member_count', 'INTEGER DEFAULT 0'),
                ('internal_member_count', 'INTEGER DEFAULT 0'),
                ('status', 'INTEGER DEFAULT 0'),
                ('version', 'INTEGER DEFAULT 0')
            ]
            
            for field_name, field_def in new_fields:
                if field_name not in columns:
                    print(f"➕ 添加字段: {field_name}")
                    cursor.execute(f"ALTER TABLE customer_groups ADD COLUMN {field_name} {field_def}")
                else:
                    print(f"✓  字段已存在: {field_name}")
            
            conn.commit()
            print("\n✅ 表结构升级完成！")
            
        else:
            print("⚠️  表不存在，创建新表...")
            cursor.execute("""
                CREATE TABLE customer_groups (
                    chat_id TEXT PRIMARY KEY,
                    name TEXT,
                    owner_userid TEXT,
                    owner_name TEXT,
                    notice TEXT,
                    member_count INTEGER DEFAULT 0,
                    external_member_count INTEGER DEFAULT 0,
                    internal_member_count INTEGER DEFAULT 0,
                    admin_list TEXT,
                    group_type TEXT DEFAULT 'external',
                    status INTEGER DEFAULT 0,
                    version INTEGER DEFAULT 0,
                    create_time INTEGER DEFAULT 0,
                    last_sync_time INTEGER DEFAULT 0,
                    created_at INTEGER DEFAULT 0,
                    updated_at INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            print("✅ 新表创建完成！")
        
        # 显示最终表结构
        cursor.execute("PRAGMA table_info(customer_groups)")
        final_columns = cursor.fetchall()
        print("\n📊 最终表结构:")
        for col in final_columns:
            print(f"   {col[1]}: {col[2]}")
        
        print("\n" + "=" * 60)
        print("🎉 数据库升级成功！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 升级失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_customer_groups_table()
