#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 add_time 字段的格式
"""

import sqlite3
from datetime import datetime

DB_PATH = "data/crm.db"

def check_add_time():
    """检查 add_time 字段的格式"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 80)
    print("🔍 检查 add_time 字段格式")
    print("=" * 80)
    
    # 查询最新的 10 条数据
    cursor.execute("""
        SELECT id, name, add_time, created_at
        FROM customers
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    
    print(f"\n📊 最新 10 条客户的时间字段：")
    print("-" * 80)
    print(f"{'ID':<10} {'姓名':<15} {'add_time':<15} {'created_at':<15}")
    print("-" * 80)
    
    for row in rows:
        add_time = row['add_time']
        created_at = row['created_at']
        
        # 尝试两种解析方式
        if add_time:
            # 10位数 = 秒级时间戳
            if len(str(add_time)) == 10:
                add_time_dt = datetime.fromtimestamp(add_time)
                add_time_format = "秒级(10位)"
            # 13位数 = 毫秒级时间戳
            elif len(str(add_time)) >= 13:
                add_time_dt = datetime.fromtimestamp(add_time / 1000)
                add_time_format = "毫秒级(13位)"
            else:
                add_time_dt = None
                add_time_format = "未知格式"
        else:
            add_time_dt = None
            add_time_format = "NULL"
        
        if created_at:
            if len(str(created_at)) == 10:
                created_at_dt = datetime.fromtimestamp(created_at)
                created_at_format = "秒级(10位)"
            elif len(str(created_at)) >= 13:
                created_at_dt = datetime.fromtimestamp(created_at / 1000)
                created_at_format = "毫秒级(13位)"
            else:
                created_at_dt = None
                created_at_format = "未知格式"
        else:
            created_at_dt = None
            created_at_format = "NULL"
        
        print(f"{row['id']:<10} {row['name']:<15} {add_time or 'NULL':<15} {created_at or 'NULL':<15}")
        if add_time_dt:
            print(f"{'':10} {'':15} {add_time_dt.strftime('%Y-%m-%d %H:%M:%S')} ({add_time_format})")
        else:
            print(f"{'':10} {'':15} {'无法解析':<30} ({add_time_format})")
        
        if created_at_dt:
            print(f"{'':10} {'':15} {'':30} {created_at_dt.strftime('%Y-%m-%d %H:%M:%S')} ({created_at_format})")
        else:
            print(f"{'':10} {'':15} {'':30} {'无法解析':<30} ({created_at_format})")
        print()
    
    # 统计 add_time 的位数分布
    print("=" * 80)
    print("📊 add_time 字段位数分布统计：")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN LENGTH(CAST(add_time AS TEXT)) = 10 THEN '10位(秒级)'
                WHEN LENGTH(CAST(add_time AS TEXT)) >= 13 THEN '13位+(毫秒级)'
                WHEN add_time IS NULL THEN 'NULL'
                ELSE '其他'
            END as time_format,
            COUNT(*) as count
        FROM customers
        GROUP BY time_format
    """)
    
    for row in cursor.fetchall():
        print(f"{row['time_format']:<20} {row['count']:>8} 条")
    
    # 查询今天的数据（按 add_time 秒级计算）
    print("\n" + "=" * 80)
    print("📊 今天新增客户（按 add_time 秒级时间戳计算）：")
    print("=" * 80)
    
    today_start = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    
    cursor.execute("""
        SELECT id, name, add_time
        FROM customers
        WHERE add_time >= ?
        ORDER BY add_time DESC
    """, (today_start,))
    
    rows = cursor.fetchall()
    print(f"找到 {len(rows)} 条记录")
    for row in rows[:10]:
        add_time_dt = datetime.fromtimestamp(row['add_time'])
        print(f"  {row['name']:<20} {add_time_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 查询今天的数据（按 add_time 毫秒级计算）
    print("\n" + "=" * 80)
    print("📊 今天新增客户（按 add_time 毫秒级时间戳计算）：")
    print("=" * 80)
    
    today_start_ms = today_start * 1000
    
    cursor.execute("""
        SELECT id, name, add_time
        FROM customers
        WHERE add_time >= ?
        ORDER BY add_time DESC
    """, (today_start_ms,))
    
    rows = cursor.fetchall()
    print(f"找到 {len(rows)} 条记录")
    for row in rows[:10]:
        add_time_dt = datetime.fromtimestamp(row['add_time'] / 1000)
        print(f"  {row['name']:<20} {add_time_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn.close()

if __name__ == "__main__":
    check_add_time()
