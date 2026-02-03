#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化客户群标签数据库表
"""

import sqlite3
import os
from config import DB_PATH

def init_group_tag_tables():
    """初始化客户群标签相关表"""
    
    # 确保数据库目录存在
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("📊 开始创建客户群标签表...")
    
    # 1. 创建标签组表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_chat_tag_groups (
            group_id TEXT PRIMARY KEY,
            group_name TEXT NOT NULL,
            create_time INTEGER,
            order_index INTEGER DEFAULT 0,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    ''')
    print("✅ group_chat_tag_groups 表创建成功")
    
    # 2. 创建标签表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_chat_tags (
            id TEXT PRIMARY KEY,
            group_id TEXT NOT NULL,
            name TEXT NOT NULL,
            create_time INTEGER,
            order_index INTEGER DEFAULT 0,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (group_id) REFERENCES group_chat_tag_groups(group_id) ON DELETE CASCADE
        )
    ''')
    print("✅ group_chat_tags 表创建成功")
    
    # 3. 创建索引
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_group_chat_tags_group_id 
        ON group_chat_tags(group_id)
    ''')
    print("✅ 索引创建成功")
    
    conn.commit()
    conn.close()
    
    print("🎉 客户群标签表初始化完成！")
    
    # 打印表结构
    print("\n📋 表结构信息：")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n1️⃣ group_chat_tag_groups:")
    cursor.execute("PRAGMA table_info(group_chat_tag_groups)")
    for row in cursor.fetchall():
        print(f"  - {row[1]} ({row[2]})")
    
    print("\n2️⃣ group_chat_tags:")
    cursor.execute("PRAGMA table_info(group_chat_tags)")
    for row in cursor.fetchall():
        print(f"  - {row[1]} ({row[2]})")
    
    # 统计数据
    cursor.execute("SELECT COUNT(*) FROM group_chat_tag_groups")
    group_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM group_chat_tags")
    tag_count = cursor.fetchone()[0]
    
    print(f"\n📊 当前数据统计：")
    print(f"  - 标签组：{group_count} 个")
    print(f"  - 标签：{tag_count} 个")
    
    conn.close()

if __name__ == '__main__':
    init_group_tag_tables()
