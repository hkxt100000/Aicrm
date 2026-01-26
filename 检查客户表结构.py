#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查客户表和标签表的结构
"""
import sqlite3

DB_PATH = 'wecom_crm.db'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("customers 表字段：")
    print("="*80)
    cursor.execute("PRAGMA table_info(customers)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]:<30} ({col[2]})")
    
    print("\n" + "="*80)
    print("customer_tags 表字段：")
    print("="*80)
    cursor.execute("PRAGMA table_info(customer_tags)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]:<30} ({col[2]})")
    
    print("\n" + "="*80)
    print("查询一条客户数据示例：")
    print("="*80)
    cursor.execute("SELECT * FROM customers LIMIT 1")
    row = cursor.fetchone()
    if row:
        cursor.execute("PRAGMA table_info(customers)")
        columns = cursor.fetchall()
        for i, col in enumerate(columns):
            field_value = row[i]
            if isinstance(field_value, str) and len(str(field_value)) > 50:
                field_value = str(field_value)[:50] + "..."
            print(f"  {col[1]:<30} = {field_value}")
    else:
        print("  customers 表是空的")
    
    print("\n" + "="*80)
    print("查询一条标签数据示例：")
    print("="*80)
    cursor.execute("SELECT * FROM customer_tags LIMIT 1")
    row = cursor.fetchone()
    if row:
        cursor.execute("PRAGMA table_info(customer_tags)")
        columns = cursor.fetchall()
        for i, col in enumerate(columns):
            print(f"  {col[1]:<30} = {row[i]}")
    else:
        print("  customer_tags 表是空的")
    
    print("\n" + "="*80)
    print("统计数据：")
    print("="*80)
    cursor.execute("SELECT COUNT(*) FROM customers")
    print(f"  客户总数: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM customer_tags")
    print(f"  标签总数: {cursor.fetchone()[0]}")
    
    conn.close()
    print("\n执行完成！")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")

input("\n按回车退出...")
