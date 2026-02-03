#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询数据库并输出到文本文件
"""

import sqlite3
import os

def query_database():
    try:
        db_path = 'data/crm.db'
        
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            return
        
        print(f"连接数据库: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        output = []
        output.append("=" * 80)
        output.append("数据库查询结果")
        output.append("=" * 80)
        
        # 1. 查询标签库
        output.append("\n【1】customer_tags 表 - 标签库：")
        cursor.execute("SELECT id, name, group_name FROM customer_tags LIMIT 20")
        tags = cursor.fetchall()
        if tags:
            for tag in tags:
                output.append(f"  ID={tag[0]}, 标签名={tag[1]}, 标签组={tag[2]}")
        else:
            output.append("  (空)")
        
        # 2. 查询客户的标签
        output.append("\n【2】customers 表 - 客户标签示例：")
        cursor.execute("""
            SELECT id, name, enterprise_tags 
            FROM customers 
            WHERE enterprise_tags IS NOT NULL AND enterprise_tags != ''
            LIMIT 5
        """)
        customers = cursor.fetchall()
        if customers:
            for c in customers:
                output.append(f"  客户: {c[1]}")
                output.append(f"  标签: {c[2]}")
                output.append("")
        else:
            output.append("  (没有客户有标签)")
        
        # 3. 查询 add_way 分布
        output.append("\n【3】add_way 字段分布：")
        cursor.execute("""
            SELECT add_way, COUNT(*) as count
            FROM customers
            WHERE add_way IS NOT NULL
            GROUP BY add_way
            ORDER BY add_way
        """)
        add_ways = cursor.fetchall()
        if add_ways:
            for way in add_ways:
                output.append(f"  add_way={way[0]}: {way[1]}人")
        else:
            output.append("  (无数据)")
        
        # 4. 查询 gender 分布
        output.append("\n【4】gender 字段分布：")
        cursor.execute("""
            SELECT gender, COUNT(*) as count
            FROM customers
            WHERE gender IS NOT NULL
            GROUP BY gender
            ORDER BY gender
        """)
        genders = cursor.fetchall()
        if genders:
            for g in genders:
                output.append(f"  gender={g[0]}: {g[1]}人")
        else:
            output.append("  (无数据)")
        
        # 5. 统计总数
        output.append("\n【5】统计信息：")
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]
        output.append(f"  客户总数: {total_customers}")
        
        cursor.execute("SELECT COUNT(*) FROM customer_tags")
        total_tags = cursor.fetchone()[0]
        output.append(f"  标签总数: {total_tags}")
        
        cursor.execute("""
            SELECT COUNT(*) FROM customers 
            WHERE enterprise_tags IS NOT NULL AND enterprise_tags != ''
        """)
        customers_with_tags = cursor.fetchone()[0]
        output.append(f"  有标签的客户: {customers_with_tags}")
        
        conn.close()
        
        output.append("\n" + "=" * 80)
        output.append("查询完成！")
        output.append("=" * 80)
        
        # 输出到屏幕
        result_text = "\n".join(output)
        print(result_text)
        
        # 保存到文件
        with open('数据库查询结果.txt', 'w', encoding='utf-8') as f:
            f.write(result_text)
        
        print("\n✅ 结果已保存到: 数据库查询结果.txt")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    query_database()
    input("\n按回车键退出...")
