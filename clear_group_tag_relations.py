#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清空客户群标签关联数据
"""

import sqlite3
from config import DB_PATH

def clear_group_tag_relations():
    """清空客户群标签关联表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("清空客户群标签关联数据")
    print("=" * 60)
    
    # 1. 统计当前数据
    try:
        cursor.execute("SELECT COUNT(*) FROM group_chat_tag_relations")
        count = cursor.fetchone()[0]
        
        print(f"\n当前数据：")
        print(f"  - 标签关联记录: {count} 条")
        
        if count == 0:
            print("\n✅ 表中没有数据，无需清空")
            conn.close()
            return
        
        # 2. 确认清空
        print(f"\n⚠️  即将删除所有 {count} 条标签关联记录")
        confirm = input("确定要清空吗？(输入 yes 确认): ")
        
        if confirm.lower() != 'yes':
            print("\n❌ 已取消清空操作")
            conn.close()
            return
        
        # 3. 清空数据
        print("\n开始清空...")
        cursor.execute("DELETE FROM group_chat_tag_relations")
        deleted = cursor.rowcount
        
        conn.commit()
        
        print(f"✅ 已删除 {deleted} 条记录")
        
        # 4. 验证结果
        cursor.execute("SELECT COUNT(*) FROM group_chat_tag_relations")
        remaining = cursor.fetchone()[0]
        
        print("\n" + "=" * 60)
        print(f"✅ 清空完成！剩余记录: {remaining} 条")
        print("=" * 60)
        
        print("\n提示：")
        print("  - 标签组和标签本身未被删除")
        print("  - 只是清除了群与标签的关联关系")
        print("  - 现在可以在前端重新打标签了")
        
    except Exception as e:
        print(f"\n❌ 清空失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clear_group_tag_relations()
