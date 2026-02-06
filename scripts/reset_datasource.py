#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据源数据清空与重新导入脚本

功能：
1. 清空指定数据源的所有记录
2. 重置数据源的统计信息（总记录数、同步次数）
3. 可选：重新导入新的 Excel 数据

使用方法：
python reset_datasource.py --source-id <数据源ID>
python reset_datasource.py --source-name "VIP订单"
python reset_datasource.py --source-id <数据源ID> --import-excel <Excel文件路径>
"""

import sys
import os
import argparse
import sqlite3
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'crm.db')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def find_datasource(source_id=None, source_name=None):
    """
    查找数据源
    
    Args:
        source_id: 数据源ID
        source_name: 数据源名称
        
    Returns:
        数据源信息字典，如果未找到返回 None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if source_id:
        cursor.execute("SELECT * FROM data_sources WHERE id = ?", (source_id,))
    elif source_name:
        cursor.execute("SELECT * FROM data_sources WHERE name = ?", (source_name,))
    else:
        print("❌ 错误：必须提供 source_id 或 source_name")
        return None
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def clear_datasource_records(source_id):
    """
    清空数据源的所有记录
    
    Args:
        source_id: 数据源ID
        
    Returns:
        删除的记录数
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询记录数
    cursor.execute("SELECT COUNT(*) as count FROM raw_data_records WHERE source_id = ?", (source_id,))
    count = cursor.fetchone()['count']
    
    # 删除所有记录
    cursor.execute("DELETE FROM raw_data_records WHERE source_id = ?", (source_id,))
    
    # 重置数据源统计信息
    cursor.execute("""
        UPDATE data_sources 
        SET total_records = 0,
            sync_count = 0,
            last_sync_time = NULL,
            updated_at = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), source_id))
    
    conn.commit()
    conn.close()
    
    return count


def reset_datasource(source_id=None, source_name=None):
    """
    重置数据源
    
    Args:
        source_id: 数据源ID
        source_name: 数据源名称
    """
    print("\n" + "=" * 60)
    print("🔄 数据源重置工具")
    print("=" * 60 + "\n")
    
    # 查找数据源
    print("📋 正在查找数据源...")
    source = find_datasource(source_id=source_id, source_name=source_name)
    
    if not source:
        print(f"❌ 错误：数据源未找到")
        print(f"   - 数据源ID: {source_id}")
        print(f"   - 数据源名称: {source_name}")
        return False
    
    print(f"✅ 找到数据源：")
    print(f"   - ID: {source['id']}")
    print(f"   - 名称: {source['name']}")
    print(f"   - 类型: {source['source_type']}")
    print(f"   - 当前记录数: {source['total_records']}")
    print(f"   - 同步次数: {source['sync_count']}")
    
    # 确认删除
    print(f"\n⚠️  警告：此操作将删除该数据源的所有 {source['total_records']} 条记录！")
    confirm = input("   确认删除？输入 'YES' 继续: ")
    
    if confirm != 'YES':
        print("\n❌ 操作已取消")
        return False
    
    # 清空记录
    print("\n🗑️  正在清空记录...")
    deleted_count = clear_datasource_records(source['id'])
    
    print(f"✅ 清空完成！")
    print(f"   - 删除记录数: {deleted_count}")
    print(f"   - 总记录数: 0")
    print(f"   - 同步次数: 0")
    print(f"   - 最后同步时间: 已清空")
    
    print("\n" + "=" * 60)
    print("✅ 数据源重置成功！")
    print("=" * 60 + "\n")
    
    print("📝 下一步操作：")
    print("   1. 在系统中进入\"内部数据源\"模块")
    print("   2. 点击该数据源的\"查看数据\"按钮")
    print("   3. 点击\"导入 Excel\"按钮")
    print("   4. 选择新的 Excel 文件进行导入")
    print()
    
    return True


def list_datasources():
    """列出所有数据源"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM data_sources ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("暂无数据源")
        return
    
    print("\n" + "=" * 80)
    print("📋 数据源列表")
    print("=" * 80)
    print(f"{'ID':<40} {'名称':<20} {'记录数':<10} {'状态':<10}")
    print("-" * 80)
    
    for row in rows:
        status = "✅ 正常" if row['status'] == 'active' else "❌ 停用"
        print(f"{row['id']:<40} {row['name']:<20} {row['total_records']:<10} {status:<10}")
    
    print("-" * 80)
    print(f"共 {len(rows)} 个数据源\n")


def import_excel(source_id, excel_path):
    """
    导入 Excel 文件到指定数据源
    
    Args:
        source_id: 数据源ID
        excel_path: Excel 文件路径
    """
    print(f"\n📥 正在导入 Excel 文件...")
    print(f"   - 文件路径: {excel_path}")
    
    # 检查文件是否存在
    if not os.path.exists(excel_path):
        print(f"❌ 错误：文件不存在")
        return False
    
    # 这里需要调用系统的导入接口
    # 由于这是后端脚本，我们可以直接使用 API 逻辑
    print("⚠️  注意：Excel 导入功能需要通过系统界面完成")
    print("   请按照以下步骤手动导入：")
    print("   1. 打开浏览器访问系统")
    print("   2. 进入\"内部数据源\"模块")
    print("   3. 点击该数据源的\"查看数据\"按钮")
    print("   4. 点击\"导入 Excel\"按钮")
    print(f"   5. 选择文件: {excel_path}")
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='数据源数据清空与重新导入工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 列出所有数据源
  python reset_datasource.py --list
  
  # 按ID清空数据源
  python reset_datasource.py --source-id a1b2c3d4-1234-5678-90ab-cdef12345678
  
  # 按名称清空数据源
  python reset_datasource.py --source-name "VIP订单"
  
  # 清空并准备导入（需要手动导入Excel）
  python reset_datasource.py --source-id <数据源ID> --import-excel data.xlsx

注意事项:
  1. 此操作会永久删除数据源的所有记录，请谨慎操作
  2. 删除前需要输入 'YES' 确认
  3. Excel 导入需要通过系统界面完成
        """
    )
    
    parser.add_argument('--list', action='store_true', help='列出所有数据源')
    parser.add_argument('--source-id', help='数据源ID')
    parser.add_argument('--source-name', help='数据源名称')
    parser.add_argument('--import-excel', help='Excel 文件路径（导入功能需通过界面完成）')
    
    args = parser.parse_args()
    
    # 列出数据源
    if args.list:
        list_datasources()
        return
    
    # 检查参数
    if not args.source_id and not args.source_name:
        parser.print_help()
        print("\n❌ 错误：必须提供 --source-id 或 --source-name")
        sys.exit(1)
    
    # 重置数据源
    success = reset_datasource(source_id=args.source_id, source_name=args.source_name)
    
    if not success:
        sys.exit(1)
    
    # 导入 Excel（提示手动操作）
    if args.import_excel:
        import_excel(args.source_id or args.source_name, args.import_excel)


if __name__ == '__main__':
    main()
