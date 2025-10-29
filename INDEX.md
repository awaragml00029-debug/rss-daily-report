# 📖 文档索引

欢迎使用 RSS Daily Report！这个索引帮助你快速找到需要的文档。

---

## 🚀 快速开始

**首次使用？从这里开始：**

1. 📘 [QUICK_START.md](QUICK_START.md) - **5分钟快速上手**
2. 📗 [SETUP_GUIDE.md](SETUP_GUIDE.md) - **详细设置指南**
3. 📕 [README.md](README.md) - **完整项目说明**

---

## 📚 按用途查找

### 🎯 我想快速开始使用

👉 直接阅读：[QUICK_START.md](QUICK_START.md)

最快的方式，5 分钟内完成配置并生成第一份报告。

---

### 🔧 我需要详细的设置说明

👉 阅读：[SETUP_GUIDE.md](SETUP_GUIDE.md)

包含完整的步骤说明、截图、常见问题解答。

---

### 📖 我想了解所有功能

👉 阅读：[README.md](README.md)

完整的功能介绍、使用说明、配置选项。

---

### 🗂️ 我想了解项目结构

👉 阅读：[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

详细的目录结构、文件用途、使用流程。

---

### 📊 我想查看完整项目信息

👉 阅读：[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

项目概述、技术栈、设计亮点、扩展建议。

---

### 📋 我想查看所有文件清单

👉 阅读：[FILE_LIST.md](FILE_LIST.md)

完整的文件列表、每个文件的详细说明、文件大小统计。

---

### ⚙️ 我想修改配置

👉 编辑：[config.yaml](config.yaml)  
👉 参考：[config.example.yaml](config.example.yaml)

配置文件包含所有可调整的选项，示例文件有详细注释。

---

### 🖥️ 我想在本地测试

👉 运行：[test.sh](test.sh)

一键检查环境、安装依赖、运行测试。

---

### 💻 我想修改代码

👉 查看：[scripts/generate_report.py](scripts/generate_report.py)  
👉 阅读：[CONTRIBUTING.md](CONTRIBUTING.md)

主程序代码和贡献指南。

---

### 📅 我想看报告示例

👉 查看日报：[reports/2025/10/daily-2025-10-29.md](reports/2025/10/daily-2025-10-29.md)  
👉 查看月报：[reports/2025/monthly-2025-10.md](reports/2025/monthly-2025-10.md)

了解最终生成的报告格式。

---

### 🔄 我想了解更新历史

👉 阅读：[CHANGELOG.md](CHANGELOG.md)

版本历史、功能变更、Bug 修复记录。

---

### 🤝 我想为项目做贡献

👉 阅读：[CONTRIBUTING.md](CONTRIBUTING.md)

贡献指南、代码规范、提交流程。

---

### ⚖️ 我想了解许可证

👉 阅读：[LICENSE](LICENSE)

MIT 开源许可证。

---

## 📊 文档路线图

### 路线 1：快速使用（10分钟）
```
QUICK_START.md
    ↓
运行 test.sh
    ↓
开始使用
```

### 路线 2：深入了解（30分钟）
```
README.md
    ↓
SETUP_GUIDE.md
    ↓
PROJECT_STRUCTURE.md
    ↓
开始使用
```

### 路线 3：完全掌握（1小时）
```
README.md
    ↓
SETUP_GUIDE.md
    ↓
PROJECT_SUMMARY.md
    ↓
FILE_LIST.md
    ↓
查看代码
    ↓
完全掌握
```

---

## 🎯 常见场景

### 场景 1：我是新手，第一次使用

**推荐阅读顺序：**
1. README.md（了解项目）
2. QUICK_START.md（快速开始）
3. SETUP_GUIDE.md（遇到问题时查阅）

### 场景 2：我想调整关键词

**直接操作：**
1. 编辑 config.yaml
2. 修改 keywords 部分
3. 提交到 GitHub
4. 等待下次自动运行

### 场景 3：报告格式不满意

**需要修改：**
1. 查看 scripts/generate_report.py
2. 找到 `_get_daily_template()` 方法
3. 修改 Jinja2 模板
4. 本地测试
5. 提交修改

### 场景 4：出现错误

**故障排查：**
1. 查看 GitHub Actions 日志
2. 阅读 SETUP_GUIDE.md 常见问题部分
3. 检查配置文件
4. 在 Issues 中提问

---

## 📞 获取帮助

### 自助解决

1. ✅ 查看 [SETUP_GUIDE.md](SETUP_GUIDE.md) 的常见问题部分
2. ✅ 查看 GitHub Actions 运行日志
3. ✅ 检查配置文件是否正确

### 寻求帮助

1. 📝 在 GitHub Issues 中提问
2. 📧 提供详细的错误信息
3. 📊 附上配置文件（隐藏敏感信息）

---

## 🗺️ 完整文档地图

```
rss-daily-report/
│
├── 📘 入门文档
│   ├── README.md           ⭐ 项目主文档
│   ├── QUICK_START.md      ⭐ 5分钟上手
│   └── SETUP_GUIDE.md      ⭐ 详细设置
│
├── 📗 项目信息
│   ├── PROJECT_SUMMARY.md  📊 项目总结
│   ├── PROJECT_STRUCTURE.md 🗂️ 结构说明
│   ├── FILE_LIST.md        📋 文件清单
│   └── INDEX.md            📖 本文档
│
├── 📕 开发文档
│   ├── CONTRIBUTING.md     🤝 贡献指南
│   ├── CHANGELOG.md        🔄 更新历史
│   └── LICENSE             ⚖️ 许可证
│
├── ⚙️ 配置文件
│   ├── config.yaml         🔧 主配置
│   └── config.example.yaml 📝 配置示例
│
├── 🖥️ 代码文件
│   ├── scripts/generate_report.py  💻 主程序
│   └── test.sh                     🧪 测试脚本
│
├── 📊 示例报告
│   ├── daily-2025-10-29.md    📅 日报示例
│   └── monthly-2025-10.md     📆 月报示例
│
└── 🤖 自动化
    └── .github/workflows/generate-report.yml
```

---

## ✨ 提示

- 💡 **新手**：从 QUICK_START.md 开始
- 💡 **进阶**：阅读 SETUP_GUIDE.md 和 PROJECT_SUMMARY.md
- 💡 **开发**：查看 CONTRIBUTING.md 和源代码
- 💡 **问题**：查看 SETUP_GUIDE.md 常见问题部分

---

**最后更新**：2025-10-29  
**文档版本**：1.0.0

祝使用愉快！🎉
