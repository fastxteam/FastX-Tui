# 开发环境

## 概述

本文档介绍了如何搭建 FastX-Tui 的开发环境，包括依赖安装、代码结构和开发工具。

## 环境要求

- Python 3.10 或更高版本
- Git
- 适当的 IDE 或文本编辑器（推荐 VS Code、PyCharm）
- 操作系统：Windows、macOS 或 Linux

## 安装依赖

### 1. 克隆仓库

```bash
git clone https://github.com/FastXTeam/FastX-Tui.git
cd FastX-Tui
```

### 2. 安装 uv（推荐）

uv 是一个现代的 Python 包管理器，比 pip 更快、更高效。

```bash
# 安装 uv
pip install uv
```

### 3. 安装依赖

```bash
# 安装开发依赖
uv pip install -e .[dev]
```

### 4. 安装预提交钩子

```bash
uv pip install pre-commit
pre-commit install
```

## 代码结构

FastX-Tui 采用了模块化的代码结构，主要包括以下目录：

### 1. 核心模块 (`core/`)

包含 FastX-Tui 的核心功能：

- `app_manager.py` - 应用管理器
- `config_manager.py` - 配置管理器
- `plugin_manager.py` - 插件管理器
- `menu_system.py` - 菜单系统
- `view_manager.py` - 视图管理器
- `task_manager.py` - 任务管理器

### 2. 功能模块 (`features/`)

包含 FastX-Tui 的各种功能：

- `config/` - 配置功能
- `help/` - 帮助功能
- `logging/` - 日志功能
- `plugin/` - 插件功能
- `search/` - 搜索功能
- `task/` - 任务功能
- `update/` - 更新功能

### 3. 模型 (`models/`)

包含数据模型：

- `config_schema.py` - 配置模式
- `plugin_schema.py` - 插件模式

### 4. 插件 (`plugins/`)

包含示例插件：

- `FastX-Tui-Plugin-Example/` - 基础示例插件
- `FastX-Tui-Plugin-DEMFaultAnalyzer/` - 高级示例插件

### 5. 工具 (`tools/`)

包含开发和部署工具：

- `build_commands.py` - 构建命令
- `docs_commands.py` - 文档命令
- `ruff_commands.py` - 代码检查命令

### 6. 文档 (`docs/`)

包含项目文档。

## 开发工具

### 1. IDE 推荐

- **VS Code**：轻量级编辑器，支持 Python 开发
- **PyCharm**：专业的 Python IDE，功能强大

### 2. 推荐插件

#### VS Code 插件

- Python
- Pylance
- Ruff
- GitLens
- YAML
- Prettier

#### PyCharm 插件

- Ruff
- GitToolBox
- YAML/Ansible support

### 3. 代码检查工具

FastX-Tui 使用 Ruff 进行代码检查和格式化：

```bash
# 运行代码检查
uv run ruff check .

# 自动修复代码
uv run ruff check . --fix

# 格式化代码
uv run ruff format .
```

### 4. 测试工具

FastX-Tui 使用 pytest 进行测试：

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_example.py

# 运行特定测试用例
uv run pytest tests/test_example.py::test_function
```

## 运行开发版本

### 1. 直接运行

```bash
# 运行开发版本
python main.py

# 启用调试模式
python main.py --debug
```

### 2. 安装为开发模式

```bash
# 安装为开发模式
uv pip install -e .

# 运行
fastx-tui
```

## 开发工作流

### 1. 创建分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 编写代码

- 遵循项目的代码风格
- 添加适当的类型提示
- 编写详细的文档字符串
- 编写测试用例

### 3. 运行测试

```bash
# 运行代码检查
uv run ruff check .

# 运行测试
uv run pytest
```

### 4. 提交代码

```bash
git add .
git commit -m "feat: 添加新功能"
```

### 5. 推送分支

```bash
git push -u origin feature/your-feature-name
```

### 6. 创建 Pull Request

在 GitHub 上创建 Pull Request，等待代码审查。

## 开发技巧

### 1. 使用调试模式

```bash
python main.py --debug
```

调试模式将输出更详细的日志，有助于开发和调试。

### 2. 热重载

FastX-Tui 支持热重载，当代码文件发生变化时，应用会自动重新加载：

```bash
uv run python -m tools.dev_server
```

### 3. 查看日志

开发过程中可以通过以下方式查看日志：

- 在应用中按 `L` 键查看日志
- 直接查看日志文件（位于 `~/.config/fastx-tui/logs/`）
- 在终端中查看实时日志：
  ```bash
  tail -f ~/.config/fastx-tui/logs/fastx-tui_*.log
  ```

## 常见问题

### 1. 依赖冲突

如果遇到依赖冲突，可以尝试：

```bash
# 清理缓存
uv cache clean

# 重新安装依赖
uv pip install -e .[dev]
```

### 2. 预提交钩子失败

如果预提交钩子失败，可以尝试：

```bash
# 手动运行预提交钩子
pre-commit run --all-files

# 跳过预提交钩子（不推荐）
git commit -m "feat: 添加新功能" --no-verify
```

### 3. 测试失败

如果测试失败，可以尝试：

```bash
# 运行特定测试用例并显示详细信息
uv run pytest tests/test_example.py::test_function -v
```

## 下一步

- 了解 [开发流程](workflow.md)
- 学习 [贡献指南](contributing.md)
- 开始 [开发插件](../plugin_development/guide.md)
