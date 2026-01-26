#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清空客户群数据 - 简化版
直接运行即可
"""
import sqlite3
import os

# 数据库文件路径 - 自动查找
DB_PATH = 'wecom_crm.db'

if not os.path.exists(DB_PATH):
    print(f"❌ 当前目录下找不到数据库文件: {DB_PATH}")
    print(f"当前目录: {os.getcwd()}")
    print("\n请确保你在正确的目录下运行此脚本！")
    print("应该在包含 wecom_crm.db 的目录下运行。")
    input("\n按回车键退出...")
    exit(1)

try:
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询当前客户群数量
    cursor.execute("SELECT COUNT(*) FROM customer_groups")
    count = cursor.fetchone()[0]
    
    print(f"\n{'='*60}")
    print(f"当前客户群数量: {count}")
    print(f"{'='*60}")
    
    if count == 0:
        print("\n✅ 客户群表已经是空的，无需清空")
        conn.close()
        input("\n按回车键退出...")
        exit(0)
    
    # 确认删除
    print(f"\n⚠️  即将删除 {count} 条客户群数据")
    confirm = input("确认删除？(输入 yes 继续): ").strip().lower()
    
    if confirm != 'yes':
        print("\n❌ 取消删除操作")
        conn.close()
        input("\n按回车键退出...")
        exit(0)
    
    # 执行删除
    print("\n🗑️  正在删除...")
    cursor.execute("DELETE FROM customer_groups")
    conn.commit()
    
    # 验证
    cursor.execute("SELECT COUNT(*) FROM customer_groups")
    new_count = cursor.fetchone()[0]
    
    if new_count == 0:
        print(f"\n✅ 成功删除 {count} 条客户群数据")
        print("✅ customer_groups 表已清空")
    else:
        print(f"\n⚠️  删除后还有 {new_count} 条数据")
    
    conn.close()
    
    print(f"\n{'='*60}")
    print("下一步：重启服务并重新同步")
    print("1. 重启服务: python start.py")
    print("2. 访问: http://localhost:9999")
    print("3. 进入: 客户群管理 -> 客户群列表")  
    print("4. 点击: 同步群聊")
    print(f"{'='*60}")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")

input("\n按回车键退出...")
