#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 Excel 文件结构
"""
import openpyxl

# 读取 Excel
wb = openpyxl.load_workbook('test_excel.xlsx')
ws = wb.active

print("=" * 80)
print("Excel 文件分析")
print("=" * 80)

# 获取数据
rows = list(ws.values)

print(f"\n总行数: {len(rows)}")
print(f"总列数: {len(rows[0]) if rows else 0}")

# 表头
print(f"\n表头（前10个字段）:")
headers = rows[0]
for i, header in enumerate(headers[:10]):
    print(f"  列{i}: {header}")

# 第一行数据
print(f"\n第一行数据（前10列）:")
if len(rows) > 1:
    first_row = rows[1]
    for i, value in enumerate(first_row[:10]):
        print(f"  列{i} ({headers[i]}): {value}")

# 第二行数据
print(f"\n第二行数据（前10列）:")
if len(rows) > 2:
    second_row = rows[2]
    for i, value in enumerate(second_row[:10]):
        print(f"  列{i} ({headers[i]}): {value}")

print("\n" + "=" * 80)
