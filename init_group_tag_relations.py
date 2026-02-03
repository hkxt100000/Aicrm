#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化客户群标签关联表
"""

import sqlite3
import os
from config import DB_PATH

def init_group_tag_relations():
    """创建客户群标签关联表"""
    # 确保数据库目录存在
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("开始创建客户群标签关联表...")
    
    # 创建群标签关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_chat_tag_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            tag_id TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            UNIQUE(chat_id, tag_id)
        )
    ''')
    print("✅ group_chat_tag_relations 表创建成功")
    
    # 创建索引
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_chat_id ON group_chat_tag_relations(chat_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_tag_id ON group_chat_tag_relations(tag_id)
    ''')
    print("✅ 索引创建成功")
    
    conn.commit()
    conn.close()
    
    print("\n初始化完成！")
    print("=" * 50)
    
    # 显示表结构
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(group_chat_tag_relations)")
    columns = cursor.fetchall()
    
    print("\n表结构信息：")
    print("group_chat_tag_relations:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 显示统计
    cursor.execute("SELECT COUNT(*) FROM group_chat_tag_relations")
    relations_count = cursor.fetchone()[0]
    
    print(f"\n当前数据统计：")
    print(f"  - 标签关联: {relations_count} 条")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("初始化客户群标签关联表")
    print("=" * 50)
    init_group_tag_relations()
