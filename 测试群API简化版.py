#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试企业微信客户群详情API - 简化版
直接输入配置信息
"""
import requests
import json

# ========== 请填写你的企业微信配置 ==========
CORP_ID = "wwae4f99f11753a5ea"  # 你的企业ID
APP_SECRET = ""  # 你的应用Secret（如果为空，下面会提示输入）

# ===========================================

def get_token(corp_id, app_secret):
    """获取access_token"""
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    params = {
        'corpid': corp_id,
        'corpsecret': app_secret
    }
    response = requests.get(url, params=params, timeout=10)
    result = response.json()
    
    if result.get('errcode') == 0:
        return result.get('access_token')
    else:
        print(f"❌ 获取token失败: {result}")
        return None

def get_group_list(token):
    """获取客户群列表（前10个）"""
    url = "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/groupchat/list"
    params = {'access_token': token}
    data = {
        'status_filter': 0,
        'offset': 0,
        'limit': 10
    }
    
    response = requests.post(url, params=params, json=data, timeout=10)
    result = response.json()
    
    if result.get('errcode') == 0:
        return result.get('group_chat_list', [])
    else:
        print(f"❌ 获取群列表失败: {result}")
        return []

def get_group_detail(token, chat_id):
    """获取客户群详情"""
    url = "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/groupchat/get"
    params = {'access_token': token}
    data = {
        'chat_id': chat_id,
        'need_name': 0
    }
    
    response = requests.post(url, params=params, json=data, timeout=10)
    return response.json()

# ========== 主程序 ==========
print("\n" + "="*80)
print("测试企业微信客户群详情API")
print("="*80)

# 如果没有填写APP_SECRET，提示输入
if not APP_SECRET:
    print("\n请输入你的应用Secret（app_secret）：")
    APP_SECRET = input().strip()

print(f"\n正在获取 access_token...")
token = get_token(CORP_ID, APP_SECRET)

if not token:
    print("\n❌ 无法获取access_token，请检查配置")
    input("\n按回车退出...")
    exit(1)

print(f"✅ 获取到 access_token")

print(f"\n正在获取客户群列表...")
groups = get_group_list(token)

if not groups:
    print("\n❌ 无法获取客户群列表")
    input("\n按回车退出...")
    exit(1)

print(f"✅ 获取到 {len(groups)} 个客户群")

# 获取第一个群的详情
first_group = groups[0]
chat_id = first_group.get('chat_id')

print(f"\n正在获取群详情: {chat_id}")
print("-"*80)

result = get_group_detail(token, chat_id)

if result.get('errcode') == 0:
    group_chat = result.get('group_chat', {})
    member_list = group_chat.get('member_list', [])
    
    print(f"\n✅ 获取成功！")
    print(f"\n群名称: {group_chat.get('name')}")
    print(f"群主: {group_chat.get('owner')}")
    print(f"成员总数: {len(member_list)}")
    
    if member_list:
        print(f"\n前3个成员的详细信息：\n")
        for i, member in enumerate(member_list[:3], 1):
            print(f"成员 {i}:")
            print(f"  userid: {member.get('userid')}")
            print(f"  type: {member.get('type')} ← 关键字段！")
            print(f"  unionid: {member.get('unionid', '无')}")
            print(f"  join_time: {member.get('join_time')}")
            print(f"  join_scene: {member.get('join_scene')}")
            print()
        
        # 统计type分布
        type_count = {}
        for member in member_list:
            t = member.get('type')
            type_count[t] = type_count.get(t, 0) + 1
        
        print("="*80)
        print("所有成员的 type 分布：")
        print("-"*80)
        for t, count in sorted(type_count.items()):
            print(f"  type = {t}: {count} 个成员")
        
        print("\n根据企业微信官方文档：")
        print("  type = 1: 企业成员（内部员工）")
        print("  type = 2: 外部联系人（客户）")
        
        external_count = sum(1 for m in member_list if m.get('type') == 2)
        internal_count = sum(1 for m in member_list if m.get('type') == 1)
        
        print(f"\n根据代码计算的结果：")
        print(f"  外部客户数 (type=2): {external_count}")
        print(f"  内部员工数 (type=1): {internal_count}")
        
        if external_count == 0 and internal_count == 0:
            print("\n" + "="*80)
            print("⚠️  发现问题！")
            print("="*80)
            print("所有成员的 type 都不是 1 或 2！")
            print("这就是为什么数据库里 external_member_count 和 internal_member_count 都是 0！")
            print("\n可能的原因：")
            print("1. 企业微信API返回的数据结构有变化")
            print("2. 这个群里没有外部客户，也没有内部员工")
            print("3. type字段的定义和我们理解的不一样")
            print("="*80)
        else:
            print("\n✅ type 字段正常，代码逻辑没问题")
    else:
        print("\n⚠️  这个群没有成员！")
    
    print("\n" + "="*80)
    
else:
    print(f"\n❌ 获取群详情失败: errcode={result.get('errcode')}, errmsg={result.get('errmsg')}")

input("\n按回车退出...")
