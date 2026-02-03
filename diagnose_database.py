#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断数据库表结构问题
"""

import sqlite3
import os

DB_PATH = os.getenv('DB_PATH', 'wecom_crm.db')

def diagnose_database():
    """诊断数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("数据库诊断报告")
    print("=" * 80)
    print(f"数据库路径: {DB_PATH}\n")
    
    # 检查 customers 表
    print("📊 customers 表结构:")
    print("-" * 80)
    try:
        cursor.execute("PRAGMA table_info(customers)")
        columns = cursor.fetchall()
        
        if not columns:
            print("❌ customers 表不存在！")
        else:
            print(f"✅ customers 表存在，共 {len(columns)} 个字段:\n")
            for col in columns:
                cid, name, type_, notnull, default, pk = col
                pk_mark = " [PRIMARY KEY]" if pk else ""
                default_mark = f" DEFAULT {default}" if default else ""
                print(f"  {cid+1:2d}. {name:30s} {type_:15s}{pk_mark}{default_mark}")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 检查 customer_groups 表
    print("\n" + "=" * 80)
    print("📊 customer_groups 表结构:")
    print("-" * 80)
    try:
        cursor.execute("PRAGMA table_info(customer_groups)")
        columns = cursor.fetchall()
        
        if not columns:
            print("❌ customer_groups 表不存在！")
        else:
            print(f"✅ customer_groups 表存在，共 {len(columns)} 个字段:\n")
            for col in columns:
                cid, name, type_, notnull, default, pk = col
                pk_mark = " [PRIMARY KEY]" if pk else ""
                default_mark = f" DEFAULT {default}" if default else ""
                print(f"  {cid+1:2d}. {name:30s} {type_:15s}{pk_mark}{default_mark}")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    
    # 检查所有表
    print("\n" + "=" * 80)
    print("📋 所有表列表:")
    print("-" * 80)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    for i, (table_name,) in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  {i:2d}. {table_name:30s} ({count} 条记录)")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)

if __name__ == "__main__":
    diagnose_database()
