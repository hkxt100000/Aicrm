#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证昨天的新增客户数据
"""

import sqlite3
from datetime import datetime, timedelta

DB_PATH = "data/crm.db"

def check_yesterday_customers():
    """检查昨天的新增客户"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 昨天的时间范围
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    
    yesterday_start_ts = int(yesterday_start.timestamp())
    today_start_ts = int(today_start.timestamp())
    
    print("=" * 80)
    print("📊 昨天（2026-01-25）新增客户统计")
    print("=" * 80)
    print(f"昨天开始: {yesterday_start.strftime('%Y-%m-%d %H:%M:%S')} (时间戳: {yesterday_start_ts})")
    print(f"今天开始: {today_start.strftime('%Y-%m-%d %H:%M:%S')} (时间戳: {today_start_ts})")
    print()
    
    # 查询昨天新增的客户
    cursor.execute("""
        SELECT id, name, add_time
        FROM customers
        WHERE add_time >= ? AND add_time < ?
        ORDER BY add_time DESC
    """, (yesterday_start_ts, today_start_ts))
    
    rows = cursor.fetchall()
    
    print(f"找到 {len(rows)} 条昨天新增的客户：")
    print("-" * 80)
    
    for i, row in enumerate(rows, 1):
        add_time_dt = datetime.fromtimestamp(row['add_time'])
        print(f"{i}. {row['name']:<30} {add_time_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 80)
    print(f"✅ 昨日新增统计：{len(rows)} 人")
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    check_yesterday_customers()
