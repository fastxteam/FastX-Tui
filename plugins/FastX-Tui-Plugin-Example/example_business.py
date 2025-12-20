#!/usr/bin/env python3
"""
FastX-Tui Example Plugin - 业务逻辑模块
这个模块包含了插件的核心业务逻辑
"""

from typing import List, Dict
from core.menu_system import MenuSystem, ActionItem, CommandType

class ExampleBusiness:
    """示例插件业务逻辑类"""
    
    def __init__(self, plugin_instance):
        """初始化业务逻辑"""
        self.plugin = plugin_instance
        self.log_info("示例插件业务逻辑初始化完成")
    
    def log_info(self, msg: str, *args, **kwargs):
        """记录信息日志"""
        self.plugin.log_info(msg, *args, **kwargs)
    
    def log_warning(self, msg: str, *args, **kwargs):
        """记录警告日志"""
        self.plugin.log_warning(msg, *args, **kwargs)
    
    def register_commands(self, menu_system: MenuSystem):
        """注册插件命令到菜单系统"""
        # 创建插件的子菜单
        self.create_plugin_submenu(menu_system)
        
        # 向主菜单添加命令
        self.add_to_main_menu(menu_system)
        
        # 向现有子菜单添加命令
        self.add_to_existing_submenu(menu_system)
    
    def create_plugin_submenu(self, menu_system: MenuSystem):
        """创建插件自己的子菜单"""
        # 创建子菜单
        plugin_submenu = menu_system.create_submenu(
            menu_id="example_plugin_submenu",
            name="示例插件菜单",
            description="示例插件的专属菜单",
            icon="🔌"
        )
        
        # 注册命令
        menu_system.register_item(ActionItem(
            id="example_hello",
            name="插件问候",
            description="这是一个插件命令示例，展示了如何创建插件命令",
            command_type=CommandType.PYTHON,
            python_func=lambda: "Hello from FastX-Tui Example Plugin!"
        ))
        
        menu_system.register_item(ActionItem(
            id="example_info",
            name="插件信息",
            description="显示插件的详细信息",
            command_type=CommandType.PYTHON,
            python_func=self.show_plugin_info
        ))
        
        menu_system.register_item(ActionItem(
            id="example_resource",
            name="资源示例",
            description="展示如何访问插件资源文件",
            command_type=CommandType.PYTHON,
            python_func=self.show_resource_example
        ))
        
        # 将命令添加到子菜单
        plugin_submenu.add_item("example_hello")
        plugin_submenu.add_item("example_info")
        plugin_submenu.add_item("example_resource")
        
        # 将子菜单添加到主菜单
        menu_system.add_item_to_main_menu("example_plugin_submenu")
    
    def add_to_main_menu(self, menu_system: MenuSystem):
        """向主菜单添加命令"""
        menu_system.register_item(ActionItem(
            id="main_example_command",
            name="主菜单示例命令",
            description="这是直接添加到主菜单的插件命令",
            icon="⭐",
            command_type=CommandType.PYTHON,
            python_func=lambda: "这是一个直接添加到主菜单的命令！"
        ))
        
        # 将命令添加到主菜单
        menu_system.add_item_to_main_menu("main_example_command")
    
    def add_to_existing_submenu(self, menu_system: MenuSystem):
        """向现有子菜单添加命令"""
        # 注册命令
        menu_system.register_item(ActionItem(
            id="system_example_command",
            name="系统工具示例命令",
            description="这是添加到系统工具菜单的插件命令",
            icon="🔧",
            command_type=CommandType.PYTHON,
            python_func=lambda: "这是一个添加到系统工具菜单的命令！"
        ))
        
        # 将命令添加到系统工具菜单（如果存在）
        if not menu_system.add_item_to_menu("system_tools_menu", "system_example_command"):
            self.log_warning("无法将命令添加到系统工具菜单，该菜单可能不存在")
    
    def show_plugin_info(self) -> str:
        """显示插件信息"""
        info = self.plugin.get_info()
        return f"""
📦 插件信息
===========
名称：{info.name}
版本：v{info.version}
作者：{info.author}
分类：{info.category}
标签：{', '.join(info.tags)}
描述：{info.description}
许可证：{info.license}
兼容性：{', '.join([f"{k}: {v}" for k, v in info.compatibility.items()])}
依赖：{', '.join(info.dependencies)}
仓库：{info.repository}
主页：{info.homepage}
最后更新：{info.last_updated}
评分：{info.rating}
下载次数：{info.downloads}
        """
    
    def show_resource_example(self) -> str:
        """展示资源文件访问"""
        # 尝试获取资源文件路径
        resource_path = self.plugin.get_resource_path("example.txt")
        
        try:
            with open(resource_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"📄 资源文件内容：\n{content}"
        except FileNotFoundError:
            return f"⚠️  资源文件不存在：{resource_path}\n请在插件目录的resources文件夹中创建example.txt文件"
