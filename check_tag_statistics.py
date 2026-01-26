"""
检查客户画像分析中的标签统计数据准确性
"""
import sqlite3
import json
from collections import Counter

DB_PATH = './data/crm.db'  # 修改为正确的路径

def check_tag_statistics():
    """检查标签统计数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*100)
    print("客户画像分析 - 标签统计数据检查")
    print("="*100)
    
    # 1. 检查客户总数
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]
    print(f"\n📊 数据库中客户总数: {total_customers}")
    
    # 2. 检查有标签的客户数量（使用 enterprise_tags 字段）
    cursor.execute("SELECT COUNT(*) FROM customers WHERE enterprise_tags IS NOT NULL AND enterprise_tags != '[]' AND enterprise_tags != ''")
    customers_with_tags = cursor.fetchone()[0]
    print(f"📊 有企业标签的客户数: {customers_with_tags}")
    print(f"📊 无企业标签的客户数: {total_customers - customers_with_tags}")
    
    # 3. 获取所有客户的企业标签数据
    cursor.execute("SELECT id, name, enterprise_tags FROM customers WHERE enterprise_tags IS NOT NULL AND enterprise_tags != '[]' AND enterprise_tags != ''")
    customers = cursor.fetchall()
    
    print(f"\n" + "="*100)
    print("开始统计每个标签的客户数量（基于 enterprise_tags 字段）...")
    print("="*100)
    
    # 标签统计字典
    tag_customer_count = {}  # {tag_name: count}
    tag_customer_details = {}  # {tag_name: [(customer_id, customer_name), ...]}
    
    # 遍历每个客户
    for customer_id, customer_name, tags_str in customers:
        try:
            # 解析标签 JSON
            tags = json.loads(tags_str) if tags_str else []
            
            # 统计每个标签
            for tag in tags:
                tag_name = tag.get('tag_name', '')
                if tag_name:
                    # 计数
                    if tag_name not in tag_customer_count:
                        tag_customer_count[tag_name] = 0
                        tag_customer_details[tag_name] = []
                    
                    tag_customer_count[tag_name] += 1
                    tag_customer_details[tag_name].append((customer_id, customer_name or customer_id))
        except Exception as e:
            print(f"❌ 解析客户 {customer_id} 的企业标签失败: {e}")
            print(f"   标签数据: {tags_str[:100]}...")
    
    # 4. 显示所有标签统计
    print(f"\n" + "="*100)
    print("所有标签统计结果:")
    print("="*100)
    print(f"{'标签名称':<30} {'客户数量':>10}")
    print("-"*100)
    
    # 按客户数量降序排序
    sorted_tags = sorted(tag_customer_count.items(), key=lambda x: x[1], reverse=True)
    
    for tag_name, count in sorted_tags:
        print(f"{tag_name:<30} {count:>10}")
    
    # 5. 重点检查问题标签
    print(f"\n" + "="*100)
    print("🔍 重点检查问题标签:")
    print("="*100)
    
    problem_tags = ['原有老代理商', '代理商']
    
    for tag_name in problem_tags:
        if tag_name in tag_customer_count:
            count = tag_customer_count[tag_name]
            print(f"\n📌 标签: {tag_name}")
            print(f"   实际客户数: {count}")
            print(f"   前10个客户:")
            
            for i, (cid, cname) in enumerate(tag_customer_details[tag_name][:10], 1):
                print(f"      {i}. {cname} (ID: {cid})")
            
            if count > 10:
                print(f"      ... 还有 {count - 10} 个客户")
        else:
            print(f"\n⚠️ 标签 '{tag_name}' 在数据库中不存在")
    
    # 6. 检查标签数据格式
    print(f"\n" + "="*100)
    print("🔍 检查企业标签数据格式 (前5个有标签的客户):")
    print("="*100)
    
    cursor.execute("SELECT id, name, enterprise_tags FROM customers WHERE enterprise_tags IS NOT NULL AND enterprise_tags != '[]' AND enterprise_tags != '' LIMIT 5")
    sample_customers = cursor.fetchall()
    
    for customer_id, customer_name, tags_str in sample_customers:
        print(f"\n客户: {customer_name or customer_id}")
        print(f"ID: {customer_id}")
        print(f"企业标签数据 (原始): {tags_str[:200]}...")
        try:
            tags = json.loads(tags_str)
            print(f"标签数量: {len(tags)}")
            for tag in tags[:3]:  # 只显示前3个标签
                print(f"  - {tag.get('tag_name', '未命名')} (组: {tag.get('group_name', '未分组')})")
        except Exception as e:
            print(f"  ❌ 解析失败: {e}")
    
    # 7. 与前端显示的数据对比
    print(f"\n" + "="*100)
    print("📊 对比结果:")
    print("="*100)
    
    print("\n根据你的描述:")
    print("  - '原有老代理商' 标签: 外面显示 5000+ 人，点击弹窗显示 2263 人")
    print("  - '代理商' 标签: 外面显示 1 人，点击弹窗显示 2660+ 人")
    
    print("\n数据库实际统计:")
    for tag_name in ['原有老代理商', '代理商']:
        if tag_name in tag_customer_count:
            actual_count = tag_customer_count[tag_name]
            print(f"  - '{tag_name}' 标签: {actual_count} 人")
        else:
            print(f"  - '{tag_name}' 标签: 0 人 (不存在)")
    
    # 8. 检查是否有重复标签
    print(f"\n" + "="*100)
    print("🔍 检查标签名称重复问题:")
    print("="*100)
    
    all_tag_names = []
    for customer_id, customer_name, tags_str in customers:
        try:
            tags = json.loads(tags_str) if tags_str else []
            for tag in tags:
                tag_name = tag.get('tag_name', '')
                if tag_name:
                    all_tag_names.append(tag_name)
        except:
            pass
    
    # 查找相似的标签名
    tag_counter = Counter(all_tag_names)
    
    # 检查是否有前后空格的标签
    similar_tags = {}
    for tag_name in tag_counter.keys():
        stripped = tag_name.strip()
        if stripped not in similar_tags:
            similar_tags[stripped] = []
        similar_tags[stripped].append(tag_name)
    
    print("\n可能的重复标签 (含空格或特殊字符):")
    for stripped, variants in similar_tags.items():
        if len(variants) > 1:
            print(f"\n标签组: '{stripped}'")
            for variant in variants:
                count = tag_counter[variant]
                print(f"  - '{variant}' (长度:{len(variant)}, 客户数:{count})")
    
    # 9. 检查前端代码中的标签统计逻辑
    print(f"\n" + "="*100)
    print("🔍 需要检查前端代码:")
    print("="*100)
    
    print("\n可能的问题原因:")
    print("  1. 前端统计时重复计算了标签")
    print("  2. 前端使用的是标签 ID 而不是标签名称")
    print("  3. 前端的标签分组逻辑有误")
    print("  4. 弹窗显示的是实际客户数，外面显示的是标签出现次数")
    print("  5. 标签名称有空格或特殊字符导致匹配不上")
    
    print(f"\n" + "="*100)
    print("建议:")
    print("="*100)
    print("  1. 使用本脚本统计的数据为准")
    print("  2. 检查前端 script.js 中的 renderCustomerProfile() 函数")
    print("  3. 检查前端如何统计标签数量")
    print("  4. 检查弹窗显示的客户列表查询逻辑")
    
    conn.close()


if __name__ == '__main__':
    check_tag_statistics()
