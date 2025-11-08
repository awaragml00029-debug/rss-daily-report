# Web Push 快速配置指南

## 🚀 5 分钟快速启用推送通知

### 步骤 1: 注册 OneSignal（1 分钟）

1. 访问 https://onesignal.com/ 并注册
2. 创建新应用，选择 **Web Push** 平台
3. 获取 **App ID** 和 **REST API Key**

### 步骤 2: 修改代码（2 分钟）

**编辑**: `scripts/generate_report.py`

找到第 1021-1022 行，修改为：

```python
<meta name="push-enabled" content="true">
<meta name="onesignal-app-id" content="你的-App-ID">
```

### 步骤 3: 配置 GitHub Secrets（1 分钟）

在 GitHub 仓库 **Settings → Secrets → Actions** 添加：

| Secret Name | Value |
|-------------|-------|
| `ONESIGNAL_APP_ID` | 你的 OneSignal App ID |
| `ONESIGNAL_API_KEY` | 你的 OneSignal REST API Key |

### 步骤 4: 修改 GitHub Actions（1 分钟）

**编辑**: `.github/workflows/generate-report.yml`

在 `env:` 部分添加：

```yaml
env:
  # 原有配置...
  GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}
  SHEET_ID: ${{ secrets.SHEET_ID }}
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  B_ACCOUNT_TOKEN: ${{ secrets.B_ACCOUNT_TOKEN }}

  # 新增以下两行
  ONESIGNAL_APP_ID: ${{ secrets.ONESIGNAL_APP_ID }}
  ONESIGNAL_API_KEY: ${{ secrets.ONESIGNAL_API_KEY }}
```

### 步骤 5: 提交并测试

```bash
git add .
git commit -m "feat: 启用 Web Push 推送通知"
git push
```

访问 `https://figureblog.top/latest.html`，点击右下角订阅按钮即可！

---

## 📋 完整清单

- [ ] 注册 OneSignal 账号
- [ ] 创建 Web Push 应用
- [ ] 获取 App ID 和 API Key
- [ ] 修改 `generate_report.py` 启用推送
- [ ] 配置 GitHub Secrets
- [ ] 修改 GitHub Actions 工作流
- [ ] 提交代码到 GitHub
- [ ] 访问网页测试订阅
- [ ] 等待下次报告生成，验证推送

---

## 🔍 验证推送是否成功

### 方法 1: 查看 GitHub Actions 日志

在 Actions 运行日志中搜索：

```
📱 触发推送通知...
✅ 推送通知已发送
```

### 方法 2: OneSignal 控制台

登录 OneSignal，查看 **Delivery** 页面，应该能看到推送记录。

### 方法 3: 手机实测

1. 在手机 Chrome 访问 `latest.html`
2. 订阅通知
3. 等待下次报告生成
4. 查看手机通知栏

---

## ❓ 遇到问题？

查看详细文档: [WEB_PUSH_SETUP.md](./WEB_PUSH_SETUP.md)

---

**配置完成后，你的用户就能收到这样的通知了**：

```
┌─────────────────────────────────┐
│ 🔔 科研日报更新                 │
│ 2025-11-08 科研日报已生成，      │
│ 点击查看最新内容                │
└─────────────────────────────────┘
```

**祝配置顺利！** 🎉
