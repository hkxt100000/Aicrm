@echo off
chcp 65001 > nul
echo ================================================
echo   导出数据库数据用于分析
echo ================================================
echo.

cd /d "%~dp0"

echo 正在导出数据...
echo.

python -c "import sqlite3, json; conn = sqlite3.connect('data/crm.db'); cursor = conn.cursor(); cursor.execute('SELECT * FROM customer_tags LIMIT 50'); tags = cursor.fetchall(); cursor.execute('SELECT id, name, enterprise_tags, add_way, gender, owner_userid FROM customers LIMIT 50'); customers = cursor.fetchall(); data = {'tags': tags, 'customers': [[str(c) if c else '' for c in row] for row in customers]}; open('数据导出.json', 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=2)); print('导出成功！文件：数据导出.json'); conn.close()"

echo.
echo ================================================
echo 导出完成！请把 "数据导出.json" 文件发给我
echo ================================================
echo.
pause
