# 📦 RSS Daily Report - 项目交付文档

## 🎯 项目概述

这是一个完整的自动化 RSS 订阅日报生成系统，基于你的需求定制开发。

### 核心功能

✅ **自动化采集**：从 Google Sheets 读取 RSS 订阅数据  
✅ **智能筛选**：支持正则表达式关键词匹配  
✅ **日报生成**：每天自动生成 Markdown 格式日报  
✅ **月报汇总**：每月自动生成月度统计报告  
✅ **完全自动化**：使用 GitHub Actions，无需手动操作  
✅ **版本控制**：所有报告都存储在 Git 中，便于追溯

## 📁 项目文件说明

### 核心代码

1. **scripts/generate_report.py** (约 600 行)
   - 主程序脚本
   - 实现了所有核心功能：
     - Google Sheets API 连接
     - 数据读取和日期识别
     - 正则表达式关键词匹配
     - Markdown 报告生成
     - 日报和月报逻辑
   - 支持命令行参数
   - 详细的日志输出

2. **.github/workflows/generate-report.yml**
   - GitHub Actions 工作流配置
   - 定时任务：每天 23:00（北京时间）
   - 支持手动触发
   - 自动提交生成的报告

### 配置文件

3. **config.yaml**
   - 主配置文件
   - 包含：
     - Google Sheets 连接信息
     - 关键词列表（支持正则）
     - 排除关键词
     - 输出路径设置
     - 月报生成规则

4. **config.example.yaml**
   - 配置示例文件
   - 包含详细注释
   - 提供了生物信息学领域的关键词示例

5. **requirements.txt**
   - Python 依赖包
   - 包含所有必需的库

### 文档

6. **README.md**
   - 项目主文档
   - 功能介绍
   - 快速开始
   - 使用说明

7. **SETUP_GUIDE.md**
   - 详细的设置指南
   - 图文步骤说明
   - 常见问题解答

8. **QUICK_START.md**
   - 5分钟快速上手指南
   - 最精简的步骤

9. **PROJECT_STRUCTURE.md**
   - 项目结构说明
   - 每个目录和文件的用途

10. **CONTRIBUTING.md**
    - 贡献指南
    - 代码规范
    - 提交流程

11. **CHANGELOG.md**
    - 版本更新日志
    - 功能变更记录

### 辅助文件

12. **test.sh**
    - 本地测试脚本
    - 自动检查环境配置
    - 一键运行测试

13. **.gitignore**
    - Git 忽略文件
    - 保护敏感信息

14. **LICENSE**
    - MIT 开源许可证

### 示例文件

15. **reports/2025/10/daily-2025-10-29.md**
    - 示例日报
    - 展示最终生成的报告格式

16. **reports/2025/monthly-2025-10.md**
    - 示例月报
    - 展示月度汇总格式

## 🎨 设计亮点

### 1. 灵活的关键词匹配

```yaml
keywords:
  - "单细胞"          # 简单匹配
  - "单细胞.*测序"    # 正则表达式，匹配更多变体
  - "RNA-?seq"       # 匹配有无连字符的情况
  - "肿瘤|癌症"       # 匹配多个关键词
```

### 2. 智能日期识别

- 自动获取 Google Sheets 中最新的抓取日期
- 支持多种日期格式自动解析
- 不受时区影响（按抓取时间简化处理）

### 3. 完善的报告格式

日报包含：
- 📊 统计概览
- 📰 内容列表（按时间排序）
- 🏷️ 关键词频次统计
- 🔗 原文链接

月报包含：
- 📊 月度统计
- 📈 每日数据
- 🏷️ 关键词排行（Top 20）
- 📰 精选内容（Top 50）

### 4. 自动化流程

```
23:00 每天触发
    ↓
读取 Google Sheets
    ↓
筛选最新一天数据
    ↓
关键词匹配
    ↓
生成 Markdown
    ↓
自动提交到 Git
    ↓
可以随时查看
```

### 5. 月报智能生成

- 每月 30 号（2月 28 号）自动生成上月汇总
- 无需手动触发
- 包含完整的月度分析

## 🔧 技术栈

- **Python 3.10+**
- **gspread** - Google Sheets API
- **Jinja2** - 模板引擎
- **PyYAML** - 配置管理
- **GitHub Actions** - 自动化
- **Markdown** - 报告格式

## 📊 使用流程

### 初次设置（一次性，约 10 分钟）

1. Fork 仓库到你的 GitHub
2. 创建 Google Service Account
3. 共享 Google Sheets
4. 配置 GitHub Secrets
5. 修改 config.yaml
6. 启用 GitHub Actions
7. 手动测试运行

### 日常使用（完全自动）

- 每天 23:00 自动生成报告
- 自动提交到仓库
- 随时查看 `reports/` 目录

### 手动操作（可选）

- 在 Actions 页面手动触发
- 生成指定日期的报告
- 生成特定月份的月报

## 🎯 已实现的需求

根据你的需求，以下功能已完全实现：

✅ **从 Google Sheets 采集数据**
- 支持读取所有数据
- 自动识别最新日期

✅ **基于来源和日期筛选**
- 按抓取时间筛选当天数据
- 支持来源筛选（可选）

✅ **关键词筛选**
- 支持正则表达式
- 支持排除关键词
- 自动统计关键词频次

✅ **生成 Markdown 报告**
- 日报格式完善
- 月报格式完善
- 内容清晰易读

✅ **自动化流程**
- GitHub Actions 定时任务
- 自动提交到仓库
- 支持手动触发

✅ **月报生成**
- 每月 30 号（2月 28 号）自动生成
- 包含完整统计信息

## 📝 配置示例

你的 Google Sheets 表头（已根据截图配置）：
```
A列：抓取时间
B列：属性
C列：适名称
D列：适分类
E列：标题
F列：链接
G列：发布时间
H列：作者
```

关键词配置（生物信息学领域）：
```yaml
keywords:
  - "肿瘤"
  - "测序"
  - "单细胞"
  - "R包"
  # 更多关键词...
```

## 🚀 部署步骤

1. **上传到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/rss-daily-report.git
   git push -u origin main
   ```

2. **配置 Secrets**
   - 在 GitHub 仓库设置中添加 `GOOGLE_CREDENTIALS` 和 `SHEET_ID`

3. **启用 Actions**
   - 在 Actions 标签页启用工作流

4. **测试运行**
   - 手动触发一次，验证配置正确

## 📈 后续扩展建议

如果将来需要，可以轻松扩展以下功能：

1. **HTML 格式报告**
   - 添加 HTML 模板
   - 生成更美观的报告

2. **邮件通知**
   - 每天自动发送报告到邮箱

3. **统计图表**
   - 使用 matplotlib 生成趋势图
   - 关键词词云

4. **AI 摘要**
   - 集成 LLM API
   - 自动生成内容摘要

5. **RSS 订阅**
   - 生成报告的 RSS feed
   - 便于订阅阅读

## ✅ 质量保证

- ✅ 代码有详细注释
- ✅ 支持错误处理
- ✅ 详细的日志输出
- ✅ 配置文件有示例
- ✅ 文档完善齐全
- ✅ 包含使用示例

## 📞 技术支持

使用过程中如有问题：

1. 查看 SETUP_GUIDE.md 的常见问题
2. 查看 GitHub Actions 的运行日志
3. 在 GitHub Issues 中提问

## 🎓 学习建议

如果你想深入了解或修改代码：

1. **学习 gspread 库**
   - 官方文档：https://docs.gspread.org/

2. **学习 Jinja2 模板**
   - 官方文档：https://jinja.palletsprojects.com/

3. **学习 GitHub Actions**
   - 官方文档：https://docs.github.com/cn/actions

## 🎉 总结

这是一个**完整、可用、可扩展**的自动化报告生成系统。

**开箱即用**：按照 QUICK_START.md 配置即可使用  
**高度自动化**：无需手动干预  
**灵活配置**：通过 YAML 文件轻松调整  
**良好文档**：包含详细的使用和设置说明  
**版本控制**：所有报告都有历史记录  

祝使用愉快！如有问题，欢迎随时反馈。🚀
