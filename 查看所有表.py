#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看数据库中所有的表
"""

import sqlite3
from datetime import datetime

DB_PATH = "data/crm.db"

def list_all_tables():
    """列出数据库中所有的表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("🔍 数据库中的所有表")
    print("=" * 80)
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table'
        ORDER BY name
    """)
    
    tables = cursor.fetchall()
    
    if not tables:
        print("❌ 数据库中没有表！")
        conn.close()
        return
    
    print(f"\n找到 {len(tables)} 个表：")
    print("-" * 80)
    
    for i, (table_name,) in enumerate(tables, 1):
        print(f"{i}. {table_name}")
        
        # 查询表的行数
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   └─ 共 {count:,} 条数据")
        
        # 查询表的列
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"   └─ 列：{', '.join([col[1] for col in columns])}")
        print()
    
    conn.close()

def check_customer_table():
    """检查客户表的结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 尝试查找包含 "customer" 的表
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE '%customer%'
        ORDER BY name
    """)
    
    customer_tables = cursor.fetchall()
    
    if not customer_tables:
        print("=" * 80)
        print("❌ 没有找到包含 'customer' 的表！")
        print("=" * 80)
        conn.close()
        return
    
    print("=" * 80)
    print("🔍 客户相关的表")
    print("=" * 80)
    
    for (table_name,) in customer_tables:
        print(f"\n表名：{table_name}")
        print("-" * 80)
        
        # 查询表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("列信息：")
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            pk_str = " (主键)" if pk else ""
            not_null_str = " NOT NULL" if not_null else ""
            default_str = f" DEFAULT {default_val}" if default_val else ""
            print(f"  {col_name:<20} {col_type:<15}{pk_str}{not_null_str}{default_str}")
        
        # 查询数据量
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\n数据量：{count:,} 条")
        
        # 查询最新 3 条数据
        print(f"\n最新 3 条数据示例：")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 尝试按不同字段排序
        order_by = None
        for col_name in ['created_at', 'add_time', 'id']:
            try:
                cursor.execute(f"SELECT * FROM {table_name} ORDER BY {col_name} DESC LIMIT 3")
                order_by = col_name
                break
            except:
                continue
        
        if order_by:
            rows = cursor.fetchall()
            for row in rows:
                print(f"\n  ID: {row['id'] if 'id' in row.keys() else 'N/A'}")
                for key in row.keys()[:5]:  # 只显示前5个字段
                    value = row[key]
                    if key in ['add_time', 'created_at', 'updated_at'] and value:
                        # 尝试转换时间戳
                        try:
                            if len(str(value)) == 10:
                                dt = datetime.fromtimestamp(value)
                            elif len(str(value)) >= 13:
                                dt = datetime.fromtimestamp(value / 1000)
                            else:
                                dt = None
                            if dt:
                                value = f"{value} ({dt.strftime('%Y-%m-%d %H:%M:%S')})"
                        except:
                            pass
                    print(f"    {key}: {value}")
    
    conn.close()

if __name__ == "__main__":
    list_all_tables()
    print("\n")
    check_customer_table()
