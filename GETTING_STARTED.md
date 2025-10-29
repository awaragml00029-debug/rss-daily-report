# 🎯 开始使用

欢迎使用 RSS Daily Report Generator！

## 📚 文档导航

根据你的需求选择合适的文档：

### 🚀 快速开始
- **[QUICKSTART.md](QUICKSTART.md)** - 5分钟快速部署指南
- **[SETUP.md](SETUP.md)** - 详细设置步骤
- **[CHECKLIST.md](CHECKLIST.md)** - 部署前检查清单

### 📖 深入了解
- **[README.md](README.md)** - 完整项目文档
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - 技术架构和工作原理
- **[reports/](reports/)** - 查看示例报告

### 🔧 配置与使用
- **[config.yaml](config.yaml)** - 配置文件
- **[test.py](test.py)** - 本地测试脚本
- **[scripts/generate_report.py](scripts/generate_report.py)** - 核心代码

## 🎬 推荐路径

### 新手用户
1. 阅读 [QUICKSTART.md](QUICKSTART.md)
2. 按照步骤操作
3. 遇到问题查看 [README.md](README.md) 的故障排查部分

### 进阶用户
1. 阅读 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) 了解架构
2. 根据需求修改 [config.yaml](config.yaml)
3. 查看 [scripts/generate_report.py](scripts/generate_report.py) 自定义功能

## 📝 快速参考

### 重要文件位置
```
rss-daily-report/
├── config.yaml                    # 配置文件（修改关键词）
├── .github/workflows/             # GitHub Actions（修改运行时间）
├── scripts/generate_report.py    # 主程序（修改报告格式）
└── reports/                       # 生成的报告
```

### 常用命令
```bash
# 本地测试
python test.py --mode mock

# 手动生成报告
python scripts/generate_report.py --mode daily

# 生成指定日期
python scripts/generate_report.py --mode daily --date 2025-10-29
```

## 🆘 需要帮助？

1. 查看 [README.md](README.md) 的常见问题
2. 检查 GitHub Actions 日志
3. 在 GitHub 提交 Issue

---

**准备好了吗？从 [QUICKSTART.md](QUICKSTART.md) 开始吧！** 🚀
