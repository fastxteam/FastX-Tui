# FastX-Tui 插件开发指南

## 📖 概述

本文档将指导您如何开发 FastX-Tui 插件。FastX-Tui 插件系统支持多文件结构、二进制文件和在线安装，为开发者提供了强大的扩展能力。

## 📁 插件结构

### 插件仓库命名规范

插件仓库必须使用以下命名格式：
```
FastX-Tui-Plugin-{PluginName}
```

其中 `PluginName` 是插件的名称，建议使用驼峰命名法。

### 插件目录结构

一个完整的插件应该包含以下结构：

```
FastX-Tui-Plugin-{PluginName}/
├── fastx_plugin.py          # 插件入口文件（必须，固定命名）
├── pyproject.toml           # 插件元数据和依赖声明
├── README.md                # 插件说明文档
├── LICENSE                  # 许可证文件
├── resources/               # 插件资源文件目录（可选）
└── bin/                     # 二进制文件目录（可选）
```

### 核心文件说明

#### fastx_plugin.py（必须）

这是插件的入口文件，必须包含一个继承自 `Plugin` 类的插件类。该文件包含插件的配置信息和基本结构，业务逻辑应该分离到其他文件中。

#### pyproject.toml

用于声明插件的元数据、依赖项和其他配置信息。

#### README.md

插件的说明文档，包含插件的功能、安装方法和使用说明。

#### LICENSE

插件的许可证文件，默认使用 MIT 许可证。

#### resources/

插件资源文件目录，用于存放插件使用的图片、配置文件等资源。

#### bin/

二进制文件目录，用于存放插件使用的二进制可执行文件。

## 🛠️ 插件开发

### 1. 创建插件目录

首先，创建一个符合命名规范的插件目录：

```bash
mkdir -p plugins/FastX-Tui-Plugin-{PluginName}
```

### 2. 创建入口文件

在插件目录中创建 `fastx_plugin.py` 文件，实现 `Plugin` 接口。

#### 基本结构

```python
#!/usr/bin/env python3
from core.plugin_manager import Plugin, PluginInfo
from core.menu_system import MenuSystem

class {PluginName}Plugin(Plugin):
    """{PluginName} 插件"""
    
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        return PluginInfo(
            name="{PluginName}",
            version="1.0.0",
            author="Your Name",
            description="插件描述",
            category="插件分类",
            tags=["标签1", "标签2"]
        )
    
    def initialize(self):
        """初始化插件"""
        pass
    
    def cleanup(self):
        """清理插件资源"""
        pass
    
    def register(self, menu_system: MenuSystem):
        """注册插件命令到菜单系统"""
        pass
```

#### 必须实现的方法

| 方法名 | 描述 | 必须实现 |
|-------|------|----------|
| `get_info()` | 返回插件信息，包括名称、版本、作者等 | ✅ |
| `initialize()` | 初始化插件资源，如连接数据库、加载配置等 | ✅ |
| `cleanup()` | 清理插件资源，如关闭连接、释放内存等 | ✅ |
| `register()` | 将插件命令注册到菜单系统 | ✅ |

#### 可选实现的方法

| 方法名 | 描述 | 必须实现 |
|-------|------|----------|
| `get_binary_path()` | 返回插件二进制文件路径 | ❌ |
| `get_resource_path()` | 获取插件资源文件路径（已有默认实现） | ❌ |

### 3. 分离业务逻辑

为了保持代码的清晰和可维护性，建议将业务逻辑分离到单独的文件中。例如：

```python
# example_business.py
class ExampleBusiness:
    def __init__(self, plugin_instance):
        self.plugin = plugin_instance
    
    def register_commands(self, menu_system):
        # 注册命令的业务逻辑
        pass
```

然后在入口文件中引用：

```python
from example_business import ExampleBusiness

class ExamplePlugin(Plugin):
    def initialize(self):
        self.business = ExampleBusiness(self)
    
    def register(self, menu_system):
        self.business.register_commands(menu_system)
```

### 4. 注册菜单和命令

插件可以通过 `menu_system` 对象注册菜单和命令。

#### 创建子菜单

```python
def register_commands(self, menu_system):
    # 创建子菜单
    submenu = menu_system.create_submenu(
        menu_id="plugin_submenu",
        name="插件菜单",
        description="插件的专属菜单",
        icon="🔌"
    )
```

#### 注册命令

```python
from core.menu_system import ActionItem, CommandType

def register_commands(self, menu_system):
    # 注册命令
    menu_system.register_item(ActionItem(
        id="plugin_command",
        name="命令名称",
        description="命令描述",
        command_type=CommandType.PYTHON,
        python_func=lambda: "命令执行结果"
    ))
```

#### 将命令添加到菜单

```python
def register_commands(self, menu_system):
    # 将命令添加到子菜单
    submenu.add_item("plugin_command")
    
    # 将命令添加到主菜单
    menu_system.add_item_to_main_menu("plugin_command")
    
    # 将命令添加到现有子菜单
    menu_system.add_item_to_menu("existing_menu_id", "plugin_command")
```

### 5. 访问资源文件

插件可以使用 `get_resource_path()` 方法访问自己的资源文件：

```python
def some_method(self):
    resource_path = self.get_resource_path("resource_name.txt")
    with open(resource_path, 'r') as f:
        content = f.read()
    return content
```

### 6. 使用二进制文件

插件可以使用 `get_binary_path()` 方法获取二进制文件的路径：

```python
def get_binary_path(self) -> str:
    return self.get_resource_path("../bin/plugin_binary")
```

### 7. 使用日志接口

插件可以使用系统提供的日志接口记录日志：

```python
def some_method(self):
    self.log_debug("调试日志")
    self.log_info("信息日志")
    self.log_warning("警告日志")
    self.log_error("错误日志")
    self.log_critical("严重错误日志")
```

## 📋 插件信息

`PluginInfo` 类包含以下字段：

| 字段名 | 类型 | 描述 | 默认值 |
|-------|------|------|--------|
| `name` | `str` | 插件名称 | 必填 |
| `version` | `str` | 插件版本 | 必填 |
| `author` | `str` | 插件作者 | 必填 |
| `description` | `str` | 插件描述 | 必填 |
| `enabled` | `bool` | 是否启用 | `True` |
| `category` | `str` | 插件分类 | `"其他"` |
| `tags` | `List[str]` | 插件标签 | `[]` |
| `compatibility` | `Dict[str, str]` | 兼容性信息 | `{}` |
| `dependencies` | `List[str]` | 依赖项 | `[]` |
| `repository` | `str` | 插件仓库 | `""` |
| `homepage` | `str` | 插件主页 | `""` |
| `license` | `str` | 许可证 | `"MIT"` |
| `last_updated` | `str` | 最后更新时间 | `""` |
| `rating` | `float` | 评分 | `0.0` |
| `downloads` | `int` | 下载次数 | `0` |

## 📦 依赖管理

插件的依赖项应该在 `pyproject.toml` 文件中声明：

```toml
[project]
dependencies = [
    "requests>=2.31.0",
    "numpy>=1.21.0",
]
```

## 🧪 测试插件

### 本地测试

您可以使用以下脚本测试插件是否能够正常加载：

```python
#!/usr/bin/env python3
from core.plugin_manager import PluginManager

plugin_manager = PluginManager(plugin_dir="plugins")
plugin = plugin_manager.load_plugin("FastX-Tui-Plugin-{PluginName}")

if plugin:
    print(f"插件加载成功: {plugin.get_info().name}")
else:
    print("插件加载失败")
```

### 在线测试

将插件发布到 GitHub 仓库，然后通过 FastX-Tui 的插件管理器在线安装和测试。

## 🚀 发布插件

### 1. 准备发布

- 确保插件的命名符合规范
- 确保插件包含所有必要的文件
- 确保插件的依赖项已经在 `pyproject.toml` 中声明
- 编写详细的 `README.md` 文件

### 2. 发布到 GitHub

将插件代码推送到 GitHub 仓库，仓库名称必须符合 `FastX-Tui-Plugin-{PluginName}` 格式。

### 3. 提交到官方插件仓库

联系 FastX-Tui 官方团队，将您的插件添加到官方插件仓库中。

## 📚 最佳实践

1. **分离关注点**：将插件的配置信息和业务逻辑分离到不同的文件中
2. **使用类型提示**：为所有方法和参数添加类型提示
3. **编写文档**：为所有方法和类编写详细的文档字符串
4. **错误处理**：在插件中添加适当的错误处理
5. **资源管理**：及时清理插件使用的资源
6. **日志记录**：使用系统提供的日志接口记录日志
7. **兼容性**：在 `compatibility` 字段中声明插件的兼容性要求
8. **依赖管理**：在 `pyproject.toml` 中声明插件的依赖项

## 🤝 插件安全

1. **不要修改系统核心文件**：插件不应该修改 FastX-Tui 的核心文件
2. **限制权限**：插件应该只请求必要的权限
3. **避免全局变量**：尽量避免使用全局变量
4. **安全的文件操作**：使用系统提供的方法访问文件
5. **防止无限循环**：确保插件不会进入无限循环
6. **错误处理**：使用 try-except 包装所有可能出错的代码

## 📄 许可证

FastX-Tui 插件系统支持各种许可证，默认使用 MIT 许可证。插件开发者可以根据自己的需求选择合适的许可证。

## 📞 联系方式

如果您在开发插件过程中遇到问题，可以通过以下方式联系我们：

- GitHub Issues: [https://github.com/fastxteam/FastX-Tui/issues](https://github.com/fastxteam/FastX-Tui/issues)
- 邮件: team@fastx-tui.com
- 社区: [https://discord.gg/fastx-tui](https://discord.gg/fastx-tui)

## 📋 插件示例

您可以参考 `plugins/FastX-Tui-Plugin-Example` 目录中的示例插件，了解插件的完整结构和实现方式。

## 📖 更新日志

### v1.0.0 (2025-12-21)

- 初始版本
- 支持多文件插件结构
- 支持二进制文件
- 支持资源文件访问
- 支持在线安装和更新
- 提供完善的插件开发指南

## 📌 结论

FastX-Tui 插件系统为开发者提供了强大的扩展能力，支持多文件结构、二进制文件和在线安装。通过遵循本指南，您可以轻松开发和发布 FastX-Tui 插件，为 FastX-Tui 生态系统做出贡献。
