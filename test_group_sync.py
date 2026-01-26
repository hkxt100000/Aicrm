"""
测试客户群同步 - 调试版本
"""
import time
from wecom_client import wecom_client

print("=" * 60)
print("🧪 测试客户群同步")
print("=" * 60)

# 测试1: 获取客户群ID列表
print("\n[测试1] 获取客户群ID列表...")
start_time = time.time()
chat_ids = wecom_client.get_group_chat_list(limit=100)
elapsed = time.time() - start_time
print(f"✅ 获取到 {len(chat_ids)} 个群ID，耗时 {elapsed:.2f} 秒")

if len(chat_ids) > 0:
    # 测试2: 获取单个群详情
    print(f"\n[测试2] 获取第一个群的详情 (chat_id: {chat_ids[0]})...")
    start_time = time.time()
    detail = wecom_client.get_group_chat_detail(chat_ids[0], need_name=False)
    elapsed = time.time() - start_time
    
    if detail:
        print(f"✅ 获取成功，耗时 {elapsed:.2f} 秒")
        print(f"   群名: {detail.get('name')}")
        print(f"   群主: {detail.get('owner')}")
        print(f"   总人数: {detail.get('member_count')}")
        print(f"   外部客户: {detail.get('external_member_count')}")
        print(f"   内部员工: {detail.get('internal_member_count')}")
    else:
        print(f"❌ 获取失败")
    
    # 测试3: 并发获取前10个群的详情
    print(f"\n[测试3] 并发获取前10个群的详情...")
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    test_chat_ids = chat_ids[:10]
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(wecom_client.get_group_chat_detail, cid, False): cid for cid in test_chat_ids}
        
        success_count = 0
        for future in as_completed(futures):
            result = future.result()
            if result:
                success_count += 1
    
    elapsed = time.time() - start_time
    print(f"✅ 完成，成功 {success_count}/{len(test_chat_ids)} 个，耗时 {elapsed:.2f} 秒")
    print(f"   平均每个群耗时: {elapsed/len(test_chat_ids):.2f} 秒")
    
    # 估算全量同步时间
    total_estimated_time = (elapsed / len(test_chat_ids)) * len(chat_ids) / 10
    print(f"\n📊 估算全量同步 {len(chat_ids)} 个群需要: {total_estimated_time:.2f} 秒 ({total_estimated_time/60:.2f} 分钟)")

print("\n" + "=" * 60)
print("🎉 测试完成")
print("=" * 60)
