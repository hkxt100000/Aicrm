#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime, timedelta

# 连接数据库
conn = sqlite3.connect('data/crm.db')
cursor = conn.cursor()

print("=" * 80)
print("检查 customers 表结构和数据")
print("=" * 80)

# 1. 查看表结构
print("\n【1】customers 表的所有列：")
cursor.execute("PRAGMA table_info(customers)")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# 2. 查看最近10条数据的所有时间相关字段
print("\n【2】最近10条客户的时间字段数据：")
print("-" * 80)

cursor.execute("""
    SELECT id, name, add_time, created_at, updated_at
    FROM customers 
    ORDER BY id DESC 
    LIMIT 10
""")

for row in cursor.fetchall():
    cid, name, add_time, created_at, updated_at = row
    print(f"\nID: {cid}, 姓名: {name}")
    
    if add_time:
        dt = datetime.fromtimestamp(add_time)
        print(f"  add_time: {add_time} -> {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"  add_time: NULL")
    
    if created_at:
        print(f"  created_at: {created_at}")
    
    if updated_at:
        print(f"  updated_at: {updated_at}")

# 3. 统计 add_time 字段的数据情况
print("\n" + "=" * 80)
print("【3】add_time 字段统计：")
print("-" * 80)

cursor.execute("SELECT COUNT(*) FROM customers")
total = cursor.fetchone()[0]
print(f"总客户数: {total}")

cursor.execute("SELECT COUNT(*) FROM customers WHERE add_time IS NOT NULL")
has_add_time = cursor.fetchone()[0]
print(f"有 add_time 的客户数: {has_add_time}")

cursor.execute("SELECT COUNT(*) FROM customers WHERE add_time IS NULL")
null_add_time = cursor.fetchone()[0]
print(f"add_time 为 NULL 的客户数: {null_add_time}")

# 4. 查看今天和昨天的数据
print("\n" + "=" * 80)
print("【4】今天和昨天的数据（按 add_time）：")
print("-" * 80)

now = datetime.now()
print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"当前时间戳: {int(now.timestamp())}")

today_start = datetime(now.year, now.month, now.day)
today_ts = int(today_start.timestamp())

yesterday_start = today_start - timedelta(days=1)
yesterday_ts = int(yesterday_start.timestamp())

print(f"\n今天开始时间: {today_start.strftime('%Y-%m-%d %H:%M:%S')} (时间戳: {today_ts})")
print(f"昨天开始时间: {yesterday_start.strftime('%Y-%m-%d %H:%M:%S')} (时间戳: {yesterday_ts})")

# 今天的数据
cursor.execute("""
    SELECT COUNT(*) FROM customers 
    WHERE add_time >= ?
""", (today_ts,))
today_count = cursor.fetchone()[0]
print(f"\n今天新增客户数 (add_time >= {today_ts}): {today_count}")

if today_count > 0:
    cursor.execute("""
        SELECT name, add_time 
        FROM customers 
        WHERE add_time >= ?
        ORDER BY add_time DESC
    """, (today_ts,))
    print("今天新增的客户列表:")
    for row in cursor.fetchall():
        name, add_time = row
        dt = datetime.fromtimestamp(add_time)
        print(f"  - {name}: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

# 昨天的数据
cursor.execute("""
    SELECT COUNT(*) FROM customers 
    WHERE add_time >= ? AND add_time < ?
""", (yesterday_ts, today_ts))
yesterday_count = cursor.fetchone()[0]
print(f"\n昨天新增客户数: {yesterday_count}")

if yesterday_count > 0:
    cursor.execute("""
        SELECT name, add_time 
        FROM customers 
        WHERE add_time >= ? AND add_time < ?
        ORDER BY add_time DESC
        LIMIT 5
    """, (yesterday_ts, today_ts))
    print("昨天新增的客户（前5条）:")
    for row in cursor.fetchall():
        name, add_time = row
        dt = datetime.fromtimestamp(add_time)
        print(f"  - {name}: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

# 5. 检查 created_at 字段
print("\n" + "=" * 80)
print("【5】检查 created_at 字段（可能客户列表用的是这个）：")
print("-" * 80)

cursor.execute("""
    SELECT name, created_at
    FROM customers 
    WHERE created_at IS NOT NULL
    ORDER BY created_at DESC 
    LIMIT 10
""")

print("最近10条客户的 created_at:")
for row in cursor.fetchall():
    name, created_at = row
    try:
        # 尝试解析为时间戳
        dt = datetime.fromtimestamp(int(created_at) / 1000)  # 可能是毫秒
        print(f"  - {name}: {created_at} -> {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    except:
        print(f"  - {name}: {created_at} (无法解析)")

conn.close()

print("\n" + "=" * 80)
print("检查完成！")
print("=" * 80)
print("\n请截图这个结果发给我！")
