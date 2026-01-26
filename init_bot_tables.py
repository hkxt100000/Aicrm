"""
企微机器人模块 - 数据库初始化脚本
创建供应商通知群和代理商通知群相关的表
"""

import sqlite3
from datetime import datetime

DB_PATH = 'data/crm.db'

def init_bot_tables():
    """初始化机器人相关表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("🤖 企微机器人模块 - 数据库初始化")
    print("=" * 60)
    
    try:
        # 1. 创建机器人配置表（供应商群/代理商群的webhook配置）
        print("\n1️⃣ 创建机器人配置表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,              -- 群名称
                group_type TEXT NOT NULL,              -- 'supplier' 或 'agent'
                webhook_url TEXT NOT NULL UNIQUE,      -- Webhook地址
                purpose TEXT,                          -- 机器人用途
                remark TEXT,                           -- 备注
                status TEXT DEFAULT 'active',          -- 状态：active(正常), inactive(停用)
                created_at INTEGER,                    -- 创建时间（毫秒时间戳）
                updated_at INTEGER                     -- 更新时间（毫秒时间戳）
            )
        """)
        print("   ✅ bot_webhooks 表创建成功")
        
        # 2. 创建通知消息表
        print("\n2️⃣ 创建通知消息表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_type TEXT NOT NULL,              -- 'supplier' 或 'agent'
                title TEXT,                            -- 消息标题
                content TEXT NOT NULL,                 -- 消息内容
                msg_type TEXT NOT NULL,                -- 消息类型：text, markdown, image, news, file, template_card
                target_webhooks TEXT,                  -- 目标webhook ID列表（JSON数组）
                mentioned_list TEXT,                   -- @成员列表（JSON数组）
                send_mode TEXT DEFAULT 'manual',       -- 发送模式：manual(手工), auto(自动)
                send_time INTEGER,                     -- 发送时间（毫秒时间戳）
                status TEXT DEFAULT 'draft',           -- 状态：draft(草稿), pending(待发送), sending(发送中), sent(已发送), failed(失败)
                need_approval INTEGER DEFAULT 0,       -- 是否需要审核（0不需要，1需要）
                approval_status TEXT,                  -- 审核状态：pending(待审核), approved(已通过), rejected(已拒绝)
                approver_id TEXT,                      -- 审核人ID
                approved_at INTEGER,                   -- 审核时间（毫秒时间戳）
                created_by TEXT,                       -- 创建人
                created_at INTEGER,                    -- 创建时间（毫秒时间戳）
                updated_at INTEGER                     -- 更新时间（毫秒时间戳）
            )
        """)
        print("   ✅ bot_notifications 表创建成功")
        
        # 3. 创建发送记录表
        print("\n3️⃣ 创建发送记录表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_send_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notification_id INTEGER NOT NULL,      -- 关联的通知ID
                webhook_id INTEGER NOT NULL,           -- 关联的webhook ID
                webhook_name TEXT,                     -- 群名称（冗余字段，便于查询）
                send_time INTEGER,                     -- 实际发送时间（毫秒时间戳）
                status TEXT,                           -- 发送状态：success, failed
                error_msg TEXT,                        -- 错误信息
                response TEXT,                         -- 企业微信API响应
                created_at INTEGER,                    -- 创建时间（毫秒时间戳）
                FOREIGN KEY (notification_id) REFERENCES bot_notifications(id),
                FOREIGN KEY (webhook_id) REFERENCES bot_webhooks(id)
            )
        """)
        print("   ✅ bot_send_logs 表创建成功")
        
        # 4. 创建消息模板表（用于自动推送）
        print("\n4️⃣ 创建消息模板表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,                    -- 模板名称
                group_type TEXT NOT NULL,              -- 'supplier' 或 'agent'
                category TEXT,                         -- 模板分类（结算通知、价格通知等）
                msg_type TEXT NOT NULL,                -- 消息类型
                content_template TEXT NOT NULL,        -- 消息内容模板（支持变量）
                trigger_type TEXT,                     -- 触发类型：time(定时), event(事件)
                trigger_config TEXT,                   -- 触发配置（JSON）
                status TEXT DEFAULT 'active',          -- 状态：active(启用), inactive(停用)
                created_by TEXT,
                created_at INTEGER,                    -- 创建时间（毫秒时间戳）
                updated_at INTEGER                     -- 更新时间（毫秒时间戳）
            )
        """)
        print("   ✅ bot_templates 表创建成功")
        
        # 5. 创建索引
        print("\n5️⃣ 创建索引...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_webhooks_group_type ON bot_webhooks(group_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_group_type ON bot_notifications(group_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_status ON bot_notifications(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_send_logs_notification ON bot_send_logs(notification_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_templates_group_type ON bot_templates(group_type)")
        print("   ✅ 索引创建成功")
        
        conn.commit()
        print("\n" + "=" * 60)
        print("✅ 数据库初始化完成！")
        print("=" * 60)
        
        # 6. 显示表结构
        print("\n📊 表结构统计：")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'bot_%'")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   📋 {table[0]}: {count} 条记录")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == '__main__':
    init_bot_tables()
