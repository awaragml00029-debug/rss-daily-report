# 🚀 5分钟快速开始

按照以下 5 个步骤，快速部署你的 RSS 日报系统！

## Step 1: 创建 Google Service Account (2分钟)

1. 访问 https://console.cloud.google.com/
2. 创建项目 > 启用 APIs
   - Google Sheets API
   - Google Drive API
3. 创建服务账号 > 下载 JSON 密钥
4. 复制服务账号邮箱（形如 xxx@xxx.iam.gserviceaccount.com）

## Step 2: 配置 Google Sheets (1分钟)

1. 打开你的 Google Sheets
2. 点击 "Share" 
3. 添加服务账号邮箱为编辑者
4. 复制 Sheet ID（从 URL 获取）

## Step 3: 上传到 GitHub (1分钟)

1. 创建新的 GitHub 仓库
2. 上传本项目所有文件
3. 进入 Settings > Secrets > Actions
4. 添加两个 Secrets：
   - `GOOGLE_CREDENTIALS`: 粘贴 JSON 文件完整内容
   - `SHEET_ID`: 粘贴你的 Sheet ID

## Step 4: 修改配置 (30秒)

编辑 `config.yaml`:

```yaml
google_sheets:
  sheet_name: "Sheet1"  # 改成你的工作表名

keywords:
  - "肿瘤"
  - "测序"
  - "单细胞"
  - "R包"
  # 添加你的关键词
```

提交并推送更改。

## Step 5: 启用 Actions (30秒)

1. 进入 GitHub 仓库的 "Actions" 标签
2. 点击 "I understand my workflows, go ahead and enable them"
3. 选择 "Generate Daily Report" 工作流
4. 点击 "Run workflow" 测试运行

## ✅ 完成！

系统将在每天 23:00 (北京时间) 自动生成报告。

查看生成的报告：进入 `reports/` 目录

---

## 🔍 验证是否成功

运行后检查：
- [ ] Actions 显示绿色 ✅
- [ ] `reports/` 目录出现新文件
- [ ] 报告内容符合预期

## ❓ 遇到问题？

**常见问题**：

1. **Actions 失败**
   - 检查 Secrets 是否正确设置
   - 查看 Actions 日志找到具体错误

2. **报告为空**
   - 检查关键词是否太严格
   - 确认 Sheet 中有今天的数据

3. **连接失败**
   - 确认服务账号有 Sheet 访问权限
   - 检查 Sheet ID 是否正确

详细文档：
- 📖 [README.md](README.md) - 完整文档
- 📋 [CHECKLIST.md](CHECKLIST.md) - 检查清单
- 🎯 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - 项目概览

---

**祝你使用愉快！** 🎉
