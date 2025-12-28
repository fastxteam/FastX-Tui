# 贡献指南

## 概述

感谢您对 FastX-Tui 项目的兴趣！本文档将指导您如何为 FastX-Tui 项目做出贡献，包括报告 Bug、提交功能请求、提交代码等。

## 行为准则

参与 FastX-Tui 项目的每个人都应遵循以下行为准则：

- 尊重他人，包括不同观点和经验
- 保持开放和包容的态度
- 专注于项目的最佳利益
- 接受建设性的反馈
- 避免人身攻击和歧视性语言

## 贡献方式

### 1. 报告 Bug

如果您发现了 Bug，可以通过以下方式报告：

1. **搜索现有 Issue**：首先搜索 GitHub Issues，看看是否已经有人报告了相同的 Bug
2. **创建新 Issue**：如果没有找到相关 Issue，创建一个新的 Issue
3. **提供详细信息**：
   - 清晰的标题和描述
   - FastX-Tui 版本
   - 操作系统和 Python 版本
   - 重现步骤
   - 预期行为
   - 实际行为
   - 错误日志（如果有）
   - 截图或录屏（如果有）

### 2. 提交功能请求

如果您有新功能的想法，可以通过以下方式提交：

1. **搜索现有 Issue**：首先搜索 GitHub Issues，看看是否已经有人提出了相同的功能请求
2. **创建新 Issue**：如果没有找到相关 Issue，创建一个新的 Issue
3. **提供详细信息**：
   - 清晰的标题和描述
   - 功能的目的和价值
   - 功能的详细描述
   - 实现建议（如果有）
   - 截图或原型（如果有）

### 3. 提交代码

如果您想直接贡献代码，可以通过以下方式：

1. **Fork 仓库**：在 GitHub 上 Fork FastX-Tui 仓库
2. **克隆仓库**：将 Fork 后的仓库克隆到本地
3. **创建分支**：创建一个新的分支来开发您的功能或修复 Bug
4. **编写代码**：实现功能或修复 Bug
5. **运行测试**：确保所有测试都通过
6. **提交代码**：提交您的代码，使用符合规范的提交信息
7. **创建 Pull Request**：在 GitHub 上创建 Pull Request

### 4. 改进文档

文档改进也是非常重要的贡献：

1. **改进现有文档**：修复文档中的错误、补充遗漏的信息
2. **添加新文档**：为新功能或复杂功能添加文档
3. **翻译文档**：将文档翻译成其他语言

### 5. 测试和反馈

测试是确保软件质量的重要环节：

1. **测试新功能**：测试最新的开发版本，提供反馈
2. **报告兼容性问题**：在不同环境中测试，报告兼容性问题
3. **提供性能反馈**：报告性能问题和优化建议

## 代码贡献流程

### 1. Fork 和克隆仓库

```bash
# Fork 仓库（在 GitHub 上操作）

# 克隆 Fork 后的仓库
git clone https://github.com/your-username/FastX-Tui.git
cd FastX-Tui

# 添加上游仓库
git remote add upstream https://github.com/FastXTeam/FastX-Tui.git
```

### 2. 创建分支

```bash
# 拉取最新代码
git checkout develop
git pull upstream develop

# 创建新分支
git checkout -b feature/feature-name
```

### 3. 编写代码

- 遵循项目的代码规范
- 编写测试用例
- 编写文档

### 4. 运行测试

```bash
# 运行代码检查
uv run ruff check .

# 自动修复代码
uv run ruff check . --fix

# 格式化代码
uv run ruff format .

# 运行测试
uv run pytest
```

### 5. 提交代码

```bash
# 添加更改
git add .

# 提交更改（使用符合规范的提交信息）
git commit -m "feat: 添加新功能"

# 推送到 Fork 仓库
git push origin feature/feature-name
```

### 6. 创建 Pull Request

1. 在 GitHub 上导航到您的 Fork 仓库
2. 点击「New Pull Request」按钮
3. 选择目标分支（通常是 `develop`）
4. 添加详细的描述
5. 关联相关的 Issue
6. 点击「Create Pull Request」按钮

### 7. 代码审查

- 等待项目维护者审查您的代码
- 根据审查意见修改代码
- 重新提交代码

### 8. 合并代码

- 代码审查通过后，项目维护者会合并您的代码
- 合并后，您可以删除您的分支

## 贡献者的权利和责任

### 权利

- 参与项目决策
- 获得项目维护者的支持和指导
- 获得社区的认可和感谢

### 责任

- 遵循项目的规范和流程
- 保持代码质量
- 尊重其他贡献者
- 提供有用的反馈

## 被认可的贡献

所有贡献者都会在以下地方被认可：

- GitHub 贡献者列表
- 项目文档的贡献者部分
- 发布说明中的致谢

## 常见问题

### 1. 如何获得帮助？

- 查看现有文档
- 在 GitHub Issues 中搜索相关问题
- 在 GitHub Discussions 中提问
- 加入项目的社区频道

### 2. 如何成为项目维护者？

项目维护者是通过邀请产生的，通常是对项目有重大贡献的人。如果您想成为项目维护者，可以通过持续的高质量贡献来展示您的能力和对项目的承诺。

### 3. 如何处理冲突？

- 保持冷静和专业
- 专注于问题本身，而不是人
- 寻求第三方的调解
- 遵循项目的决策流程

## 致谢

感谢所有为 FastX-Tui 项目做出贡献的人！您的贡献对于项目的成功至关重要。

## 联系我们

- **GitHub Issues**：https://github.com/FastXTeam/FastX-Tui/issues
- **GitHub Discussions**：https://github.com/FastXTeam/FastX-Tui/discussions
- **电子邮件**：team@fastx-tui.com

---

再次感谢您对 FastX-Tui 项目的支持和贡献！
