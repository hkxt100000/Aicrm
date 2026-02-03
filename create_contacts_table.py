"""
创建企微通讯录表
"""
import sqlite3

DB_PATH = "data/crm.db"

# 创建企微通讯录表
sql = """
CREATE TABLE IF NOT EXISTS employees_contacts (
    id TEXT PRIMARY KEY,                    -- 企微userid
    name TEXT NOT NULL,                     -- 姓名
    mobile TEXT,                            -- 手机号
    email TEXT,                             -- 邮箱
    department TEXT,                        -- 部门（JSON数组）
    position TEXT,                          -- 职位
    gender INTEGER DEFAULT 0,               -- 性别 0未知 1男 2女
    avatar TEXT,                            -- 头像URL
    status INTEGER DEFAULT 1,               -- 状态 1启用 2禁用 4离职
    qr_code TEXT,                           -- 二维码
    external_position TEXT,                 -- 对外职务
    address TEXT,                           -- 地址
    open_userid TEXT,                       -- openid
    main_department INTEGER,                -- 主部门
    is_leader_in_dept TEXT,                 -- 是否为部门leader（JSON数组）
    direct_leader TEXT,                     -- 直接上级（JSON数组）
    enable INTEGER DEFAULT 1,               -- 是否启用
    hide_mobile INTEGER DEFAULT 0,          -- 是否隐藏手机号
    telephone TEXT,                         -- 座机
    alias TEXT,                             -- 别名
    extattr TEXT,                           -- 扩展属性（JSON）
    created_at INTEGER NOT NULL,            -- 创建时间
    updated_at INTEGER NOT NULL             -- 更新时间
);
"""

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("正在创建企微通讯录表...")
cursor.execute(sql)
conn.commit()
print("✅ 企微通讯录表创建成功！")

# 创建索引
print("正在创建索引...")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_name ON employees_contacts(name)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_mobile ON employees_contacts(mobile)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_status ON employees_contacts(status)")
print("✅ 索引创建成功！")

conn.close()

print("\n下一步：")
print("1. 修改 app.py 中的 /api/employees API，查询 employees_contacts 表")
print("2. 在系统配置页面点击'同步员工'，同步企微通讯录数据")
