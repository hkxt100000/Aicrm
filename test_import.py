#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导入 app 模块
"""
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("=" * 80)
print("测试导入模块")
print("=" * 80)

try:
    print("\n1. 测试导入 config...")
    import config
    print(f"✅ config 导入成功")
    print(f"   CORP_ID: {config.CORP_ID[:10]}..." if config.CORP_ID else "   CORP_ID: 空")
    
    print("\n2. 测试导入 wecom_client...")
    from wecom_client import WeComClient
    print(f"✅ wecom_client 导入成功")
    
    print("\n3. 测试导入 app...")
    import app
    print(f"✅ app 导入成功")
    
    print("\n" + "=" * 80)
    print("🎉 所有模块导入成功！")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 导入失败: {e}")
    import traceback
    print("\n完整错误:")
    traceback.print_exc()
