# FastX-Tui 插件开发指南

## 插件类型

FastX-Tui支持两种类型的插件：

1. **单文件插件** - 简单插件，单个Python文件
2. **目录插件** - 复杂插件，支持多文件和依赖管理

## 目录插件结构

推荐使用目录结构的插件，便于管理复杂业务：

```
plugins/
└── FastX-Tui-Plugin-Example/          # 插件目录（推荐命名格式）
    ├── plugin.json                    # 插件配置文件
    ├── main.py                        # 插件入口文件
    ├── requirements.txt               # Python依赖（可选）
    ├── README.md                      # 插件说明（可选）
    └── src/                           # 插件源码目录（可选）
        └── utils.py
```

## plugin.json 配置

**plugin.json** 是目录插件的核心配置文件：

```json
{
  "name": "FastX-Tui-Plugin-Example",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "示例插件，展示FastX-Tui插件系统的使用",
  "repository": "https://github.com/yourusername/FastX-Tui-Plugin-Example",
  "license": "MIT",
  "categories": ["工具", "开发"],
  "permissions": ["network", "file_system"],
  "entry": "main.py",
  "binary": {
    "enabled": false,
    "path": "bin/plugin.exe",
    "args": []
  },
  "dependencies": {
    "python": [
      "requests>=2.28.0",
      "psutil>=5.9.0"
    ],
    "system": []
  },
  "compatibility": {
    "fastx-tui": ">=1.0.0"
  },
  "enabled": true
}
```

## 插件开发

### 1. 继承FastXPlugin基类

```python
#!/usr/bin/env python3
from core.plugin_manager import FastXPlugin, PluginInfo
from core.menu_system import MenuNode, MenuType, ActionItem, CommandType

class ExamplePlugin(FastXPlugin):
    """示例插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "示例插件"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "这是一个示例插件"
        self.repository = "https://github.com/yourusername/FastX-Tui-Plugin-Example"
        self.categories = ["工具", "开发"]
    
    def initialize(self) -> bool:
        """初始化插件"""
        self.log_info("示例插件初始化完成")
        return True
    
    def get_plugin_info(self) -> PluginInfo:
        """获取插件信息"""
        return PluginInfo(
            name=self.name,
            version=self.version,
            author=self.author,
            description=self.description,
            repository=self.repository,
            categories=self.categories
        )
    
    def register_commands(self):
        """注册插件命令到菜单系统"""
        if not self.menu_system:
            self.log_error("菜单系统未初始化")
            return
        
        # 创建示例菜单
        example_menu = MenuNode(
            id="example_menu",
            name="示例菜单",
            description="示例插件功能",
            menu_type=MenuType.SUB,
            icon="📦"
        )
        
        # 注册菜单
        self.menu_system.register_item(example_menu)
        
        # 添加示例功能
        example_action = ActionItem(
            id="example_action",
            name="示例功能",
            description="这是一个示例功能",
            icon="✨",
            command_type=CommandType.PYTHON,
            python_func=self.example_function,
            args=["Hello, FastX-Tui!"]
        )
        
        self.menu_system.register_item(example_action)
        example_menu.add_item("example_action")
        
        # 将菜单添加到主菜单
        main_menu = self.menu_system.get_item_by_id("main_menu")
        if main_menu and hasattr(main_menu, 'add_item'):
            main_menu.add_item("example_menu")
    
    def example_function(self, message: str) -> str:
        """示例功能实现"""
        return f"✅ 示例功能执行成功！\n\n📝 消息: {message}"
    
    def cleanup(self):
        """清理插件资源"""
        self.log_info("示例插件清理完成")
```

### 2. 单文件插件（兼容旧版）

```python
#!/usr/bin/env python3
from core.plugin_manager import FastXPlugin, PluginInfo
from core.menu_system import MenuNode, MenuType, ActionItem, CommandType

class SimplePlugin(FastXPlugin):
    """简单插件"""
    
    def initialize(self) -> bool:
        """初始化插件"""
        self.name = "简单插件"
        self.version = "1.0.0"
        return True
    
    def register_commands(self):
        """注册命令"""
        # 实现命令注册逻辑
        pass
```

## 插件安装

### 1. 本地安装

将插件目录或Python文件放入 `plugins/` 目录下即可。

### 2. 从GitHub安装

使用插件管理器的 `install_from_github` 方法，支持HTTPS和SSH格式：

```python
plugin_manager.install_from_github("https://github.com/yourusername/FastX-Tui-Plugin-Example")
# 或
plugin_manager.install_from_github("git@github.com:yourusername/FastX-Tui-Plugin-Example.git")
```

## 插件使用

### 加载插件

```python
# 加载所有插件
plugin_manager.load_all_plugins()

# 加载单个插件
plugin_manager.load_plugin("example_plugin")

# 从GitHub URL加载并安装
plugin_manager.load_plugin_from_url("https://github.com/yourusername/FastX-Tui-Plugin-Example")
```

### 插件管理

```python
# 列出所有插件
plugins = plugin_manager.list_plugins()

# 按分类获取插件
plugins = plugin_manager.get_plugins_by_category("工具")

# 搜索插件
plugins = plugin_manager.search_plugins("示例")

# 启用/禁用插件
plugin_manager.enable_plugin("example_plugin")
plugin_manager.disable_plugin("example_plugin")

# 检查插件更新
updates = plugin_manager.check_updates()

# 卸载插件
plugin_manager.uninstall_plugin("example_plugin")
```

## 插件API

### FastXPlugin基类

- `initialize()` - 初始化插件
- `register_commands()` - 注册命令
- `get_plugin_info()` - 获取插件信息
- `cleanup()` - 清理资源
- `on_unload()` - 插件卸载时调用
- `on_system_event(event_name, data)` - 系统事件监听
- `log_debug(msg)` - 记录调试日志
- `log_info(msg)` - 记录信息日志
- `log_warning(msg)` - 记录警告日志
- `log_error(msg)` - 记录错误日志
- `log_critical(msg)` - 记录严重错误日志

### 日志API

插件可以使用内置的日志系统：

```python
self.log_info("插件信息")
self.log_error("插件错误")
```

### 菜单API

通过 `self.menu_system` 访问菜单系统，用于注册菜单项和命令。

## 最佳实践

1. **命名规范** - 推荐使用 `FastX-Tui-Plugin-{Name}` 格式命名GitHub仓库
2. **版本管理** - 使用语义化版本号（如 1.0.0）
3. **依赖管理** - 在 `plugin.json` 中声明所有依赖
4. **错误处理** - 所有操作都应包含适当的错误处理
5. **权限声明** - 明确声明插件需要的权限
6. **日志记录** - 关键操作添加日志
7. **资源清理** - 在 `cleanup()` 方法中释放资源
8. **兼容性** - 在 `compatibility` 中声明兼容的FastX-Tui版本

## 插件示例

### 1. 简单示例插件

```python
from core.plugin_manager import FastXPlugin

class HelloPlugin(FastXPlugin):
    def initialize(self):
        self.name = "Hello Plugin"
        self.version = "1.0.0"
        return True
    
    def register_commands(self):
        if self.menu_system:
            action = ActionItem(
                id="hello",
                name="Hello",
                description="Say hello",
                icon="👋",
                command_type=CommandType.PYTHON,
                python_func=lambda: "Hello from plugin!"
            )
            self.menu_system.register_item(action)
```

### 2. 网络工具插件示例

```python
import requests
from core.plugin_manager import FastXPlugin

class NetworkPlugin(FastXPlugin):
    def initialize(self):
        self.name = "Network Tools"
        self.version = "1.0.0"
        self.categories = ["网络", "工具"]
        return True
    
    def check_website(self, url):
        try:
            response = requests.get(url, timeout=5)
            return f"✅ {url} - Status: {response.status_code}"
        except Exception as e:
            return f"❌ {url} - Error: {str(e)}"
```

## 插件安全

1. **权限控制** - 插件需要声明权限，系统会根据权限限制插件功能
2. **沙箱环境** - 插件在独立环境中运行，防止冲突
3. **错误隔离** - 单个插件的错误不会影响整个系统
4. **动态加载** - 插件可以动态加载和卸载，无需重启系统
5. **版本验证** - 支持插件版本检查和更新

## 常见问题

### Q: 插件加载失败怎么办？
A: 检查插件目录结构是否正确，plugin.json配置是否完整，入口文件是否存在。

### Q: 如何调试插件？
A: 使用插件内置的日志系统，或查看系统日志文件。

### Q: 插件可以使用哪些第三方库？
A: 可以在plugin.json的dependencies中声明，系统会自动安装。

### Q: 插件支持哪些语言？
A: 目前主要支持Python，未来可能扩展到其他语言。

## 插件仓库

### 官方推荐插件

1. **FastX-Tui-Plugin-Network** - 网络工具插件
2. **FastX-Tui-Plugin-FileManager** - 文件管理插件
3. **FastX-Tui-Plugin-SystemMonitor** - 系统监控插件
4. **FastX-Tui-Plugin-DevTools** - 开发工具插件

### 如何发布插件

1. 创建符合命名规范的GitHub仓库
2. 编写plugin.json和插件代码
3. 发布版本（使用语义化版本号）
4. 将插件添加到官方推荐列表

---

**开始开发你的第一个FastX-Tui插件吧！** 🚀
