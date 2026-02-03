import ast
import sys

print("检查 wecom_client.py 语法...")

try:
    with open('wecom_client.py', 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # 尝试解析 AST
    ast.parse(source_code)
    print("✅ wecom_client.py 语法正确！")
    
except SyntaxError as e:
    print(f"❌ 语法错误:")
    print(f"   行号: {e.lineno}")
    print(f"   列号: {e.offset}")
    print(f"   错误: {e.msg}")
    if e.text:
        print(f"   代码: {e.text.strip()}")
    sys.exit(1)
    
except FileNotFoundError:
    print("❌ 文件不存在: wecom_client.py")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ 未知错误: {e}")
    sys.exit(1)
