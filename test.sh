#!/bin/bash

# RSS Daily Report - 快速测试脚本
# 此脚本用于本地测试，确保一切配置正确

echo "=========================================="
echo "  RSS Daily Report - 快速测试"
echo "=========================================="
echo ""

# 检查 Python 版本
echo "🔍 检查 Python 版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi
echo "✅ Python 版本检查通过"
echo ""

# 检查配置文件
echo "🔍 检查配置文件..."
if [ ! -f "config.yaml" ]; then
    echo "⚠️  未找到 config.yaml，从示例文件复制..."
    cp config.example.yaml config.yaml
    echo "📝 请编辑 config.yaml 填入你的配置"
    exit 0
fi
echo "✅ 配置文件存在"
echo ""

# 安装依赖
echo "📦 安装 Python 依赖..."
pip3 install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi
echo "✅ 依赖安装完成"
echo ""

# 检查环境变量
echo "🔍 检查环境变量..."
if [ -z "$GOOGLE_CREDENTIALS" ]; then
    echo "⚠️  未设置 GOOGLE_CREDENTIALS 环境变量"
    echo ""
    echo "请先设置环境变量："
    echo "  export GOOGLE_CREDENTIALS='你的JSON凭证内容'"
    echo ""
    echo "或者创建 .env 文件："
    echo "  GOOGLE_CREDENTIALS='你的JSON凭证内容'"
    echo "  SHEET_ID='你的Spreadsheet ID'"
    exit 1
fi

if [ -z "$SHEET_ID" ]; then
    echo "⚠️  未设置 SHEET_ID 环境变量"
    echo ""
    echo "请先设置环境变量："
    echo "  export SHEET_ID='your-spreadsheet-id'"
    exit 1
fi

echo "✅ 环境变量检查通过"
echo ""

# 运行测试
echo "=========================================="
echo "  开始运行测试..."
echo "=========================================="
echo ""

python3 scripts/generate_report.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  ✅ 测试成功！"
    echo "=========================================="
    echo ""
    echo "生成的报告在 reports/ 目录下"
    echo ""
    echo "下一步："
    echo "  1. 查看生成的 Markdown 文件"
    echo "  2. 调整 config.yaml 中的关键词"
    echo "  3. 提交到 GitHub 并配置 Actions"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "  ❌ 测试失败"
    echo "=========================================="
    echo ""
    echo "请检查："
    echo "  1. Google Sheets 是否正确共享给服务账号"
    echo "  2. Spreadsheet ID 是否正确"
    echo "  3. 工作表名称是否正确"
    echo "  4. 是否有网络连接"
    echo ""
fi
