#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复客户群标签关联表中的 tag_name
从 group_chat_tags 表同步标签名称
"""

import sqlite3
from config import DB_PATH

def fix_tag_names():
    """修复关联表中的 tag_name"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("修复客户群标签关联表的 tag_name")
    print("=" * 60)
    
    # 1. 检查表是否存在
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='group_chat_tag_relations'
    """)
    
    if not cursor.fetchone():
        print("❌ 表 group_chat_tag_relations 不存在")
        conn.close()
        return
    
    # 2. 统计当前数据
    cursor.execute("SELECT COUNT(*) FROM group_chat_tag_relations")
    total = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM group_chat_tag_relations 
        WHERE tag_name IS NULL OR tag_name = '' OR tag_name = 'undefined'
    """)
    empty_count = cursor.fetchone()[0]
    
    print(f"\n数据统计：")
    print(f"  - 总记录数: {total}")
    print(f"  - 需要修复: {empty_count}")
    
    if empty_count == 0:
        print("\n✅ 所有记录都有标签名，无需修复")
        conn.close()
        return
    
    # 3. 显示需要修复的记录
    print(f"\n需要修复的记录：")
    cursor.execute("""
        SELECT r.id, r.chat_id, r.tag_id, r.tag_name, t.name as correct_name
        FROM group_chat_tag_relations r
        LEFT JOIN group_chat_tags t ON r.tag_id = t.id
        WHERE r.tag_name IS NULL OR r.tag_name = '' OR r.tag_name = 'undefined'
        LIMIT 10
    """)
    
    records = cursor.fetchall()
    for record in records:
        print(f"  ID: {record[0]}, chat_id: {record[1]}, tag_id: {record[2]}")
        print(f"    当前 tag_name: '{record[3]}'")
        print(f"    正确 tag_name: '{record[4] or '(标签不存在)'}'")
    
    if len(records) == 10:
        print(f"  ... 还有 {empty_count - 10} 条记录")
    
    # 4. 开始修复
    print(f"\n开始修复...")
    
    try:
        # 从 group_chat_tags 表更新 tag_name
        cursor.execute("""
            UPDATE group_chat_tag_relations
            SET tag_name = (
                SELECT name FROM group_chat_tags 
                WHERE group_chat_tags.id = group_chat_tag_relations.tag_id
            )
            WHERE (tag_name IS NULL OR tag_name = '' OR tag_name = 'undefined')
              AND tag_id IN (SELECT id FROM group_chat_tags)
        """)
        
        updated = cursor.rowcount
        print(f"✅ 已从标签表同步 {updated} 条记录")
        
        # 删除无效记录（tag_id 不存在于标签表）
        cursor.execute("""
            DELETE FROM group_chat_tag_relations
            WHERE (tag_name IS NULL OR tag_name = '' OR tag_name = 'undefined')
              AND tag_id NOT IN (SELECT id FROM group_chat_tags)
        """)
        
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"🗑️  已删除 {deleted} 条无效记录（标签不存在）")
        
        conn.commit()
        
        # 5. 验证修复结果
        cursor.execute("""
            SELECT COUNT(*) FROM group_chat_tag_relations 
            WHERE tag_name IS NULL OR tag_name = '' OR tag_name = 'undefined'
        """)
        remaining = cursor.fetchone()[0]
        
        print("\n" + "=" * 60)
        if remaining == 0:
            print("✅ 修复完成！所有记录都有正确的标签名")
        else:
            print(f"⚠️  还有 {remaining} 条记录未修复（可能标签已被删除）")
        print("=" * 60)
        
        # 6. 显示修复后的数据
        print("\n修复后的数据示例：")
        cursor.execute("""
            SELECT chat_id, tag_id, tag_name, created_at
            FROM group_chat_tag_relations
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"  chat_id: {row[0][:20]}..., tag_id: {row[1]}, tag_name: {row[2]}")
        
    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_tag_names()
