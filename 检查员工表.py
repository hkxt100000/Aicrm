#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查 employees 表结构和数据
"""
import sqlite3

DB_PATH = 'wecom_crm.db'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取表结构
    cursor.execute("PRAGMA table_info(employees)")
    columns = cursor.fetchall()
    
    print("\n" + "="*80)
    print("employees 表结构")
    print("="*80)
    print(f"{'索引':<6} {'字段名':<30} {'类型':<15}")
    print("-"*80)
    
    for col in columns:
        idx = col[0]
        name = col[1]
        type_ = col[2]
        print(f"{idx:<6} {name:<30} {type_:<15}")
    
    print("\n" + "="*80)
    print("查询前5个员工的数据（包含对外名称）")
    print("="*80)
    
    # 查询数据
    cursor.execute("SELECT userid, name, external_name FROM employees LIMIT 5")
    rows = cursor.fetchall()
    
    if rows:
        print(f"\n{'userid':<20} {'姓名(name)':<20} {'对外名称(external_name)':<30}")
        print("-"*80)
        for row in rows:
            userid = row[0] or '-'
            name = row[1] or '-'
            external_name = row[2] or '-'
            print(f"{userid:<20} {name:<20} {external_name:<30}")
    else:
        print("\n⚠️  employees 表是空的！")
    
    conn.close()
    
    print("\n" + "="*80)
    
except Exception as e:
    print(f"❌ 错误: {e}")

input("\n按回车退出...")
