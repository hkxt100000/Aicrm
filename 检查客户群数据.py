#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查客户群数据 - 诊断脚本
"""
import sqlite3
import json

DB_PATH = 'wecom_crm.db'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询前5条数据
    cursor.execute("""
        SELECT 
            chat_id,
            name,
            member_count,
            external_member_count,
            internal_member_count,
            notice,
            group_type,
            status
        FROM customer_groups 
        LIMIT 5
    """)
    
    rows = cursor.fetchall()
    
    print("\n" + "="*80)
    print("数据库中的实际数据（前5条）")
    print("="*80)
    
    for i, row in enumerate(rows, 1):
        print(f"\n【第 {i} 条】")
        print(f"  chat_id: {row[0]}")
        print(f"  群名称: {row[1]}")
        print(f"  总人数: {row[2]}")
        print(f"  外部客户数: {row[3]} ← 检查这个值")
        print(f"  内部员工数: {row[4]} ← 检查这个值")
        print(f"  群公告: {row[5][:50] if row[5] else '无'} ← 检查这个值")
        print(f"  群类型: {row[6]}")
        print(f"  状态: {row[7]}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("如果上面显示：")
    print("  - 外部客户数 = 0")
    print("  - 内部员工数 = 0")
    print("  - 群公告显示的不是公告内容")
    print("说明：后端同步代码有问题！")
    print("\n如果上面显示的数据都正确：")
    print("说明：前端代码字段映射错误！")
    print("="*80)
    
except Exception as e:
    print(f"❌ 错误: {e}")

input("\n按回车退出...")
