# 🚀 快速设置指南

## 第一步：创建 Google Service Account

1. 访问 https://console.cloud.google.com/
2. 创建新项目或选择现有项目
3. 启用 API：
   - Google Sheets API
   - Google Drive API
4. 创建服务账号并下载 JSON 密钥文件

## 第二步：配置 Google Sheets

1. 打开你的 Google Sheets
2. 点击右上角的 "Share" 按钮
3. 将服务账号邮箱（xxx@xxx.iam.gserviceaccount.com）添加为编辑者
4. 复制 Sheets URL 中的 ID
   - 例如：`https://docs.google.com/spreadsheets/d/1ABC123XYZ/edit`
   - ID 为：`1ABC123XYZ`

## 第三步：配置 GitHub Secrets

1. 进入仓库 Settings > Secrets and variables > Actions
2. 添加 Secret：**GOOGLE_CREDENTIALS**
   - 粘贴整个 JSON 文件的内容
3. 添加 Secret：**SHEET_ID**
   - 粘贴你的 Sheets ID

## 第四步：修改配置文件

编辑 `config.yaml`：

```yaml
google_sheets:
  sheet_name: "Sheet1"  # 改为你的工作表名称

keywords:
  - "肿瘤"
  - "测序"
  # 添加你的关键词
```

## 第五步：启用 Actions

1. 进入 GitHub Actions 标签
2. 启用工作流
3. 等待每天 23:00 自动运行，或手动触发测试

## 完成！

现在你的 RSS 日报系统已经设置完成，每天会自动生成报告！

## 测试运行

```bash
# 本地测试（可选）
export GOOGLE_CREDENTIALS='...'
export SHEET_ID='...'
python scripts/generate_report.py --mode daily
```

## 常见问题

**Q: 如何修改运行时间？**  
A: 编辑 `.github/workflows/generate-report.yml` 中的 cron 表达式

**Q: 如何添加更多关键词？**  
A: 编辑 `config.yaml` 中的 keywords 列表

**Q: 报告保存在哪里？**  
A: `reports/` 目录，按年月组织

**Q: 如何生成历史报告？**  
A: 手动触发 workflow，指定日期参数
