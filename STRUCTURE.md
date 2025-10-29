# 📂 项目结构

```
rss-daily-report/
│
├── 📄 核心配置文件
│   ├── config.yaml                  # 主配置（关键词、输出等）
│   ├── requirements.txt             # Python 依赖
│   └── .gitignore                   # Git 忽略规则
│
├── 📜 文档（按优先级）
│   ├── GETTING_STARTED.md          # ⭐ 从这里开始！
│   ├── QUICKSTART.md               # ⭐ 5分钟快速部署
│   ├── README.md                    # 完整文档
│   ├── SETUP.md                     # 详细设置
│   ├── CHECKLIST.md                 # 部署检查清单
│   ├── PROJECT_OVERVIEW.md          # 技术架构
│   ├── FILES.md                     # 文件说明
│   └── STRUCTURE.md                 # 本文件
│
├── 🤖 自动化配置
│   └── .github/
│       └── workflows/
│           └── generate-report.yml  # GitHub Actions 工作流
│
├── 💻 代码文件
│   ├── scripts/
│   │   └── generate_report.py      # 主程序（核心逻辑）
│   └── test.py                      # 本地测试脚本
│
└── 📊 报告目录
    └── reports/
        ├── README.md                # 目录说明
        └── 2025/                    # 按年份组织
            ├── 10/                  # 按月份组织
            │   ├── daily-2025-10-29.md           # 每日报告
            │   └── daily-2025-10-29-example.md   # 示例
            └── monthly-2025-10.md   # 月度报告
```

## 🎯 快速导航

### 我是新手，想快速部署
→ 阅读 [GETTING_STARTED.md](GETTING_STARTED.md)

### 我想了解技术细节
→ 阅读 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### 我想修改配置
→ 编辑 [config.yaml](config.yaml)

### 我想查看示例报告
→ 进入 [reports/2025/10/](reports/2025/10/)

### 我想本地测试
→ 运行 `python test.py --mode mock`

## 📝 重要提示

### ✅ 需要修改的文件
1. `config.yaml` - 配置关键词
2. GitHub Secrets - 添加凭证

### ❌ 不需要修改的文件
- `scripts/generate_report.py` - 除非自定义功能
- `.github/workflows/generate-report.yml` - 除非改时间
- `requirements.txt` - 除非更新依赖

## 🔧 配置流程

1. **Google Cloud 设置**
   - 创建服务账号
   - 下载 JSON 密钥

2. **Google Sheets 设置**
   - 分享给服务账号
   - 获取 Sheet ID

3. **GitHub 设置**
   - 添加 Secrets
   - 启用 Actions

4. **修改配置**
   - 编辑 config.yaml
   - 设置关键词

5. **测试运行**
   - 手动触发或等待定时运行
   - 检查生成的报告

## 📚 相关链接

- [GitHub Actions 文档](https://docs.github.com/actions)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Python gspread 库](https://docs.gspread.org/)

---

**开始使用：[GETTING_STARTED.md](GETTING_STARTED.md)** 🚀
