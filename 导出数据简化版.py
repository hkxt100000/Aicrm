#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导出数据库关键数据用于分析
"""

import sqlite3
import json

def export_data():
    try:
        print("连接数据库...")
        conn = sqlite3.connect('data/crm.db')
        cursor = conn.cursor()
        
        print("导出标签数据...")
        cursor.execute('SELECT * FROM customer_tags LIMIT 50')
        tags = cursor.fetchall()
        
        print("导出客户数据...")
        cursor.execute('''
            SELECT id, name, enterprise_tags, add_way, gender, owner_userid, tags
            FROM customers 
            LIMIT 100
        ''')
        customers = cursor.fetchall()
        
        # 转换为可序列化的格式
        data = {
            'tags': [[str(c) if c else '' for c in row] for row in tags],
            'customers': [[str(c) if c else '' for c in row] for row in customers]
        }
        
        print("保存到文件...")
        with open('数据导出.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("\n✅ 导出成功！")
        print(f"   标签数量: {len(tags)}")
        print(f"   客户数量: {len(customers)}")
        print(f"   文件位置: 数据导出.json")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    export_data()
    input("\n按回车键退出...")
