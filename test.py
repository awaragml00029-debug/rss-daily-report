#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本地测试脚本
用于在本地环境测试报告生成功能
"""

import os
import sys
from datetime import datetime, timedelta

# 添加脚本目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def test_with_mock_data():
    """使用模拟数据测试（不需要 Google Sheets 访问）"""
    print("🧪 使用模拟数据进行测试...")
    
    # 创建模拟数据
    mock_data = [
        # 表头
        ["抓取时间", "属性", "适名称", "适分类", "标题", "链接", "发布时间", "作者"],
        # 数据行
        [
            datetime.now().strftime("%m/%d/%Y"),
            "Week012025",
            "生信菜鸟团",
            "mpRss",
            "单细胞测序在肿瘤研究中的应用",
            "https://mp.weixin.qq.com/s/example1",
            "Mon, 29 Oct 2025 14:30:00 +0800",
            "张三"
        ],
        [
            datetime.now().strftime("%m/%d/%Y"),
            "Week012025",
            "生物信息学",
            "mpRss",
            "R包开发教程：从零开始",
            "https://mp.weixin.qq.com/s/example2",
            "Mon, 29 Oct 2025 15:20:00 +0800",
            "李四"
        ],
        [
            datetime.now().strftime("%m/%d/%Y"),
            "Week012025",
            "测序中国",
            "mpRss",
            "空间转录组测序技术进展",
            "https://mp.weixin.qq.com/s/example3",
            "Mon, 29 Oct 2025 16:10:00 +0800",
            "王五"
        ],
        [
            (datetime.now() - timedelta(days=1)).strftime("%m/%d/%Y"),
            "Week012025",
            "其他公众号",
            "mpRss",
            "这篇文章不包含关键词",
            "https://mp.weixin.qq.com/s/example4",
            "Sun, 28 Oct 2025 10:00:00 +0800",
            "赵六"
        ],
    ]
    
    # 模拟 RSSReportGenerator 类
    from generate_report import RSSReportGenerator
    
    class MockGenerator(RSSReportGenerator):
        def __init__(self):
            # 跳过配置和认证
            import yaml
            with open('config.yaml', 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.client = None
            self.sheet = None
        
        def get_all_data(self):
            return mock_data
    
    # 运行测试
    try:
        generator = MockGenerator()
        
        # 测试日报生成
        print("\n📅 测试每日报告生成...")
        target_date = datetime.now()
        filtered_items = generator.filter_data_by_date(mock_data, target_date)
        
        print(f"✅ 筛选出 {len(filtered_items)} 条数据")
        
        if filtered_items:
            report_content = generator.generate_daily_report(filtered_items, target_date)
            
            # 保存测试报告
            test_filepath = f"test-report-{target_date.strftime('%Y-%m-%d')}.md"
            with open(test_filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ 测试报告已保存: {test_filepath}")
            print("\n--- 报告预览（前30行）---")
            print("\n".join(report_content.split("\n")[:30]))
            print("\n--- 预览结束 ---")
        else:
            print("⚠️  没有筛选到数据")
        
        print("\n✨ 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_with_real_data():
    """使用真实 Google Sheets 数据测试"""
    print("🧪 连接到 Google Sheets 进行测试...")
    
    # 检查环境变量
    if not os.getenv('GOOGLE_CREDENTIALS'):
        print("❌ 未设置 GOOGLE_CREDENTIALS 环境变量")
        print("请运行: export GOOGLE_CREDENTIALS='...'")
        return
    
    if not os.getenv('SHEET_ID'):
        print("❌ 未设置 SHEET_ID 环境变量")
        print("请运行: export SHEET_ID='...'")
        return
    
    try:
        from generate_report import RSSReportGenerator
        
        generator = RSSReportGenerator()
        
        # 测试连接
        print("📊 正在读取数据...")
        all_data = generator.get_all_data()
        print(f"✅ 成功读取 {len(all_data) - 1} 行数据")
        
        # 获取最新日期
        latest_date = generator.get_latest_crawl_date(all_data)
        if latest_date:
            print(f"📅 最新数据日期: {latest_date.strftime('%Y-%m-%d')}")
            
            # 生成报告
            print("\n📝 生成测试报告...")
            generator.run_daily(latest_date)
        else:
            print("❌ 未找到有效数据")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='测试 RSS 报告生成器')
    parser.add_argument(
        '--mode',
        choices=['mock', 'real'],
        default='mock',
        help='测试模式：mock（模拟数据）或 real（真实数据）'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'mock':
        test_with_mock_data()
    else:
        test_with_real_data()


if __name__ == '__main__':
    main()
