import py_compile
import sys

try:
    py_compile.compile('wecom_client.py', doraise=True)
    print("✅ wecom_client.py 语法正确")
except SyntaxError as e:
    print(f"❌ 语法错误:")
    print(f"   文件: {e.filename}")
    print(f"   行号: {e.lineno}")
    print(f"   错误: {e.msg}")
    print(f"   代码: {e.text}")
    sys.exit(1)
