@echo off
cd /d %~dp0
echo ========================================
echo 检查 Python 语法错误
echo ========================================

echo.
echo 1. 检查 config.py...
python -m py_compile config.py
if %errorlevel% == 0 (
    echo [OK] config.py 语法正确
) else (
    echo [ERROR] config.py 有语法错误！
)

echo.
echo 2. 检查 wecom_client.py...
python -m py_compile wecom_client.py
if %errorlevel% == 0 (
    echo [OK] wecom_client.py 语法正确
) else (
    echo [ERROR] wecom_client.py 有语法错误！
)

echo.
echo 3. 检查 app.py...
python -m py_compile app.py
if %errorlevel% == 0 (
    echo [OK] app.py 语法正确
) else (
    echo [ERROR] app.py 有语法错误！
)

echo.
echo ========================================
echo 检查完成
echo ========================================
pause
