#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
升级客户群标签关联表 - 添加 tag_name 字段
"""

import sqlite3
import os
from config import DB_PATH

def upgrade_table():
    """升级表结构，添加 tag_name 字段"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("升级客户群标签关联表")
    print("=" * 60)
    
    # 检查表是否存在
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='group_chat_tag_relations'
    """)
    
    if not cursor.fetchone():
        print("❌ 表 group_chat_tag_relations 不存在，请先运行 init_group_tag_relations.py")
        conn.close()
        return
    
    # 检查 tag_name 字段是否已存在
    cursor.execute("PRAGMA table_info(group_chat_tag_relations)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f"\n当前字段列表: {', '.join(columns)}")
    
    if 'tag_name' in columns:
        print("✅ tag_name 字段已存在，无需升级")
        conn.close()
        return
    
    print("\n开始升级表结构...")
    
    try:
        # 方案：重建表（SQLite 不支持直接 ALTER TABLE 添加 UNIQUE 约束）
        
        # 1. 备份旧数据
        print("1. 备份旧数据...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS group_chat_tag_relations_backup AS 
            SELECT * FROM group_chat_tag_relations
        """)
        
        backup_count = cursor.execute("""
            SELECT COUNT(*) FROM group_chat_tag_relations_backup
        """).fetchone()[0]
        print(f"   ✅ 已备份 {backup_count} 条数据")
        
        # 2. 删除旧表
        print("2. 删除旧表...")
        cursor.execute("DROP TABLE IF EXISTS group_chat_tag_relations")
        print("   ✅ 旧表已删除")
        
        # 3. 创建新表（包含 tag_name）
        print("3. 创建新表...")
        cursor.execute('''
            CREATE TABLE group_chat_tag_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                tag_id TEXT NOT NULL,
                tag_name TEXT NOT NULL DEFAULT '',
                created_at INTEGER NOT NULL,
                UNIQUE(chat_id, tag_id)
            )
        ''')
        print("   ✅ 新表已创建（包含 tag_name 字段）")
        
        # 4. 恢复数据（tag_name 使用默认值）
        print("4. 恢复数据...")
        cursor.execute("""
            INSERT INTO group_chat_tag_relations (id, chat_id, tag_id, tag_name, created_at)
            SELECT id, chat_id, tag_id, '', created_at
            FROM group_chat_tag_relations_backup
        """)
        
        restored_count = cursor.execute("""
            SELECT COUNT(*) FROM group_chat_tag_relations
        """).fetchone()[0]
        print(f"   ✅ 已恢复 {restored_count} 条数据")
        
        # 5. 从标签表同步 tag_name
        print("5. 从标签表同步 tag_name...")
        cursor.execute("""
            UPDATE group_chat_tag_relations
            SET tag_name = (
                SELECT name FROM group_chat_tags 
                WHERE group_chat_tags.id = group_chat_tag_relations.tag_id
            )
            WHERE tag_id IN (SELECT id FROM group_chat_tags)
        """)
        
        updated_count = cursor.rowcount
        print(f"   ✅ 已更新 {updated_count} 条记录的 tag_name")
        
        # 6. 重建索引
        print("6. 重建索引...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_chat_id ON group_chat_tag_relations(chat_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tag_id ON group_chat_tag_relations(tag_id)
        ''')
        print("   ✅ 索引已重建")
        
        # 7. 删除备份表
        print("7. 清理备份表...")
        cursor.execute("DROP TABLE IF EXISTS group_chat_tag_relations_backup")
        print("   ✅ 备份表已清理")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ 升级完成！")
        print("=" * 60)
        
        # 显示新表结构
        cursor.execute("PRAGMA table_info(group_chat_tag_relations)")
        columns = cursor.fetchall()
        
        print("\n新表结构：")
        for col in columns:
            print(f"  - {col[1]:15} {col[2]:10} {'NOT NULL' if col[3] else ''}")
        
        # 显示数据统计
        cursor.execute("SELECT COUNT(*) FROM group_chat_tag_relations")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM group_chat_tag_relations WHERE tag_name != ''")
        with_name = cursor.fetchone()[0]
        
        print(f"\n数据统计：")
        print(f"  - 总记录数: {total}")
        print(f"  - 有标签名: {with_name}")
        print(f"  - 无标签名: {total - with_name}")
        
    except Exception as e:
        print(f"\n❌ 升级失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_table()
