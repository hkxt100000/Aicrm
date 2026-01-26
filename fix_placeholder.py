# -*- coding: utf-8 -*-
"""
紧急修复脚本：移除外部占位图片
日期：2024-01-23
问题：via.placeholder.com 请求失败导致页面无法正常加载
解决：替换为本地 SVG 图片
"""

import os
import sys

def fix_placeholders():
    print("=" * 60)
    print("🔧 开始修复占位图片问题")
    print("=" * 60)
    
    # 定义替换规则
    replacements = {
        'script.js': [
            # 客户头像 45x45
            (
                "'https://via.placeholder.com/45'",
                "'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2245%22 height=%2245%22%3E%3Crect fill=%22%23ddd%22 width=%2245%22 height=%2245%22/%3E%3Ctext fill=%22%23999%22 font-family=%22sans-serif%22 font-size=%2216%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22%3E头像%3C/text%3E%3C/svg%3E'"
            ),
            # 员工头像 60x60
            (
                "'https://via.placeholder.com/60'",
                "'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2260%22 height=%2260%22%3E%3Crect fill=%22%23ddd%22 width=%2260%22 height=%2260%22/%3E%3Ctext fill=%22%23999%22 font-family=%22sans-serif%22 font-size=%2220%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22%3E头像%3C/text%3E%3C/svg%3E'"
            ),
        ],
        'customer-detail.html': [
            # 客户详情页头像 100x100
            (
                "'https://via.placeholder.com/100'",
                "'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22%3E%3Crect fill=%22%23ddd%22 width=%22100%22 height=%22100%22/%3E%3Ctext fill=%22%23999%22 font-family=%22sans-serif%22 font-size=%2230%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22%3E头像%3C/text%3E%3C/svg%3E'"
            ),
        ]
    }
    
    fixed_count = 0
    error_count = 0
    
    for filename, rules in replacements.items():
        file_path = os.path.join('static', filename)
        
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            error_count += 1
            continue
        
        print(f"\n📝 处理文件: {file_path}")
        
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            replace_count = 0
            
            # 应用所有替换规则
            for old_text, new_text in rules:
                count = content.count(old_text)
                if count > 0:
                    content = content.replace(old_text, new_text)
                    replace_count += count
                    print(f"  ✅ 替换了 {count} 处: {old_text[:50]}...")
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  💾 已保存，共替换 {replace_count} 处")
                fixed_count += 1
            else:
                print(f"  ⚠️  无需修改")
        
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            error_count += 1
    
    # 输出总结
    print("\n" + "=" * 60)
    if error_count == 0:
        print("🎉 修复完成！")
        print(f"✅ 成功修复 {fixed_count} 个文件")
        print("\n下一步：")
        print("1. 重启 CRM 服务")
        print("2. 刷新浏览器 (Ctrl + Shift + R)")
        print("3. 测试智能表格功能")
    else:
        print(f"⚠️  修复完成，但有 {error_count} 个错误")
        print("请检查错误信息并手动修复")
    print("=" * 60)

if __name__ == '__main__':
    try:
        fix_placeholders()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        sys.exit(1)
