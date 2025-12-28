# 示例插件

## 概述

FastX-Tui 提供了多个示例插件，用于展示插件系统的功能和最佳实践。这些示例插件可以作为您开发自己插件的参考。

## 示例插件列表

### 1. FastX-Tui-Plugin-Example

**描述**：这是一个基础示例插件，展示了插件系统的基本功能。

**功能**：
- 插件基本结构
- 菜单注册
- 命令执行
- 日志记录

**目录结构**：
```
FastX-Tui-Plugin-Example/
├── fastx_tui_plugin.py      # 插件入口文件
├── example_business.py      # 业务逻辑文件
├── README.md                # 插件说明文档
├── LICENSE                  # 许可证文件
├── pyproject.toml           # 插件元数据
├── config_schema.json       # 配置模式
├── manual.md                # 插件手册
├── resources/               # 资源文件目录
│   └── example.txt          # 示例资源文件
└── demos/                   # 演示代码目录
    └── rich/                # Rich 库演示
```

**使用方法**：
1. 安装示例插件
2. 在主菜单中选择「示例插件」
3. 浏览示例插件的功能

### 2. FastX-Tui-Plugin-DEMFaultAnalyzer

**描述**：这是一个高级示例插件，展示了插件系统的高级功能。

**功能**：
- 多文件插件结构
- 二进制文件支持
- 复杂业务逻辑
- 配置管理

**目录结构**：
```
FastX-Tui-Plugin-DEMFaultAnalyzer/
├── fastx_tui_plugin.py      # 插件入口文件
├── dem_fault_analyzer.py    # 业务逻辑文件
├── README.md                # 插件说明文档
├── LICENSE                  # 许可证文件
├── pyproject.toml           # 插件元数据
├── config_schema.json       # 配置模式
└── manual.md                # 插件手册
```

**使用方法**：
1. 安装 DEMFaultAnalyzer 插件
2. 在主菜单中选择「DEMFaultAnalyzer」
3. 按照提示使用故障分析功能

## 使用示例插件

### 1. 本地安装示例插件

```bash
# 安装 Example 插件
fastx-tui plugin install --local plugins/FastX-Tui-Plugin-Example

# 安装 DEMFaultAnalyzer 插件
fastx-tui plugin install --local plugins/FastX-Tui-Plugin-DEMFaultAnalyzer
```

### 2. 启用示例插件

1. 启动 FastX-Tui
2. 按 `S` 键打开设置
3. 选择「插件设置」
4. 启用您想要使用的示例插件
5. 按 `Esc` 键保存设置

### 3. 运行示例插件

1. 从主菜单选择「示例插件」或「DEMFaultAnalyzer」
2. 浏览插件提供的功能
3. 选择要执行的命令

## 示例插件代码分析

### 1. 插件入口文件

所有插件都必须有一个入口文件，文件名必须为 `fastx_tui_plugin.py`。

**示例入口文件**：

```python
#!/usr/bin/env python3
"""示例插件入口文件"""
from core.plugin_manager import Plugin, PluginInfo
from core.menu_system import MenuSystem
from example_business import ExampleBusiness

class ExamplePlugin(Plugin):
    """示例插件"""
    
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        return PluginInfo(
            name="ExamplePlugin",
            version="1.0.0",
            author="FastXTeam",
            description="FastX-Tui 示例插件",
            category="示例",
            tags=["示例", "基础"]
        )
    
    def initialize(self):
        """初始化插件"""
        self.business = ExampleBusiness(self)
    
    def cleanup(self):
        """清理插件资源"""
        pass
    
    def register(self, menu_system: MenuSystem):
        """注册插件命令到菜单系统"""
        self.business.register_commands(menu_system)
```

### 2. 业务逻辑分离

示例插件展示了业务逻辑与插件入口分离的最佳实践。

**示例业务逻辑文件**：

```python
#!/usr/bin/env python3
"""示例插件业务逻辑"""
from core.menu_system import ActionItem, CommandType

class ExampleBusiness:
    """示例插件业务逻辑"""
    
    def __init__(self, plugin_instance):
        """初始化业务逻辑"""
        self.plugin = plugin_instance
    
    def register_commands(self, menu_system):
        """注册命令"""
        # 创建子菜单
        submenu = menu_system.create_submenu(
            menu_id="example_submenu",
            name="示例菜单",
            description="示例插件的子菜单",
            icon="📝"
        )
        
        # 注册示例命令
        menu_system.register_item(ActionItem(
            id="example_command",
            name="示例命令",
            description="执行示例命令",
            command_type=CommandType.PYTHON,
            python_func=self.example_command
        ))
        
        # 将命令添加到子菜单
        submenu.add_item("example_command")
    
    def example_command(self):
        """示例命令实现"""
        self.plugin.log_info("执行示例命令")
        return "示例命令执行成功！"
```

## 开发自己的插件

您可以基于示例插件开发自己的插件：

1. **复制示例插件目录**：
   ```bash
   cp -r plugins/FastX-Tui-Plugin-Example plugins/FastX-Tui-Plugin-YourPlugin
   ```

2. **修改插件信息**：
   - 更新 `fastx_tui_plugin.py` 中的插件信息
   - 更新 `pyproject.toml` 中的插件元数据
   - 更新 `README.md` 和 `manual.md`

3. **实现业务逻辑**：
   - 修改 `example_business.py` 或创建新的业务逻辑文件
   - 实现您的插件功能

4. **测试插件**：
   - 安装您的插件
   - 测试插件功能
   - 调试和优化

## 示例插件最佳实践

1. **业务逻辑与入口分离**：将业务逻辑放在单独的文件中
2. **使用类型提示**：为所有方法和参数添加类型提示
3. **编写文档字符串**：为所有公共方法编写详细的文档字符串
4. **使用日志记录**：使用系统提供的日志API记录日志
5. **遵循目录结构**：按照推荐的目录结构组织文件
6. **声明依赖**：在 `pyproject.toml` 中声明插件依赖
7. **提供配置模式**：如果插件需要配置，提供 `config_schema.json`
8. **编写详细文档**：为插件编写详细的 README.md 和 manual.md

## 下一步

- 学习 [配置参考](../configuration/options.md)
- 了解 [开发指南](../development/environment.md)
- 开始 [开发您的插件](guide.md)
