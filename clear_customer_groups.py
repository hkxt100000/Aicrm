#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清空客户群数据库
只删除 customer_groups 表中的数据，不影响其他表
"""
import sqlite3
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'wecom_crm.db')

def clear_customer_groups():
    """清空客户群数据"""
    
    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查询当前客户群数量
        cursor.execute("SELECT COUNT(*) FROM customer_groups")
        count = cursor.fetchone()[0]
        
        print(f"\n📊 当前客户群数量: {count}")
        
        if count == 0:
            print("✅ 客户群表已经是空的，无需清空")
            conn.close()
            return True
        
        # 确认删除
        print(f"\n⚠️  即将删除 {count} 条客户群数据")
        confirm = input("确认删除？(yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("❌ 取消删除操作")
            conn.close()
            return False
        
        # 执行删除
        print("\n🗑️  正在删除客户群数据...")
        cursor.execute("DELETE FROM customer_groups")
        conn.commit()
        
        # 验证删除结果
        cursor.execute("SELECT COUNT(*) FROM customer_groups")
        new_count = cursor.fetchone()[0]
        
        if new_count == 0:
            print(f"✅ 成功删除 {count} 条客户群数据")
            print("✅ customer_groups 表已清空")
        else:
            print(f"⚠️  删除后还有 {new_count} 条数据，可能删除不完整")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ 数据库操作失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("清空客户群数据库")
    print("=" * 60)
    print(f"数据库路径: {DB_PATH}")
    print("⚠️  注意: 此操作只会清空 customer_groups 表，不影响其他表")
    print("=" * 60)
    
    success = clear_customer_groups()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 操作完成！")
        print("下一步: 重新同步客户群数据")
        print("1. 启动服务: python start.py")
        print("2. 访问: http://localhost:9999")
        print("3. 进入: 客户群管理 -> 客户群列表")
        print("4. 点击: 同步群聊")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 操作失败，请检查错误信息")
        print("=" * 60)
