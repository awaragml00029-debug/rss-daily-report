# 贡献指南

感谢你考虑为 RSS Daily Report 做贡献！🎉

## 📋 如何贡献

### 报告 Bug

如果你发现了 Bug，请：

1. 检查 [Issues](https://github.com/your-username/rss-daily-report/issues) 中是否已有类似问题
2. 如果没有，创建新 Issue，包含：
   - 清晰的标题
   - 详细的问题描述
   - 复现步骤
   - 预期行为 vs 实际行为
   - 环境信息（操作系统、Python 版本等）
   - 相关截图或日志

### 建议新功能

我们欢迎新想法！请：

1. 先在 Issues 中讨论你的想法
2. 说明为什么这个功能有用
3. 如果可能，提供实现思路

### 提交代码

1. **Fork 仓库**
   ```bash
   # Fork 后克隆到本地
   git clone https://github.com/your-username/rss-daily-report.git
   cd rss-daily-report
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **进行修改**
   - 遵循代码风格
   - 添加必要的注释
   - 更新相关文档

4. **测试修改**
   ```bash
   # 运行测试脚本
   ./test.sh
   
   # 或手动测试
   python scripts/generate_report.py
   ```

5. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   # 或
   git commit -m "fix: 修复某个问题"
   ```

6. **推送到 GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 在 GitHub 上创建 Pull Request
   - 清晰描述你的修改
   - 引用相关的 Issue

## 📝 代码风格

### Python 代码

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 风格指南
- 使用 4 个空格缩进
- 函数和方法添加文档字符串
- 变量命名使用小写加下划线

```python
def fetch_data(self, date=None):
    """
    从 Google Sheets 获取数据
    
    Args:
        date: 指定日期，格式 'YYYY-MM-DD'
    
    Returns:
        list: 数据列表
    """
    pass
```

### 提交信息

使用 [约定式提交](https://www.conventionalcommits.org/zh-hans/) 格式：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式调整（不影响功能）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具/依赖更新

示例：
```
feat: 添加 HTML 格式报告导出功能

- 实现 HTML 模板
- 添加样式表
- 更新配置选项
```

## 🧪 测试

在提交 PR 之前，请确保：

- [ ] 代码能够正常运行
- [ ] 没有引入新的错误
- [ ] 更新了相关文档
- [ ] 测试了边缘情况

## 📚 文档

如果你的修改影响到使用方式：

- 更新 README.md
- 更新 SETUP_GUIDE.md
- 添加示例（如果适用）
- 更新 CHANGELOG.md

## 🎯 优先级

我们特别欢迎以下类型的贡献：

1. **Bug 修复**：让项目更稳定
2. **文档改进**：让新用户更容易上手
3. **性能优化**：提升运行效率
4. **新功能**：增强实用性

## ❓ 问题讨论

不确定从哪里开始？可以：

1. 查看标有 `good first issue` 的 Issues
2. 查看标有 `help wanted` 的 Issues
3. 在 Discussions 中提问

## 🤝 行为准则

- 尊重他人
- 包容不同观点
- 友好地提供建设性反馈
- 关注对项目最有利的事情

## 📜 许可证

通过贡献，你同意你的代码将以 [MIT License](LICENSE) 发布。

---

再次感谢你的贡献！🙏
