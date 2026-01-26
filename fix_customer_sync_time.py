#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复客户同步时间记录问题
将 sync_logs 表中错误的记录迁移到 config 表
"""

import sqlite3
import os
import time

# 获取数据库路径
DB_PATH = os.getenv('DB_PATH', 'wecom_crm.db')

def fix_sync_time():
    """修复同步时间记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("🔍 检查数据库状态...")
        
        # 1. 检查 sync_logs 表是否有错误的数据
        try:
            cursor.execute("SELECT * FROM sync_logs WHERE id = 'last_sync_time' OR key = 'last_sync_time'")
            old_records = cursor.fetchall()
            if old_records:
                print(f"⚠️  发现 {len(old_records)} 条错误的同步时间记录")
        except Exception as e:
            print(f"ℹ️  sync_logs 表检查跳过: {e}")
        
        # 2. 确保 config 表存在
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at INTEGER
            )
        """)
        print("✅ config 表已就绪")
        
        # 3. 检查 config 表中是否已有同步时间记录
        cursor.execute("SELECT key, value, updated_at FROM config WHERE key = ?", ('last_customer_sync_time',))
        result = cursor.fetchone()
        
        if result:
            sync_time = int(result[1])
            updated_at = result[2]
            print(f"ℹ️  当前记录的同步时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sync_time))}")
            print(f"ℹ️  记录更新时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(updated_at))}")
        else:
            print("⚠️  未找到同步时间记录，将初始化为当前时间")
            current_time = int(time.time())
            cursor.execute(
                "INSERT INTO config (key, value, updated_at) VALUES (?, ?, ?)",
                ('last_customer_sync_time', str(current_time), current_time)
            )
            print(f"✅ 已初始化同步时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}")
        
        # 4. 查询最近一条客户记录的更新时间
        cursor.execute("SELECT MAX(updated_at) FROM customers")
        max_updated = cursor.fetchone()[0]
        if max_updated:
            print(f"ℹ️  数据库中最新客户记录的更新时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(max_updated))}")
            
            # 如果 config 中的时间比最新客户记录还旧，更新它
            if not result or int(result[1]) < max_updated:
                cursor.execute(
                    "INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, ?)",
                    ('last_customer_sync_time', str(max_updated), max_updated)
                )
                print(f"✅ 已将同步时间更新为最新客户记录时间")
        
        conn.commit()
        print("\n✅ 修复完成！下次增量同步将使用正确的时间戳")
        print("\n💡 建议:")
        print("   1. 重启后端服务")
        print("   2. 点击同步客户时，观察后台日志，应该显示正确的'上次同步时间'")
        print("   3. 第一次可能还是全量同步，之后就是增量了")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("修复客户同步时间记录")
    print("=" * 60)
    fix_sync_time()
