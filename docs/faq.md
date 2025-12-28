# 常见问题

## 概述

本文档收集了 FastX-Tui 的常见问题和解答，帮助用户解决使用过程中遇到的问题。

## 安装问题

### 1. 如何安装 FastX-Tui？

您可以使用 pip 或 uv 安装 FastX-Tui：

```bash
# 使用 pip 安装
pip install fastx-tui

# 使用 uv 安装（推荐）
uv pip install fastx-tui
```

### 2. 安装时遇到依赖冲突怎么办？

如果遇到依赖冲突，可以尝试以下方法：

```bash
# 升级 pip
pip install --upgrade pip

# 使用 uv 安装
uv pip install fastx-tui

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
pip install fastx-tui
```

### 3. 如何验证 FastX-Tui 是否安装成功？

```bash
fastx-tui --version
```

如果安装成功，会显示 FastX-Tui 的版本信息。

## 使用问题

### 1. 如何启动 FastX-Tui？

```bash
# 直接启动
fastx-tui

# 启用调试模式
fastx-tui --debug
```

### 2. 如何查看任务列表？

按 `T` 键快速打开任务列表，或从主菜单选择「任务管理」。

### 3. 如何打开设置？

按 `S` 键打开设置界面，或从主菜单选择「设置」。

### 4. 如何查看帮助？

按 `H` 键查看帮助信息，或从主菜单选择「帮助」。

### 5. 如何退出 FastX-Tui？

按 `Q` 键退出 FastX-Tui，或从主菜单选择「退出」。

### 6. 如何查看日志？

从主菜单选择「日志管理」，然后选择「查看日志」。

### 7. 如何安装插件？

从主菜单选择「插件管理」，然后选择「安装插件」。

## 配置问题

### 1. 配置文件在哪里？

配置文件位于以下位置：

- **Windows**: `%APPDATA%\FastX-Tui\config.yml`
- **macOS**: `~/.config/fastx-tui/config.yml`
- **Linux**: `~/.config/fastx-tui/config.yml`

### 2. 如何恢复默认配置？

1. 按 `S` 键打开设置界面
2. 选择「高级设置」
3. 选择「恢复默认配置」
4. 确认恢复

或者直接删除配置文件，FastX-Tui 会自动重新创建默认配置文件。

### 3. 如何自定义键位？

编辑配置文件，添加自定义键位映射：

```yaml
keyboard:
  key_bindings:
    "main_menu":
      "q": "quit"
      "h": "help"
```

## 插件问题

### 1. 如何开发插件？

请参考 [插件开发指南](plugin_development/guide.md)。

### 2. 插件无法加载怎么办？

- 检查插件是否符合 FastX-Tui 插件规范
- 检查插件依赖是否已安装
- 检查插件日志，查看具体错误信息
- 确保插件版本与 FastX-Tui 版本兼容

### 3. 插件运行缓慢怎么办？

- 检查插件是否使用了过多资源
- 确保插件代码高效
- 考虑将耗时操作改为异步执行

## 性能问题

### 1. FastX-Tui 运行缓慢怎么办？

- 关闭不必要的插件
- 禁用动画效果
- 启用紧凑模式
- 减少日志级别
- 调整工作线程数量

### 2. 如何优化 FastX-Tui 性能？

- 关闭不必要的功能
- 调整配置参数
- 定期清理缓存和日志
- 确保系统资源充足

## 兼容性问题

### 1. FastX-Tui 支持哪些操作系统？

FastX-Tui 支持 Windows、macOS 和 Linux 操作系统。

### 2. FastX-Tui 支持哪些 Python 版本？

FastX-Tui 支持 Python 3.10 或更高版本。

### 3. FastX-Tui 与其他软件冲突吗？

FastX-Tui 是一个独立的应用程序，通常不会与其他软件冲突。如果遇到冲突，建议：

- 检查是否有端口冲突
- 尝试在虚拟环境中运行
- 更新 FastX-Tui 到最新版本

## 故障排除

### 1. FastX-Tui 无法启动怎么办？

- 检查 Python 版本是否符合要求
- 检查 FastX-Tui 是否已正确安装
- 尝试重新安装 FastX-Tui
- 查看错误日志

### 2. 遇到崩溃怎么办？

- 检查错误日志，查看崩溃原因
- 尝试禁用最近安装的插件
- 更新 FastX-Tui 到最新版本
- 报告问题到 GitHub Issues

### 3. 如何获取帮助？

- 查看 [官方文档](https://fastxteam.github.io/FastX-Tui/)
- 在 GitHub Issues 中搜索或创建问题
- 加入项目社区频道

## 高级问题

### 1. 如何贡献代码？

请参考 [贡献指南](development/contributing.md)。

### 2. 如何构建 FastX-Tui？

```bash
# 克隆仓库
git clone https://github.com/FastXTeam/FastX-Tui.git
cd FastX-Tui

# 安装依赖
uv pip install -e .[dev]

# 构建包
uv build
```

### 3. 如何运行测试？

```bash
uv run pytest
```

## 联系我们

如果您遇到了文档中没有涵盖的问题，可以通过以下方式联系我们：

- **GitHub Issues**：https://github.com/FastXTeam/FastX-Tui/issues
- **GitHub Discussions**：https://github.com/FastXTeam/FastX-Tui/discussions
- **电子邮件**：team@fastx-tui.com
