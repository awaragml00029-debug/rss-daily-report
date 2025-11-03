#!/bin/bash
set -e

# 跨仓库推送脚本
# 将生成的报告推送到 Hugo 仓库和备份仓库

echo "🚀 开始跨仓库推送..."

# 检查必需的环境变量
if [ -z "$B_ACCOUNT_TOKEN" ]; then
    echo "❌ 错误: 未设置 B_ACCOUNT_TOKEN 环境变量"
    exit 1
fi

# 从 config.yaml 读取配置（或从环境变量）
HUGO_REPO="${HUGO_REPO:-ixxmu/ixxmu.github.io.source}"
HUGO_BRANCH="${HUGO_BRANCH:-FigureYY}"
HUGO_PATH="${HUGO_PATH:-content/posts/DailyReports}"

BACKUP_REPO="${BACKUP_REPO:-ixxmu/duty_bk}"
BACKUP_BRANCH="${BACKUP_BRANCH:-main}"
BACKUP_PATH="${BACKUP_PATH:-DailyReports/reports}"

STATIC_REPO="${STATIC_REPO:-ixxmu/FigureYa_blog}"
STATIC_BRANCH="${STATIC_BRANCH:-main}"

# 检查文件是否存在
if [ ! -f "temp_hugo/daily-*.md" ] && [ ! -f temp_hugo/latest.html ]; then
    echo "⚠️  未找到要推送的文件"
    exit 0
fi

# 配置 Git
git config --global user.name "GitHub Actions Bot"
git config --global user.email "actions@github.com"

# ============================================
# 推送到 Hugo 仓库
# ============================================
echo ""
echo "📝 推送到 Hugo 仓库..."

# 克隆 Hugo 仓库
HUGO_CLONE_DIR="temp_hugo_repo"
rm -rf "$HUGO_CLONE_DIR"

echo "克隆 Hugo 仓库: $HUGO_REPO (分支: $HUGO_BRANCH)"
git clone --depth=1 --branch="$HUGO_BRANCH" \
    "https://${B_ACCOUNT_TOKEN}@github.com/${HUGO_REPO}.git" \
    "$HUGO_CLONE_DIR"

# 创建目标目录
mkdir -p "$HUGO_CLONE_DIR/$HUGO_PATH"

# 复制 markdown 文件
if ls temp_hugo/daily-*.md 1> /dev/null 2>&1; then
    cp temp_hugo/daily-*.md "$HUGO_CLONE_DIR/$HUGO_PATH/"
    echo "✅ Markdown 文件已复制到 Hugo 仓库"
fi

# 复制 HTML 文件到 static 目录
# Hugo 构建时会自动将 static/ 下的文件复制到 public/
# 然后 Hugo Actions 会全量推送 public/ 到静态网站仓库
if [ -f "temp_hugo/latest.html" ]; then
    mkdir -p "$HUGO_CLONE_DIR/static"
    cp temp_hugo/latest.html "$HUGO_CLONE_DIR/static/"
    echo "✅ HTML 文件已复制到 Hugo 仓库的 static/ 目录"
    echo "   (Hugo 构建后会自动推送到静态网站仓库)"
fi

# 提交并推送
cd "$HUGO_CLONE_DIR"
git add .

if git diff --staged --quiet; then
    echo "ℹ️  Hugo 仓库没有变化，跳过推送"
else
    DATE=$(date +%Y-%m-%d)
    git commit -m "📝 Add daily report $DATE"
    git push origin "$HUGO_BRANCH"
    echo "✅ 已推送到 Hugo 仓库"
fi

cd ..

# ============================================
# 推送到备份仓库
# ============================================
echo ""
echo "💾 推送到备份仓库..."

# 克隆备份仓库
BACKUP_CLONE_DIR="temp_backup_repo"
rm -rf "$BACKUP_CLONE_DIR"

echo "克隆备份仓库: $BACKUP_REPO (分支: $BACKUP_BRANCH)"
git clone --depth=1 --branch="$BACKUP_BRANCH" \
    "https://${B_ACCOUNT_TOKEN}@github.com/${BACKUP_REPO}.git" \
    "$BACKUP_CLONE_DIR"

# 创建目标目录（按年月分类）
YEAR=$(date +%Y)
MONTH=$(date +%m)
BACKUP_TARGET="$BACKUP_CLONE_DIR/$BACKUP_PATH/$YEAR/$MONTH"
mkdir -p "$BACKUP_TARGET"

# 复制 markdown 文件
if ls temp_hugo/daily-*.md 1> /dev/null 2>&1; then
    cp temp_hugo/daily-*.md "$BACKUP_TARGET/"
    echo "✅ Markdown 文件已复制到备份仓库"
fi

# 提交并推送
cd "$BACKUP_CLONE_DIR"
git add .

if git diff --staged --quiet; then
    echo "ℹ️  备份仓库没有变化，跳过推送"
else
    DATE=$(date +%Y-%m-%d)
    git commit -m "📝 Backup daily report $DATE"
    git push origin "$BACKUP_BRANCH"
    echo "✅ 已推送到备份仓库"
fi

cd ..

# ============================================
# 静态网站仓库由 Hugo Actions 自动处理
# ============================================
# latest.html 已推送到 Hugo 源码仓库的 static/ 目录
# Hugo Actions 会：
#   1. 检测到源码仓库更新
#   2. 运行 Hugo 构建（static/ → public/）
#   3. 全量推送 public/ 到静态网站仓库
# 因此 latest.html 会自动出现在静态网站仓库的根目录
echo ""
echo "ℹ️  latest.html 将由 Hugo Actions 自动推送到静态网站仓库"

# 清理临时目录
echo ""
echo "🧹 清理临时文件..."
rm -rf "$HUGO_CLONE_DIR" "$BACKUP_CLONE_DIR" temp_hugo

echo "✨ 跨仓库推送完成！"
