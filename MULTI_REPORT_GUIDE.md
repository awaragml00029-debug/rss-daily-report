# 多报告配置使用指南

## 📋 概述

本系统现在支持多个独立报告，每个报告可以有：
- ✅ 独立的 Google Sheets 数据源
- ✅ 独立的关键词和筛选规则
- ✅ 独立的输出文件名
- ✅ 独立的 GitHub Actions 工作流
- ✅ 共享的 Gemini AI 配置

## 🚀 快速开始

### 1. 配置文件结构

新的 `config.yaml` 使用以下结构：

```yaml
# 全局默认配置（所有报告继承）
defaults:
  columns: ...
  source_mapping: ...
  report_format: ...
  output: ...

# Gemini AI 配置（全局共享）
gemini:
  enabled: true
  model: "gemini-2.5-flash-lite"
  ...

# 多报告配置
report_configs:
  bioinfo:  # 报告1
    name: "生物信息学日报"
    enabled: true
    google_sheets:
      spreadsheet_env: "SHEET_ID_1"
      sheet_name: "RSS处理数据"
    keywords: [...]
    ...

  imaging:  # 报告2
    name: "医学影像日报"
    enabled: false  # 默认禁用
    google_sheets:
      spreadsheet_env: "SHEET_ID_2"
      sheet_name: "Imaging数据"
    keywords: [...]
    ...
```

### 2. 环境变量设置

在 GitHub Secrets 中设置：

```
GOOGLE_CREDENTIALS     # 共享的 Google 服务账号凭证
SHEET_ID_1            # 生物信息学报告的 Sheet ID
SHEET_ID_2            # 医学影像报告的 Sheet ID (如果启用)
GEMINI_API_KEY        # 共享的 Gemini API Key
GEMINI_API_URL        # (可选) 自定义 Gemini API URL
B_ACCOUNT_TOKEN       # 推送到 Hugo/备份仓库的 Token
```

### 3. 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export GOOGLE_CREDENTIALS='...'
export SHEET_ID_1='your-sheet-id-1'
export SHEET_ID_2='your-sheet-id-2'
export GEMINI_API_KEY='your-api-key'

# 生成生物信息学日报
python scripts/generate_report.py --config-name bioinfo --mode daily

# 生成医学影像日报
python scripts/generate_report.py --config-name imaging --mode daily

# 生成指定日期的报告
python scripts/generate_report.py --config-name bioinfo --mode daily --date 2025-12-29

# 生成月度报告
python scripts/generate_report.py --config-name bioinfo --mode monthly
```

### 4. GitHub Actions 设置

#### 现有报告（bioinfo）

现有的 `.github/workflows/generate-report.yml` 已更新为使用 `bioinfo` 配置。

**关键改动**：
- 环境变量从 `SHEET_ID` 改为 `SHEET_ID_1`
- 命令增加了 `--config-name bioinfo` 参数

**需要的操作**：
1. 在 GitHub Secrets 中将 `SHEET_ID` 重命名为 `SHEET_ID_1`
2. 或者直接添加 `SHEET_ID_1`，保留原有的 `SHEET_ID`（向后兼容）

#### 新报告（imaging）

参考 `.github/workflows/generate-report-imaging.yml.example` 创建新的 workflow：

1. 复制示例文件并重命名：
   ```bash
   cp .github/workflows/generate-report-imaging.yml.example \
      .github/workflows/generate-report-imaging.yml
   ```

2. 在 `config.yaml` 中启用 imaging 报告：
   ```yaml
   report_configs:
     imaging:
       enabled: true  # 改为 true
   ```

3. 在 GitHub Secrets 中添加 `SHEET_ID_2`

4. 推送到远程仓库，workflow 将自动运行

## 📝 添加新报告

### 步骤 1：在 config.yaml 中添加新报告配置

```yaml
report_configs:
  # ... 现有报告 ...

  # 新报告：蛋白质组学
  proteomics:
    name: "蛋白质组学日报"
    enabled: true
    description: "蛋白质组学相关的RSS日报"

    google_sheets:
      spreadsheet_env: "SHEET_ID_3"  # 新的环境变量
      sheet_name: "Proteomics数据"

    keywords:
      - "蛋白质"
      - "proteomics"
      - "质谱"
      - "mass spectrometry"
      # ... 更多关键词

    exclude_keywords:
      - "广告"
      - "推广"

    output:
      daily_filename: "proteomics-{date}.md"
      monthly_filename: "proteomics-monthly-{year}-{month}.md"

    hugo:
      enabled: true
      repo: "ixxmu/ixxmu.github.io.source"
      branch: "FigureYY"
      path: "content/posts/ProteomicsReports"  # 独立路径
      author: "oknet"

    backup:
      enabled: true
      repo: "ixxmu/duty_bk"
      branch: "main"
      path: "ProteomicsReports/reports"
```

### 步骤 2：添加 GitHub Secret

在仓库的 Settings > Secrets and variables > Actions 中添加：
```
SHEET_ID_3 = your-proteomics-sheet-id
```

### 步骤 3：创建 GitHub Actions workflow

复制 `generate-report-imaging.yml.example`：

```bash
cp .github/workflows/generate-report-imaging.yml.example \
   .github/workflows/generate-report-proteomics.yml
```

修改文件中的关键部分：
- 将 `imaging` 改为 `proteomics`
- 将 `SHEET_ID_2` 改为 `SHEET_ID_3`
- 调整 cron 时间（避免与其他报告冲突）

### 步骤 4：测试

本地测试：
```bash
python scripts/generate_report.py --config-name proteomics --mode daily
```

推送到 GitHub 后，workflow 将自动运行。

## 🔧 配置说明

### defaults（默认配置）

所有报告继承这些配置，除非在具体报告中覆盖：

- `columns`: 列索引映射（A列=1, B列=2...）
- `source_mapping`: 来源分类映射
- `report_format`: 报告格式配置
- `output`: 输出路径配置

### 具体报告配置

每个报告可以覆盖默认配置，例如：

```yaml
imaging:
  # 如果列结构不同，可以覆盖
  columns:
    crawl_time: 1
    source_name: 2
    title: 3
    link: 4
    description: 5
    # 注意：只有5列，没有 author, zhtitle 等
```

### gemini（AI 配置）

所有报告共享 Gemini AI 配置，无法单独覆盖。

## 🐛 故障排查

### 问题 1：未找到环境变量

**错误**：
```
ValueError: 未找到环境变量 'SHEET_ID_1'
```

**解决**：
1. 本地运行：确保设置了对应的环境变量
2. GitHub Actions：在 Secrets 中添加对应的变量

### 问题 2：未找到报告配置

**错误**：
```
ValueError: 未找到报告配置 'xxx'。
可用的报告: bioinfo, imaging
```

**解决**：
1. 检查 `config.yaml` 中是否有该报告配置
2. 检查 `--config-name` 参数是否正确
3. 运行 `python -c "import yaml; print(list(yaml.safe_load(open('config.yaml'))['report_configs'].keys()))"` 查看可用报告

### 问题 3：报告已禁用

**错误**：
```
ValueError: 报告配置 'imaging' 已禁用
```

**解决**：
在 `config.yaml` 中将 `enabled: false` 改为 `enabled: true`

### 问题 4：配置文件包含多报告配置，请使用 --config-name 参数

**错误**：
```
ValueError: 配置文件包含多报告配置，请使用 --config-name 参数指定报告名称
可用的报告: bioinfo, imaging
```

**解决**：
添加 `--config-name` 参数：
```bash
python scripts/generate_report.py --config-name bioinfo --mode daily
```

## 📊 架构图

```
config.yaml
├── defaults (全局默认)
│   ├── columns
│   ├── source_mapping
│   ├── report_format
│   └── output
├── gemini (全局共享)
└── report_configs
    ├── bioinfo
    │   ├── google_sheets.spreadsheet_env = "SHEET_ID_1"
    │   ├── keywords = [...]
    │   ├── output.daily_filename = "daily-{date}.md"
    │   ├── hugo.path = "content/posts/DailyReports"
    │   └── backup.path = "DailyReports/reports"
    │
    └── imaging
        ├── google_sheets.spreadsheet_env = "SHEET_ID_2"
        ├── keywords = [...]
        ├── output.daily_filename = "imaging-{date}.md"
        ├── hugo.path = "content/posts/ImagingReports"
        └── backup.path = "ImagingReports/reports"
```

## ✅ 最佳实践

1. **命名约定**：
   - 配置名称：小写字母，如 `bioinfo`, `imaging`, `proteomics`
   - 环境变量：大写加数字，如 `SHEET_ID_1`, `SHEET_ID_2`
   - 输出文件名：包含配置名称，如 `imaging-{date}.md`

2. **独立性**：
   - 每个报告使用独立的 workflow 文件
   - 使用不同的 Hugo 路径和备份路径
   - 避免输出文件名冲突

3. **时间调度**：
   - 错开不同报告的 cron 时间
   - 例如：bioinfo 在 21:30 UTC，imaging 在 22:00 UTC

4. **测试流程**：
   - 先在本地测试新配置
   - 手动触发 GitHub Actions 测试
   - 确认无误后再启用定时任务

## 📞 获取帮助

如有问题，请：
1. 查看本文档的故障排查部分
2. 检查 GitHub Actions 日志
3. 在仓库中提交 Issue

---

**祝使用愉快！🎉**
