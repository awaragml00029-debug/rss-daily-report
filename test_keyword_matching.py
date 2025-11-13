#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
关键词匹配功能测试
"""

import sys
import re
from typing import List

class KeywordMatcher:
    """复制了修复后的关键词匹配逻辑"""

    def __init__(self, keywords: List[str], exclude_keywords: List[str]):
        self.keywords = keywords
        self.exclude_keywords = exclude_keywords

    def filter_by_keywords(self, title: str) -> List[str]:
        """根据关键词筛选，返回匹配的关键词列表"""
        if not title:
            return []

        # 检查排除关键词（优先级最高）
        for exclude_kw in self.exclude_keywords:
            if self._match_keyword(exclude_kw, title):
                return []  # 如果匹配排除词，直接返回空列表

        # 检查匹配关键词
        matched = []
        for keyword in self.keywords:
            if self._match_keyword(keyword, title):
                matched.append(keyword)

        return matched

    def _match_keyword(self, keyword: str, text: str) -> bool:
        """智能关键词匹配"""
        if not keyword or not text:
            return False

        # 检测关键词是否包含中文字符
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', keyword))

        # 检测关键词是否包含正则特殊字符
        has_special = bool(re.search(r'[.\-+*?^\[\](){}|\\]', keyword))

        if has_chinese:
            # 中文关键词：使用宽松匹配（允许字符间插入）
            pattern = '.*'.join(list(keyword))
            return bool(re.search(pattern, text, re.IGNORECASE))
        elif has_special or ' ' in keyword:
            # 包含特殊字符或空格的关键词
            try:
                escaped = re.escape(keyword).replace(r'\-', '-').replace(r'\ ', r'\s+')
                pattern = r'\b' + escaped + r'\b'
                return bool(re.search(pattern, text, re.IGNORECASE))
            except re.error:
                return keyword.lower() in text.lower()
        else:
            # 纯英文/数字关键词：使用单词边界匹配
            pattern = r'\b' + re.escape(keyword) + r'\b'
            return bool(re.search(pattern, text, re.IGNORECASE))


def run_tests():
    """运行测试用例"""

    # 准备关键词列表（从config.yaml中选取部分关键词）
    keywords = [
        "TME", "tumor", "cancer", "scRNA", "scDNA", "scATAC",
        "Scanpy", "histone", "单细胞", "肿瘤", "RNA-seq",
        "single-cell", "tumor microenvironment"
    ]

    exclude_keywords = [
        "advertisement", "广告", "recruitment", "聘", "correction"
    ]

    matcher = KeywordMatcher(keywords, exclude_keywords)

    # 测试用例
    test_cases = [
        {
            "title": "New research finds no clear link between acetaminophen (Tylenol) and autism",
            "expected_match": False,
            "should_match": [],
            "description": "用户报告的问题：不应该匹配任何关键词"
        },
        {
            "title": "TME analysis reveals immune landscape in cancer",
            "expected_match": True,
            "should_match": ["TME", "cancer"],
            "description": "应该匹配 TME 和 cancer"
        },
        {
            "title": "Single-cell RNA-seq analysis of tumor samples",
            "expected_match": True,
            "should_match": ["single-cell", "RNA-seq", "tumor"],
            "description": "应该匹配 single-cell, RNA-seq, tumor"
        },
        {
            "title": "scRNA-seq analysis using Scanpy",
            "expected_match": True,
            "should_match": ["scRNA", "Scanpy"],
            "description": "应该匹配 scRNA 和 Scanpy"
        },
        {
            "title": "单细胞测序技术在肿瘤研究中的应用",
            "expected_match": True,
            "should_match": ["单细胞", "肿瘤"],
            "description": "应该匹配中文关键词"
        },
        {
            "title": "Histone modifications in cancer cells",
            "expected_match": True,
            "should_match": ["histone", "cancer"],
            "description": "应该匹配 histone 和 cancer"
        },
        {
            "title": "Job recruitment advertisement for TME research position",
            "expected_match": False,
            "should_match": [],
            "description": "包含排除词 advertisement 和 recruitment，应该被过滤"
        },
        {
            "title": "招聘生信工程师：单细胞分析",
            "expected_match": False,
            "should_match": [],
            "description": "包含排除词'聘'，应该被过滤"
        },
        {
            "title": "scATAC-seq reveals chromatin accessibility",
            "expected_match": True,
            "should_match": ["scATAC"],
            "description": "应该匹配 scATAC"
        },
        {
            "title": "The ultimate guide to cancer treatment",
            "expected_match": True,
            "should_match": ["cancer"],
            "description": "应该只匹配 cancer，不应该误匹配 TME（ultimate 中包含 t,m,e）"
        }
    ]

    # 运行测试
    print("=" * 80)
    print("关键词匹配功能测试")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        title = test["title"]
        matched_keywords = matcher.filter_by_keywords(title)

        print(f"测试 {i}: {test['description']}")
        print(f"  标题: {title}")
        print(f"  匹配结果: {matched_keywords if matched_keywords else '(无匹配)'}")

        # 验证结果
        if test["expected_match"]:
            # 应该有匹配
            if matched_keywords:
                # 检查是否匹配了预期的关键词
                is_correct = all(kw in matched_keywords for kw in test["should_match"])
                if is_correct:
                    print(f"  ✅ 通过 - 正确匹配了关键词")
                    passed += 1
                else:
                    print(f"  ❌ 失败 - 预期匹配 {test['should_match']}")
                    failed += 1
            else:
                print(f"  ❌ 失败 - 预期有匹配，实际无匹配")
                failed += 1
        else:
            # 不应该有匹配
            if not matched_keywords:
                print(f"  ✅ 通过 - 正确地没有匹配")
                passed += 1
            else:
                print(f"  ❌ 失败 - 预期无匹配，实际匹配了 {matched_keywords}")
                failed += 1

        print()

    # 总结
    print("=" * 80)
    print(f"测试总结: 通过 {passed}/{len(test_cases)}, 失败 {failed}/{len(test_cases)}")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
