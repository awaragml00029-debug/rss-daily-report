# Web Push 推送通知设置指南

## 📱 功能概述

本项目已集成 **Web Push 推送通知** 功能，支持在手机端 Chrome、Firefox、Safari 等浏览器接收更新提醒。

当每日科研日报生成后，订阅用户的手机（或电脑）会自动收到推送通知，即使浏览器已关闭也能收到。

---

## 🎯 实现效果

### 用户体验流程

1. **首次访问** `latest.html` 页面
2. 页面右下角出现 **「订阅科研日报更新通知」** 按钮
3. 点击按钮，浏览器弹出授权框：**"允许 xxx 发送通知？"**
4. 用户点击 **「允许」**
5. 订阅成功，立即收到欢迎通知
6. 以后每天新报告生成时，自动收到推送（即使没打开网页）

### 通知样式示例

```
┌─────────────────────────────────┐
│ 🔔 科研日报更新                 │
│ 2025-11-08 科研日报已生成，      │
│ 点击查看最新内容                │
│                                  │
│ [查看详情]  [关闭]              │
└─────────────────────────────────┘
```

---

## 🛠️ 配置步骤

### 方案 A：使用 OneSignal（推荐，免费）

OneSignal 是一个免费的推送通知服务平台，每月提供 10,000 次推送免费额度。

#### 第一步：注册 OneSignal 账号

1. 访问 [OneSignal 官网](https://onesignal.com/)
2. 点击 **「Sign Up」** 注册账号（可用 GitHub 登录）
3. 登录后进入控制台

#### 第二步：创建 Web Push 应用

1. 点击 **「New App/Website」**
2. 填写应用信息：
   - **App Name**: 科研日报
   - **Platform**: 选择 **「Web Push」**
3. 点击 **「Create」** 创建应用

#### 第三步：配置网站信息

1. 选择 **「Typical Site」**（典型网站）
2. 填写网站信息：
   - **Site URL**: `https://figureblog.top`
   - **Default Icon URL**: `https://figureblog.top/favicon.ico`（可选）
   - **Auto Resubscribe**: 开启（推荐）
3. 点击 **「Save」**

#### 第四步：获取配置信息

完成配置后，OneSignal 会显示：

- **App ID**: 类似 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **REST API Key**: 类似 `YourRestAPIKey`

**请妥善保存这两个值！**

#### 第五步：修改项目配置

##### 5.1 修改 HTML 模板启用推送

编辑 `scripts/generate_report.py`，找到第 1021-1022 行：

```python
<meta name="push-enabled" content="false">
<meta name="onesignal-app-id" content="">
```

修改为：

```python
<meta name="push-enabled" content="true">
<meta name="onesignal-app-id" content="你的-OneSignal-App-ID">
```

示例：

```python
<meta name="push-enabled" content="true">
<meta name="onesignal-app-id" content="12345678-90ab-cdef-1234-567890abcdef">
```

##### 5.2 添加 GitHub Secrets

在 GitHub 仓库中设置环境变量：

1. 进入仓库 **Settings → Secrets and variables → Actions**
2. 点击 **「New repository secret」**
3. 添加以下两个 Secrets：

| Secret Name | Value |
|-------------|-------|
| `ONESIGNAL_APP_ID` | 你的 OneSignal App ID |
| `ONESIGNAL_API_KEY` | 你的 OneSignal REST API Key |

##### 5.3 修改 GitHub Actions 工作流

编辑 `.github/workflows/generate-report.yml`，在 `env:` 部分添加：

```yaml
env:
  GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}
  SHEET_ID: ${{ secrets.SHEET_ID }}
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  B_ACCOUNT_TOKEN: ${{ secrets.B_ACCOUNT_TOKEN }}

  # 添加以下两行
  ONESIGNAL_APP_ID: ${{ secrets.ONESIGNAL_APP_ID }}
  ONESIGNAL_API_KEY: ${{ secrets.ONESIGNAL_API_KEY }}
```

#### 第六步：测试推送

1. 提交并推送代码到 GitHub
2. 等待 GitHub Actions 运行完成
3. 访问 `https://figureblog.top/latest.html`
4. 点击右下角的订阅按钮
5. 允许通知权限
6. 等待下次报告生成（或手动触发 GitHub Actions）

---

### 方案 B：自建推送服务器（高级）

如果不想依赖第三方服务，可以自建推送服务器。

#### 技术栈

- **后端**: Node.js + Express
- **数据库**: SQLite / PostgreSQL（存储订阅信息）
- **推送库**: `web-push` (npm 包)
- **部署**: VPS / Heroku / Railway / Fly.io

#### 实现步骤（简要）

1. **生成 VAPID 密钥对**

```bash
npm install -g web-push
web-push generate-vapid-keys
```

2. **创建后端 API**

```javascript
// server.js
const webpush = require('web-push');

webpush.setVapidDetails(
  'mailto:your@email.com',
  'YOUR_PUBLIC_KEY',
  'YOUR_PRIVATE_KEY'
);

// 订阅端点
app.post('/subscribe', (req, res) => {
  const subscription = req.body;
  // 保存到数据库
});

// 推送端点
app.post('/push', (req, res) => {
  const payload = JSON.stringify({
    title: '科研日报更新',
    body: '今日报告已生成'
  });

  // 从数据库读取所有订阅
  // 遍历发送推送
  subscriptions.forEach(sub => {
    webpush.sendNotification(sub, payload);
  });
});
```

3. **修改前端代码**

编辑 `scripts/generate_report.py`，在 JavaScript 部分添加自定义推送逻辑（替换 OneSignal）。

4. **部署服务器**

将后端部署到 VPS 或云平台，确保 HTTPS 可访问。

5. **修改推送脚本**

编辑 `scripts/push_to_repos.sh`，将 OneSignal API 调用替换为你的推送服务器 API。

> **注意**: 方案 B 需要较强的后端开发能力，推荐先使用方案 A。

---

## 📋 文件说明

### 新增/修改的文件

| 文件路径 | 说明 |
|---------|------|
| `static/sw.js` | Service Worker 文件，处理推送通知接收 |
| `scripts/generate_report.py` | 修改 HTML 模板，添加推送初始化代码 |
| `scripts/push_to_repos.sh` | 添加 Service Worker 推送和通知触发 |
| `docs/WEB_PUSH_SETUP.md` | 本配置文档 |

### Service Worker 功能

`static/sw.js` 文件提供以下功能：

- ✅ 接收推送通知
- ✅ 显示通知（带操作按钮）
- ✅ 处理通知点击事件（打开/聚焦页面）
- ✅ 缓存 `latest.html`（离线访问）
- ✅ 自动清理旧缓存

### HTML 模板集成

`scripts/generate_report.py` 的 HTML 模板中：

- **第 1021-1022 行**: 推送配置（需要修改）
- **第 1025 行**: OneSignal SDK 引用
- **第 1527-1590 行**: 推送初始化 JavaScript

### 推送脚本集成

`scripts/push_to_repos.sh` 脚本：

- **第 71-76 行**: 复制 Service Worker 到 Hugo 仓库
- **第 147-185 行**: 触发 OneSignal 推送通知

---

## 🧪 测试清单

完成配置后，按以下步骤测试：

- [ ] 访问 `latest.html`，页面右下角出现订阅按钮
- [ ] 点击订阅按钮，浏览器弹出授权框
- [ ] 允许通知后，立即收到欢迎通知
- [ ] 等待下次报告生成（或手动触发 Actions）
- [ ] 收到推送通知（即使浏览器关闭）
- [ ] 点击通知，自动打开 `latest.html`
- [ ] 在 OneSignal 控制台查看推送历史和订阅人数

---

## ❓ 常见问题

### Q1: 为什么点击订阅没有反应？

**可能原因**：

1. ✅ 检查 `push-enabled` 是否设置为 `true`
2. ✅ 检查 `onesignal-app-id` 是否正确填写
3. ✅ 检查浏览器控制台是否有错误信息
4. ✅ 确认网站使用 HTTPS（HTTP 不支持推送）

### Q2: 为什么没有收到推送通知？

**可能原因**：

1. ✅ 检查 GitHub Secrets 是否正确配置
2. ✅ 查看 GitHub Actions 日志，确认推送是否成功
3. ✅ 在 OneSignal 控制台查看推送历史
4. ✅ 检查手机浏览器是否允许了通知权限
5. ✅ 确认手机没有开启"勿扰模式"

### Q3: 推送通知是否收费？

OneSignal 免费版提供：

- ✅ 每月 10,000 次推送
- ✅ 无限订阅用户
- ✅ 基础推送功能

如果超过免费额度，可升级到付费版或自建服务器。

### Q4: 推送通知是否支持所有浏览器？

| 浏览器 | 桌面端 | 移动端 |
|--------|--------|--------|
| Chrome | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Safari | ✅ | ✅ (iOS 16.4+) |
| Edge | ✅ | ✅ |
| Opera | ✅ | ✅ |

### Q5: 用户如何取消订阅？

用户可以通过以下方式取消订阅：

1. 点击页面右下角的订阅按钮 → 取消订阅
2. 在浏览器设置中屏蔽网站通知
3. 点击推送通知上的"取消订阅"链接（需自定义）

### Q6: 推送通知的内容可以自定义吗？

可以！编辑 `scripts/push_to_repos.sh` 第 155-163 行：

```bash
NOTIFICATION_PAYLOAD='{
    "app_id": "'"$ONESIGNAL_APP_ID"'",
    "included_segments": ["Subscribed Users"],
    "headings": {"zh": "自定义标题"},
    "contents": {"zh": "自定义内容"},
    "url": "https://figureblog.top/latest.html"
}'
```

---

## 🔒 安全考虑

### VAPID 密钥安全

- ⚠️ **不要** 将 API Key 提交到 Git 仓库
- ✅ **务必** 使用 GitHub Secrets 存储敏感信息
- ✅ **定期** 轮换 API Key（建议每季度一次）

### HTTPS 要求

Web Push 推送通知**必须**在 HTTPS 环境下运行：

- ✅ GitHub Pages 自动提供 HTTPS
- ✅ Netlify / Vercel 默认支持 HTTPS
- ⚠️ HTTP 站点无法使用推送功能

### 用户隐私

- ✅ 订阅信息由 OneSignal 管理（符合 GDPR）
- ✅ 不收集用户个人信息
- ✅ 用户可随时取消订阅

---

## 📊 监控和分析

### OneSignal 控制台

登录 OneSignal 控制台可查看：

- 📈 订阅用户数量
- 📊 推送发送成功率
- 📱 设备类型分布（桌面/移动）
- 🌍 用户地理位置分布
- 📅 推送历史记录

### GitHub Actions 日志

在 GitHub Actions 的运行日志中可查看：

```
📱 触发推送通知...
✅ 推送通知已发送
   响应: {"id":"12345678-90ab-cdef-1234-567890abcdef","recipients":42}
```

- `recipients`: 实际接收推送的用户数

---

## 🚀 进阶优化

### 优化 1: 智能推送时间

根据用户所在时区推送（需要 OneSignal 付费版）。

### 优化 2: 个性化推送

根据用户订阅的关键词推送相关内容（需要自建后端）。

### 优化 3: 推送摘要

在推送通知中包含今日热门话题（修改 `push_to_repos.sh`）。

### 优化 4: A/B 测试

测试不同推送文案的点击率（OneSignal 支持）。

---

## 📚 参考资料

- [OneSignal 官方文档](https://documentation.onesignal.com/docs)
- [Web Push Notifications API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [Service Worker API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Notifications API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API)

---

## 💡 支持

如有问题，请：

1. 查看 GitHub Actions 运行日志
2. 检查浏览器控制台错误信息
3. 在 OneSignal 控制台查看推送状态
4. 提交 GitHub Issue

---

**最后更新**: 2025-11-08
**文档版本**: v1.0
