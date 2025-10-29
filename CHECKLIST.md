# 📋 部署检查清单

在部署项目前，请确保完成以下所有步骤：

## ✅ Google Cloud 设置

- [ ] 创建或选择 Google Cloud 项目
- [ ] 启用 Google Sheets API
- [ ] 启用 Google Drive API
- [ ] 创建服务账号
- [ ] 下载服务账号 JSON 密钥文件
- [ ] 记录服务账号邮箱地址（例如：xxx@xxx.iam.gserviceaccount.com）

## ✅ Google Sheets 设置

- [ ] 确认 Sheet 包含所有必需列（A-H列）
- [ ] 将服务账号添加为 Sheet 的编辑者
- [ ] 复制 Sheet ID（从 URL 中）
- [ ] 确认工作表名称（默认为 "Sheet1"）

## ✅ GitHub 仓库设置

- [ ] Fork 或上传项目到 GitHub
- [ ] 进入 Settings > Secrets and variables > Actions
- [ ] 添加 Secret：GOOGLE_CREDENTIALS（完整的 JSON 内容）
- [ ] 添加 Secret：SHEET_ID（你的 Sheets ID）
- [ ] 进入 Actions 标签页
- [ ] 启用 GitHub Actions 工作流

## ✅ 配置文件修改

- [ ] 编辑 `config.yaml`
- [ ] 修改 `sheet_name` 为你的工作表名称
- [ ] 配置 `keywords` 关键词列表
- [ ] （可选）配置 `exclude_keywords` 排除词
- [ ] 提交并推送修改

## ✅ 测试运行

### 方式一：GitHub Actions 手动触发
- [ ] 进入 Actions 标签
- [ ] 选择 "Generate Daily Report"
- [ ] 点击 "Run workflow"
- [ ] 选择 mode: daily
- [ ] 点击运行
- [ ] 检查运行结果
- [ ] 查看 reports/ 目录是否生成报告

### 方式二：本地测试（可选）
- [ ] 安装 Python 3.10+
- [ ] 安装依赖：`pip install -r requirements.txt`
- [ ] 设置环境变量 GOOGLE_CREDENTIALS 和 SHEET_ID
- [ ] 运行：`python test.py --mode mock`
- [ ] 运行：`python test.py --mode real`
- [ ] 检查生成的测试报告

## ✅ 验证

- [ ] 确认报告文件已生成在 `reports/` 目录
- [ ] 打开报告检查内容格式
- [ ] 确认关键词筛选正确
- [ ] 确认日期和统计信息正确
- [ ] 检查 Git 提交历史

## 🎉 完成

如果所有步骤都完成，恭喜！你的 RSS 日报系统已经成功部署！

系统将在每天 23:00 (北京时间) 自动生成报告。

## 📝 后续维护

定期检查：
- [ ] GitHub Actions 运行状态
- [ ] 报告生成质量
- [ ] 关键词匹配效果
- [ ] 存储空间使用情况

需要调整时：
- 修改关键词：编辑 `config.yaml`
- 修改运行时间：编辑 `.github/workflows/generate-report.yml`
- 修改报告格式：编辑 `scripts/generate_report.py`

## 🆘 遇到问题？

1. 查看 GitHub Actions 日志
2. 检查 README.md 的故障排查部分
3. 在 GitHub Issues 提问
