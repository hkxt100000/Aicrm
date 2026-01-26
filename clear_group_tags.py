#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理客户群标签数据
"""

import sqlite3
from config import DB_PATH

def clear_group_tags():
    """清空客户群标签数据"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 清空标签表
        cursor.execute('DELETE FROM group_chat_tags')
        tags_count = cursor.rowcount
        
        # 清空标签组表
        cursor.execute('DELETE FROM group_chat_tag_groups')
        groups_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✅ 清理完成！")
        print(f"   - 删除了 {groups_count} 个标签组")
        print(f"   - 删除了 {tags_count} 个标签")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("开始清理客户群标签数据...")
    print("=" * 50)
    clear_group_tags()
    print("=" * 50)
