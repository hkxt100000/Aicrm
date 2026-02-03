#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 customers 表的 add_time 字段格式
"""

import sqlite3
from datetime import datetime

DB_PATH = "data/crm.db"

def check_customer_add_time():
    """检查客户表的 add_time 字段"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 80)
    print("🔍 检查 customers 表的 add_time 字段格式")
    print("=" * 80)
    
    # 查询最新 10 条数据的时间字段
    cursor.execute("""
        SELECT id, name, add_time, created_at, updated_at
        FROM customers
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    
    print(f"\n📊 最新 10 条客户的时间字段：")
    print("-" * 80)
    
    for row in rows:
        print(f"\n客户：{row['name']} (ID: {row['id']})")
        
        # add_time
        add_time = row['add_time']
        if add_time:
            add_time_len = len(str(add_time))
            print(f"  add_time: {add_time} ({add_time_len}位)")
            
            if add_time_len == 10:
                # 秒级时间戳
                add_time_dt = datetime.fromtimestamp(add_time)
                print(f"    └─ 秒级解析: {add_time_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            elif add_time_len >= 13:
                # 毫秒级时间戳
                add_time_dt = datetime.fromtimestamp(add_time / 1000)
                print(f"    └─ 毫秒级解析: {add_time_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"  add_time: NULL")
        
        # created_at
        created_at = row['created_at']
        if created_at:
            created_at_len = len(str(created_at))
            print(f"  created_at: {created_at} ({created_at_len}位)")
            
            if created_at_len == 10:
                created_at_dt = datetime.fromtimestamp(created_at)
                print(f"    └─ 秒级解析: {created_at_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            elif created_at_len >= 13:
                created_at_dt = datetime.fromtimestamp(created_at / 1000)
                print(f"    └─ 毫秒级解析: {created_at_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"  created_at: NULL")
    
    # 统计 add_time 的位数分布
    print("\n" + "=" * 80)
    print("📊 add_time 字段位数分布统计：")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN add_time IS NULL THEN 'NULL'
                WHEN LENGTH(CAST(add_time AS TEXT)) = 10 THEN '10位(秒级)'
                WHEN LENGTH(CAST(add_time AS TEXT)) >= 13 THEN '13位+(毫秒级)'
                ELSE '其他'
            END as time_format,
            COUNT(*) as count
        FROM customers
        GROUP BY time_format
        ORDER BY count DESC
    """)
    
    for row in cursor.fetchall():
        print(f"{row['time_format']:<20} {row['count']:>8,} 条")
    
    # 查询今天的数据（按 add_time 秒级计算）
    print("\n" + "=" * 80)
    print("📊 今天新增客户（按 add_time 秒级时间戳计算）：")
    print("=" * 80)
    
    today_start = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    print(f"今天开始时间戳: {today_start} ({datetime.fromtimestamp(today_start).strftime('%Y-%m-%d %H:%M:%S')})")
    
    cursor.execute("""
        SELECT id, name, add_time
        FROM customers
        WHERE add_time >= ? AND add_time < 9999999999
        ORDER BY add_time DESC
        LIMIT 10
    """, (today_start,))
    
    rows = cursor.fetchall()
    print(f"\n找到 {len(rows)} 条记录（显示前10条）")
    
    if rows:
        for row in rows:
            add_time_dt = datetime.fromtimestamp(row['add_time'])
            print(f"  {row['name']:<20} {add_time_dt.strftime('%Y-%m-%d %H:%M:%S')} (add_time: {row['add_time']})")
    else:
        print("  无数据")
    
    # 查询今天的数据（按 add_time 毫秒级计算）
    print("\n" + "=" * 80)
    print("📊 今天新增客户（按 add_time 毫秒级时间戳计算）：")
    print("=" * 80)
    
    today_start_ms = today_start * 1000
    print(f"今天开始时间戳(毫秒): {today_start_ms} ({datetime.fromtimestamp(today_start_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')})")
    
    cursor.execute("""
        SELECT id, name, add_time
        FROM customers
        WHERE add_time >= ?
        ORDER BY add_time DESC
        LIMIT 10
    """, (today_start_ms,))
    
    rows = cursor.fetchall()
    print(f"\n找到 {len(rows)} 条记录（显示前10条）")
    
    if rows:
        for row in rows:
            add_time_dt = datetime.fromtimestamp(row['add_time'] / 1000)
            print(f"  {row['name']:<20} {add_time_dt.strftime('%Y-%m-%d %H:%M:%S')} (add_time: {row['add_time']})")
    else:
        print("  无数据")
    
    # 查询今天的数据（按 created_at 毫秒级计算）
    print("\n" + "=" * 80)
    print("📊 今天同步的客户（按 created_at 毫秒级时间戳计算）：")
    print("=" * 80)
    
    cursor.execute("""
        SELECT id, name, add_time, created_at
        FROM customers
        WHERE created_at >= ?
        ORDER BY created_at DESC
        LIMIT 10
    """, (today_start_ms,))
    
    rows = cursor.fetchall()
    print(f"\n找到 {len(rows)} 条记录（显示前10条）")
    
    if rows:
        for row in rows:
            created_at_dt = datetime.fromtimestamp(row['created_at'] / 1000)
            if row['add_time']:
                if len(str(row['add_time'])) == 10:
                    add_time_dt = datetime.fromtimestamp(row['add_time'])
                else:
                    add_time_dt = datetime.fromtimestamp(row['add_time'] / 1000)
                add_time_str = add_time_dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                add_time_str = 'NULL'
            
            print(f"  {row['name']:<20}")
            print(f"    add_time: {add_time_str} ({row['add_time']})")
            print(f"    created_at: {created_at_dt.strftime('%Y-%m-%d %H:%M:%S')} ({row['created_at']})")
    else:
        print("  无数据")
    
    conn.close()

if __name__ == "__main__":
    check_customer_add_time()
