# 🚀 5分钟快速开始

本指南帮助你在 5 分钟内快速配置并运行 RSS Daily Report。

## ✅ 前置要求

- GitHub 账号
- Google 账号
- Google Sheets 中已有 RSS 数据

## 📋 快速步骤

### 第 1 步：Fork 仓库（30秒）

1. 点击 GitHub 页面右上角的「Fork」按钮
2. 等待仓库复制完成

### 第 2 步：创建 Google Service Account（2分钟）

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目（或选择现有项目）
3. 启用 API：
   - Google Sheets API
   - Google Drive API
4. 创建服务账号：
   - 进入「IAM 和管理」→「服务账号」
   - 点击「创建服务账号」
   - 输入名称（如 `rss-bot`）
   - 点击「创建并继续」→「完成」
5. 生成密钥：
   - 点击刚创建的服务账号
   - 进入「密钥」标签
   - 「添加密钥」→「创建新密钥」→ 选择「JSON」
   - 下载 JSON 文件

### 第 3 步：共享 Google Sheets（30秒）

1. 打开你的 RSS Google Sheets
2. 点击「共享」
3. 添加服务账号邮箱（在 JSON 文件中的 `client_email` 字段）
4. 权限选择「查看者」
5. 取消勾选「通知用户」
6. 点击「共享」

### 第 4 步：配置 GitHub Secrets（1分钟）

在你 Fork 的仓库中：

1. 进入「Settings」→「Secrets and variables」→「Actions」
2. 添加第一个 Secret：
   - Name: `GOOGLE_CREDENTIALS`
   - Value: 粘贴整个 JSON 文件的内容
3. 添加第二个 Secret：
   - Name: `SHEET_ID`
   - Value: 从 Google Sheets URL 中复制 ID
     ```
     https://docs.google.com/spreadsheets/d/{这里是SHEET_ID}/edit
     ```

### 第 5 步：修改配置（1分钟）

1. 编辑仓库中的 `config.yaml` 文件
2. 修改 `sheet_name` 为你的工作表名称（默认 `Sheet1`）
3. 根据需要调整 `keywords` 关键词列表
4. 提交修改

### 第 6 步：启用 Actions（10秒）

1. 进入仓库的「Actions」标签
2. 点击「I understand my workflows, go ahead and enable them」

### 第 7 步：测试运行（10秒）

1. 在「Actions」页面，选择「Generate Daily Report」
2. 点击「Run workflow」
3. 点击绿色的「Run workflow」按钮
4. 等待运行完成（约 30 秒）

### 第 8 步：查看结果（10秒）

1. 进入仓库的「Code」标签
2. 打开 `reports/` 目录
3. 查看生成的 Markdown 报告

## 🎉 完成！

现在你的 RSS Daily Report 已经配置完成！

- ⏰ **自动运行**：每天 23:00（北京时间）自动生成报告
- 📝 **手动运行**：在 Actions 页面随时手动触发
- 🔧 **调整配置**：随时修改 `config.yaml` 调整关键词

## 📚 下一步

- 阅读 [README.md](README.md) 了解更多功能
- 查看 [SETUP_GUIDE.md](SETUP_GUIDE.md) 获取详细说明
- 调整 `config.yaml` 中的关键词以符合你的需求

## ❓ 遇到问题？

查看 [SETUP_GUIDE.md](SETUP_GUIDE.md) 的常见问题部分，或在 GitHub Issues 中提问。

---

**预计总时间**：5 分钟  
**难度等级**：⭐⭐☆☆☆（简单）

祝使用愉快！🚀
