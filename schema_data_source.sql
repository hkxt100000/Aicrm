-- ============================================================================
-- 源数据管理系统 - 数据库表结构
-- 设计原则：灵活、可扩展、不写死字段
-- ============================================================================

-- 表1：数据源配置表
CREATE TABLE IF NOT EXISTS data_sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,                    -- 数据源名称，如"天号城订单源数据"
    source_type TEXT NOT NULL,             -- 数据源类型：order/product/supplier/custom
    description TEXT,                      -- 数据源描述
    
    -- 配置信息
    api_key TEXT UNIQUE NOT NULL,          -- API密钥（用于推送认证）
    status TEXT DEFAULT 'active',          -- 状态：active/inactive/deleted
    
    -- 同步配置
    auto_sync BOOLEAN DEFAULT 0,           -- 是否启用自动同步
    sync_interval INTEGER DEFAULT 3600,    -- 同步间隔（秒），默认1小时
    last_sync_time TEXT,                   -- 最后同步时间
    
    -- 字段定义（JSON格式，动态配置）
    field_schema TEXT,                     -- 字段定义JSON，格式见下方示例
    
    -- 统计信息
    total_records INTEGER DEFAULT 0,       -- 总记录数
    sync_count INTEGER DEFAULT 0,          -- 同步次数
    last_error TEXT,                       -- 最后错误信息
    
    -- 系统字段
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    created_by TEXT,
    deleted BOOLEAN DEFAULT 0
);

-- field_schema 示例：
-- {
--   "fields": [
--     {"name": "订单号", "key": "order_no", "type": "text", "required": true, "indexed": true},
--     {"name": "订单金额", "key": "amount", "type": "number", "required": false, "indexed": false},
--     {"name": "创建时间", "key": "created_time", "type": "datetime", "required": false, "indexed": true}
--   ],
--   "primary_key": "order_no",           // 主键字段
--   "display_fields": ["订单号", "代理商", "订单金额"],  // 列表页显示字段
--   "search_fields": ["订单号", "代理商"]   // 搜索字段
-- }

CREATE INDEX IF NOT EXISTS idx_data_sources_type ON data_sources(source_type);
CREATE INDEX IF NOT EXISTS idx_data_sources_status ON data_sources(status);
CREATE INDEX IF NOT EXISTS idx_data_sources_deleted ON data_sources(deleted);

-- ============================================================================

-- 表2：原始数据表（通用表，存储所有类型的数据）
CREATE TABLE IF NOT EXISTS raw_data_records (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,               -- 关联到 data_sources.id
    
    -- 原始数据（JSON格式，完整保存）
    raw_data TEXT NOT NULL,                -- 完整的JSON数据
    
    -- 提取的关键字段（用于快速查询和索引）
    data_key TEXT,                         -- 数据主键（如订单号、产品编码）
    data_type TEXT,                        -- 数据类型（order/product/supplier）
    
    -- 状态管理
    sync_time TEXT NOT NULL,               -- 同步时间
    is_processed BOOLEAN DEFAULT 0,        -- 是否已加工处理
    process_time TEXT,                     -- 加工时间
    process_result TEXT,                   -- 加工结果
    
    -- 数据版本（支持增量更新）
    version INTEGER DEFAULT 1,             -- 数据版本号
    is_latest BOOLEAN DEFAULT 1,           -- 是否最新版本
    
    -- 系统字段
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    deleted BOOLEAN DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_raw_data_source ON raw_data_records(source_id);
CREATE INDEX IF NOT EXISTS idx_raw_data_key ON raw_data_records(data_key);
CREATE INDEX IF NOT EXISTS idx_raw_data_type ON raw_data_records(data_type);
CREATE INDEX IF NOT EXISTS idx_raw_data_sync_time ON raw_data_records(sync_time);
CREATE INDEX IF NOT EXISTS idx_raw_data_processed ON raw_data_records(is_processed);
CREATE INDEX IF NOT EXISTS idx_raw_data_latest ON raw_data_records(is_latest);
CREATE INDEX IF NOT EXISTS idx_raw_data_deleted ON raw_data_records(deleted);

-- ============================================================================

-- 表3：数据同步日志表
CREATE TABLE IF NOT EXISTS data_sync_logs (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,               -- 关联到 data_sources.id
    
    -- 同步信息
    sync_type TEXT NOT NULL,               -- 同步类型：manual/auto/push
    sync_method TEXT NOT NULL,             -- 同步方式：api/excel/csv
    
    -- 统计信息
    total_count INTEGER DEFAULT 0,         -- 总记录数
    success_count INTEGER DEFAULT 0,       -- 成功数
    failed_count INTEGER DEFAULT 0,        -- 失败数
    skipped_count INTEGER DEFAULT 0,       -- 跳过数
    
    -- 结果信息
    status TEXT NOT NULL,                  -- 状态：success/failed/partial
    error_message TEXT,                    -- 错误信息
    error_details TEXT,                    -- 详细错误（JSON格式）
    
    -- 时间信息
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration INTEGER,                      -- 耗时（秒）
    
    -- 系统字段
    created_at INTEGER NOT NULL,
    created_by TEXT
);

CREATE INDEX IF NOT EXISTS idx_sync_logs_source ON data_sync_logs(source_id);
CREATE INDEX IF NOT EXISTS idx_sync_logs_status ON data_sync_logs(status);
CREATE INDEX IF NOT EXISTS idx_sync_logs_start_time ON data_sync_logs(start_time);

-- ============================================================================

-- 表4：数据源统计表（按天统计）
CREATE TABLE IF NOT EXISTS data_source_stats (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,               -- 关联到 data_sources.id
    stat_date TEXT NOT NULL,               -- 统计日期 YYYY-MM-DD
    
    -- 统计数据
    new_records INTEGER DEFAULT 0,         -- 新增记录数
    updated_records INTEGER DEFAULT 0,     -- 更新记录数
    total_records INTEGER DEFAULT 0,       -- 当日总记录数
    sync_count INTEGER DEFAULT 0,          -- 同步次数
    
    -- 系统字段
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    
    UNIQUE(source_id, stat_date)
);

CREATE INDEX IF NOT EXISTS idx_stats_source ON data_source_stats(source_id);
CREATE INDEX IF NOT EXISTS idx_stats_date ON data_source_stats(stat_date);

-- ============================================================================
