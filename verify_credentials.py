# -*- coding: utf-8 -*-
"""
企业微信凭证验证工具
用于测试企业ID和Secret是否正确
"""
import requests
import json

print("=" * 60)
print("🔍 企业微信凭证验证工具")
print("=" * 60)
print()

# 从用户输入获取配置
print("请输入企业微信配置信息：")
print()

corp_id = input("企业 ID (Corp ID): ").strip()
app_secret = input("自建应用 Secret (App Secret): ").strip()

print()
print("=" * 60)
print("开始验证...")
print("=" * 60)
print()

# 1. 检查输入
print("[1/3] 检查输入格式...")
if not corp_id:
    print("❌ 企业 ID 不能为空")
    exit(1)

if not app_secret:
    print("❌ Secret 不能为空")
    exit(1)

print(f"✅ 企业 ID: {corp_id}")
print(f"✅ Secret 长度: {len(app_secret)} 字符")
print(f"✅ Secret 前10位: {app_secret[:10]}...")
print()

# 2. 调用企业微信 API 获取 access_token
print("[2/3] 调用企业微信 API...")

url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
params = {
    'corpid': corp_id,
    'corpsecret': app_secret
}

try:
    response = requests.get(url, params=params, timeout=10)
    result = response.json()
    
    print(f"HTTP 状态码: {response.status_code}")
    print(f"API 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    print()
    
    # 3. 分析结果
    print("[3/3] 分析结果...")
    print()
    
    errcode = result.get('errcode', 0)
    errmsg = result.get('errmsg', '')
    
    if errcode == 0:
        access_token = result.get('access_token', '')
        expires_in = result.get('expires_in', 0)
        
        print("=" * 60)
        print("🎉 验证成功！")
        print("=" * 60)
        print(f"✅ Access Token: {access_token[:20]}...")
        print(f"✅ 有效期: {expires_in} 秒 ({expires_in//60} 分钟)")
        print()
        print("您的企业微信凭证配置正确！")
        print("=" * 60)
    else:
        print("=" * 60)
        print("❌ 验证失败！")
        print("=" * 60)
        print(f"错误代码: {errcode}")
        print(f"错误信息: {errmsg}")
        print()
        
        # 提供具体的错误说明
        error_tips = {
            40013: """
错误原因：企业 ID 不正确

可能的原因：
1. 企业 ID 输入错误（检查是否有多余的空格）
2. 企业 ID 格式不正确（应该是 ww 开头）
3. 复制时包含了不可见字符

解决方案：
1. 重新从企业微信管理后台复制企业 ID
2. 确保没有多余的空格或换行符
3. 企业 ID 在：企业微信管理后台 → 我的企业 → 企业信息 → 企业 ID
            """,
            40014: """
错误原因：Secret 不正确

可能的原因：
1. Secret 输入错误
2. Secret 已过期或被重置
3. Secret 与企业 ID 不匹配

解决方案：
1. 重新获取 Secret
2. 在企业微信管理后台点击"重置"获取新的 Secret
3. 确保使用的是同一个企业的 ID 和 Secret
            """,
            40001: """
错误原因：Secret 不合法

可能的原因：
1. Secret 格式不正确
2. Secret 包含了不可见字符

解决方案：
1. 重新复制 Secret
2. 确保没有多余的空格
            """,
            600001: """
错误原因：IP 地址不在白名单内

可能的原因：
1. 应用配置了 IP 白名单，但当前 IP 不在列表中

解决方案：
1. 在企业微信管理后台 → 应用管理 → 自建应用 → 选择应用
2. 设置 → 企业可信 IP → 添加当前服务器 IP
3. 或者关闭 IP 白名单限制
            """
        }
        
        if errcode in error_tips:
            print(error_tips[errcode])
        else:
            print("请参考企业微信开发文档：")
            print("https://developer.work.weixin.qq.com/document/path/90313")
        
        print("=" * 60)

except requests.exceptions.Timeout:
    print("❌ 请求超时，请检查网络连接")
except requests.exceptions.RequestException as e:
    print(f"❌ 请求失败: {e}")
except Exception as e:
    print(f"❌ 发生错误: {e}")

print()
input("按回车键退出...")
