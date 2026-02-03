"""
企微机器人 API 诊断脚本
检查 API 为什么返回 500 错误
"""
import sqlite3
import sys
import os
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DB_PATH

def diagnose_bot_api():
    """诊断企微机器人API"""
    print("=" * 70)
    print("🔍 企微机器人 API 诊断")
    print("=" * 70)
    
    # 1. 检查配置
    print("\n1️⃣ 检查配置")
    print("-" * 70)
    print(f"DB_PATH 配置: {DB_PATH}")
    print(f"DB_PATH 绝对路径: {Path(DB_PATH).absolute()}")
    print(f"数据库文件是否存在: {'✅ 是' if Path(DB_PATH).exists() else '❌ 否'}")
    
    if not Path(DB_PATH).exists():
        print("\n❌ 错误：数据库文件不存在！")
        print(f"请检查路径: {Path(DB_PATH).absolute()}")
        return
    
    # 2. 检查表结构
    print("\n2️⃣ 检查表结构")
    print("-" * 70)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        bot_tables = ['bot_webhooks', 'bot_notifications', 'bot_send_logs', 'bot_templates']
        
        for table in bot_tables:
            exists = table in all_tables
            status = "✅ 存在" if exists else "❌ 缺失"
            print(f"{status} - {table}")
            
            if exists:
                # 检查记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"    └─ 记录数: {count}")
                
                # 显示表结构
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print(f"    └─ 字段数: {len(columns)}")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ 检查表结构失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 模拟 API 调用
    print("\n3️⃣ 模拟 API 调用")
    print("-" * 70)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 模拟 GET /api/bot/webhooks?group_type=supplier
        print("测试: GET /api/bot/webhooks?group_type=supplier")
        cursor.execute("""
            SELECT id, group_name, group_type, webhook_url, purpose, remark, status, 
                   created_at, updated_at
            FROM bot_webhooks 
            WHERE group_type = ?
            ORDER BY created_at DESC
        """, ('supplier',))
        
        rows = cursor.fetchall()
        print(f"✅ 查询成功，返回 {len(rows)} 条记录")
        
        if rows:
            print("\n记录示例:")
            for i, row in enumerate(rows[:3], 1):
                print(f"  {i}. ID={row[0]}, 群名={row[1]}, 类型={row[2]}")
        else:
            print("  (无记录)")
        
        # 模拟 GET /api/bot/notifications?group_type=supplier&limit=50
        print("\n测试: GET /api/bot/notifications?group_type=supplier&limit=50")
        cursor.execute("""
            SELECT id, group_type, title, content, msg_type, status, created_at
            FROM bot_notifications 
            WHERE group_type = ?
            ORDER BY created_at DESC
            LIMIT 50
        """, ('supplier',))
        
        rows = cursor.fetchall()
        print(f"✅ 查询成功，返回 {len(rows)} 条记录")
        
        if rows:
            print("\n记录示例:")
            for i, row in enumerate(rows[:3], 1):
                print(f"  {i}. ID={row[0]}, 标题={row[2]}, 类型={row[1]}")
        else:
            print("  (无记录)")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ 模拟API调用失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 检查 FastAPI 路由
    print("\n4️⃣ 检查 FastAPI 路由")
    print("-" * 70)
    
    try:
        # 检查 bot_api.py 是否可以导入
        import bot_api
        print("✅ bot_api.py 可以正常导入")
        print(f"   路由器: {bot_api.router}")
        
        # 检查路由数量
        routes = bot_api.router.routes
        print(f"   注册的路由数: {len(routes)}")
        
        for route in routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                print(f"   - {methods:8} {route.path}")
        
    except Exception as e:
        print(f"❌ 导入 bot_api 失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. 检查 app.py 中的路由注册
    print("\n5️⃣ 检查主应用路由注册")
    print("-" * 70)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'bot_router' in content:
            print("✅ bot_router 已在 app.py 中导入")
        else:
            print("❌ bot_router 未在 app.py 中导入")
            
        if 'include_router(bot_router' in content:
            print("✅ bot_router 已注册到主应用")
            # 查找注册行
            for line in content.split('\n'):
                if 'include_router(bot_router' in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ bot_router 未注册到主应用")
            
    except Exception as e:
        print(f"❌ 检查 app.py 失败: {e}")
    
    # 总结
    print("\n" + "=" * 70)
    print("✅ 诊断完成！")
    print("=" * 70)
    print("\n💡 如果上面所有检查都通过，但仍然 500 错误，可能原因：")
    print("   1. 认证中间件问题：api_token 验证失败")
    print("   2. CORS 问题：跨域请求被阻止")
    print("   3. FastAPI 异常未被捕获")
    print("   4. 请查看后端控制台的实际错误日志")
    print()

if __name__ == '__main__':
    diagnose_bot_api()
