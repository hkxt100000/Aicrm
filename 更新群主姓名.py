#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新现有客户群的群主姓名
从企业微信API重新获取并更新
"""
import sqlite3
import sys
sys.path.append('.')
from wecom_client import WeComClient

DB_PATH = 'wecom_crm.db'

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 获取所有群
cursor.execute("SELECT chat_id, name, owner_userid FROM customer_groups WHERE owner_name = '' OR owner_name IS NULL")
groups = cursor.fetchall()

print(f"\n需要更新群主姓名的群: {len(groups)} 个\n")

if len(groups) == 0:
    print("✅ 所有群的群主姓名都已填写")
    conn.close()
    exit(0)

# 初始化企业微信客户端
wecom_client = WeComClient()

updated = 0
failed = 0

for chat_id, name, owner_userid in groups:
    print(f"正在更新: {name[:20]}...", end=' ')
    
    try:
        # 重新获取群详情
        detail = wecom_client.get_group_chat_detail(chat_id, need_name=False)
        
        if detail and detail.get('owner_name'):
            owner_name = detail['owner_name']
            
            # 更新数据库
            cursor.execute("UPDATE customer_groups SET owner_name = ? WHERE chat_id = ?", (owner_name, chat_id))
            conn.commit()
            
            print(f"✅ {owner_name}")
            updated += 1
        else:
            print(f"⚠️  无法获取")
            failed += 1
            
    except Exception as e:
        print(f"❌ {e}")
        failed += 1

conn.close()

print(f"\n" + "="*60)
print(f"更新完成！")
print(f"  成功: {updated}")
print(f"  失败: {failed}")
print("="*60)

input("\n按回车退出...")
