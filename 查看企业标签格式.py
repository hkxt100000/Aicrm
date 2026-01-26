#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看企业标签的实际存储格式
"""

import sqlite3
import json

def check_enterprise_tags():
    """检查企业标签格式"""
    try:
        conn = sqlite3.connect('data/crm.db')
        cursor = conn.cursor()
        
        print("=" * 80)
        print("查看企业标签格式")
        print("=" * 80)
        
        # 1. 检查 customer_tags 表
        cursor.execute("""
            SELECT id, name, group_name, order_num 
            FROM customer_tags 
            LIMIT 10
        """)
        tags = cursor.fetchall()
        
        print("\n【customer_tags 表】企业标签库：")
        if tags:
            for tag in tags:
                print(f"  ID={tag[0]}, 标签名={tag[1]}, 标签组={tag[2]}, 排序={tag[3]}")
        else:
            print("  ❌ 标签库为空！需要先同步标签数据")
        
        # 2. 检查 customers 表的 enterprise_tags 字段
        cursor.execute("""
            SELECT id, name, enterprise_tags 
            FROM customers 
            WHERE enterprise_tags IS NOT NULL AND enterprise_tags != ''
            LIMIT 5
        """)
        customers = cursor.fetchall()
        
        print("\n【customers 表】客户的企业标签：")
        if customers:
            for customer in customers:
                print(f"\n  客户ID: {customer[0]}")
                print(f"  客户名: {customer[1]}")
                print(f"  标签原始值: {customer[2]}")
                
                # 尝试解析标签格式
                try:
                    # 可能是 JSON 数组
                    if customer[2].startswith('['):
                        tags_data = json.loads(customer[2])
                        print(f"  标签格式: JSON数组")
                        print(f"  标签内容: {tags_data}")
                    else:
                        # 可能是逗号分隔
                        print(f"  标签格式: 逗号分隔字符串")
                        print(f"  标签列表: {customer[2].split(',')}")
                except:
                    print(f"  标签格式: 未知格式")
        else:
            print("  ❌ 没有客户有企业标签！")
        
        # 3. 统计标签使用情况
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN enterprise_tags IS NOT NULL AND enterprise_tags != '' THEN 1 END) as has_tags
            FROM customers
        """)
        stats = cursor.fetchone()
        
        print(f"\n【统计】")
        print(f"  客户总数: {stats[0]}")
        print(f"  有企业标签的客户: {stats[1]}")
        
        # 4. 检查 add_way 的实际值
        cursor.execute("""
            SELECT DISTINCT add_way, COUNT(*) as count
            FROM customers
            WHERE add_way IS NOT NULL
            GROUP BY add_way
            ORDER BY add_way
        """)
        add_ways = cursor.fetchall()
        
        print(f"\n【add_way 字段的实际值】")
        add_way_map = {
            0: "未知",
            1: "扫描二维码",
            2: "搜索手机号",
            3: "名片分享",
            4: "群聊",
            5: "手机通讯录",
            6: "微信联系人",
            7: "来自微信的添加好友申请",
            8: "安装第三方应用时自动添加的客服人员",
            9: "搜索邮箱",
            201: "内部成员共享",
            202: "管理员/负责人分配"
        }
        
        if add_ways:
            for way in add_ways:
                desc = add_way_map.get(way[0], "未知")
                print(f"  add_way={way[0]} ({desc}): {way[1]}人")
        else:
            print("  ❌ 没有 add_way 数据")
        
        # 5. 检查 gender 的实际值
        cursor.execute("""
            SELECT DISTINCT gender, COUNT(*) as count
            FROM customers
            WHERE gender IS NOT NULL
            GROUP BY gender
            ORDER BY gender
        """)
        genders = cursor.fetchall()
        
        print(f"\n【gender 字段的实际值】")
        gender_map = {0: "未知", 1: "男", 2: "女"}
        
        if genders:
            for g in genders:
                desc = gender_map.get(g[0], "未知")
                print(f"  gender={g[0]} ({desc}): {g[1]}人")
        else:
            print("  ❌ 没有 gender 数据")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("检查完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_enterprise_tags()
