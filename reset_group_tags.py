#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键重置客户群标签系统
"""

import sqlite3
import os
from config import DB_PATH

print("=" * 60)
print("一键重置客户群标签系统")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. 清空关联表
print("\n1. 清空标签关联...")
cursor.execute("DELETE FROM group_chat_tag_relations")
deleted = cursor.rowcount
print(f"   ✅ 已删除 {deleted} 条关联记录")

# 2. 检查表结构
print("\n2. 检查表结构...")
cursor.execute("PRAGMA table_info(group_chat_tag_relations)")
columns = {col[1]: col[2] for col in cursor.fetchall()}

if 'tag_name' not in columns:
    print("   ⚠️  缺少 tag_name 字段，正在添加...")
    
    # 重建表
    cursor.execute("DROP TABLE IF EXISTS group_chat_tag_relations")
    cursor.execute('''
        CREATE TABLE group_chat_tag_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            tag_id TEXT NOT NULL,
            tag_name TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            UNIQUE(chat_id, tag_id)
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_id ON group_chat_tag_relations(chat_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tag_id ON group_chat_tag_relations(tag_id)')
    print("   ✅ 表结构已更新")
else:
    print("   ✅ 表结构正常")

conn.commit()
conn.close()

print("\n" + "=" * 60)
print("✅ 重置完成！")
print("=" * 60)
print("\n下一步：")
print("  1. 重启后端服务")
print("  2. 刷新浏览器")
print("  3. 创建标签组")
print("  4. 重新打标签")
