# 更新日志

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

## [1.0.0] - 2025-10-29

### 新增
- 🎉 首次发布
- ✨ 支持从 Google Sheets 读取 RSS 数据
- 🔍 支持正则表达式关键词匹配
- 📅 每日报告自动生成
- 📊 月度报告自动生成
- 🤖 GitHub Actions 自动化工作流
- 📝 完整的设置文档和示例

### 功能特性
- 智能日期识别（使用抓取时间）
- 关键词高亮显示
- 关键词频次统计
- 支持排除关键词
- Markdown 格式输出
- 按发布时间排序
- 详细的日志输出

### 文档
- README.md - 项目说明
- SETUP_GUIDE.md - 详细设置指南
- config.example.yaml - 示例配置文件
- 示例报告展示

### 技术栈
- Python 3.10+
- gspread - Google Sheets API
- Jinja2 - 模板引擎
- GitHub Actions - 自动化
- YAML - 配置管理

---

## 版本说明

### [语义化版本规则]
- **主版本号（Major）**：不兼容的 API 修改
- **次版本号（Minor）**：向下兼容的功能性新增
- **修订号（Patch）**：向下兼容的问题修正

### [更新类型标识]
- `新增` - 新功能
- `变更` - 已有功能的变更
- `废弃` - 即将移除的功能
- `移除` - 已移除的功能
- `修复` - 问题修复
- `安全` - 安全相关修复
