#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整初始化数据库表结构
"""

import sqlite3
import os

DB_PATH = os.getenv('DB_PATH', 'wecom_crm.db')

def init_database():
    """初始化所有必需的数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("开始初始化数据库表结构")
        print("=" * 60)
        
        # 1. 创建 customers 表
        print("\n1️⃣  创建 customers 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT,
                avatar TEXT,
                type INTEGER,
                gender INTEGER,
                unionid TEXT,
                position TEXT,
                corp_name TEXT,
                corp_full_name TEXT,
                external_profile TEXT,
                owner_userid TEXT,
                owner_name TEXT,
                add_time INTEGER,
                tags TEXT,
                remark TEXT,
                description TEXT,
                remark_company TEXT,
                remark_mobiles TEXT,
                remark_corp_name TEXT,
                add_way INTEGER,
                im_status TEXT,
                state TEXT,
                enterprise_tags_json TEXT,
                personal_tags_json TEXT,
                rule_tags_json TEXT,
                created_at INTEGER DEFAULT 0,
                updated_at INTEGER DEFAULT 0
            )
        """)
        print("✅ customers 表创建成功")
        
        # 2. 创建 customer_tags 表
        print("\n2️⃣  创建 customer_tags 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT,
                tag_id TEXT,
                tag_name TEXT,
                group_name TEXT,
                type INTEGER,
                created_at INTEGER DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        print("✅ customer_tags 表创建成功")
        
        # 3. 创建 employees 表
        print("\n3️⃣  创建 employees 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                userid TEXT PRIMARY KEY,
                name TEXT,
                department TEXT,
                position TEXT,
                mobile TEXT,
                email TEXT,
                avatar TEXT,
                status INTEGER,
                created_at INTEGER DEFAULT 0,
                updated_at INTEGER DEFAULT 0
            )
        """)
        print("✅ employees 表创建成功")
        
        # 4. 创建 follow_records 表
        print("\n4️⃣  创建 follow_records 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS follow_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT,
                employee_id TEXT,
                follow_time INTEGER,
                follow_type TEXT,
                content TEXT,
                next_follow_time INTEGER,
                created_at INTEGER DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        print("✅ follow_records 表创建成功")
        
        # 5. 创建 config 表
        print("\n5️⃣  创建 config 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at INTEGER
            )
        """)
        print("✅ config 表创建成功")
        
        # 6. 创建 customer_groups 表
        print("\n6️⃣  创建 customer_groups 表...")
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
        print("✅ customer_groups 表创建成功")
        
        # 7. 创建智能表格相关表
        print("\n7️⃣  创建智能表格相关表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS smart_spreadsheets (
                id TEXT PRIMARY KEY,
                docid TEXT,
                sheet_id TEXT,
                name TEXT,
                data_type TEXT DEFAULT 'order',
                data_scope TEXT DEFAULT 'global',
                supplier_code TEXT,
                file_name TEXT,
                file_path TEXT,
                fields_config TEXT,
                field_mapping TEXT,
                sync_config TEXT,
                row_count INTEGER DEFAULT 0,
                col_count INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT 0,
                updated_at INTEGER DEFAULT 0,
                last_sync_at INTEGER DEFAULT 0,
                version INTEGER DEFAULT 1,
                data_hash TEXT,
                status TEXT DEFAULT 'active',
                url TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spreadsheet_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spreadsheet_id TEXT NOT NULL,
                row_index INTEGER,
                col_index INTEGER,
                col_name TEXT,
                value TEXT,
                version INTEGER DEFAULT 1,
                created_at INTEGER DEFAULT 0,
                updated_at INTEGER DEFAULT 0,
                FOREIGN KEY (spreadsheet_id) REFERENCES smart_spreadsheets(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS field_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                data_type TEXT,
                fields_config TEXT,
                description TEXT,
                is_system INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT 0,
                updated_at INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                id TEXT PRIMARY KEY,
                spreadsheet_id TEXT NOT NULL,
                sync_type TEXT,
                sync_direction TEXT,
                changes_count INTEGER DEFAULT 0,
                status TEXT,
                error_message TEXT,
                sync_data TEXT,
                created_at INTEGER DEFAULT 0,
                FOREIGN KEY (spreadsheet_id) REFERENCES smart_spreadsheets(id)
            )
        """)
        print("✅ 智能表格相关表创建成功")
        
        conn.commit()
        
        # 检查创建的表
        print("\n" + "=" * 60)
        print("数据库表检查")
        print("=" * 60)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f"\n✅ 共创建 {len(tables)} 个表:")
        for i, (table_name,) in enumerate(tables, 1):
            # 获取表的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   {i}. {table_name} ({count} 条记录)")
        
        print("\n" + "=" * 60)
        print("✅ 数据库初始化完成！")
        print("=" * 60)
        print("\n💡 下一步:")
        print("   1. 运行: python fix_customer_sync_time.py")
        print("   2. 重启后端服务")
        print("   3. 测试同步功能")
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
