# config.example.py - 配置文件示例
# 使用说明：复制此文件为 config.py，然后填入真实的配置信息

# ========== 企业微信配置 ==========
CORP_ID = "你的企业ID"  # 企业微信后台的企业ID
SECRET = "你的应用Secret"  # 应用的Secret
AGENT_ID = "你的应用AgentID"  # 应用的AgentID

# ========== 数据库配置 ==========
DB_PATH = "data/crm.db"  # 数据库文件路径

# ========== 同步配置 ==========
SYNC_MAX_WORKERS = 10  # 同步时的最大并发线程数
SYNC_INTERVAL_HOURS = 1  # 自动同步间隔（小时）

# ========== 服务器配置 ==========
HOST = "0.0.0.0"
PORT = 9999

# ========== 其他配置 ==========
# 根据实际需要添加其他配置项
