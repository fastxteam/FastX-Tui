#!/usr/bin/env python3
"""
{{ cookiecutter.plugin_display_name }}业务逻辑

该文件包含{{ cookiecutter.plugin_display_name }}的业务逻辑，演示了如何使用FastX-Tui插件接口实现业务功能。
"""
from typing import Any
from core.menu_system import MenuSystem, ActionItem, CommandType

class {{ cookiecutter.plugin_name }}Business:
    """{{ cookiecutter.plugin_display_name }}业务逻辑类
    
    该类包含{{ cookiecutter.plugin_display_name }}的业务逻辑，包括：
    - 初始化业务逻辑
    - 注册插件命令到菜单系统
    - 实现示例命令
    - 清理业务逻辑资源
    """
    
    def __init__(self, plugin):
        """初始化业务逻辑
        
        Args:
            plugin: 插件实例，用于访问插件的配置、日志等功能
        """
        self.plugin = plugin
        self.logger = plugin.logger
        
        # 初始化配置
        self.example_config = "default_value"
    
    def initialize(self):
        """初始化业务逻辑
        
        从配置中获取初始化参数，并记录初始化日志。
        """
        # 从配置中获取初始化参数
        self.example_config = self.plugin.get_config("example_config", "default_value")
        
        self.plugin.log_info(f"{{ cookiecutter.plugin_display_name }}业务逻辑初始化完成，示例配置: {self.example_config}")
    
    def register_commands(self, menu_system: MenuSystem):
        """注册插件命令到菜单系统
        
        将插件的命令和菜单注册到菜单系统中。
        
        Args:
            menu_system: 菜单系统实例，用于注册插件的命令和菜单
        """
        # 创建主菜单
        main_menu = menu_system.create_submenu(
            menu_id='{{ cookiecutter.plugin_name.lower() }}_main_menu',
            name='{{ cookiecutter.plugin_display_name }}',
            description='{{ cookiecutter.plugin_display_name }}相关命令'
        )
        
        # 注册示例命令
        example_command = ActionItem(
            id='{{ cookiecutter.plugin_name.lower() }}_example_command',
            name='示例命令',
            description='执行{{ cookiecutter.plugin_display_name }}示例命令',
            command_type=CommandType.PYTHON,
            python_func=self.example_command,
            category='{{ cookiecutter.plugin_display_name }}'
        )
        menu_system.register_item(example_command)
        
        # 将命令添加到菜单
        main_menu.add_item(example_command.id)
        
        # 将菜单添加到主菜单
        main_menu_item = menu_system.get_item_by_id('main_menu')
        if main_menu_item and hasattr(main_menu_item, 'add_item'):
            main_menu_item.add_item(main_menu.id)
    
    def example_command(self) -> str:
        """示例命令实现
        
        返回一个示例响应字符串。
        
        Returns:
            str: 示例响应字符串
        """
        # 获取配置
        example_config = self.plugin.get_config("example_config", "default_value")
        
        # 构建响应
        result = f"{{ cookiecutter.plugin_display_name }}命令执行成功！\n"
        result += f"示例配置值: {example_config}\n"
        result += "这是一个示例命令，您可以根据需要修改业务逻辑。"
        
        return result
    
    def cleanup(self):
        """清理业务逻辑资源
        
        清理业务逻辑使用的资源，并记录清理日志。
        """
        self.plugin.log_info("{{ cookiecutter.plugin_display_name }}业务逻辑清理完成")