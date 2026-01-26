"""
检查数据库连接和客户数据
"""
import sqlite3
import os

# 可能的数据库路径
possible_paths = [
    './crm.db',
    '../crm.db',
    'D:/tianhao-webhook/wecom-crm/backend/crm.db',
    'crm.db'
]

print("="*100)
print("检查数据库文件和连接")
print("="*100)

for db_path in possible_paths:
    print(f"\n检查路径: {db_path}")
    
    # 检查文件是否存在
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        print(f"  ✅ 文件存在")
        print(f"  📁 文件大小: {file_size:,} 字节 ({file_size / 1024 / 1024:.2f} MB)")
        
        try:
            # 尝试连接并查询
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"  📊 表数量: {len(tables)}")
            
            if tables:
                print(f"  📋 表列表:")
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"     - {table_name}: {count} 行")
            
            # 检查 customers 表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM customers")
                customer_count = cursor.fetchone()[0]
                print(f"\n  👥 客户总数: {customer_count}")
                
                if customer_count > 0:
                    # 检查标签字段
                    cursor.execute("SELECT COUNT(*) FROM customers WHERE enterprise_tags IS NOT NULL AND enterprise_tags != '' AND enterprise_tags != '[]'")
                    with_tags = cursor.fetchone()[0]
                    print(f"  🏷️  有企业标签的客户: {with_tags}")
                    
                    # 显示前5个客户
                    cursor.execute("SELECT id, name, enterprise_tags FROM customers LIMIT 5")
                    print(f"\n  📝 前5个客户:")
                    for row in cursor.fetchall():
                        cid, cname, tags = row
                        tag_info = "无标签" if not tags or tags == '[]' else f"有标签 ({len(tags)} 字符)"
                        print(f"     - {cname or cid}: {tag_info}")
            else:
                print(f"  ⚠️  customers 表不存在")
            
            conn.close()
            
        except Exception as e:
            print(f"  ❌ 连接失败: {e}")
    else:
        print(f"  ❌ 文件不存在")

print("\n" + "="*100)
print("建议:")
print("="*100)
print("1. 找到正确的 crm.db 文件（大小应该 > 1MB）")
print("2. 修改 config.py 中的 DB_PATH 指向正确的文件")
print("3. 或者在 check_tag_statistics.py 中使用绝对路径")
