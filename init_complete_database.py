#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的数据库初始化脚本
整合原有功能 + 新增的客户群管理功能
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = os.getenv('DB_PATH', 'wecom_crm.db')

def init_complete_database():
    """初始化完整的数据库结构"""
    
    # 确保数据目录存在
    db_dir = Path(DB_PATH).parent
    if db_dir and not db_dir.exists():
        db_dir.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("🚀 天号城 企业微信 CRM 数据库初始化")
    print("=" * 80)
    
    try:
        # 1. 创建客户表（原有字段 + 标签字段）
        print("\n1️⃣  创建 customers 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT,
                avatar TEXT,
                gender INTEGER DEFAULT 0,
                type INTEGER DEFAULT 1,
                unionid TEXT,
                position TEXT,
                corp_name TEXT,
                owner_userid TEXT,
                owner_name TEXT,
                add_time INTEGER,
                tags TEXT,
                remark TEXT,
                description TEXT,
                add_way INTEGER DEFAULT 0,
                im_status TEXT,
                state TEXT,
                remark_mobiles TEXT,
                remark_corp_name TEXT,
                enterprise_tags TEXT,
                personal_tags TEXT,
                rule_tags TEXT,
                created_at INTEGER DEFAULT 0,
                updated_at INTEGER DEFAULT 0
            )
        """)
        print("   ✅ customers 表创建成功 (23 个字段)")
        
        # 2. 创建员工表
        print("\n2️⃣  创建 employees 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT,
                avatar TEXT,
                mobile TEXT,
                email TEXT,
                department TEXT,
                position TEXT,
                status INTEGER DEFAULT 1,
                customer_count INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT 0,
                updated_at INTEGER DEFAULT 0
            )
        """)
        print("   ✅ employees 表创建成功")
        
        # 3. 创建客户群表（新增功能）
        print("\n3️⃣  创建 customer_groups 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_groups (
                chat_id TEXT PRIMARY KEY,
                name TEXT,
                owner_userid TEXT,
                owner_name TEXT,
                notice TEXT,
                member_count INTEGER DEFAULT 0,
                external_member_count INTEGER DEFAULT 0,
                internal_member_count INTEGER DEFAULT 0,
                admin_list TEXT,
                group_type TEXT DEFAULT 'external',
                status INTEGER DEFAULT 0,
                version INTEGER DEFAULT 0,
                create_time INTEGER DEFAULT 0,
                last_sync_time INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT 0,
                updated_at INTEGER DEFAULT 0
            )
        """)
        print("   ✅ customer_groups 表创建成功 (16 个字段)")
        
        # 4. 创建配置表（用于存储同步时间等配置）
        print("\n4️⃣  创建 config 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at INTEGER
            )
        """)
        print("   ✅ config 表创建成功")
        
        # 5. 创建标签表
        print("\n5️⃣  创建 customer_tags 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_tags (
                id TEXT PRIMARY KEY,
                name TEXT,
                group_name TEXT,
                order_num INTEGER DEFAULT 0
            )
        """)
        print("   ✅ customer_tags 表创建成功")
        
        # 6. 创建跟进记录表
        print("\n6️⃣  创建 follow_records 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS follow_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT,
                employee_id TEXT,
                content TEXT,
                follow_type TEXT,
                follow_time INTEGER,
                created_at INTEGER,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)
        print("   ✅ follow_records 表创建成功")
        
        # 7. 创建索引
        print("\n7️⃣  创建索引...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_owner ON customers(owner_userid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_updated ON customers(updated_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_id ON employees(id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer_groups_owner ON customer_groups(owner_userid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer_groups_updated ON customer_groups(updated_at)')
        print("   ✅ 索引创建成功")
        
        conn.commit()
        
        # 8. 验证表创建
        print("\n" + "=" * 80)
        print("📊 数据库表验证")
        print("=" * 80)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f"\n✅ 共创建 {len(tables)} 个表:\n")
        for i, (table_name,) in enumerate(tables, 1):
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            # 获取表的字段数
            cursor.execute(f"PRAGMA table_info({table_name})")
            fields = cursor.fetchall()
            print(f"   {i}. {table_name:30s} ({len(fields):2d} 个字段, {count:4d} 条记录)")
        
        print("\n" + "=" * 80)
        print("✅ 数据库初始化完成！")
        print("=" * 80)
        print("\n📝 功能清单:")
        print("   ✅ 客户管理 (customers)")
        print("   ✅ 员工管理 (employees)")
        print("   ✅ 客户群管理 (customer_groups) ⭐ 新增")
        print("   ✅ 标签管理 (customer_tags)")
        print("   ✅ 跟进记录 (follow_records)")
        print("   ✅ 配置管理 (config) ⭐ 新增")
        print("\n💡 下一步:")
        print("   1. 运行: python start.py")
        print("   2. 浏览器访问: http://localhost:9999")
        print("   3. 配置企业微信参数")
        print("   4. 开始同步数据")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_complete_database()
