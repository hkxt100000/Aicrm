#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试企业微信客户群详情API
查看实际返回的数据结构
"""
import requests
import json
from config import Config

config = Config()

# 获取access_token
def get_token():
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    params = {
        'corpid': config.corp_id,
        'corpsecret': config.app_secret  # 使用app_secret
    }
    response = requests.get(url, params=params)
    result = response.json()
    
    if result.get('errcode') == 0:
        return result.get('access_token')
    else:
        print(f"获取token失败: {result}")
        return None

# 获取客户群列表
def get_group_list(token):
    url = "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/groupchat/list"
    params = {'access_token': token}
    data = {
        'status_filter': 0,
        'offset': 0,
        'limit': 10  # 只获取前10个
    }
    
    response = requests.post(url, params=params, json=data)
    result = response.json()
    
    if result.get('errcode') == 0:
        return result.get('group_chat_list', [])
    else:
        print(f"获取群列表失败: {result}")
        return []

# 获取客户群详情
def get_group_detail(token, chat_id):
    url = "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/groupchat/get"
    params = {'access_token': token}
    data = {
        'chat_id': chat_id,
        'need_name': 0
    }
    
    response = requests.post(url, params=params, json=data, timeout=10)
    result = response.json()
    
    return result

# 主程序
print("\n" + "="*80)
print("测试企业微信客户群详情API")
print("="*80)

token = get_token()
if not token:
    print("\n❌ 无法获取access_token")
    input("\n按回车退出...")
    exit(1)

print(f"\n✅ 获取到 access_token")

groups = get_group_list(token)
if not groups:
    print("\n❌ 无法获取客户群列表")
    input("\n按回车退出...")
    exit(1)

print(f"\n✅ 获取到 {len(groups)} 个客户群")

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
    print(f"成员总数: {len(member_list)}")
    
    print(f"\n成员列表（前3个）：\n")
    for i, member in enumerate(member_list[:3], 1):
        print(f"成员 {i}:")
        print(f"  userid: {member.get('userid')}")
        print(f"  type: {member.get('type')} ← 检查这个值！")
        print(f"  join_time: {member.get('join_time')}")
        print(f"  join_scene: {member.get('join_scene')}")
        print()
    
    # 统计type分布
    type_count = {}
    for member in member_list:
        t = member.get('type')
        type_count[t] = type_count.get(t, 0) + 1
    
    print("="*80)
    print("成员类型分布：")
    for t, count in type_count.items():
        print(f"  type={t}: {count} 个成员")
    
    print("\n根据企业微信文档：")
    print("  type=1: 内部员工")
    print("  type=2: 外部联系人")
    
    external_count = sum(1 for m in member_list if m.get('type') == 2)
    internal_count = sum(1 for m in member_list if m.get('type') == 1)
    
    print(f"\n计算结果：")
    print(f"  外部客户数: {external_count}")
    print(f"  内部员工数: {internal_count}")
    
    if external_count == 0 and internal_count == 0:
        print("\n⚠️  警告：所有成员的 type 都不是 1 或 2！")
        print("这就是为什么数据库里存的都是0的原因！")
    
    print("="*80)
    
else:
    print(f"\n❌ 获取失败: {result}")

input("\n按回车退出...")
