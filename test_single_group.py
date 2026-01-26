#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单个客户群获取
"""
import sys
sys.path.insert(0, '.')

from wecom_client import wecom_client
import json

# 测试获取单个群
print("=" * 60)
print("测试客户群详情获取")
print("=" * 60)

# 从日志中看到有1398个群，随便取第一个测试
chat_ids = wecom_client.get_group_chat_list()
print(f"\n✅ 获取到 {len(chat_ids)} 个群ID")

if chat_ids:
    test_chat_id = chat_ids[0]
    print(f"\n📝 测试群ID: {test_chat_id}")
    print("🔄 正在获取详情...")
    
    import time
    start = time.time()
    
    detail = wecom_client.get_group_chat_detail(test_chat_id, need_name=False)
    
    duration = time.time() - start
    
    if detail:
        print(f"\n✅ 获取成功 (耗时 {duration:.2f} 秒)")
        print(f"\n详情:")
        print(json.dumps(detail, ensure_ascii=False, indent=2))
    else:
        print(f"\n❌ 获取失败 (耗时 {duration:.2f} 秒)")
        print("\n可能原因:")
        print("1. API限流")
        print("2. 权限不足")
        print("3. 网络超时")
        print("4. 群已解散")
else:
    print("\n❌ 未获取到群ID列表")
