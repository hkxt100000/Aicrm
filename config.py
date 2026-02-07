"""
企业微信 CRM 配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ==================== 企业微信配置 ====================
CORP_ID = os.getenv("WECOM_CORP_ID", "wwae4f99f11753a5ea")  # 企业 ID
CONTACT_SECRET = os.getenv("WECOM_CONTACT_SECRET", "OYemZulEpaL3b5_qxnOVHqd29ZR5UEGWYsBxvFoZEnc")  # 通讯录 Secret
CUSTOMER_SECRET = os.getenv("WECOM_CUSTOMER_SECRET", "OYemZulEpaL3b5_qxnOVHqd29ZR5UEGWYsBxvFoZEnc")  # 客户联系 Secret
APP_SECRET = os.getenv("WECOM_APP_SECRET", "OYemZulEpaL3b5_qxnOVHqd29ZR5UEGWYsBxvFoZEnc")  # 自建应用 Secret（推荐使用）
AGENT_ID = os.getenv("WECOM_AGENT_ID", "1000013")  # 应用 AgentId

# ==================== 数据库配置 ====================
DB_PATH = os.getenv("DB_PATH", "data/crm.db")

# ==================== 服务配置 ====================
PORT = int(os.getenv("PORT", "9999"))  # 服务端口（默认9999）
HOST = os.getenv("HOST", "0.0.0.0")

# ==================== API Token ====================
API_TOKEN = os.getenv("API_TOKEN", "crm-default-token-2026")

# ==================== 企业微信 API 地址 ====================
WECOM_API_BASE = "https://qyapi.weixin.qq.com/cgi-bin"

# ==================== 公网访问配置 ====================
# 用于内网穿透或部署到服务器后的公网访问地址
# 例如: https://crm.yourdomain.com 或 https://xxxx.ngrok.io
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "")  

# ==================== 缓存配置 ====================
CACHE_DIR = "data/cache"
ACCESS_TOKEN_CACHE_KEY = "wecom_access_token"
ACCESS_TOKEN_EXPIRES = 7000  # access_token 有效期 7200s，提前 200s 刷新

# ==================== JWT 认证配置 ====================
JWT_SECRET = os.getenv("JWT_SECRET", "crm-jwt-secret-key-2026-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24 * 7  # Token 有效期 7 天

# ==================== Redis 配置（可选） ====================
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# ==================== 日志配置 ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = "logs"

# ==================== 文件上传配置 ====================
UPLOAD_DIR = "data/uploads"
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# ==================== 数据同步配置 ====================
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "3600"))  # 自动同步间隔（秒），默认1小时
SYNC_MAX_WORKERS = int(os.getenv("SYNC_MAX_WORKERS", "10"))  # 同步并发线程数

# 指定同步客户数据的员工ID（只同步该员工的客户）
# 如果为空，则同步所有员工的客户
SYNC_OWNER_USERID = os.getenv("SYNC_OWNER_USERID", "msYang")  # 默认同步 msYang 的客户

# ==================== 环境标识 ====================
ENV = os.getenv("ENV", "development")  # development / production
DEBUG = ENV == "development"

# ==================== 配置验证 ====================
def validate_config():
    """验证必要的配置项"""
    required_configs = {
        "CORP_ID": CORP_ID,
        "CONTACT_SECRET": CONTACT_SECRET,
        "CUSTOMER_SECRET": CUSTOMER_SECRET,
        "AGENT_ID": AGENT_ID,
    }
    
    missing = [key for key, value in required_configs.items() if not value]
    
    if missing:
        print(f"⚠️  警告: 以下配置项未设置: {', '.join(missing)}")
        print("📝 请在 .env 文件中配置或直接修改 config.py")
        return False
    
    print("✅ 配置验证通过")
    return True

# ==================== 配置信息打印 ====================
def print_config():
    """打印当前配置（脱敏）"""
    print("=" * 50)
    print("🚀 企业微信 CRM 配置")
    print("=" * 50)
    print(f"环境模式: {ENV}")
    print(f"企业ID: {CORP_ID[:10]}..." if CORP_ID else "企业ID: 未配置")
    print(f"服务地址: http://{HOST}:{PORT}")
    print(f"数据库路径: {DB_PATH}")
    print(f"公网地址: {PUBLIC_BASE_URL or '未配置（仅本地访问）'}")
    print("=" * 50)

if __name__ == "__main__":
    validate_config()
    print_config()
