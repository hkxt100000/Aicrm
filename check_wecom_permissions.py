#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业微信权限检查工具
检查通讯录 API 的权限配置
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wecom_client import WeComClient
from config import CORP_ID, CONTACT_SECRET, CUSTOMER_SECRET, APP_SECRET, AGENT_ID

def check_wecom_permissions():
    """检查企业微信权限"""
    print("=" * 70)
    print("企业微信权限检查工具")
    print("=" * 70)
    
    # 初始化客户端
    client = WeComClient()
    client.update_config(
        corp_id=CORP_ID,
        contact_secret=CONTACT_SECRET,
        customer_secret=CUSTOMER_SECRET,
        app_secret=APP_SECRET,
        agent_id=AGENT_ID
    )
    
    print("\n📋 配置信息:")
    print(f"  - 企业ID (CorpID): {CORP_ID}")
    print(f"  - 通讯录密钥: {'✅ 已配置' if CONTACT_SECRET else '❌ 未配置'}")
    print(f"  - 客户联系密钥: {'✅ 已配置' if CUSTOMER_SECRET else '❌ 未配置'}")
    print(f"  - 应用密钥: {'✅ 已配置' if APP_SECRET else '❌ 未配置'}")
    
    if not CONTACT_SECRET:
        print("\n❌ 错误：未配置通讯录密钥！")
        print("   无法获取手机号和邮箱")
        print("\n📖 解决方法：")
        print("   1. 登录企业微信管理后台")
        print("   2. 应用管理 → 通讯录同步")
        print("   3. 复制 Secret")
        print("   4. 配置到 .env 文件的 WECOM_CONTACT_SECRET")
        return
    
    print("\n" + "=" * 70)
    print("🔍 获取员工列表...")
    print("=" * 70)
    
    try:
        # 获取员工列表
        users = client.get_user_list()
        
        if not users:
            print("\n❌ 未获取到任何员工！")
            print("\n可能的原因：")
            print("  1. 通讯录密钥错误")
            print("  2. 没有员工在可见范围内")
            print("  3. API 权限不足")
            return
        
        print(f"\n✅ 成功获取 {len(users)} 个员工")
        
        # 统计字段
        stats = {
            'mobile': 0,
            'email': 0,
            'biz_mail': 0,
            'telephone': 0
        }
        
        print("\n" + "=" * 70)
        print("📊 前5个员工详细信息:")
        print("=" * 70)
        
        for idx, user in enumerate(users[:5], 1):
            print(f"\n{idx}. {user.get('name', '未知')}")
            print(f"   {'─' * 60}")
            print(f"   userid      : {user.get('userid')}")
            print(f"   部门        : {user.get('department', [])}")
            print(f"   职位        : {user.get('position', '无')}")
            print(f"   状态        : {user.get('status', 1)}")
            
            # 联系方式字段
            print(f"\n   📞 联系方式:")
            mobile = user.get('mobile')
            email = user.get('email')
            biz_mail = user.get('biz_mail')
            telephone = user.get('telephone')
            
            if mobile:
                print(f"   ✅ mobile       : {mobile}")
                stats['mobile'] += 1
            else:
                print(f"   ❌ mobile       : 无")
            
            if email:
                print(f"   ✅ email        : {email}")
                stats['email'] += 1
            else:
                print(f"   ❌ email        : 无")
            
            if biz_mail:
                print(f"   ✅ biz_mail     : {biz_mail}")
                stats['biz_mail'] += 1
            else:
                print(f"   ❌ biz_mail     : 无")
            
            if telephone:
                print(f"   ✅ telephone    : {telephone}")
                stats['telephone'] += 1
            else:
                print(f"   ❌ telephone    : 无")
        
        # 统计所有员工
        for user in users:
            if user.get('mobile'):
                stats['mobile'] += 1
            if user.get('email'):
                stats['email'] += 1
            if user.get('biz_mail'):
                stats['biz_mail'] += 1
            if user.get('telephone'):
                stats['telephone'] += 1
        
        print("\n" + "=" * 70)
        print(f"📊 全员统计（共 {len(users)} 人）:")
        print("=" * 70)
        print(f"  - mobile    : {stats['mobile']:3d} 人 ({stats['mobile']/len(users)*100:.1f}%)")
        print(f"  - email     : {stats['email']:3d} 人 ({stats['email']/len(users)*100:.1f}%)")
        print(f"  - biz_mail  : {stats['biz_mail']:3d} 人 ({stats['biz_mail']/len(users)*100:.1f}%)")
        print(f"  - telephone : {stats['telephone']:3d} 人 ({stats['telephone']/len(users)*100:.1f}%)")
        
        # 诊断建议
        print("\n" + "=" * 70)
        print("💡 诊断建议:")
        print("=" * 70)
        
        if stats['mobile'] == 0 and stats['email'] == 0:
            print("\n❌ 问题：所有员工都没有手机号和邮箱！")
            print("\n🔧 解决方法：")
            print("  1. 登录企业微信管理后台")
            print("  2. 应用管理 → 通讯录同步")
            print("  3. 检查应用权限：")
            print("     - 是否有「通讯录-成员信息-手机号」权限")
            print("     - 是否有「通讯录-成员信息-邮箱」权限")
            print("  4. 检查可见范围：")
            print("     - 应用可见范围是否包含这些员工")
            print("  5. 保存并重新获取 Secret")
            
        elif stats['mobile'] > 0 and stats['email'] > 0:
            print("\n✅ 成功：可以正常获取手机号和邮箱！")
            print(f"   - {stats['mobile']} 人有手机号")
            print(f"   - {stats['email']} 人有邮箱")
            print("\n下一步：在界面点击「同步通讯录」按钮")
            
        elif stats['biz_mail'] > 0:
            print("\n⚠️ 提示：未获取到 email，但有 biz_mail")
            print("   系统会自动使用 biz_mail 作为邮箱")
            print(f"   - {stats['biz_mail']} 人有企业邮箱")
            
        else:
            print("\n⚠️ 警告：部分员工没有联系方式")
            print("   可能原因：")
            print("   - 员工在企业微信中未填写")
            print("   - 部分员工不在可见范围内")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n🔧 常见错误解决方法：")
        print("  - 40014: access_token 无效")
        print("    → 检查 contact_secret 是否正确")
        print("  - 60011: 无权访问")
        print("    → 检查应用权限配置")
        print("  - 60020: 部门不存在")
        print("    → 检查部门ID是否正确")

if __name__ == '__main__':
    check_wecom_permissions()
