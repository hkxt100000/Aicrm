#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闪退问题诊断脚本
功能：全面检测可能导致页面闪退的问题
版本：1.0
日期：2027-01-27
"""

import sqlite3
import os
import json
import time

DB_PATH = 'data/crm.db'

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_database():
    """检查数据库连接和表结构"""
    print_header("1. 数据库完整性检查")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return False
    
    print(f"✓ 数据库文件存在: {DB_PATH}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查关键表
        tables = ['employees', 'departments', 'sessions', 'customers']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} 条记录")
        
        conn.close()
        print("✓ 数据库连接正常")
        return True
    except Exception as e:
        print(f"❌ 数据库检查失败: {str(e)}")
        return False

def check_super_admin():
    """检查超级管理员账号"""
    print_header("2. 超级管理员账号检查")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, account, name, department_id, status, is_super_admin, 
                   wecom_user_id, wecom_name
            FROM employees 
            WHERE account = '19938885888'
        """)
        
        row = cursor.fetchone()
        if not row:
            print("❌ 超级管理员账号不存在")
            conn.close()
            return False
        
        emp_id, account, name, dept_id, status, is_super, wecom_id, wecom_name = row
        
        print(f"✓ 账号存在: {account}")
        print(f"  - ID: {emp_id}")
        print(f"  - 姓名: {name}")
        print(f"  - 部门ID: {dept_id or '未分配'}")
        print(f"  - 状态: {status} ({'启用' if str(status) in ['1', 'active'] else '禁用'})")
        print(f"  - 超级管理员: {is_super}")
        print(f"  - 企微用户ID: {wecom_id or '未绑定'}")
        print(f"  - 企微姓名: {wecom_name or '未绑定'}")
        
        # 检查状态
        if str(status) not in ['1', 'active']:
            print(f"❌ 账号被禁用: status = {status}")
            conn.close()
            return False
        
        # 检查是否绑定企微
        if not wecom_id:
            print("⚠️  未绑定企业微信账号")
        
        conn.close()
        print("✓ 超级管理员账号正常")
        return True
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False

def check_departments():
    """检查部门配置"""
    print_header("3. 部门权限配置检查")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, menu_permissions 
            FROM departments
        """)
        
        rows = cursor.fetchall()
        if not rows:
            print("⚠️  暂无部门配置")
            conn.close()
            return True
        
        print(f"✓ 找到 {len(rows)} 个部门:")
        for dept_id, dept_name, permissions in rows:
            print(f"\n  部门: {dept_name} (ID: {dept_id})")
            if permissions:
                try:
                    perms = json.loads(permissions)
                    print(f"    - 权限数量: {len(perms)}")
                    print(f"    - 权限列表: {', '.join(perms[:5])}{'...' if len(perms) > 5 else ''}")
                except:
                    print(f"    - 权限配置: {permissions}")
            else:
                print("    - 无权限配置")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False

def check_sessions():
    """检查会话状态"""
    print_header("4. 会话状态检查")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取所有会话
        cursor.execute("""
            SELECT s.id, s.employee_id, s.token, s.created_at, s.expires_at, s.last_activity,
                   e.account, e.name
            FROM sessions s
            LEFT JOIN employees e ON s.employee_id = e.id
            ORDER BY s.created_at DESC
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        if not rows:
            print("⚠️  暂无会话记录")
            conn.close()
            return False
        
        print(f"✓ 找到 {len(rows)} 条最近的会话:")
        
        now = int(time.time() * 1000)
        valid_count = 0
        
        for sess_id, emp_id, token, created, expires, activity, account, name in rows:
            is_valid = expires > now
            status_icon = "✓" if is_valid else "✗"
            status_text = "有效" if is_valid else "已过期"
            
            print(f"\n  {status_icon} 会话 {sess_id[:12]}...")
            print(f"    - 员工: {name} ({account})")
            print(f"    - Token: {token[:20]}...")
            print(f"    - 创建: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(created/1000))}")
            print(f"    - 过期: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires/1000))}")
            print(f"    - 状态: {status_text}")
            
            if is_valid:
                valid_count += 1
        
        conn.close()
        
        if valid_count == 0:
            print("\n❌ 没有有效的会话")
            return False
        
        print(f"\n✓ 有 {valid_count} 个有效会话")
        return True
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False

def check_customer_data():
    """检查客户数据"""
    print_header("5. 客户数据检查")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 总数
        cursor.execute("SELECT COUNT(*) FROM customers")
        total = cursor.fetchone()[0]
        print(f"✓ 客户总数: {total:,}")
        
        if total == 0:
            print("⚠️  暂无客户数据")
            conn.close()
            return False
        
        # 按员工统计
        cursor.execute("""
            SELECT owner_userid, owner_name, COUNT(*) as count
            FROM customers
            GROUP BY owner_userid
            ORDER BY count DESC
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        print(f"\n✓ 客户分布 (前10名员工):")
        for owner_id, owner_name, count in rows:
            print(f"  - {owner_name or owner_id}: {count:,} 个客户")
        
        # msYang 的数据
        cursor.execute("""
            SELECT COUNT(*) FROM customers WHERE owner_userid = 'msYang'
        """)
        msyang_count = cursor.fetchone()[0]
        print(f"\n✓ msYang 的客户数: {msyang_count:,}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False

def check_frontend_files():
    """检查前端文件"""
    print_header("6. 前端文件检查")
    
    static_dir = 'static'
    if not os.path.exists(static_dir):
        print(f"❌ 静态文件目录不存在: {static_dir}")
        return False
    
    print(f"✓ 静态文件目录存在: {static_dir}")
    
    # 检查关键文件
    key_files = [
        'index.html',
        'login.html',
        'script.js',
        'auth.js',
        'employee-manage.js',
        'permission-manage.js',
        'group-tags-v2.js',
        'style.css',
        'auth-styles.css'
    ]
    
    print("\n✓ 关键文件检查:")
    all_exist = True
    for filename in key_files:
        filepath = os.path.join(static_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            mod_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                    time.localtime(os.path.getmtime(filepath)))
            print(f"  ✓ {filename}")
            print(f"    - 大小: {size:,} 字节")
            print(f"    - 修改: {mod_time}")
        else:
            print(f"  ❌ {filename} - 不存在")
            all_exist = False
    
    return all_exist

def check_js_syntax():
    """检查 JS 文件是否有明显的语法问题"""
    print_header("7. JavaScript 文件快速检查")
    
    static_dir = 'static'
    js_files = [
        'employee-manage.js',
        'permission-manage.js',
        'group-tags-v2.js'
    ]
    
    print("检查 JavaScript 文件的 IIFE 包装:")
    
    for js_file in js_files:
        filepath = os.path.join(static_dir, js_file)
        if not os.path.exists(filepath):
            print(f"  ❌ {js_file} - 文件不存在")
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否使用 IIFE 包装
            has_iife = content.strip().startswith('(function()')
            
            # 检查是否有重复声明
            has_duplicate = 'employeesData' in content and content.count('let employeesData') > 1
            
            print(f"\n  {js_file}:")
            print(f"    - IIFE 包装: {'✓' if has_iife else '❌ 未使用'}")
            print(f"    - 重复声明: {'❌ 发现' if has_duplicate else '✓ 无'}")
            print(f"    - 文件大小: {len(content):,} 字符")
            
        except Exception as e:
            print(f"  ❌ {js_file} - 读取失败: {str(e)}")
    
    return True

def check_auth_middleware():
    """检查认证中间件配置"""
    print_header("8. 认证中间件配置检查")
    
    middleware_file = 'auth_middleware.py'
    if not os.path.exists(middleware_file):
        print(f"❌ 中间件文件不存在: {middleware_file}")
        return False
    
    print(f"✓ 中间件文件存在: {middleware_file}")
    
    try:
        with open(middleware_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查白名单
        if "'/api/auth/login'" in content:
            print("  ✓ 登录接口在白名单中")
        else:
            print("  ❌ 登录接口不在白名单中")
        
        # 检查 status 类型兼容
        if "status = 1 OR e.status = '1'" in content or "status = '1' OR e.status = 1" in content:
            print("  ✓ status 类型兼容已修复")
        else:
            print("  ⚠️  status 类型兼容可能有问题")
        
        # 检查权限列表
        permission_keywords = [
            'dashboard', 'customers', 'customer-groups', 'wecom-bot',
            'data-sources', 'spreadsheet', 'system-manage'
        ]
        
        missing_perms = []
        for perm in permission_keywords:
            if f"'{perm}'" not in content:
                missing_perms.append(perm)
        
        if missing_perms:
            print(f"  ⚠️  可能缺少权限: {', '.join(missing_perms)}")
        else:
            print("  ✓ 权限列表看起来完整")
        
        return True
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  闪退问题诊断脚本 v1.0")
    print("  正在进行全面检查...")
    print("="*60)
    
    # 执行所有检查
    results = []
    
    results.append(("数据库完整性", check_database()))
    results.append(("超级管理员账号", check_super_admin()))
    results.append(("部门权限配置", check_departments()))
    results.append(("会话状态", check_sessions()))
    results.append(("客户数据", check_customer_data()))
    results.append(("前端文件", check_frontend_files()))
    results.append(("JavaScript 文件", check_js_syntax()))
    results.append(("认证中间件", check_auth_middleware()))
    
    # 汇总结果
    print_header("诊断结果汇总")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n检查项目: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    
    print("\n详细结果:")
    for name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"  {status} - {name}")
    
    # 给出建议
    print_header("诊断建议")
    
    if passed == total:
        print("✓ 所有检查都通过了！")
        print("\n如果仍然有闪退问题，请检查:")
        print("  1. 浏览器控制台 (F12 -> Console) 的错误信息")
        print("  2. 网络请求 (F12 -> Network) 是否有失败的 API")
        print("  3. 清除浏览器缓存后重试 (Ctrl+Shift+Delete)")
        print("  4. 尝试使用无痕模式访问")
    else:
        print("发现以下问题需要修复:\n")
        
        for name, result in results:
            if not result:
                if "超级管理员" in name:
                    print("  ❌ 超级管理员账号问题:")
                    print("     → 运行: python bind_super_admin.py")
                    print("     → 运行: python reset_password.py")
                
                elif "会话" in name:
                    print("  ❌ 会话问题:")
                    print("     → 需要重新登录")
                
                elif "前端文件" in name or "JavaScript" in name:
                    print("  ❌ 前端文件问题:")
                    print("     → 下载最新的 JS 文件")
                    print("     → 确保使用了 IIFE 包装")
                    print("     → 更新 index.html 版本号")
                
                elif "认证中间件" in name:
                    print("  ❌ 认证中间件问题:")
                    print("     → 下载最新的 auth_middleware.py")
                    print("     → 下载最新的 auth_api.py")
    
    print("\n" + "="*60)
    print("  诊断完成")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
