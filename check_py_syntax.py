#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 Python 文件的语法
"""
import sys
import py_compile

print("=" * 60)
print("检查 Python 语法")
print("=" * 60)

files = ['config.py', 'wecom_client.py', 'app.py']

for filename in files:
    print(f"\n检查 {filename}...")
    try:
        py_compile.compile(filename, doraise=True)
        print(f"✅ {filename} 语法正确")
    except py_compile.PyCompileError as e:
        print(f"❌ {filename} 有语法错误:")
        print(str(e))
        sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有文件语法正确！")
print("=" * 60)
