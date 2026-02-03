#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

# 连接数据库
conn = sqlite3.connect('data/crm.db')
cursor = conn.cursor()

print("=" * 80)
print("检查最新客户的 add_time 数据")
print("=" * 80)

# 按 add_time 降序查询最新的20条客户
cursor.execute("""
    SELECT name, add_time, created_at
    FROM customers 
    WHERE add_time IS NOT NULL
    ORDER BY add_time DESC 
    LIMIT 20
""")

print("\n最新20条客户（按 add_time 排序）：")
print("-" * 80)

for row in cursor.fetchall():
    name, add_time, created_at = row
    
    # add_time 转换（秒级时间戳）
    dt_add = datetime.fromtimestamp(add_time)
    
    # created_at 转换（毫秒级时间戳）
    if created_at:
        dt_created = datetime.fromtimestamp(created_at / 1000)
        created_str = dt_created.strftime('%Y-%m-%d %H:%M:%S')
    else:
        created_str = 'NULL'
    
    print(f"{name}:")
    print(f"  add_time: {add_time} -> {dt_add.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  created_at: {created_at} -> {created_str}")
    print()

# 统计2026年1月25日的数据
print("=" * 80)
print("检查 2026-01-25 的数据")
print("=" * 80)

# 2026-01-25 的时间戳范围
date_2026_01_25 = datetime(2026, 1, 25)
date_2026_01_26 = datetime(2026, 1, 26)
ts_start = int(date_2026_01_25.timestamp())
ts_end = int(date_2026_01_26.timestamp())

print(f"\n时间范围: {date_2026_01_25.strftime('%Y-%m-%d')} 00:00:00 到 {date_2026_01_26.strftime('%Y-%m-%d')} 00:00:00")
print(f"时间戳范围: {ts_start} 到 {ts_end}")

cursor.execute("""
    SELECT COUNT(*) FROM customers 
    WHERE add_time >= ? AND add_time < ?
""", (ts_start, ts_end))

count = cursor.fetchone()[0]
print(f"\n2026-01-25 新增客户数（按 add_time）: {count}")

if count > 0:
    cursor.execute("""
        SELECT name, add_time 
        FROM customers 
        WHERE add_time >= ? AND add_time < ?
        ORDER BY add_time DESC
    """, (ts_start, ts_end))
    
    print("\n客户列表:")
    for row in cursor.fetchall():
        name, add_time = row
        dt = datetime.fromtimestamp(add_time)
        print(f"  - {name}: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

# 按 created_at 排序查看最新的数据
print("\n" + "=" * 80)
print("按 created_at 排序的最新20条客户：")
print("=" * 80)

cursor.execute("""
    SELECT name, add_time, created_at
    FROM customers 
    WHERE created_at IS NOT NULL
    ORDER BY created_at DESC 
    LIMIT 20
""")

for row in cursor.fetchall():
    name, add_time, created_at = row
    
    # add_time 转换
    if add_time:
        dt_add = datetime.fromtimestamp(add_time)
        add_str = dt_add.strftime('%Y-%m-%d %H:%M:%S')
    else:
        add_str = 'NULL'
    
    # created_at 转换（毫秒）
    dt_created = datetime.fromtimestamp(created_at / 1000)
    
    print(f"{name}:")
    print(f"  add_time: {add_time} -> {add_str}")
    print(f"  created_at: {created_at} -> {dt_created.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

conn.close()

print("=" * 80)
print("检查完成！")
print("=" * 80)
