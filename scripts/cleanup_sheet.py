#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Sheet 数据清理脚本
独立运行，用于清理超过指定天数的旧数据
"""

import sys
import os

# 将项目根目录添加到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from generate_report import BioinfoReportGenerator
import argparse


def main():
    parser = argparse.ArgumentParser(description='清理 Google Sheet 中的旧数据')
    parser.add_argument('--days', type=int, default=15, help='保留多少天内的数据（默认15天）')
    args = parser.parse_args()

    print("=" * 60)
    print("📋 Google Sheet 数据清理工具")
    print("=" * 60)
    print(f"⏰ 保留近 {args.days} 天的数据")
    print("=" * 60)

    try:
        # 创建报告生成器实例
        generator = BioinfoReportGenerator()

        # 连接到 Google Sheet
        print("\n🔗 连接到 Google Sheet...")
        generator.connect_sheet()
        print("✅ 连接成功！")

        # 执行清理
        print()
        generator.cleanup_old_data(days=args.days)

        print("\n" + "=" * 60)
        print("✅ 清理完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 清理失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
