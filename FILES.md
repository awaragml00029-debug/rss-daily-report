# 📁 项目文件说明

## 核心文件

### 配置文件
- **config.yaml** - 主配置文件（关键词、输出路径等）
- **.gitignore** - Git 忽略规则
- **requirements.txt** - Python 依赖包

### 代码文件
- **scripts/generate_report.py** - 主程序（核心逻辑）
- **test.py** - 本地测试脚本

### 自动化
- **.github/workflows/generate-report.yml** - GitHub Actions 工作流

## 文档文件

### 快速入门
- **GETTING_STARTED.md** - 入门指南（文档导航）
- **QUICKSTART.md** - 5分钟快速开始
- **SETUP.md** - 详细设置指南
- **CHECKLIST.md** - 部署检查清单

### 详细文档
- **README.md** - 完整项目文档
- **PROJECT_OVERVIEW.md** - 技术架构和原理

## 报告目录

### reports/
生成的报告存放目录，结构如下：

```
reports/
├── README.md                          # 目录说明
├── 2025/
│   ├── 10/
│   │   ├── daily-2025-10-29.md       # 每日报告
│   │   ├── daily-2025-10-29-example.md  # 示例报告
│   │   └── ...
│   ├── 11/
│   │   └── ...
│   ├── monthly-2025-10.md            # 月度报告
│   └── monthly-2025-10-example.md    # 示例月报
└── 2026/
    └── ...
```

## 文件用途说明

| 文件 | 作用 | 需要修改 |
|------|------|----------|
| config.yaml | 配置关键词和输出 | ✅ 是 |
| scripts/generate_report.py | 核心业务逻辑 | ❌ 否（除非自定义） |
| .github/workflows/generate-report.yml | 定时任务配置 | ❌ 否（除非改时间） |
| test.py | 本地测试 | ❌ 否 |
| requirements.txt | 依赖管理 | ❌ 否 |
| README.md | 项目文档 | ❌ 否 |
| QUICKSTART.md | 快速指南 | ❌ 否 |

## 配置优先级

1. GitHub Secrets（最高优先级）
   - GOOGLE_CREDENTIALS
   - SHEET_ID

2. 环境变量
   - GOOGLE_CREDENTIALS
   - SHEET_ID

3. config.yaml
   - google_sheets.spreadsheet_id
   - 其他所有配置

## 修改建议

### 需要经常修改
- `config.yaml` - 关键词、排除词

### 偶尔修改
- `.github/workflows/generate-report.yml` - 运行时间

### 基本不修改
- `scripts/generate_report.py` - 除非需要自定义功能
- `requirements.txt` - 除非更新依赖版本

## 文件大小参考

| 类型 | 大小 |
|------|------|
| 配置文件 | < 5KB |
| 代码文件 | < 50KB |
| 每日报告 | 10-30KB |
| 月度报告 | 100-300KB |
| 文档文件 | 5-20KB |

## 存储建议

- **每日报告**：约 20KB × 365天 = 7.3MB/年
- **月度报告**：约 200KB × 12月 = 2.4MB/年
- **总计**：约 10MB/年

建议每 2-3 年归档一次旧报告。

---

📅 最后更新：2025-10-29
