# Hugo 集成配置指南

本文档说明如何配置跨仓库推送功能，将生成的报告自动推送到 Hugo 博客和备份仓库。

## 🔐 安全配置

### 1. 撤销旧Token（重要！）

如果你之前在聊天中暴露了 GitHub Token，请立即：

1. 访问 https://github.com/settings/tokens
2. 找到并删除之前的 token
3. 重新生成新的 token（见下文）

### 2. 生成新的 Personal Access Token

使用**B账号**（ixxmu）登录 GitHub：

1. 进入 Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 配置 Token：
   - Note: `RSS Daily Report Cross-Repo Access`
   - Expiration: 选择有效期（建议 90 days 或 No expiration）
   - 勾选权限：
     - ✅ **repo** (完整勾选，包括所有子项)
       - repo:status
       - repo_deployment
       - public_repo
       - repo:invite
       - security_events
4. 点击 "Generate token"
5. **立即复制 token**（只显示一次！）

### 3. 在当前项目添加 GitHub Secret

在**当前项目**（rss-daily-report，A账号）中：

1. 进入仓库 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加以下 Secret：

| Name | Value | 说明 |
|------|-------|------|
| `B_ACCOUNT_TOKEN` | 刚才复制的token | B账号的访问令牌 |

**⚠️ 重要提示**：
- Token 只在当前项目（A账号）配置
- 不要在任何地方（包括聊天、代码、文档）直接写入 token
- 定期更新 token（建议每90天）

---

## 📁 文件推送说明

### 生成的文件

每次运行后，系统会生成3个文件：

1. **本地 Markdown**
   - 位置：`reports/2025/10/daily-2025-10-29.md`
   - 用途：在当前项目中保存
   - 格式：普通 Markdown

2. **Hugo Markdown**
   - 临时位置：`temp_hugo/daily-2025-10-29.md`
   - 推送到：`ixxmu/ixxmu.github.io.source` (分支: FigureYY)
   - 目标路径：`content/posts/DailyReports/`
   - 格式：带 Hugo Front Matter 的 Markdown

3. **静态 HTML**
   - 临时位置：`temp_hugo/latest.html`
   - 推送到：`ixxmu/ixxmu.github.io.source` (分支: FigureYY)
   - 目标路径：`static/latest.html`
   - 用途：可通过 Hugo 网站直接访问最新日报

### 推送目标

#### Hugo 仓库
- **仓库**: `ixxmu/ixxmu.github.io.source`
- **分支**: `FigureYY`
- **路径**:
  - Markdown: `content/posts/DailyReports/daily-YYYY-MM-DD.md`
  - HTML: `static/latest.html`

#### 备份仓库
- **仓库**: `ixxmu/duty_bk`
- **分支**: `main`
- **路径**: `DailyReports/reports/YYYY/MM/daily-YYYY-MM-DD.md`
  - 按年月自动分类存储

---

## 🎨 HTML 页面访问

生成的 HTML 页面将推送到 Hugo 的 `static` 目录，可以通过以下方式访问：

```
https://你的Hugo网站域名/latest.html
```

HTML 特点：
- ✅ 响应式设计（手机/PC 自适应）
- ✅ AI 总结区域有渐变背景高亮
- ✅ 简洁专业的学术风格
- ✅ 无需额外依赖，直接打开即可查看

---

## 🔧 配置修改

如果需要修改推送目标，编辑 `config.yaml`:

```yaml
# Hugo 博客集成配置
hugo:
  enabled: true
  repo: "ixxmu/ixxmu.github.io.source"
  branch: "FigureYY"
  path: "content/posts/DailyReports"
  author: "oknet"

# 备份仓库配置
backup:
  enabled: true
  repo: "ixxmu/duty_bk"
  branch: "main"
  path: "DailyReports/reports"
```

---

## 🧪 测试

### 手动触发测试

1. 访问 Actions → Generate Daily Report
2. 点击 "Run workflow"
3. 选择分支和日期
4. 运行并查看日志

### 检查推送结果

运行完成后，检查：

1. **Hugo 仓库**:
   ```
   https://github.com/ixxmu/ixxmu.github.io.source/tree/FigureYY/content/posts/DailyReports
   ```

2. **备份仓库**:
   ```
   https://github.com/ixxmu/duty_bk/tree/main/DailyReports/reports
   ```

3. **HTML 页面**:
   ```
   https://github.com/ixxmu/ixxmu.github.io.source/blob/FigureYY/static/latest.html
   ```

---

## ❌ 故障排除

### 推送失败

如果看到错误：
```
remote: Permission denied
```

检查：
1. ✅ B_ACCOUNT_TOKEN 是否正确配置
2. ✅ Token 是否有 `repo` 权限
3. ✅ Token 是否过期
4. ✅ 仓库名称和分支是否正确

### 文件未生成

如果 `temp_hugo/` 目录为空：

检查：
1. ✅ Python 脚本是否正常运行
2. ✅ 查看 Actions 日志中的错误信息
3. ✅ 确认数据源有数据

---

## 📝 工作流程图

```
GitHub Actions 触发
        ↓
生成报告（Python）
        ├─ 本地 Markdown → reports/
        ├─ Hugo Markdown → temp_hugo/
        └─ HTML → temp_hugo/
        ↓
提交到当前仓库（A账号）
        ↓
跨仓库推送脚本（push_to_repos.sh）
        ├─ 克隆 Hugo 仓库（B账号）
        │   ├─ 复制 Markdown → content/posts/DailyReports/
        │   ├─ 复制 HTML → static/
        │   └─ 提交并推送
        │
        └─ 克隆备份仓库（B账号）
            ├─ 复制 Markdown → DailyReports/reports/YYYY/MM/
            └─ 提交并推送
```

---

## 🎯 完成检查清单

配置完成后，确认以下项目：

- [ ] 已撤销旧的 GitHub Token
- [ ] 已用 B账号生成新的 PAT Token
- [ ] 已在 A账号项目中添加 `B_ACCOUNT_TOKEN` Secret
- [ ] 已测试手动运行 workflow
- [ ] 已确认 Hugo 仓库收到文件
- [ ] 已确认备份仓库收到文件
- [ ] 已验证 HTML 页面可访问

---

## 📞 需要帮助？

如果遇到问题，检查：
1. GitHub Actions 的运行日志
2. 推送脚本的输出信息
3. Token 权限和有效期

**安全提示**：永远不要在公开场合（包括聊天、代码、Issues）暴露你的 GitHub Token！
