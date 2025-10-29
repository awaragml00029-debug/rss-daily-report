# 设置指南

本文档详细说明如何设置 Google Sheets API 并配置 GitHub Actions。

## 📋 目录

1. [创建 Google Cloud 项目](#1-创建-google-cloud-项目)
2. [启用 API](#2-启用-api)
3. [创建服务账号](#3-创建服务账号)
4. [共享 Google Sheets](#4-共享-google-sheets)
5. [配置 GitHub Secrets](#5-配置-github-secrets)
6. [测试运行](#6-测试运行)

---

## 1. 创建 Google Cloud 项目

### 步骤 1.1：访问 Google Cloud Console

1. 打开浏览器，访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 使用你的 Google 账号登录

### 步骤 1.2：创建新项目

1. 点击顶部导航栏的项目下拉菜单
2. 点击「新建项目」
3. 输入项目名称（如 `RSS-Report-Bot`）
4. 点击「创建」
5. 等待项目创建完成（约 30 秒）

---

## 2. 启用 API

### 步骤 2.1：启用 Google Sheets API

1. 在 Google Cloud Console 中，确保选中了刚创建的项目
2. 点击左侧菜单「API 和服务」→「库」
3. 搜索「Google Sheets API」
4. 点击进入，然后点击「启用」

### 步骤 2.2：启用 Google Drive API

1. 同样在「库」中搜索「Google Drive API」
2. 点击进入，然后点击「启用」

---

## 3. 创建服务账号

### 步骤 3.1：创建服务账号

1. 点击左侧菜单「IAM 和管理」→「服务账号」
2. 点击「+ 创建服务账号」
3. 填写以下信息：
   - **服务账号名称**：`rss-report-bot`（或其他名称）
   - **服务账号 ID**：会自动生成
   - **描述**：`用于读取 RSS Google Sheets 数据`
4. 点击「创建并继续」

### 步骤 3.2：授予权限（可选）

1. 在「向此服务账号授予对项目的访问权限」页面
2. 可以选择「编辑者」角色（或跳过此步骤）
3. 点击「继续」
4. 点击「完成」

### 步骤 3.3：生成 JSON 密钥

1. 在服务账号列表中，找到刚创建的服务账号
2. 点击服务账号的邮箱地址（类似 `rss-report-bot@xxx.iam.gserviceaccount.com`）
3. 切换到「密钥」标签页
4. 点击「添加密钥」→「创建新密钥」
5. 选择「JSON」格式
6. 点击「创建」
7. JSON 文件会自动下载到你的电脑

⚠️ **重要**：这个 JSON 文件包含敏感信息，请妥善保管，不要分享给他人！

### 步骤 3.4：复制服务账号邮箱

1. 在服务账号详情页面，复制「电子邮件地址」
2. 格式类似：`rss-report-bot@xxx.iam.gserviceaccount.com`
3. 保存这个邮箱地址，下一步要用

---

## 4. 共享 Google Sheets

### 步骤 4.1：打开 Google Sheets

1. 打开你的 RSS 数据 Google Sheets
2. 确保表格包含以下列：
   - 抓取时间
   - 属性
   - 适名称
   - 适分类
   - 标题
   - 链接
   - 发布时间
   - 作者

### 步骤 4.2：共享给服务账号

1. 点击右上角的「共享」按钮
2. 在「添加用户和群组」输入框中，粘贴刚才复制的服务账号邮箱
3. 权限选择「查看者」（只需要读取权限）
4. **取消勾选**「通知用户」（服务账号不需要通知）
5. 点击「共享」或「发送」

### 步骤 4.3：获取 Spreadsheet ID

1. 从浏览器地址栏复制 URL
2. URL 格式：`https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`
3. 提取 `{SPREADSHEET_ID}` 部分
4. 例如：`1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
5. 保存这个 ID，后面要用

---

## 5. 配置 GitHub Secrets

### 步骤 5.1：打开仓库设置

1. 进入你 Fork 的 GitHub 仓库
2. 点击「Settings」标签页
3. 在左侧菜单找到「Secrets and variables」→「Actions」

### 步骤 5.2：添加 GOOGLE_CREDENTIALS

1. 点击「New repository secret」
2. **Name** 填写：`GOOGLE_CREDENTIALS`
3. **Secret** 填写：
   - 打开之前下载的 JSON 密钥文件
   - 复制**整个文件的内容**（不是文件路径）
   - 粘贴到 Secret 输入框
4. 点击「Add secret」

JSON 文件内容格式类似：
```json
{
  "type": "service_account",
  "project_id": "xxx",
  "private_key_id": "xxx",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "rss-report-bot@xxx.iam.gserviceaccount.com",
  ...
}
```

### 步骤 5.3：添加 SHEET_ID

1. 点击「New repository secret」
2. **Name** 填写：`SHEET_ID`
3. **Secret** 填写：你的 Spreadsheet ID（步骤 4.3 中获取的）
4. 点击「Add secret」

### 步骤 5.4：验证 Secrets

确保你已经添加了以下两个 secrets：
- ✅ `GOOGLE_CREDENTIALS`
- ✅ `SHEET_ID`

---

## 6. 测试运行

### 方法 1：手动触发 GitHub Actions

1. 进入仓库的「Actions」标签页
2. 如果看到提示需要启用工作流，点击「I understand my workflows, go ahead and enable them」
3. 在左侧找到「Generate Daily Report」工作流
4. 点击「Run workflow」
5. 点击绿色的「Run workflow」按钮
6. 等待几秒钟，工作流开始运行
7. 点击运行的工作流查看日志
8. 如果成功，会在 `reports/` 目录下看到生成的 Markdown 文件

### 方法 2：本地测试

如果想在本地测试：

```bash
# 克隆仓库
git clone https://github.com/your-username/rss-daily-report.git
cd rss-daily-report

# 安装依赖
pip install -r requirements.txt

# 设置环境变量（使用刚才的 JSON 文件内容）
export GOOGLE_CREDENTIALS='{"type": "service_account", ...}'
export SHEET_ID='your-spreadsheet-id'

# 运行脚本
python scripts/generate_report.py
```

---

## 🎉 完成！

如果一切正常，你应该能看到：

1. ✅ GitHub Actions 成功运行
2. ✅ `reports/` 目录下生成了 Markdown 文件
3. ✅ 文件中包含了筛选后的 RSS 内容

每天 23:00（北京时间），GitHub Actions 会自动运行并生成新的报告。

---

## 🐛 常见问题排查

### 问题 1：GitHub Actions 失败，提示 "未找到 GOOGLE_CREDENTIALS"

**解决方案**：
- 检查 Secret 名称是否拼写正确（区分大小写）
- 确保 JSON 内容完整复制

### 问题 2：提示 "Permission denied" 或 "Access denied"

**解决方案**：
- 确保服务账号邮箱已添加到 Google Sheets 的共享列表
- 权限至少是「查看者」

### 问题 3：找不到数据或数据为空

**解决方案**：
- 检查 `config.yaml` 中的 `sheet_name` 是否正确
- 确保 Spreadsheet ID 正确
- 检查 Google Sheets 中是否有数据

### 问题 4：关键词没有匹配到内容

**解决方案**：
- 检查 `config.yaml` 中的关键词拼写
- 确认 Google Sheets 中的「标题」列包含这些关键词
- 查看 Actions 日志中的筛选统计信息

---

## 📞 需要帮助？

如果遇到问题，请在 GitHub Issues 中提问，附上：
1. 错误信息或截图
2. GitHub Actions 日志
3. 你的配置文件（隐藏敏感信息）

祝使用愉快！🎉
