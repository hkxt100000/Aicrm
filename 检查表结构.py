#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查 customer_groups 表结构
"""
import sqlite3

DB_PATH = 'wecom_crm.db'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取表结构
    cursor.execute("PRAGMA table_info(customer_groups)")
    columns = cursor.fetchall()
    
    print("\n" + "="*80)
    print("customer_groups 表结构")
    print("="*80)
    print(f"{'索引':<6} {'字段名':<30} {'类型':<15} {'非空':<6} {'默认值'}")
    print("-"*80)
    
    for col in columns:
        idx = col[0]
        name = col[1]
        type_ = col[2]
        notnull = 'Yes' if col[3] else 'No'
        default = col[4] if col[4] else '-'
        print(f"{idx:<6} {name:<30} {type_:<15} {notnull:<6} {default}")
    
    print("="*80)
    
    # 查询一条数据，显示每个字段的值
    cursor.execute("SELECT * FROM customer_groups LIMIT 1")
    row = cursor.fetchone()
    
    if row:
        print("\n第1条数据的字段值：\n")
        for i, col in enumerate(columns):
            field_name = col[1]
            field_value = row[i]
            print(f"  row[{i}] = {field_name} = {field_value}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("检查 app.py 中的字段映射是否正确！")
    print("特别检查：")
    print("  - external_member_count 应该是 row[?]")
    print("  - internal_member_count 应该是 row[?]")
    print("="*80)
    
except Exception as e:
    print(f"❌ 错误: {e}")

input("\n按回车退出...")
