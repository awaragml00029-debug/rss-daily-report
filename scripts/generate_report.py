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
        # 智能查找配置文件
        possible_paths = [
            config_path,                                    # 当前目录
            os.path.join('..', config_path),               # 上级目录
            os.path.join(os.path.dirname(__file__), '..', config_path),  # 脚本的上级目录
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        
        # 如果都找不到，抛出错误
        raise FileNotFoundError(
            f"找不到配置文件 '{config_path}'。尝试过的路径: {possible_paths}"
        )
    
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
            '%m/%d/%Y %H:%M:%S',  # 10/29/2025 0:58:55 - 你的格式！
            '%m/%d/%Y %H:%M',     # 8/12/2025 10:30
            '%m/%d/%Y',           # 8/12/2025
            '%Y-%m-%d %H:%M:%S',  # 2025-08-12 10:30:45
            '%Y-%m-%d %H:%M',     # 2025-08-12 10:30
            '%Y-%m-%d',           # 2025-08-12
            '%Y/%m/%d',           # 2025/08/12
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
        
        # 调试计数器
        debug_counts = {
            'total_rows': len(data) - 1,
            'parsed_dates': 0,
            'matched_dates': 0,
            'matched_keywords': 0,
        }
        
        # 只显示前3个样本用于调试
        sample_count = 0
        max_samples = 3
        
        for row in data[1:]:  # 跳过表头
            if len(row) < 6:  # 确保有最基本的列
                continue
            
            # 获取抓取时间
            crawl_time_str = row[col_map['crawl_time'] - 1]
            crawl_time = self.parse_datetime(crawl_time_str)
            
            if not crawl_time:
                continue
            
            debug_counts['parsed_dates'] += 1
            
            # 显示前几个样本
            if sample_count < max_samples:
                print(f"📝 样本 {sample_count + 1}:")
                print(f"   抓取时间: {crawl_time_str} -> {crawl_time}")
                print(f"   目标日期: {target_date.date()}")
                print(f"   匹配结果: {crawl_time.date() == target_date.date()}")
                sample_count += 1
            
            # 检查是否为目标日期（只比较年月日）
            if crawl_time.date() != target_date.date():
                continue
            
            debug_counts['matched_dates'] += 1
            
            # 获取标题并进行关键词匹配
            title = row[col_map['title'] - 1] if len(row) > col_map['title'] - 1 else ''
            matched_keywords = self.filter_by_keywords(title)
            
            # 显示匹配到的日期但未匹配关键词的前几个
            if not matched_keywords and debug_counts['matched_dates'] <= 3:
                print(f"🔍 日期匹配但关键词未匹配:")
                print(f"   标题: {title[:100]}")
                print(f"   关键词: {self.config.get('keywords', [])}")
            
            if not matched_keywords:  # 没有匹配的关键词，跳过
                continue
            
            debug_counts['matched_keywords'] += 1
            
            # 构建数据项
            item = {
                'crawl_time': crawl_time_str,
                'attribute': row[col_map['attribute'] - 1] if len(row) > col_map['attribute'] - 1 else '',
                'source_name': row[col_map['source_name'] - 1] if len(row) > col_map['source_name'] - 1 else '',
                'category': row[col_map['category'] - 1] if len(row) > col_map['category'] - 1 else '',
                'title': title,
                'link': row[col_map['link'] - 1] if len(row) > col_map['link'] - 1 else '',
                'description': row[col_map['description'] - 1] if len(row) > col_map['description'] - 1 else '',
                'publish_time': row[col_map['publish_time'] - 1] if len(row) > col_map['publish_time'] - 1 else '',
                'author': row[col_map['author'] - 1] if len(row) > col_map['author'] - 1 else '',
                'matched_keywords': matched_keywords,
            }
            filtered_items.append(item)
        
        # 输出调试统计
        print(f"\n📊 筛选统计:")
        print(f"   总行数: {debug_counts['total_rows']}")
        print(f"   成功解析日期: {debug_counts['parsed_dates']}")
        print(f"   日期匹配: {debug_counts['matched_dates']}")
        print(f"   关键词匹配: {debug_counts['matched_keywords']}")
        
        return filtered_items
    
    def generate_daily_report(
        self, 
        items: List[Dict[str, Any]], 
        date: datetime
    ) -> str:
        """生成每日 Markdown 报告 - 按来源分组，前10条详细展示"""
        
        # 获取配置
        source_mapping = self.config.get('source_mapping', {})
        detail_count = self.config.get('report_format', {}).get('detail_items_per_source', 10)
        desc_max_length = self.config.get('report_format', {}).get('description_max_length', 500)
        show_more = self.config.get('report_format', {}).get('show_more_section', True)
        
        # 统计信息
        total_count = len(items)
        keyword_counter = Counter()
        for item in items:
            keyword_counter.update(item['matched_keywords'])
        
        # 按来源分组（使用 category 字段，即D列）
        items_by_source = {}
        for item in items:
            category = item.get('category', '').strip()
            
            # 根据配置映射到显示名称
            if category in source_mapping:
                source_info = source_mapping[category]
                display_name = source_info[0]
                sort_order = source_info[1]
                icon = source_info[2]
            else:
                # 未定义的来源使用默认配置
                default_info = source_mapping.get('_default', ['其他来源', 99, '📁'])
                display_name = default_info[0]
                sort_order = default_info[1]
                icon = default_info[2]
            
            source_key = (display_name, sort_order, icon)
            if source_key not in items_by_source:
                items_by_source[source_key] = []
            items_by_source[source_key].append(item)
        
        # 按配置的排序顺序排序来源
        sorted_sources = sorted(items_by_source.items(), key=lambda x: x[0][1])
        
        # 为每个来源的条目排序：关键词数量 > 时间
        for source_key, source_items in sorted_sources:
            source_items.sort(key=lambda x: (
                -len(x['matched_keywords']),  # 关键词数多的在前
                -(self.parse_datetime(x['crawl_time']) or datetime.min).timestamp()  # 时间新的在前
            ))
        
        # 生成 Markdown
        md_lines = []
        md_lines.append(f"# 📅 Daily Report - {date.strftime('%Y-%m-%d')}")
        md_lines.append("")
        md_lines.append(f"> 今日筛选出 **{total_count}** 条内容，来自 **{len(items_by_source)}** 个来源")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # ===== 分类浏览 =====
        md_lines.append("## 📚 分类浏览")
        md_lines.append("")
        
        # 记录需要在"更多内容"区域显示的条目
        more_items_by_source = {}
        
        for (display_name, sort_order, icon), source_items in sorted_sources:
            source_count = len(source_items)
            md_lines.append(f"### {icon} {display_name} ({source_count}条)")
            md_lines.append("")
            
            # 详细展示的条目（前N条）
            detail_items = source_items[:detail_count]
            # 剩余条目
            remaining_items = source_items[detail_count:]
            
            if detail_items:
                md_lines.append("#### 详细内容" + (f"（前{len(detail_items)}条）" if remaining_items else f"（全部{len(detail_items)}条）"))
                md_lines.append("")
                
                for idx, item in enumerate(detail_items, 1):
                    keywords_str = "、".join(item['matched_keywords'])
                    
                    # 优先级标记
                    priority_mark = ""
                    if len(item['matched_keywords']) >= 3:
                        priority_mark = "⭐ "
                    
                    # 标题
                    md_lines.append(f"**{idx}.** {priority_mark}**{item['title']}**")
                    
                    # 作者（如果有）
                    if item.get('author'):
                        md_lines.append(f"- ✍️ **作者**：{item['author']}")
                    
                    # 关键词
                    md_lines.append(f"- 🏷️ **关键词**：{keywords_str}")
                    
                    # 描述
                    description = item.get('description', '').strip()
                    if description:
                        # 截断描述
                        if desc_max_length > 0 and len(description) > desc_max_length:
                            description = description[:desc_max_length] + "..."
                        md_lines.append(f"- 📝 **描述**：{description}")
                    
                    # 链接
                    if item.get('link'):
                        md_lines.append(f"- 🔗 [查看原文]({item['link']})")
                    
                    md_lines.append("")
            
            # 如果有剩余条目，添加提示
            if remaining_items:
                anchor = display_name.replace(' ', '-').lower()
                md_lines.append(f"> 💡 该来源还有 {len(remaining_items)} 条内容，详见 [文末](#更多-{anchor})")
                more_items_by_source[(display_name, icon, anchor)] = remaining_items
            
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
        
        # ===== 关键词统计 =====
        md_lines.append("## 📊 关键词统计")
        md_lines.append("")
        
        # 生成表格
        md_lines.append("| 关键词 | 出现次数 |")
        md_lines.append("|--------|----------|")
        for keyword, count in keyword_counter.most_common(20):
            md_lines.append(f"| {keyword} | {count} |")
        
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # ===== 更多内容区域 =====
        if show_more and more_items_by_source:
            md_lines.append("## 📎 更多内容")
            md_lines.append("")
            
            for (display_name, icon, anchor), remaining_items in more_items_by_source.items():
                md_lines.append(f"### <a name=\"更多-{anchor}\"></a>{icon} {display_name} 其他内容 ({len(remaining_items)}条)")
                md_lines.append("")
                
                for item in remaining_items:
                    title = item['title']
                    link = item.get('link', '')
                    if link:
                        md_lines.append(f"- [{title}]({link})")
                    else:
                        md_lines.append(f"- {title}")
                
                md_lines.append("")
            
            md_lines.append("---")
            md_lines.append("")
        
        # 页脚
        md_lines.append(f"*📅 报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*  ")
        md_lines.append(f"*🤖 由 GitHub Actions 自动生成*")
        
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
