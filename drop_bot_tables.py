"""
删除旧的机器人表
"""
import sqlite3

DB_PATH = 'data/crm.db'

def drop_old_bot_tables():
    """删除旧的机器人表"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("🗑️  删除旧的机器人表")
        print("=" * 60)
        
        tables = ['bot_webhooks', 'bot_notifications', 'bot_send_logs', 'bot_templates']
        
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"   ✅ 删除表：{table}")
            except Exception as e:
                print(f"   ⚠️  {table} 删除失败或不存在：{e}")
        
        conn.commit()
        print("\n" + "=" * 60)
        print("✅ 旧表删除完成！")
        print("=" * 60)
        print("\n下一步：运行 python init_bot_tables.py 重新创建表")
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        return False
    
    finally:
        conn.close()
    
    return True

if __name__ == '__main__':
    drop_old_bot_tables()
