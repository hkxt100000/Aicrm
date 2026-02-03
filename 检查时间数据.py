#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

# 连接数据库
conn = sqlite3.connect('data/crm.db')
cursor = conn.cursor()

print("=" * 60)
print("检查客户添加时间数据")
print("=" * 60)

# 获取当前时间
now = datetime.now()
print(f"\n当前服务器时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"当前时间戳: {int(now.timestamp())}")

# 查询最近10条客户的添加时间
print("\n" + "=" * 60)
print("最近10条客户的添加时间:")
print("=" * 60)

cursor.execute("""
    SELECT name, add_time 
    FROM customers 
    WHERE add_time IS NOT NULL 
    ORDER BY add_time DESC 
    LIMIT 10
""")

for row in cursor.fetchall():
    name = row[0]
    add_time = row[1]
    
    if add_time:
        dt = datetime.fromtimestamp(add_time)
        print(f"{name}: {dt.strftime('%Y-%m-%d %H:%M:%S')} (时间戳: {add_time})")

# 统计今日新增
print("\n" + "=" * 60)
print("按日期统计最近7天的新增:")
print("=" * 60)

for i in range(7):
    day_start = datetime(now.year, now.month, now.day) - timedelta(days=i)
    day_end = day_start + timedelta(days=1)
    
    start_ts = int(day_start.timestamp())
    end_ts = int(day_end.timestamp())
    
    cursor.execute("""
        SELECT COUNT(*) FROM customers
        WHERE add_time >= ? AND add_time < ?
    """, (start_ts, end_ts))
    
    count = cursor.fetchone()[0]
    date_str = day_start.strftime('%Y-%m-%d %A')
    print(f"{date_str}: {count}人")

# 统计本周、本月
from datetime import timedelta

today_start = datetime(now.year, now.month, now.day)
weekday = now.weekday()
week_start = today_start - timedelta(days=weekday)
month_start = datetime(now.year, now.month, 1)

print("\n" + "=" * 60)
print("汇总统计:")
print("=" * 60)

# 今日
cursor.execute("""
    SELECT COUNT(*) FROM customers
    WHERE add_time >= ? AND add_time < ?
""", (int(today_start.timestamp()), int((today_start + timedelta(days=1)).timestamp())))
print(f"今日新增 ({today_start.strftime('%Y-%m-%d')}): {cursor.fetchone()[0]}人")

# 本周
cursor.execute("""
    SELECT COUNT(*) FROM customers
    WHERE add_time >= ?
""", (int(week_start.timestamp()),))
print(f"本周新增 (从{week_start.strftime('%Y-%m-%d')}至今): {cursor.fetchone()[0]}人")

# 本月
cursor.execute("""
    SELECT COUNT(*) FROM customers
    WHERE add_time >= ?
""", (int(month_start.timestamp()),))
print(f"本月新增 (从{month_start.strftime('%Y-%m-%d')}至今): {cursor.fetchone()[0]}人")

conn.close()

print("\n" + "=" * 60)
print("检查完成！")
print("=" * 60)
print("\n请将上面的输出截图发给我，我来分析数据是否正确。")
