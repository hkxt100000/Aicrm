"""
修复客户画像标签统计 - 完整的后端API重写
"""
import sqlite3
import json
from collections import defaultdict

DB_PATH = './crm.db'

def fix_tag_stats_api():
    """生成正确的标签统计逻辑代码"""
    
    print("="*100)
    print("生成修复后的标签统计API代码")
    print("="*100)
    
    code = '''
@app.get("/api/customer-portrait/tag-stats")
async def get_tag_stats(token: str = Depends(check_token)):
    """获取标签统计数据 - 修复版"""
    import json
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取所有客户的企业标签
        cursor.execute("""
            SELECT id, name, enterprise_tags 
            FROM customers 
            WHERE enterprise_tags IS NOT NULL AND enterprise_tags != '' AND enterprise_tags != '[]'
        """)
        
        # 标签名称 -> 客户列表
        tag_customers = defaultdict(list)
        
        # 统计每个标签的客户数（一个客户有多个相同标签名，只算一次）
        for customer_id, customer_name, tags_str in cursor.fetchall():
            try:
                tags = json.loads(tags_str)
                if not isinstance(tags, list):
                    continue
                
                # 当前客户的所有标签名（去重）
                customer_tag_names = set()
                for tag in tags:
                    if isinstance(tag, dict):
                        tag_name = tag.get('tag_name', '').strip()
                        if tag_name:
                            customer_tag_names.add(tag_name)
                
                # 将客户添加到每个标签的列表中
                for tag_name in customer_tag_names:
                    tag_customers[tag_name].append({
                        'id': customer_id,
                        'name': customer_name or customer_id
                    })
                    
            except Exception as e:
                print(f"解析客户 {customer_id} 标签失败: {e}")
                continue
        
        # 计算每个标签的客户数量
        tag_stats = {}
        for tag_name, customers in tag_customers.items():
            tag_stats[tag_name] = len(customers)
        
        # 构建重点标签数据（固定的6个卡片）
        key_tags = {
            "用户标签": 0,
            "代理商": 0,
            "合伙人": 0,
            "供应商": 0,
            "同行": 0,
            "原有老代理": 0
        }
        
        # 匹配规则（严格匹配）
        for tag_name, count in tag_stats.items():
            tag_name_lower = tag_name.lower()
            
            # 用户标签
            if tag_name in ['用户', '客户', '用户标签']:
                key_tags["用户标签"] += count
            # 原有老代理（优先匹配，避免和"代理商"冲突）
            elif '原有老代理商' in tag_name or '原有老代理' in tag_name or '老代理商' in tag_name:
                key_tags["原有老代理"] += count
            # 代理商
            elif tag_name in ['代理商', '代理']:
                key_tags["代理商"] += count
            # 合伙人
            elif '合伙人' in tag_name:
                key_tags["合伙人"] += count
            # 供应商
            elif '供应商' in tag_name:
                key_tags["供应商"] += count
            # 同行
            elif '同行' in tag_name or tag_name == '同行':
                key_tags["同行"] += count
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "key_tags": key_tags,
                "all_tag_stats": tag_stats,  # 所有标签的统计
                "tag_customers": {k: v for k, v in tag_customers.items()}  # 每个标签的客户列表
            }
        }
        
    except Exception as e:
        print(f"获取标签统计失败: {e}")
        return {"success": False, "message": str(e)}
'''
    
    print("\n修复后的API代码:")
    print(code)
    
    print("\n" + "="*100)
    print("修复说明:")
    print("="*100)
    print("1. 使用 defaultdict 存储每个标签的客户列表")
    print("2. 每个客户的标签名先去重（避免重复计数）")
    print("3. 严格匹配标签名称（避免误匹配）")
    print("4. 优先匹配'原有老代理商'，避免和'代理商'冲突")
    print("5. 返回完整的标签统计数据和客户列表")
    
    print("\n" + "="*100)
    print("需要替换的文件:")
    print("="*100)
    print("文件: app.py")
    print("位置: 第 2618-2755 行")
    print("函数: get_tag_stats()")


if __name__ == '__main__':
    fix_tag_stats_api()
