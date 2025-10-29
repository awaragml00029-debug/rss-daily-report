# 项目结构说明

```
rss-daily-report/
│
├── .github/
│   └── workflows/
│       └── generate-report.yml        # GitHub Actions 工作流配置
│
├── reports/                           # 报告输出目录（自动生成）
│   └── 2025/
│       ├── 10/
│       │   ├── daily-2025-10-28.md   # 每日报告
│       │   └── daily-2025-10-29.md
│       └── monthly-2025-10.md         # 月度报告
│
├── scripts/
│   └── generate_report.py             # 主程序脚本
│
├── .gitignore                         # Git 忽略文件配置
├── CHANGELOG.md                       # 更新日志
├── CONTRIBUTING.md                    # 贡献指南
├── LICENSE                            # MIT 许可证
├── README.md                          # 项目说明（主文档）
├── SETUP_GUIDE.md                     # 详细设置指南
├── config.yaml                        # 配置文件（需要自定义）
├── config.example.yaml                # 配置文件示例
├── requirements.txt                   # Python 依赖
└── test.sh                            # 本地测试脚本
```

## 📁 目录说明

### `.github/workflows/`
包含 GitHub Actions 的自动化工作流配置。

**generate-report.yml**
- 定时任务：每天 23:00（北京时间）自动运行
- 支持手动触发（可指定日期或生成月报）
- 自动提交生成的报告到仓库

### `reports/`
存放生成的 Markdown 报告。

**结构**：
- `{year}/` - 年份目录
  - `{month}/` - 月份目录
    - `daily-{date}.md` - 每日报告
  - `monthly-{year}-{month}.md` - 月度报告

**示例**：
```
reports/
├── 2025/
│   ├── 10/
│   │   ├── daily-2025-10-01.md
│   │   ├── daily-2025-10-02.md
│   │   └── ...
│   ├── 11/
│   │   └── ...
│   ├── monthly-2025-10.md
│   └── monthly-2025-11.md
└── 2026/
    └── ...
```

### `scripts/`
包含核心 Python 脚本。

**generate_report.py**
- 主程序入口
- 从 Google Sheets 读取数据
- 执行关键词筛选
- 生成 Markdown 报告
- 支持命令行参数：
  - `--date YYYY-MM-DD` - 生成指定日期的日报
  - `--monthly YYYY-MM` - 生成指定月份的月报
  - `--config path/to/config.yaml` - 指定配置文件路径

### 配置文件

**config.yaml**
- 主配置文件，需要根据实际情况修改
- 包含：
  - Google Sheets 连接信息
  - 关键词列表（支持正则表达式）
  - 排除关键词
  - 输出路径配置
  - 月报生成规则

**config.example.yaml**
- 配置文件示例
- 包含详细的注释说明
- 首次使用时可以复制为 config.yaml

### 文档文件

**README.md**
- 项目主文档
- 包含快速开始指南
- 功能特性介绍
- 使用说明

**SETUP_GUIDE.md**
- 详细的设置指南
- 图文并茂的步骤说明
- Google Cloud Platform 配置
- GitHub Actions 设置
- 常见问题排查

**CHANGELOG.md**
- 版本更新记录
- 按语义化版本组织
- 记录新功能、修复和变更

**CONTRIBUTING.md**
- 贡献指南
- 代码规范
- 提交流程
- 行为准则

**LICENSE**
- MIT 开源许可证

### 其他文件

**requirements.txt**
- Python 依赖包列表
- 使用 `pip install -r requirements.txt` 安装

**test.sh**
- 本地测试脚本
- 检查环境配置
- 运行测试生成报告

**.gitignore**
- Git 版本控制忽略文件
- 排除敏感文件（如凭证）
- 排除临时文件

## 🔐 敏感文件（不应提交到 Git）

以下文件包含敏感信息，**绝对不要**提交到 Git：

- `credentials.json` - Google API 凭证
- `service-account.json` - 服务账号密钥
- `.env` - 环境变量文件
- 任何包含真实 API 密钥的文件

## 📝 使用流程

1. **首次设置**：
   - Fork 仓库
   - 按照 SETUP_GUIDE.md 配置 Google API
   - 修改 config.yaml
   - 在 GitHub 设置 Secrets

2. **日常使用**：
   - GitHub Actions 自动运行
   - 每天生成新报告
   - 自动提交到仓库

3. **手动操作**：
   - 在 Actions 页面手动触发
   - 或在本地运行 test.sh

4. **调整配置**：
   - 修改 config.yaml 中的关键词
   - 提交到 GitHub
   - 下次运行时生效

## 🚀 快速上手

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/rss-daily-report.git
cd rss-daily-report

# 2. 复制配置文件
cp config.example.yaml config.yaml

# 3. 编辑配置
vim config.yaml  # 修改配置

# 4. 设置环境变量
export GOOGLE_CREDENTIALS='...'
export SHEET_ID='...'

# 5. 运行测试
./test.sh

# 6. 查看生成的报告
ls reports/
```

## 📚 相关文档

- [README.md](README.md) - 项目说明
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - 设置指南
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南
- [CHANGELOG.md](CHANGELOG.md) - 更新日志
