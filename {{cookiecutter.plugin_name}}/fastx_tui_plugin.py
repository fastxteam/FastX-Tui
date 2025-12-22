#!/usr/bin/env python3
"""
FastX-Tui {{ cookiecutter.plugin_display_name }} Plugin
"""
from core.plugin_manager import Plugin, PluginInfo
from core.menu_system import MenuSystem, ActionItem, CommandType

class {{ cookiecutter.plugin_name }}Plugin(Plugin):
    """{{ cookiecutter.plugin_display_name }}插件类"""
    
    def __init__(self):
        super().__init__()
    
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        return PluginInfo(
            name="{{ cookiecutter.plugin_display_name }}",
            version="{{ cookiecutter.plugin_version }}",
            author="{{ cookiecutter.plugin_author }}",
            description="{{ cookiecutter.plugin_description }}",
            category="{{ cookiecutter.plugin_category }}",
            tags={{ cookiecutter.plugin_tags }},
            compatibility={"fastx-tui": ">=1.0.0"},
            dependencies=[],
            repository="{{ cookiecutter.plugin_repository }}",
            license="{{ cookiecutter.license }}"
        )
    
    def register(self, menu_system: MenuSystem):
        """注册插件到菜单系统"""
        # 注册命令到菜单系统
        menu_system.add_action(
            ActionItem(
                name="{{ cookiecutter.plugin_display_name }}命令",
                description="执行{{ cookiecutter.plugin_display_name }}命令",
                command="{{ cookiecutter.plugin_name.lower() }}_command",
                command_type=CommandType.PLUGIN,
                callback=self.example_command,
                category="{{ cookiecutter.plugin_display_name }}",
                plugin=self
            )
        )
    
    def initialize(self):
        """初始化插件"""
        self.log_info("{{ cookiecutter.plugin_display_name }}插件已初始化")
    
    def cleanup(self):
        """清理插件资源"""
        self.log_info("{{ cookiecutter.plugin_display_name }}插件已清理")
    
    def example_command(self):
        """示例命令实现"""
        self.log_info("执行{{ cookiecutter.plugin_display_name }}命令")
        return "{{ cookiecutter.plugin_display_name }}命令执行成功"