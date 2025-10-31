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

# Markdown 转换支持
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("警告: markdown 未安装，HTML生成将使用简化版本", file=sys.stderr)


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

    def cleanup_old_data(self, days: int = 15):
        """清理 Google Sheet 中超过指定天数的旧数据"""
        try:
            if not self.sheet:
                return

            print(f"🧹 开始清理 {days} 天前的旧数据...")

            all_data = self.sheet.get_all_values()
            if len(all_data) <= 1:  # 只有标题行或空表
                print("  ℹ️  没有数据需要清理")
                return

            header = all_data[0]
            rows = all_data[1:]

            # 使用配置的列索引（从1开始，转换为从0开始的数组索引）
            crawl_time_idx = self.config['columns']['crawl_time'] - 1  # A列 = 1，数组索引 = 0
            print(f"  📍 使用第 {crawl_time_idx + 1} 列（{header[crawl_time_idx] if crawl_time_idx < len(header) else '未知'}）作为抓取时间")

            # 计算截止日期
            cutoff_date = datetime.now() - timedelta(days=days)
            print(f"  📅 截止日期：{cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")

            # 找出需要保留的行（日期在截止日期之后的）
            rows_to_keep = []
            rows_to_delete = []

            for idx, row in enumerate(rows, start=2):  # start=2 因为第1行是标题
                if crawl_time_idx < len(row):
                    crawl_time_str = row[crawl_time_idx]
                    crawl_time = self.parse_datetime(crawl_time_str)

                    if crawl_time and crawl_time >= cutoff_date:
                        rows_to_keep.append(row)
                    else:
                        rows_to_delete.append(idx)
                else:
                    # 没有 crawl_time 的行也保留
                    rows_to_keep.append(row)

            if not rows_to_delete:
                print(f"  ✅ 所有数据都在 {days} 天内，无需清理")
                return

            print(f"  📊 找到 {len(rows_to_delete)} 行旧数据需要删除")
            print(f"  📈 保留 {len(rows_to_keep)} 行近期数据")

            # 删除旧数据行（从后往前删除，避免索引变化）
            print(f"  🗑️  开始删除旧数据...")
            for row_idx in reversed(rows_to_delete):
                self.sheet.delete_rows(row_idx)

            print(f"  ✅ 成功清理 {len(rows_to_delete)} 行旧数据")

        except Exception as e:
            print(f"  ⚠️  清理数据时出错: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            # 不抛出异常，避免影响主流程

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
        md_lines.append('<div class="powered-by-top">Powered by <a href="https://kyplus.de">科研普拉斯</a> & <a href="https://claude.ai">Claude</a></div>')
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

            # 使用 details/summary 实现折叠功能
            md_lines.append(f"<details>")
            md_lines.append(f'<summary style="text-align: right; direction: rtl; padding: 10px 15px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-right: 4px solid #667eea; font-weight: 600; cursor: pointer; margin: 15px 0; border-radius: 6px;">{icon} {display_name} ({source_count}条)</summary>')
            md_lines.append("")
            md_lines.append(f'<div class="details-content" markdown="1">')
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
            md_lines.append("</div>")
            md_lines.append("")
            md_lines.append("</details>")
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
                # 使用 details 折叠，但标题居左（不加 style 属性）
                md_lines.append(f"<details>")
                md_lines.append(f"<summary><a name=\"更多-{anchor}\"></a>{icon} {display_name} 其他内容 ({len(remaining_items)}条)</summary>")
                md_lines.append("")
                md_lines.append(f'<div class="details-content" markdown="1">')
                md_lines.append("")

                for item in remaining_items:
                    title = item['title']
                    link = item.get('link', '')
                    if link:
                        md_lines.append(f"- [{title}]({link})")
                    else:
                        md_lines.append(f"- {title}")

                md_lines.append("")
                md_lines.append("</div>")
                md_lines.append("")
                md_lines.append("</details>")
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
        """将markdown转换为HTML"""
        date_str = date.strftime('%Y-%m-%d')

        # 先处理所有的 details 标签（提取、转换、重新包装）
        md_content = self._process_details_tags(md_content)

        # 处理 AI 总结区域（需要特殊样式）
        ai_summary_html = ""
        remaining_content = md_content

        if '## 🤖 今日AI智能总结' in md_content:
            parts = md_content.split('## 🤖 今日AI智能总结', 1)
            before_ai = parts[0]
            after_ai = parts[1] if len(parts) > 1 else ''

            # 找到 AI 总结结束位置（下一个 ## 或 ---)
            ai_end_markers = ['---', '\n## ']
            ai_end_pos = len(after_ai)
            for marker in ai_end_markers:
                pos = after_ai.find(marker)
                if pos != -1 and pos < ai_end_pos:
                    ai_end_pos = pos

            ai_content = after_ai[:ai_end_pos]
            remaining = after_ai[ai_end_pos:]

            # 移除 remaining 开头的分隔线（避免双横线）
            remaining = remaining.lstrip()
            if remaining.startswith('---'):
                remaining = remaining[3:].lstrip()

            # 转换 AI 总结部分
            if MARKDOWN_AVAILABLE:
                ai_html = markdown.markdown(ai_content, extensions=['extra', 'nl2br'])
            else:
                ai_html = self._simple_markdown_to_html(ai_content)

            # AI 总结区域
            ai_summary_html = f'''<div class="ai-summary">
                <h2>🤖 今日AI智能总结</h2>
                {ai_html}
            </div>'''
            remaining_content = before_ai + remaining

        # 转换其余内容
        if MARKDOWN_AVAILABLE:
            body_html = markdown.markdown(remaining_content, extensions=['extra', 'nl2br', 'tables'])
        else:
            body_html = self._simple_markdown_to_html(remaining_content)

        # 插入 AI 总结到正确位置
        if ai_summary_html:
            # 在第一个 <h2> 或 <hr> 之前插入
            insert_markers = ['<h2>', '<hr>']
            insert_pos = len(body_html)
            for marker in insert_markers:
                pos = body_html.find(marker)
                if pos != -1 and pos < insert_pos:
                    insert_pos = pos
            body_html = body_html[:insert_pos] + ai_summary_html + body_html[insert_pos:]

        # 修复链接（移除内部锚点的 target="_blank"）
        import re
        body_html = re.sub(r'<a href="#([^"]+)" target="_blank">', r'<a href="#\1">', body_html)

        # 为关键词统计表格添加特殊类名
        body_html = re.sub(
            r'(<h2>📊 关键词统计</h2>.*?<table)',
            r'\1 class="keywords-table"',
            body_html,
            flags=re.DOTALL
        )

        # 完整的 HTML
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>科研日报 - {date_str}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
            line-height: 1.8;
            color: #2c3e50;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 15px;
            font-size: 16px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 35px;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        /* 标题优化 */
        h1 {{
            color: #1a202c;
            font-size: 2em;
            border-bottom: 4px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 25px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        h2 {{
            color: #2d3748;
            font-size: 1.5em;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-left: 15px;
            border-left: 5px solid #667eea;
            font-weight: 600;
        }}

        h3 {{
            color: #4a5568;
            font-size: 1.25em;
            margin-top: 28px;
            margin-bottom: 14px;
            font-weight: 600;
        }}

        /* 分类浏览折叠功能 */
        details {{
            margin: 20px 0;
            border-radius: 8px;
            overflow: hidden;
        }}

        details summary {{
            cursor: pointer;
            padding: 15px 20px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            color: #2d3748;
            font-size: 1.25em;
            font-weight: 600;
            text-align: right;
            direction: rtl;
            border-right: 5px solid #667eea;
            transition: all 0.3s ease;
            list-style: none;
            user-select: none;
        }}

        details summary * {{
            direction: ltr;
        }}

        details summary::-webkit-details-marker {{
            display: none;
        }}

        details summary::before {{
            content: '▶';
            display: inline-block;
            margin-left: 10px;
            transition: transform 0.3s ease;
            font-size: 0.8em;
        }}

        details[open] summary::before {{
            transform: rotate(90deg);
        }}

        details summary:hover {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}

        details[open] summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-right-color: white;
        }}

        details .details-content {{
            padding: 20px;
            background: white;
            border: 1px solid #e9ecef;
            border-top: none;
        }}

        h4 {{
            color: #718096;
            font-size: 1.1em;
            margin-top: 22px;
            margin-bottom: 12px;
            font-weight: 600;
        }}

        p {{
            margin-bottom: 16px;
            line-height: 1.8;
        }}

        blockquote {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-left: 4px solid #667eea;
            padding: 18px 22px;
            margin: 22px 0;
            border-radius: 8px;
            color: #4a5568;
            font-size: 0.95em;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}

        blockquote p {{
            margin-bottom: 8px;
        }}

        blockquote p:last-child {{
            margin-bottom: 0;
        }}

        blockquote em {{
            font-style: normal;
            color: #718096;
            font-size: 0.9em;
        }}

        blockquote a {{
            color: #667eea;
            font-weight: 500;
            border-bottom: 1px solid rgba(102, 126, 234, 0.3);
        }}

        blockquote a:hover {{
            color: #764ba2;
            border-bottom-color: #764ba2;
        }}

        /* 顶部署名（居右） */
        .powered-by-top {{
            text-align: right;
            font-size: 0.85em;
            color: #718096;
            font-style: italic;
            margin: 12px 0;
            padding-right: 5px;
        }}

        .powered-by-top a {{
            color: #667eea;
            font-weight: 500;
            border-bottom: 1px solid rgba(102, 126, 234, 0.3);
        }}

        .powered-by-top a:hover {{
            color: #764ba2;
            border-bottom-color: #764ba2;
        }}

        /* AI 总结区域优化 */
        .ai-summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 28px;
            border-radius: 16px;
            margin: 30px 0;
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.35);
            position: relative;
            overflow: hidden;
        }}

        .ai-summary::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            pointer-events: none;
        }}

        .ai-summary h2 {{
            color: white;
            border-left: none;
            border-right: none;
            margin-top: 0;
            margin-bottom: 18px;
            padding-left: 15px;
            padding-right: 0;
            text-align: left;
            direction: ltr;
        }}

        .ai-summary h3 {{
            color: #f0f0f0;
            margin-top: 18px;
            border-right: 3px solid rgba(255,255,255,0.5);
            padding-right: 12px;
            padding-left: 0;
            text-align: right;
            direction: rtl;
        }}

        .ai-summary h3 * {{
            direction: ltr;
        }}

        .ai-summary blockquote {{
            background: rgba(255,255,255,0.15);
            border-left-color: white;
            color: white;
            backdrop-filter: blur(10px);
        }}

        .ai-summary p {{
            color: white;
        }}

        .ai-summary strong {{
            color: #fff;
            font-weight: 600;
        }}

        ul, ol {{
            margin-left: 28px;
            margin-bottom: 18px;
        }}

        li {{
            margin-bottom: 12px;
            line-height: 1.8;
        }}

        /* 链接优化 */
        a {{
            color: #667eea;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: all 0.3s ease;
            font-weight: 500;
        }}

        a:hover {{
            border-bottom-color: #667eea;
            color: #764ba2;
        }}

        /* 表格优化 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border-radius: 10px;
            overflow: hidden;
        }}

        th, td {{
            border: 1px solid #e2e8f0;
            padding: 14px 18px;
            text-align: left;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            font-size: 0.95em;
        }}

        tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        tr:hover {{
            background: #e9ecef;
            transition: background 0.3s ease;
        }}

        /* 关键词统计表格特殊样式（更紧凑） */
        .keywords-table {{
            font-size: 0.9em;
            max-width: 600px;
        }}

        .keywords-table th,
        .keywords-table td {{
            padding: 10px 14px;
        }}

        .keywords-table th {{
            font-size: 0.9em;
        }}

        hr {{
            border: none;
            border-top: 2px solid #e2e8f0;
            margin: 40px 0;
        }}

        strong {{
            color: #2d3748;
            font-weight: 600;
        }}

        code {{
            background: #f1f5f9;
            padding: 3px 8px;
            border-radius: 5px;
            font-family: "SF Mono", Monaco, Consolas, "Courier New", monospace;
            font-size: 0.9em;
            color: #e53e3e;
        }}

        /* 美化滚动条 */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb {{
            background: #667eea;
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #764ba2;
        }}

        /* 移动端优化 */
        @media (max-width: 768px) {{
            body {{
                padding: 8px;
                font-size: 15px;
            }}

            .container {{
                padding: 22px 18px;
                border-radius: 12px;
            }}

            h1 {{
                font-size: 1.6em;
                padding-bottom: 12px;
                margin-bottom: 20px;
            }}

            h2 {{
                font-size: 1.3em;
                margin-top: 30px;
                padding-left: 12px;
            }}

            h3 {{
                font-size: 1.15em;
            }}

            h4 {{
                font-size: 1.05em;
            }}

            blockquote {{
                padding: 14px 16px;
                margin: 18px 0;
            }}

            .ai-summary {{
                padding: 20px;
                margin: 22px 0;
            }}

            .ai-summary-header {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .powered-by {{
                margin-left: 0;
                margin-top: 8px;
            }}

            table {{
                font-size: 0.85em;
            }}

            th, td {{
                padding: 10px 12px;
            }}

            .keywords-table {{
                font-size: 0.8em;
            }}

            .keywords-table th,
            .keywords-table td {{
                padding: 8px 10px;
            }}

            ul, ol {{
                margin-left: 22px;
            }}
        }}

        /* 超小屏幕 */
        @media (max-width: 480px) {{
            body {{
                font-size: 14px;
                padding: 5px;
            }}

            .container {{
                padding: 18px 14px;
            }}

            h1 {{
                font-size: 1.4em;
            }}

            h2 {{
                font-size: 1.2em;
            }}

            .ai-summary {{
                padding: 16px;
            }}

            .powered-by {{
                font-size: 0.7em;
            }}
        }}

        /* 平滑滚动 */
        html {{
            scroll-behavior: smooth;
        }}

        /* 提高可点击区域 */
        @media (pointer: coarse) {{
            a {{
                padding: 4px 0;
                display: inline-block;
            }}
        }}

        /* 打印优化 */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
                max-width: 100%;
            }}

            .ai-summary {{
                background: #f5f5f5;
                color: black;
                box-shadow: none;
            }}

            .ai-summary h2,
            .ai-summary h3,
            .ai-summary p,
            .ai-summary strong {{
                color: black;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {body_html}
    </div>
</body>
</html>"""

        return html

    def _process_details_tags(self, md_content: str) -> str:
        """处理 details 标签：提取、转换内部 markdown、重新包装"""
        import re

        # 匹配 <details>...</details> 整个块
        details_pattern = r'<details>\s*<summary([^>]*)>(.*?)</summary>\s*(?:<div[^>]*>)?\s*(.*?)\s*(?:</div>)?\s*</details>'

        def replace_details(match):
            summary_attrs = match.group(1)  # summary 的属性（如 style=""）
            summary_content = match.group(2)  # summary 的内容
            inner_markdown = match.group(3)  # details 内部的 markdown 内容

            # 转换内部 markdown 为 HTML
            if MARKDOWN_AVAILABLE:
                inner_html = markdown.markdown(inner_markdown.strip(), extensions=['extra', 'nl2br', 'tables'])
            else:
                inner_html = self._simple_markdown_to_html(inner_markdown.strip())

            # 重新组装成完整的 details HTML
            details_html = f'''<details>
<summary{summary_attrs}>{summary_content}</summary>
<div class="details-content">
{inner_html}
</div>
</details>'''

            return details_html

        # 替换所有 details 块
        processed = re.sub(details_pattern, replace_details, md_content, flags=re.DOTALL)

        return processed

    def _simple_markdown_to_html(self, md_text: str) -> str:
        """简化的 markdown 转 HTML（当 markdown 库不可用时）"""
        import re

        html = md_text

        # 标题
        html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # 粗体
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # 链接（移除内部锚点的 target）
        html = re.sub(r'\[(.+?)\]\((#.+?)\)', r'<a href="\2">\1</a>', html)
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', html)

        # 列表
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>\n)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)

        # 引用
        lines = html.split('\n')
        in_quote = False
        processed = []
        quote_lines = []

        for line in lines:
            if line.startswith('> '):
                if not in_quote:
                    in_quote = True
                quote_lines.append(line[2:])
            else:
                if in_quote:
                    processed.append('<blockquote>' + '<br>'.join(quote_lines) + '</blockquote>')
                    quote_lines = []
                    in_quote = False
                processed.append(line)

        if in_quote:
            processed.append('<blockquote>' + '<br>'.join(quote_lines) + '</blockquote>')

        html = '\n'.join(processed)

        # 段落
        html = re.sub(r'\n\n+', '</p><p>', html)
        html = '<p>' + html + '</p>'

        # 分隔线
        html = html.replace('---', '<hr>')

        return html
    
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
