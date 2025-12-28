# 安装指南

## 环境要求

FastX-Tui 需要以下环境：

- Python 3.10 或更高版本
- Windows、macOS 或 Linux 操作系统

## 安装方法

### 1. 使用 pip 安装

```bash
pip install fastx-tui
```

### 2. 从源代码安装

```bash
# 克隆仓库
git clone https://github.com/FastXTeam/FastX-Tui.git
cd FastX-Tui

# 安装依赖
uv pip install -e .
```

### 3. 安装开发版本

```bash
pip install --upgrade git+https://github.com/FastXTeam/FastX-Tui.git
```

## 验证安装

安装完成后，可以使用以下命令验证 FastX-Tui 是否成功安装：

```bash
fastx-tui --version
```

如果安装成功，会显示 FastX-Tui 的版本信息。

## 升级 FastX-Tui

### 使用 pip 升级

```bash
pip install --upgrade fastx-tui
```

### 从源代码升级

```bash
cd FastX-Tui
git pull
uv pip install -e .
```

## 卸载 FastX-Tui

```bash
pip uninstall fastx-tui
```

## 安装依赖问题

如果在安装过程中遇到依赖问题，可以尝试以下方法：

1. 升级 pip：
   ```bash
   pip install --upgrade pip
   ```

2. 使用 uv 安装：
   ```bash
   uv pip install fastx-tui
   ```

3. 安装特定版本的依赖：
   ```bash
   pip install fastx-tui[all]
   ```

## 下一步

安装完成后，您可以继续阅读 [入门指南](getting_started.md) 了解如何使用 FastX-Tui。
