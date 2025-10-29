#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RSS Daily Report Generator
从 Google Sheets 读取 RSS 数据，生成每日 Markdown 报告
"""

import os
import re
import sys
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict, Any, Optional
import yaml
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class RSSReportGenerator:
    """RSS 报告生成器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """初始化生成器"""
        self.config = self._load_config(config_path)
        self.client = self._authenticate_google_sheets()
        self.sheet = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _authenticate_google_sheets(self) -> gspread.Client:
        """认证 Google Sheets"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # 从环境变量读取凭证
        creds_json = os.getenv('GOOGLE_CREDENTIALS')
        if not creds_json:
            raise ValueError("未找到 GOOGLE_CREDENTIALS 环境变量")
        
        # 将 JSON 字符串写入临时文件
        import json
        creds_dict = json.loads(creds_json)
        
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict, scope
        )
        return gspread.authorize(credentials)
    
    def connect_sheet(self) -> gspread.Worksheet:
        """连接到指定的 Google Sheet"""
        spreadsheet_id = os.getenv('SHEET_ID') or self.config['google_sheets']['spreadsheet_id']
        sheet_name = self.config['google_sheets']['sheet_name']
        
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        self.sheet = spreadsheet.worksheet(sheet_name)
        return self.sheet
    
    def get_all_data(self) -> List[List[str]]:
        """获取所有数据"""
        if not self.sheet:
            self.connect_sheet()
        return self.sheet.get_all_values()
    
    def parse_datetime(self, date_str: str) -> Optional[datetime]:
        """解析日期时间字符串"""
        if not date_str:
            return None
        
        # 尝试多种日期格式
        formats = [
            '%m/%d/%Y',           # 8/12/2025
            '%Y-%m-%d',           # 2025-08-12
            '%Y/%m/%d',           # 2025/08/12
            '%m/%d/%Y %H:%M',     # 8/12/2025 10:30
            '%Y-%m-%d %H:%M',     # 2025-08-12 10:30
            '%Y-%m-%d %H:%M:%S',  # 2025-08-12 10:30:45
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        # 如果都失败，尝试解析更复杂的格式
        try:
            # 处理类似 "Mon, 11 Aug 2025 22:37:00 +0800" 的格式
            from dateutil import parser
            return parser.parse(date_str)
        except:
            print(f"警告: 无法解析日期 '{date_str}'", file=sys.stderr)
            return None
    
    def filter_by_keywords(self, title: str) -> List[str]:
        """
        根据关键词筛选，返回匹配的关键词列表
        支持正则表达式匹配
        """
        if not title:
            return []
        
        keywords = self.config.get('keywords', [])
        exclude_keywords = self.config.get('exclude_keywords', [])
        
        # 检查排除关键词
        for exclude_kw in exclude_keywords:
            if re.search(exclude_kw, title, re.IGNORECASE):
                return []
        
        # 检查匹配关键词
        matched = []
        for keyword in keywords:
            # 将简单关键词转换为正则（支持中间插入字符）
            # 例如: "单细胞" -> "单.*细.*胞"
            pattern = '.*'.join(list(keyword))
            if re.search(pattern, title, re.IGNORECASE):
                matched.append(keyword)
        
        return matched
    
    def get_latest_crawl_date(self, data: List[List[str]]) -> Optional[datetime]:
        """获取最新的抓取日期"""
        col_idx = self.config['columns']['crawl_time'] - 1
        dates = []
        
        for row in data[1:]:  # 跳过表头
            if len(row) > col_idx and row[col_idx]:
                dt = self.parse_datetime(row[col_idx])
                if dt:
                    dates.append(dt)
        
        return max(dates) if dates else None
    
    def filter_data_by_date(
        self, 
        data: List[List[str]], 
        target_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        筛选指定日期的数据，并进行关键词过滤
        """
        col_map = self.config['columns']
        filtered_items = []
        
        for row in data[1:]:  # 跳过表头
            if len(row) < 8:  # 确保有足够的列
                continue
            
            # 获取抓取时间
            crawl_time_str = row[col_map['crawl_time'] - 1]
            crawl_time = self.parse_datetime(crawl_time_str)
            
            if not crawl_time:
                continue
            
            # 检查是否为目标日期（只比较年月日）
            if crawl_time.date() != target_date.date():
                continue
            
            # 获取标题并进行关键词匹配
            title = row[col_map['title'] - 1]
            matched_keywords = self.filter_by_keywords(title)
            
            if not matched_keywords:  # 没有匹配的关键词，跳过
                continue
            
            # 构建数据项
            item = {
                'crawl_time': crawl_time_str,
                'attribute': row[col_map['attribute'] - 1] if len(row) > col_map['attribute'] - 1 else '',
                'source_name': row[col_map['source_name'] - 1] if len(row) > col_map['source_name'] - 1 else '',
                'category': row[col_map['category'] - 1] if len(row) > col_map['category'] - 1 else '',
                'title': title,
                'link': row[col_map['link'] - 1] if len(row) > col_map['link'] - 1 else '',
                'publish_time': row[col_map['publish_time'] - 1] if len(row) > col_map['publish_time'] - 1 else '',
                'author': row[col_map['author'] - 1] if len(row) > col_map['author'] - 1 else '',
                'matched_keywords': matched_keywords,
            }
            filtered_items.append(item)
        
        return filtered_items
    
    def generate_daily_report(
        self, 
        items: List[Dict[str, Any]], 
        date: datetime
    ) -> str:
        """生成每日 Markdown 报告"""
        
        # 统计信息
        total_count = len(items)
        keyword_counter = Counter()
        for item in items:
            keyword_counter.update(item['matched_keywords'])
        
        # 按抓取时间排序（最新在前）
        items.sort(
            key=lambda x: self.parse_datetime(x['crawl_time']) or datetime.min,
            reverse=True
        )
        
        # 生成 Markdown
        md_lines = []
        md_lines.append(f"# 📅 Daily Report - {date.strftime('%Y-%m-%d')}")
        md_lines.append("")
        md_lines.append("> 生物信息学 RSS 订阅日报")
        md_lines.append(f"> 筛选关键词：{', '.join(self.config['keywords'])}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # 统计信息
        md_lines.append("## 📊 今日概览")
        md_lines.append("")
        md_lines.append(f"- ✅ 命中条目：{total_count}")
        md_lines.append(f"- 📌 关键词命中：{sum(keyword_counter.values())} 次")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # 内容列表
        md_lines.append("## 📰 内容列表")
        md_lines.append("")
        
        for idx, item in enumerate(items, 1):
            keywords_str = "、".join(item['matched_keywords'])
            md_lines.append(f"### {idx}. {item['title']}")
            md_lines.append("")
            md_lines.append(f"**匹配关键词**：{keywords_str}  ")
            
            if item['source_name']:
                md_lines.append(f"**来源**：{item['source_name']}  ")
            
            if item['author']:
                md_lines.append(f"**作者**：{item['author']}  ")
            
            if item['publish_time']:
                md_lines.append(f"**发布时间**：{item['publish_time']}  ")
            
            if item['link']:
                md_lines.append(f"**链接**：[阅读原文]({item['link']})")
            
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
        
        # 关键词统计
        if keyword_counter:
            md_lines.append("## 🏷️ 关键词统计")
            md_lines.append("")
            for keyword, count in keyword_counter.most_common():
                md_lines.append(f"- {keyword}：{count} 次")
            md_lines.append("")
        
        # 页脚
        md_lines.append("---")
        md_lines.append("")
        md_lines.append(f"*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        
        return "\n".join(md_lines)
    
    def generate_monthly_report(
        self,
        year: int,
        month: int
    ) -> str:
        """生成月度报告（汇总当月所有日报）"""
        
        # 获取当月所有数据
        all_data = self.get_all_data()
        
        # 获取当月所有日期
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # 收集当月所有符合条件的数据
        all_items = []
        current_date = month_start
        while current_date <= month_end:
            daily_items = self.filter_data_by_date(all_data, current_date)
            all_items.extend(daily_items)
            current_date += timedelta(days=1)
        
        # 统计
        total_count = len(all_items)
        keyword_counter = Counter()
        for item in all_items:
            keyword_counter.update(item['matched_keywords'])
        
        # 按日期分组
        items_by_date = {}
        for item in all_items:
            crawl_time = self.parse_datetime(item['crawl_time'])
            if crawl_time:
                date_key = crawl_time.strftime('%Y-%m-%d')
                if date_key not in items_by_date:
                    items_by_date[date_key] = []
                items_by_date[date_key].append(item)
        
        # 生成报告
        md_lines = []
        md_lines.append(f"# 📅 Monthly Report - {year}年{month}月")
        md_lines.append("")
        md_lines.append("> 生物信息学 RSS 订阅月报")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # 月度统计
        md_lines.append("## 📊 本月概览")
        md_lines.append("")
        md_lines.append(f"- 📅 统计周期：{month_start.strftime('%Y-%m-%d')} 至 {month_end.strftime('%Y-%m-%d')}")
        md_lines.append(f"- ✅ 总命中条目：{total_count}")
        md_lines.append(f"- 📆 活跃天数：{len(items_by_date)}")
        md_lines.append(f"- 📈 日均条目：{total_count // len(items_by_date) if items_by_date else 0}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # 关键词统计
        md_lines.append("## 🏷️ 本月关键词统计")
        md_lines.append("")
        for keyword, count in keyword_counter.most_common():
            md_lines.append(f"- {keyword}：{count} 次")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # 每日摘要
        md_lines.append("## 📆 每日摘要")
        md_lines.append("")
        
        for date_key in sorted(items_by_date.keys(), reverse=True):
            items = items_by_date[date_key]
            md_lines.append(f"### {date_key} ({len(items)} 条)")
            md_lines.append("")
            
            # 列出该日的文章标题
            for item in items[:10]:  # 每天最多显示10条
                keywords_str = "、".join(item['matched_keywords'])
                md_lines.append(f"- [{item['title']}]({item['link']}) *({keywords_str})*")
            
            if len(items) > 10:
                md_lines.append(f"- *...还有 {len(items) - 10} 条*")
            
            md_lines.append("")
        
        # 页脚
        md_lines.append("---")
        md_lines.append("")
        md_lines.append(f"*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        
        return "\n".join(md_lines)
    
    def save_report(self, content: str, filepath: str):
        """保存报告到文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 报告已保存: {filepath}")
    
    def run_daily(self, target_date: Optional[datetime] = None):
        """运行每日报告生成"""
        print("🚀 开始生成每日报告...")
        
        # 获取数据
        all_data = self.get_all_data()
        print(f"📊 共读取 {len(all_data) - 1} 行数据")
        
        # 确定目标日期
        if not target_date:
            latest_date = self.get_latest_crawl_date(all_data)
            if not latest_date:
                print("❌ 未找到有效的抓取日期")
                return
            target_date = latest_date
        
        print(f"📅 目标日期: {target_date.strftime('%Y-%m-%d')}")
        
        # 筛选数据
        filtered_items = self.filter_data_by_date(all_data, target_date)
        print(f"✅ 筛选出 {len(filtered_items)} 条符合条件的数据")
        
        if not filtered_items:
            print("⚠️  没有符合条件的数据，跳过报告生成")
            return
        
        # 生成报告
        report_content = self.generate_daily_report(filtered_items, target_date)
        
        # 保存报告
        output_config = self.config['output']
        filepath = os.path.join(
            output_config['daily_path'].format(
                year=target_date.year,
                month=f"{target_date.month:02d}"
            ),
            output_config['daily_filename'].format(
                date=target_date.strftime('%Y-%m-%d')
            )
        )
        
        self.save_report(report_content, filepath)
        print("✨ 每日报告生成完成！")
    
    def run_monthly(self, year: Optional[int] = None, month: Optional[int] = None):
        """运行月度报告生成"""
        print("🚀 开始生成月度报告...")
        
        # 确定年月
        now = datetime.now()
        if not year:
            year = now.year
        if not month:
            month = now.month
        
        print(f"📅 目标月份: {year}年{month}月")
        
        # 生成报告
        report_content = self.generate_monthly_report(year, month)
        
        # 保存报告
        output_config = self.config['output']
        filepath = os.path.join(
            output_config['monthly_path'].format(year=year),
            output_config['monthly_filename'].format(
                year=year,
                month=f"{month:02d}"
            )
        )
        
        self.save_report(report_content, filepath)
        print("✨ 月度报告生成完成！")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RSS Daily Report Generator')
    parser.add_argument(
        '--mode',
        choices=['daily', 'monthly'],
        default='daily',
        help='生成模式：daily（每日）或 monthly（每月）'
    )
    parser.add_argument(
        '--date',
        help='指定日期 (YYYY-MM-DD)，仅用于 daily 模式'
    )
    parser.add_argument(
        '--year',
        type=int,
        help='指定年份，仅用于 monthly 模式'
    )
    parser.add_argument(
        '--month',
        type=int,
        help='指定月份，仅用于 monthly 模式'
    )
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = RSSReportGenerator()
    
    try:
        if args.mode == 'daily':
            # 每日报告
            target_date = None
            if args.date:
                target_date = datetime.strptime(args.date, '%Y-%m-%d')
            generator.run_daily(target_date)
            
        elif args.mode == 'monthly':
            # 月度报告
            generator.run_monthly(args.year, args.month)
    
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
