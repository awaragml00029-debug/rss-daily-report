# RSS Daily Report Generator

🤖 自动从 Google Sheets 读取 RSS 订阅数据，生成精美的每日 Markdown 报告

## ✨ 特性

- 📊 自动从 Google Sheets 读取数据
- 🔍 支持正则表达式关键词匹配
- 📅 每日自动生成报告
- 📈 每月自动生成月度汇总
- 🚀 基于 GitHub Actions 全自动运行
- 📝 生成格式化的 Markdown 报告

## 📁 项目结构

```
rss-daily-report/
├── .github/
│   └── workflows/
│       └── generate-report.yml    # GitHub Actions 工作流
├── reports/                       # 生成的报告目录
│   └── 2025/
│       ├── 10/
│       │   ├── daily-2025-10-29.md
│       │   └── daily-2025-10-30.md
│       └── monthly-2025-10.md
├── scripts/
│   └── generate_report.py        # 主脚本
├── config.yaml                    # 配置文件
├── requirements.txt               # Python 依赖
└── README.md                      # 项目说明
```

## 🚀 快速开始

### 1. 准备 Google Sheets

确保你的 Google Sheets 包含以下列（按顺序）：

| A列 | B列 | C列 | D列 | E列 | F列 | G列 | H列 |
|-----|-----|-----|-----|-----|-----|-----|-----|
| 抓取时间 | 属性 | 适名称 | 适分类 | 标题 | 链接 | 发布时间 | 作者 |

### 2. 创建 Google Service Account

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 **Google Sheets API** 和 **Google Drive API**
4. 创建服务账号：
   - 导航到 "IAM & Admin" > "Service Accounts"
   - 点击 "Create Service Account"
   - 填写服务账号名称和描述
   - 点击 "Create and Continue"
   - 跳过权限设置（可选）
   - 点击 "Done"
5. 创建密钥：
   - 点击新创建的服务账号
   - 转到 "Keys" 标签
   - 点击 "Add Key" > "Create new key"
   - 选择 "JSON" 格式
   - 下载 JSON 文件（妥善保管！）
6. 分享 Google Sheets：
   - 打开你的 Google Sheets
   - 点击 "Share" 按钮
   - 将服务账号的邮箱地址（类似 `xxx@xxx.iam.gserviceaccount.com`）添加为编辑者

### 3. 配置 GitHub 仓库

1. Fork 或创建本仓库
2. 设置 GitHub Secrets：
   - 进入仓库的 "Settings" > "Secrets and variables" > "Actions"
   - 点击 "New repository secret"
   - 添加以下 Secrets：
     
     **GOOGLE_CREDENTIALS**
     ```
     将下载的 JSON 文件的全部内容粘贴到这里
     ```
     
     **SHEET_ID**
     ```
     你的 Google Sheets ID（从 URL 中获取）
     例如：https://docs.google.com/spreadsheets/d/1ABC123XYZ/edit
     则 SHEET_ID 为：1ABC123XYZ
     ```

### 4. 修改配置文件

编辑 `config.yaml`：

```yaml
# Google Sheets 配置
google_sheets:
  spreadsheet_id: "your-spreadsheet-id-here"  # 可以留空，使用 Secret
  sheet_name: "Sheet1"  # 修改为你的工作表名称

# 筛选关键词（支持正则表达式）
keywords:
  - "肿瘤"
  - "测序"
  - "单细胞"
  - "R包"
  # 添加你的关键词

# 排除关键词
exclude_keywords:
  - "广告"
  - "推广"
  # 添加你想排除的词
```

### 5. 启用 GitHub Actions

1. 进入仓库的 "Actions" 标签
2. 如果看到提示，点击 "I understand my workflows, go ahead and enable them"
3. GitHub Actions 会在每天 23:00 (北京时间) 自动运行

## 📝 使用说明

### 自动运行

- **每日报告**：每天 23:00 (UTC+8) 自动生成
- **月度报告**：每月最后一天自动生成

### 手动触发

1. 进入仓库的 "Actions" 标签
2. 选择 "Generate Daily Report" 工作流
3. 点击 "Run workflow"
4. 选择模式和参数：
   - **daily**：生成每日报告
   - **monthly**：生成月度报告
5. 点击 "Run workflow" 确认

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export GOOGLE_CREDENTIALS='{"type": "service_account", ...}'
export SHEET_ID='your-sheet-id'

# 生成每日报告（使用最新数据）
python scripts/generate_report.py --mode daily

# 生成指定日期的报告
python scripts/generate_report.py --mode daily --date 2025-10-29

# 生成月度报告
python scripts/generate_report.py --mode monthly

# 生成指定月份的报告
python scripts/generate_report.py --mode monthly --year 2025 --month 10
```

## 🎯 关键词匹配说明

配置文件中的关键词支持**模糊匹配**，例如：

- `单细胞` 会匹配：
  - 单细胞
  - 单细胞测序
  - 单细胞转录组
  - 单个细胞分析
  
这是因为脚本会自动将关键词转换为正则表达式 `单.*细.*胞`，允许中间插入任意字符。

## 📊 报告示例

### 每日报告

```markdown
# 📅 Daily Report - 2025-10-29

> 生物信息学 RSS 订阅日报
> 筛选关键词：肿瘤、测序、单细胞、R包

---

## 📊 今日概览

- ✅ 命中条目：35
- 📌 关键词命中：52 次

---

## 📰 内容列表

### 1. 单细胞测序在肿瘤研究中的应用

**匹配关键词**：单细胞、测序、肿瘤  
**来源**：生信菜鸟团  
**作者**：张三  
**发布时间**：2025-10-29 14:30  
**链接**：[阅读原文](https://mp.weixin.qq.com/...)

---

## 🏷️ 关键词统计

- 肿瘤：12 次
- 测序：10 次
- 单细胞：15 次
- R包：8 次
```

## 🔧 配置选项

### config.yaml 详解

```yaml
# Google Sheets 配置
google_sheets:
  spreadsheet_id: "your-id"    # Sheets ID
  sheet_name: "Sheet1"          # 工作表名称

# 列索引配置（通常不需要修改）
columns:
  crawl_time: 1      # A列
  attribute: 2       # B列
  source_name: 3     # C列
  category: 4        # D列
  title: 5           # E列
  link: 6            # F列
  publish_time: 7    # G列
  author: 8          # H列

# 筛选关键词（支持模糊匹配）
keywords:
  - "关键词1"
  - "关键词2"

# 排除关键词（标题包含这些词会被过滤）
exclude_keywords:
  - "广告"
  - "推广"

# 输出配置
output:
  daily_path: "reports/{year}/{month}"
  daily_filename: "daily-{date}.md"
  monthly_path: "reports/{year}"
  monthly_filename: "monthly-{year}-{month}.md"
```

## 🐛 故障排查

### 1. GitHub Actions 运行失败

- 检查 Secrets 是否正确设置
- 确认 Google Service Account 有权限访问 Sheets
- 查看 Actions 日志了解具体错误

### 2. 没有生成报告

- 检查 Google Sheets 中是否有当天的数据
- 确认数据的"抓取时间"格式正确
- 查看是否有匹配的关键词

### 3. 关键词不匹配

- 检查关键词拼写是否正确
- 尝试使用更简单的关键词
- 检查是否被排除关键词过滤

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题，请在 GitHub 上提交 Issue。

---

**Happy Reading! 📚**
