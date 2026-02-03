#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信 CRM 系统启动脚本
解决 Windows + Python 3.13 的 asyncio 兼容性问题
"""

import sys
import os

# 设置事件循环策略（Windows 兼容）
if sys.platform == 'win32':
    import asyncio
    # Python 3.8+ Windows 需要设置事件循环策略
    if sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 导入 uvicorn
import uvicorn

if __name__ == "__main__":
    # 从环境变量或默认值获取配置
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 9999))
    
    print("=" * 60)
    print("🚀 天号城 企业微信 CRM 系统")
    print("=" * 60)
    print(f"📍 访问地址: http://{HOST}:{PORT}")
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"🐍 Python 版本: {sys.version}")
    print("=" * 60)
    print("按 Ctrl+C 停止服务\n")
    
    try:
        # 启动 uvicorn 服务器
        uvicorn.run(
            "app:app",
            host=HOST,
            port=PORT,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
