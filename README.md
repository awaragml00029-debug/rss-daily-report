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

## 🤖 AI 开发指南

> 本章节为 AI 助手（如 Claude Code）提供项目架构和设计决策的快速参考，帮助快速理解代码库并高效添加新功能。

### 📐 项目架构概览

#### 核心文件职责

```
scripts/generate_report.py     # 主脚本（1500+ 行）
├── BioinfoReportGenerator     # 核心类
│   ├── connect_sheet()        # 连接 Google Sheets，自动清理15天前数据
│   ├── generate_daily_report()        # 生成 Markdown 日报
│   ├── generate_html_report()         # 生成 HTML 静态页
│   ├── generate_hugo_report()         # 生成带 Hugo Front Matter 的报告
│   ├── _markdown_to_html()            # Markdown → HTML 转换（关键！）
│   ├── _process_details_tags()        # 处理折叠标签（修复格式问题）
│   ├── generate_ai_summary_for_source() # 调用 Gemini API 生成 AI 总结
│   └── cleanup_old_data()             # 清理 Google Sheet 旧数据

config.yaml                    # 配置文件
├── google_sheets              # Google Sheets 连接配置
├── keywords / exclude_keywords # 关键词过滤
├── gemini                     # AI 总结配置（model, prompt, API URL）
├── hugo                       # Hugo 博客集成配置
├── backup                     # 备份仓库配置
└── static_site                # 静态网站配置

scripts/push_to_repos.sh       # 多仓库推送脚本（Hugo源码、备份、静态站点）
```

#### 数据流向

```
Google Sheets (RSS数据)
    ↓ (connect_sheet + cleanup_old_data)
Python 处理 (关键词过滤、AI总结)
    ↓ (generate_daily_report)
Markdown 日报 (带折叠标签)
    ├→ Hugo Front Matter → Hugo 源码仓库 (ixxmu/ixxmu.github.io.source)
    ├→ 备份 → 备份仓库 (ixxmu/duty_bk)
    └→ HTML 转换 (_process_details_tags) → 静态网站 (ixxmu/FigureYa_blog)
```

### 🎯 重要设计决策

#### 1. Markdown vs HTML 分离处理

**为什么**：
- **Markdown 日报** 用于 Hugo 博客，Hugo 会自己渲染成 HTML
- **HTML 静态页** 是独立的 `latest.html`，需要完整的 HTML 结构

**实现**：
- `generate_daily_report()` 生成纯 Markdown（带 HTML 折叠标签）
- `generate_html_report()` 调用 `_markdown_to_html()` 转换为完整 HTML

#### 2. 折叠功能的实现（重要！）

**问题**：markdown 库的 `extra` 扩展无法正确处理 `<details>` 标签内的 markdown 内容。

**错误方式**：
```python
# ❌ 直接转换，内部 markdown 不会被解析
md_content = "<details><summary>标题</summary>\n**粗体**\n</details>"
html = markdown.markdown(md_content, extensions=['extra'])
# 结果：**粗体** 以纯文本显示
```

**正确方式**（当前实现）：
```python
# ✅ 提取 → 转换 → 重新包装
def _process_details_tags(md_content):
    # 1. 提取 <details> 块及内部 markdown
    # 2. 单独转换内部 markdown 为 HTML
    # 3. 重新包装成 <details><summary>...</summary><div>HTML</div></details>
```

**关键代码**：`generate_report.py:1365` 的 `_process_details_tags()` 方法

#### 3. 多仓库推送策略

**三个目标仓库**：
1. **Hugo 源码** (`ixxmu/ixxmu.github.io.source`, 分支 `FigureYY`)
   - 推送：Markdown 日报 + Hugo Front Matter
   - 路径：`content/posts/DailyReports/`

2. **备份仓库** (`ixxmu/duty_bk`, 分支 `main`)
   - 推送：纯 Markdown 日报
   - 路径：`DailyReports/reports/{year}/{month}/`

3. **静态网站** (`ixxmu/FigureYa_blog`, 分支 `main`)
   - 推送：`latest.html` 静态页面
   - 路径：根目录

**认证**：使用 B 账号的 Personal Access Token (`B_ACCOUNT_TOKEN`)

#### 4. AI 总结的位置和样式

**位置**：在"分类浏览"之前，顶部统计信息之后

**为什么**：用户最关心的是总结，应该放在前面

**实现**：
- Markdown：正常的 `## 🤖 今日AI智能总结` + 子标题（h3）居右
- HTML：特殊的 `.ai-summary` div，紫色渐变背景

#### 5. 数据清理策略

**自动清理**：连接 Google Sheet 后自动删除 15 天前的数据

**为什么**：
- 防止 Sheet 堆积几千条数据
- 提高读取速度
- 保持数据清洁

**实现**：`cleanup_old_data(days=15)` 在 `connect_sheet()` 中自动调用

### 🛠️ 常见开发场景

#### 场景1：修改 AI 总结的 prompt

**位置**：`config.yaml` 的 `gemini.prompt_template`

**注意**：
- 保持变量 `{source_name}` 不变
- 字数限制在 `max_tokens` 中设置
- 测试时可以降低 `max_items_per_source` 以节省成本

#### 场景2：添加新的折叠区域

**步骤**：
1. **Markdown 生成**：添加 `<details><summary>标题</summary><div markdown="1">内容</div></details>`
2. **HTML 转换**：自动被 `_process_details_tags()` 处理，无需额外代码

**样式**：
- **居右标题**：在 `<summary>` 添加 `style="text-align: right; direction: rtl; ..."`
- **居左标题**：不添加 style 属性（如"更多内容"部分）

#### 场景3：调整 HTML 样式

**位置**：`generate_report.py:847` 的 `<style>` 标签内

**关键 CSS 类**：
- `.ai-summary` - AI 总结区域（紫色渐变）
- `details summary` - 折叠标题样式
- `.details-content` - 折叠内容容器
- `.keywords-table` - 关键词统计表格
- `.powered-by-top` - 顶部署名

#### 场景4：修改运行时间

**位置**：`.github/workflows/generate-report.yml:10`

**计算方法**：
- 北京时间（UTC+8）→ UTC 时间：减去 8 小时
- 例如：北京时间 05:30 = UTC 21:30
- cron 格式：`'30 21 * * *'`（分 时 日 月 周）

### ⚠️ 常见陷阱

#### 1. ❌ markdown 库无法处理 `<details>` 内的 markdown

**问题**：
```python
# 这样不行！
md = "<details><summary>标题</summary>\n**粗体**\n</details>"
html = markdown.markdown(md, extensions=['extra'])
# 结果：**粗体** 不会被转换
```

**解决**：使用 `_process_details_tags()` 方法先提取、转换、再包装

#### 2. ❌ 内联样式 vs CSS 类的选择

**Markdown 日报（Hugo）**：
- ✅ 使用内联 `style=""` 属性（Hugo 会保留）
- ❌ 不要依赖外部 CSS 类

**HTML 静态页**：
- ✅ 使用 CSS 类（`<style>` 标签内定义）
- ✅ 可以使用内联样式覆盖

#### 3. ❌ Git push 分支命名要求

**要求**：分支必须以 `claude/` 开头，否则 push 会返回 403 错误

**正确**：`claude/add-feature-xyz`
**错误**：`feature/add-xyz`

#### 4. ❌ 删除 Google Sheet 行的顺序

**错误**：从前往后删除（索引会变化）
```python
for idx in rows_to_delete:  # [2, 5, 8]
    sheet.delete_rows(idx)  # 删除第2行后，原来的第5行变成第4行！
```

**正确**：从后往前删除
```python
for idx in reversed(rows_to_delete):  # [8, 5, 2]
    sheet.delete_rows(idx)  # 不会影响前面的索引
```

#### 5. ❌ 环境变量覆盖 config.yaml

**优先级**：`环境变量 > config.yaml`

**示例**：
```python
spreadsheet_id = os.getenv('SHEET_ID') or config['google_sheets']['spreadsheet_id']
```

**注意**：GitHub Secrets 会设置为环境变量，优先级更高

### 📝 代码约定

#### 命名规范

- **方法名**：`snake_case`，私有方法以 `_` 开头
- **CSS 类名**：`kebab-case`，如 `.ai-summary`
- **配置键**：`snake_case`，如 `max_items_per_source`

#### 折叠标签结构

```html
<!-- 标准结构 -->
<details>
<summary [style="..."]>标题内容</summary>
<div class="details-content" markdown="1">

markdown 内容

</div>
</details>
```

**注意**：
- summary 后必须有空行
- div 前后必须有空行
- `markdown="1"` 属性在 Hugo 中有用，但 HTML 转换时会被移除

#### 错误处理原则

- **Google API 调用**：捕获异常，打印警告，不中断流程
- **AI 总结失败**：跳过该来源，继续处理其他
- **Sheet 清理失败**：打印警告，不影响报告生成

### 🚀 快速上手检查清单

开发新功能前，确认你理解了：
- [ ] Markdown 和 HTML 是分开处理的
- [ ] 折叠功能需要先提取、转换、再包装
- [ ] 有三个推送目标（Hugo 源码、备份、静态站点）
- [ ] 环境变量优先级高于 config.yaml
- [ ] Google Sheet 会自动清理 15 天前的数据

**需要帮助？**
- 参考 `generate_report.py` 中的注释
- 查看 `config.yaml` 的完整配置示例
- 阅读 `HUGO_SETUP.md` 了解 Hugo 集成细节

---

**祝开发顺利！🎉**

## 🔀 Git 工作流指南

> 当使用 Claude Code 或其他 AI 助手开发功能时，如何正确合并分支到 main。

### 问题背景

Claude Code 环境和你的本地终端是**两个独立的 git 工作区**，这会导致合并流程出现混淆。

### 核心要点

#### 1. 权限限制
- ✅ Claude Code 可以 push 到 `claude/` 开头的分支
- ❌ Claude Code 无法直接 push 到 `main` 分支（会返回 403 错误）
- 📌 **结论**：Claude 的修改会自动推送到 `claude/xxx` 分支，需要你手动合并到 main

#### 2. 常见错误

##### 错误 1：合并本地不存在的分支
```bash
# ❌ 错误：你本地没有 claude/xxx 分支
git merge claude/add-ai-summary-feature-xxx
# 结果：Already up to date

# ✅ 正确：合并远程分支
git fetch origin  # 先拉取远程分支
git merge origin/claude/add-ai-summary-feature-xxx
```

##### 错误 2：分支分叉导致 push 被拒绝
```bash
# 现象
! [rejected] main -> main (non-fast-forward)
Your branch and 'origin/main' have diverged

# 原因
# - 远程 main 有新提交（如 GitHub Actions 自动生成的报告）
# - 本地 main 也有新提交（你的合并）
# - 两者分叉了

# ✅ 解决方案
git pull origin main --no-rebase  # 先拉取并合并远程改动
git push origin main              # 再推送
```

##### 错误 3：忘记 fetch 远程分支
```bash
# ❌ 直接 merge 可能拿到旧版本
git merge origin/claude/xxx

# ✅ 先 fetch 确保最新
git fetch origin
git merge origin/claude/xxx
```

### 标准操作流程

当 Claude Code 完成开发并推送到 `claude/xxx` 分支后，在**你的本地终端**执行：

```bash
# 1. 切换到 main 分支
git checkout main

# 2. 拉取所有远程更新（包括 claude 分支）
git fetch origin

# 3. 先同步远程 main 的最新改动（避免分叉）
git pull origin main --no-rebase

# 4. 合并 claude 分支
git merge origin/claude/add-ai-summary-feature-xxx -m "Merge: [描述改动内容]"

# 5. 推送到远程 main
git push origin main
```

#### 一行命令版本

```bash
git checkout main && git fetch origin && git pull origin main --no-rebase && git merge origin/claude/[分支名] -m "Merge: [描述]" && git push origin main
```

### 故障排查

#### 问题：`Already up to date` 但实际没合并

**原因**：
- 合并的是本地分支而不是远程分支
- 或者忘记 `git fetch`

**解决**：
```bash
git fetch origin  # 拉取最新的远程分支
git log origin/claude/xxx --oneline -5  # 确认远程分支有新提交
git merge origin/claude/xxx  # 合并远程分支
```

#### 问题：Push 被拒绝 (non-fast-forward)

**原因**：远程 main 有新提交，本地 main 和远程 main 分叉了

**解决**：
```bash
git pull origin main --no-rebase  # 合并远程改动
git push origin main
```

#### 问题：合并后有冲突

**解决**：
```bash
# 1. 查看冲突文件
git status

# 2. 手动编辑冲突文件，解决冲突标记
# <<<<<<< HEAD
# 你的改动
# =======
# 对方的改动
# >>>>>>> origin/claude/xxx

# 3. 标记冲突已解决
git add [冲突文件]

# 4. 完成合并
git commit -m "Merge: resolve conflicts"

# 5. 推送
git push origin main
```

### 最佳实践

1. **定期同步远程**
   ```bash
   git fetch origin  # 每次合并前执行
   ```

2. **检查状态**
   ```bash
   git status  # 确认当前分支和状态
   git log origin/main..HEAD --oneline  # 查看未推送的提交
   ```

3. **使用 --no-rebase**
   - `git pull --no-rebase` 保持提交历史清晰
   - 避免 rebase 导致的历史重写问题

4. **清晰的合并信息**
   ```bash
   # 好的合并信息
   git merge origin/claude/xxx -m "Merge: 优化 Google Sheet 批量删除功能"

   # 不好的合并信息
   git merge origin/claude/xxx  # 使用默认信息
   ```

### 关键对照表

| 问题 | 错误做法 | 正确做法 |
|------|----------|----------|
| 合并远程分支 | `git merge claude/xxx` | `git merge origin/claude/xxx` |
| 分支分叉 | 直接 push | 先 `git pull --no-rebase` 再 push |
| 确保最新 | 只 pull main | `git fetch origin` 拉取所有分支 |
| Claude 推送限制 | 期望 Claude 推送到 main | Claude 只推送到 `claude/` 分支 |

### 完整示例

假设 Claude Code 修复了一个 bug 并推送到 `claude/fix-import-error-abc123`：

```bash
# 在你的终端执行
cd ~/github/rss-daily-report

# 标准流程
git checkout main
git fetch origin
git pull origin main --no-rebase
git merge origin/claude/fix-import-error-abc123 -m "Merge: 修复导入错误和 Python 版本警告"
git push origin main

# 完成！GitHub 上的 main 分支现在包含了所有修复
```

---

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题，请在 GitHub 上提交 Issue。

---

**Happy Reading! 📚**
