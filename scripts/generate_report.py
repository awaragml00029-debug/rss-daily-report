#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RSS Daily Report Generator
从 Google Sheets 读取 RSS 数据，生成每日 Markdown 报告
"""

import os
import re
import sys
import time
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict, Any, Optional
import yaml
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Gemini AI 支持
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("警告: google-generativeai 未安装，AI总结功能将被禁用", file=sys.stderr)


class RSSReportGenerator:
    """RSS 报告生成器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """初始化生成器"""
        self.config = self._load_config(config_path)
        self.client = self._authenticate_google_sheets()
        self.sheet = None
        self.gemini_enabled = False
        self.gemini_model = None

        # 初始化 Gemini AI
        self._init_gemini()
        
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

    def _init_gemini(self):
        """初始化 Gemini AI"""
        if not GEMINI_AVAILABLE:
            print("⚠️  Gemini AI 不可用（未安装 google-generativeai）")
            return

        gemini_config = self.config.get('gemini', {})

        # 检查是否启用
        if not gemini_config.get('enabled', False):
            print("ℹ️  Gemini AI 总结功能已禁用")
            return

        # 获取 API Key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("⚠️  未找到 GEMINI_API_KEY 环境变量，AI总结功能将被禁用")
            return

        try:
            # 配置 Gemini
            genai.configure(api_key=api_key)

            # 获取自定义 API URL（优先使用环境变量，避免暴露配置）
            api_url = os.getenv('GEMINI_API_URL')  # 先检查环境变量
            if api_url:
                self.gemini_api_url = api_url
                print(f"🔧 使用环境变量中的自定义 Gemini API URL")
            else:
                # 环境变量不存在时，从配置文件读取
                api_url = gemini_config.get('api_url')
                if api_url:
                    self.gemini_api_url = api_url
                    print(f"🔧 使用配置文件中的 Gemini API URL: {api_url}")
                else:
                    self.gemini_api_url = None

            # 创建模型实例
            model_name = gemini_config.get('model', 'gemini-2.5-flash-lite')
            self.gemini_model = genai.GenerativeModel(model_name)
            self.gemini_enabled = True

            print(f"✅ Gemini AI 已初始化 (模型: {model_name})")

        except Exception as e:
            print(f"⚠️  Gemini AI 初始化失败: {str(e)}")
            self.gemini_enabled = False

    def _call_gemini_api(self, prompt: str, retry_count: int = 2) -> Optional[str]:
        """
        调用 Gemini API 生成内容

        Args:
            prompt: 提示词
            retry_count: 重试次数

        Returns:
            生成的文本，失败返回 None
        """
        if not self.gemini_enabled or not self.gemini_model:
            return None

        gemini_config = self.config.get('gemini', {})

        for attempt in range(retry_count + 1):
            try:
                # 配置生成参数
                generation_config = {
                    'temperature': gemini_config.get('temperature', 0.7),
                    'max_output_tokens': gemini_config.get('max_tokens', 1000),
                }

                # 调用 API
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=generation_config
                )

                # 检查响应
                if response and response.text:
                    return response.text.strip()
                else:
                    print(f"⚠️  Gemini API 返回空响应 (尝试 {attempt + 1}/{retry_count + 1})")

            except Exception as e:
                print(f"⚠️  Gemini API 调用失败 (尝试 {attempt + 1}/{retry_count + 1}): {str(e)}")

                # 如果不是最后一次尝试，等待后重试
                if attempt < retry_count:
                    time.sleep(2 ** attempt)  # 指数退避：1秒、2秒

        return None

    def generate_ai_summary_for_source(
        self,
        source_name: str,
        items: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        为特定来源生成 AI 总结

        Args:
            source_name: 来源名称
            items: 该来源的文章列表

        Returns:
            AI 生成的总结，失败返回 None
        """
        if not self.gemini_enabled:
            return None

        gemini_config = self.config.get('gemini', {})
        max_items = gemini_config.get('max_items_per_source', 20)

        # 限制条目数量（控制成本）
        items_to_summarize = items[:max_items]

        if not items_to_summarize:
            return None

        # 构建文章列表文本
        articles_text = ""
        for idx, item in enumerate(items_to_summarize, 1):
            title = item.get('title', '').strip()
            description = item.get('description', '').strip()

            # 截断描述（避免太长）
            if description and len(description) > 200:
                description = description[:200] + "..."

            articles_text += f"\n{idx}. 标题：{title}\n"
            if description:
                articles_text += f"   摘要：{description}\n"

        # 获取提示词模板
        prompt_template = gemini_config.get('prompt_template', '')
        if not prompt_template:
            return None

        # 填充模板
        prompt = prompt_template.format(
            source_name=source_name,
            articles=articles_text
        )

        # 调用 API
        print(f"🤖 正在为 {source_name} 生成 AI 总结...")
        summary = self._call_gemini_api(prompt)

        if summary:
            print(f"✅ {source_name} AI 总结生成成功")
        else:
            print(f"⚠️  {source_name} AI 总结生成失败")

        return summary

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

        # ===== AI 智能总结 =====
        if self.gemini_enabled:
            md_lines.append("## 🤖 今日AI智能总结")
            md_lines.append("")

            ai_summary_generated = False

            for (display_name, sort_order, icon), source_items in sorted_sources:
                # 为每个来源生成 AI 总结
                summary = self.generate_ai_summary_for_source(display_name, source_items)

                if summary:
                    ai_summary_generated = True
                    md_lines.append(f"### {icon} {display_name}")
                    md_lines.append("")
                    md_lines.append(f"> {summary}")
                    md_lines.append("")

            # 如果没有生成任何总结，则显示提示信息
            if not ai_summary_generated:
                md_lines.append("> ℹ️  今日暂无AI总结")
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

    def generate_hugo_front_matter(self, date: datetime, total_count: int) -> str:
        """生成Hugo Front Matter"""
        hugo_config = self.config.get('hugo', {})
        author = hugo_config.get('author', 'oknet')

        date_str = date.strftime('%Y-%m-%d')

        front_matter = f"""---
title: "科研日报 {date_str}"
author: {author}
date: '{date_str}'
slug: {date_str}
categories:
  - DailyReport
tags:
  - Research
  - Daily
draft: no
---

"""
        return front_matter

    def generate_hugo_report(self, items: List[Dict[str, Any]], date: datetime) -> str:
        """生成带Hugo Front Matter的报告"""
        # 生成普通报告内容
        report_content = self.generate_daily_report(items, date)

        # 添加Front Matter
        hugo_content = self.generate_hugo_front_matter(date, len(items)) + report_content

        return hugo_content

    def generate_html_report(self, items: List[Dict[str, Any]], date: datetime) -> str:
        """生成静态HTML页面"""
        # 先生成markdown内容
        md_content = self.generate_daily_report(items, date)

        # 转换为HTML（简单处理markdown语法）
        html_content = self._markdown_to_html(md_content, date)

        return html_content

    def _markdown_to_html(self, md_content: str, date: datetime) -> str:
        """将markdown转换为HTML（简化版）"""
        date_str = date.strftime('%Y-%m-%d')

        # HTML模板
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>科研日报 - {date_str}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 4px solid #3498db;
        }}

        h3 {{
            color: #555;
            margin-top: 20px;
            margin-bottom: 10px;
        }}

        h4 {{
            color: #666;
            margin-top: 15px;
            margin-bottom: 8px;
        }}

        blockquote {{
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px 20px;
            margin: 15px 0;
            border-radius: 4px;
        }}

        .ai-summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}

        .ai-summary h2 {{
            color: white;
            border-left-color: white;
        }}

        .ai-summary h3 {{
            color: #f0f0f0;
            margin-top: 15px;
        }}

        .ai-summary blockquote {{
            background: rgba(255,255,255,0.1);
            border-left-color: white;
            color: white;
        }}

        ul {{
            margin-left: 20px;
            margin-bottom: 15px;
        }}

        li {{
            margin-bottom: 8px;
        }}

        a {{
            color: #3498db;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}

        th {{
            background: #3498db;
            color: white;
        }}

        hr {{
            border: none;
            border-top: 2px solid #eee;
            margin: 30px 0;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #777;
            font-size: 14px;
            text-align: center;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}

            body {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
"""

        # 简单的markdown到HTML转换
        html_body = md_content

        # 处理标题
        html_body = html_body.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)

        # 处理AI总结区域（特殊样式）
        if '## 🤖 今日AI智能总结' in html_body:
            parts = html_body.split('## 🤖 今日AI智能总结')
            before_ai = parts[0]
            after_ai = parts[1] if len(parts) > 1 else ''

            if '---' in after_ai:
                ai_section, rest = after_ai.split('---', 1)
                html_body = before_ai + '<div class="ai-summary"><h2>🤖 今日AI智能总结</h2>' + ai_section + '</div><hr>' + rest
            else:
                html_body = before_ai + '<div class="ai-summary"><h2>🤖 今日AI智能总结</h2>' + after_ai + '</div>'

        # 处理其他标题
        html_body = html_body.replace('## ', '<h2>').replace('\n', '</h2>\n')
        html_body = html_body.replace('### ', '<h3>').replace('\n', '</h3>\n')
        html_body = html_body.replace('#### ', '<h4>').replace('\n', '</h4>\n')

        # 处理引用
        lines = html_body.split('\n')
        processed_lines = []
        in_blockquote = False

        for line in lines:
            if line.startswith('> '):
                if not in_blockquote:
                    processed_lines.append('<blockquote>')
                    in_blockquote = True
                processed_lines.append(line[2:])
            else:
                if in_blockquote:
                    processed_lines.append('</blockquote>')
                    in_blockquote = False
                processed_lines.append(line)

        if in_blockquote:
            processed_lines.append('</blockquote>')

        html_body = '\n'.join(processed_lines)

        # 处理粗体和链接
        import re
        html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
        html_body = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', html_body)

        # 处理列表
        html_body = html_body.replace('\n- ', '\n<li>').replace('<li>', '<ul><li>', 1)
        html_body = html_body.replace('\n\n', '</ul>\n\n')

        # 处理分隔线
        html_body = html_body.replace('---', '<hr>')

        # 处理表格
        html_body = html_body.replace('|', '</td><td>').replace('<td>', '<td>', 1)

        html_template += html_body

        html_template += """
    </div>
</body>
</html>"""

        return html_template
    
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

        # 1. 保存本地markdown报告
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

        # 2. 生成并保存Hugo版本（带Front Matter）
        hugo_content = self.generate_hugo_report(filtered_items, target_date)
        hugo_filepath = os.path.join(
            'temp_hugo',
            f"daily-{target_date.strftime('%Y-%m-%d')}.md"
        )
        self.save_report(hugo_content, hugo_filepath)
        print(f"📝 Hugo版本已生成: {hugo_filepath}")

        # 3. 生成并保存HTML版本
        html_content = self.generate_html_report(filtered_items, target_date)
        html_filepath = os.path.join(
            'temp_hugo',
            'latest.html'
        )
        self.save_report(html_content, html_filepath)
        print(f"🌐 HTML版本已生成: {html_filepath}")

        print("✨ 所有报告生成完成！")

        # 返回生成的文件路径，供后续推送使用
        return {
            'markdown': filepath,
            'hugo': hugo_filepath,
            'html': html_filepath,
            'date': target_date
        }
    
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
