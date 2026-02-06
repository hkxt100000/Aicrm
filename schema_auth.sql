-- ============================================================================
-- 员工和权限管理数据库
-- 创建时间：2025-01-27
-- ============================================================================

-- 表1：员工表
CREATE TABLE IF NOT EXISTS employees (
    id TEXT PRIMARY KEY,
    account TEXT UNIQUE NOT NULL,           -- 登录账号（手机号）
    password TEXT NOT NULL,                 -- 密码（bcrypt加密）
    name TEXT NOT NULL,                     -- 姓名
    department_id TEXT,                     -- 所属部门
    wecom_user_id TEXT,                     -- 企业微信成员ID
    wecom_name TEXT,                        -- 企业微信姓名
    status TEXT DEFAULT 'active',           -- 状态：active/disabled
    is_super_admin BOOLEAN DEFAULT 0,       -- 是否超级管理员
    created_at INTEGER NOT NULL,            -- 创建时间（毫秒时间戳）
    updated_at INTEGER NOT NULL,            -- 更新时间（毫秒时间戳）
    
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 员工表索引
CREATE INDEX IF NOT EXISTS idx_employees_account ON employees(account);
CREATE INDEX IF NOT EXISTS idx_employees_wecom_user_id ON employees(wecom_user_id);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(status);

-- ============================================================================

-- 表2：部门表
CREATE TABLE IF NOT EXISTS departments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,                     -- 部门名称
    description TEXT,                       -- 部门描述
    menu_permissions TEXT,                  -- 菜单权限（JSON格式）
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

-- 部门表索引
CREATE INDEX IF NOT EXISTS idx_departments_name ON departments(name);

-- ============================================================================

-- 表3：登录日志表（可选，用于审计）
CREATE TABLE IF NOT EXISTS login_logs (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,              -- 员工ID
    login_time INTEGER NOT NULL,            -- 登录时间
    ip_address TEXT,                        -- IP地址
    user_agent TEXT,                        -- 浏览器信息
    status TEXT NOT NULL,                   -- 状态：success/failed
    fail_reason TEXT,                       -- 失败原因
    
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- 登录日志表索引
CREATE INDEX IF NOT EXISTS idx_login_logs_employee ON login_logs(employee_id);
CREATE INDEX IF NOT EXISTS idx_login_logs_time ON login_logs(login_time);
CREATE INDEX IF NOT EXISTS idx_login_logs_status ON login_logs(status);

-- ============================================================================

-- 表4：会话表（Session管理）
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,                    -- Session ID
    employee_id TEXT NOT NULL,              -- 员工ID
    token TEXT UNIQUE NOT NULL,             -- 访问令牌
    expires_at INTEGER NOT NULL,            -- 过期时间
    created_at INTEGER NOT NULL,
    
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- 会话表索引
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_employee ON sessions(employee_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
