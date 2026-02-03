#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 Python 文件语法错误
"""

import py_compile
import sys

def check_syntax(filepath):
    """检查 Python 文件语法"""
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"✅ {filepath} - 语法正确")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ {filepath} - 语法错误:")
        print(f"   {e}")
        return False

if __name__ == "__main__":
    files = [
        'app.py',
        'wecom_client.py',
        'sync_service.py',
        'start.py',
        'init_database.py',
        'fix_customer_sync_time.py'
    ]
    
    print("=" * 60)
    print("检查 Python 文件语法")
    print("=" * 60)
    
    all_ok = True
    for file in files:
        if not check_syntax(file):
            all_ok = False
    
    print("=" * 60)
    if all_ok:
        print("✅ 所有文件语法正确！")
        sys.exit(0)
    else:
        print("❌ 部分文件有语法错误，请修复后再启动")
        sys.exit(1)
