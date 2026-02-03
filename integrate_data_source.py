"""
源数据管理模块 - 快速集成脚本
自动将源数据管理模块集成到 index.html
"""

def integrate_data_source_module():
    """集成源数据管理模块"""
    
    print("=" * 60)
    print("源数据管理模块 - 快速集成")
    print("=" * 60)
    print()
    
    # 读取index.html
    print("[1/4] 读取 index.html...")
    try:
        with open('static/index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return
    
    # 检查是否已集成
    if 'data-source-styles.css' in html_content:
        print("⚠️ 源数据管理模块已集成，跳过")
        return
    
    # 添加CSS引用
    print("[2/4] 添加CSS引用...")
    css_link = '    <link rel="stylesheet" href="/static/data-source-styles.css?v=20260126001">\n'
    
    # 在 style.css 之后插入
    html_content = html_content.replace(
        '<link rel="stylesheet" href="/static/style.css',
        '<link rel="stylesheet" href="/static/style.css' + '?v=20260126022">\n' + css_link[:-1]
    )
    
    # 读取模块HTML
    print("[3/4] 添加模块HTML...")
    try:
        with open('static/data-source-module.html', 'r', encoding='utf-8') as f:
            module_html = f.read()
    except Exception as e:
        print(f"❌ 读取模块HTML失败: {e}")
        return
    
    # 在 </main> 之前插入模块HTML
    html_content = html_content.replace(
        '            </main>',
        '                ' + module_html + '\n            </main>'
    )
    
    # 添加JS引用
    print("[4/4] 添加JavaScript引用...")
    js_script = '\n    <script src="/static/data-source.js?v=20260126001"></script>'
    
    # 在 </body> 之前插入
    html_content = html_content.replace('</body>', js_script + '\n</body>')
    
    # 保存备份
    print()
    print("备份原文件...")
    try:
        with open('static/index.html.backup_datasource', 'w', encoding='utf-8') as f:
            with open('static/index.html', 'r', encoding='utf-8') as original:
                f.write(original.read())
        print("✓ 备份已保存到: static/index.html.backup_datasource")
    except Exception as e:
        print(f"⚠️ 备份失败: {e}")
    
    # 写入修改后的内容
    print()
    print("保存修改...")
    try:
        with open('static/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✓ index.html 已更新")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return
    
    print()
    print("=" * 60)
    print("✅ 集成完成！")
    print("=" * 60)
    print()
    print("下一步操作：")
    print("1. 重启服务：")
    print("   taskkill /F /IM python.exe")
    print("   python start.py")
    print()
    print("2. 访问系统：http://localhost:9999")
    print("3. 点击左侧菜单「源数据管理」")
    print()

if __name__ == '__main__':
    integrate_data_source_module()
