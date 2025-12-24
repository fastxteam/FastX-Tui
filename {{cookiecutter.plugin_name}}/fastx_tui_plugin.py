#!/usr/bin/env python3
"""
FastX-Tui {{ cookiecutter.plugin_display_name }} Plugin

这个文件是插件的入口，包含插件的配置信息和基本结构
业务逻辑请参考 {{ cookiecutter.plugin_name }}_business.py
"""
import os
import json
import toml
from typing import Dict, Any
from core.plugin_manager import Plugin, PluginInfo
from core.menu_system import MenuSystem
from {{ cookiecutter.plugin_name }}_business import {{ cookiecutter.plugin_name }}Business

class {{ cookiecutter.plugin_name }}Plugin(Plugin):
    """{{ cookiecutter.plugin_display_name }}插件类"""
    
    def __init__(self):
        """初始化插件"""
        super().__init__()
        self.business = None
    
    @classmethod
    def get_version(cls) -> str:
        """从pyproject.toml获取当前版本号"""
        try:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建pyproject.toml的路径
            pyproject_path = os.path.join(current_dir, "pyproject.toml")
            # 读取文件
            with open(pyproject_path, "r", encoding="utf-8") as f:
                data = toml.load(f)
            # 返回版本号
            return data["project"]["version"]
        except Exception as e:
            # 如果读取失败，返回默认版本
            return "1.0.0"
    
    def get_info(self) -> PluginInfo:
        """获取插件信息
        
        必须实现此方法，返回插件的详细信息
        """
        return PluginInfo(
            name="{{ cookiecutter.plugin_display_name }}",
            version=self.get_version(),
            author="{{ cookiecutter.plugin_author }}",
            description="{{ cookiecutter.plugin_description }}",
            category="{{ cookiecutter.plugin_category }}",
            tags=["{{ cookiecutter.plugin_tags }}"],
            compatibility={"fastx-tui": ">=1.0.0"},
            dependencies=[],
            repository="{{ cookiecutter.plugin_repository }}",
            homepage="{{ cookiecutter.plugin_repository }}",
            license="{{ cookiecutter.license }}",
            last_updated="{{ cookiecutter.year }}-12-25",
            rating=0.0,
            downloads=0
        )
    
    def initialize(self):
        """初始化插件
        
        必须实现此方法，用于初始化插件的资源、连接数据库等
        """
        # 初始化业务逻辑
        self.business = {{ cookiecutter.plugin_name }}Business(self)
        self.business.initialize()
        self.log_info("{{ cookiecutter.plugin_display_name }}插件初始化完成")
    
    def cleanup(self):
        """清理插件资源
        
        必须实现此方法，用于清理插件使用的资源，如关闭连接、释放内存等
        """
        self.log_info("{{ cookiecutter.plugin_display_name }}插件清理完成")
        # 清理业务逻辑资源
        if self.business:
            self.business.cleanup()
            self.business = None
    
    def register(self, menu_system: MenuSystem):
        """注册插件命令到菜单系统
        
        必须实现此方法，用于将插件命令注册到菜单系统中
        
        参数：
        - menu_system: 菜单系统实例，用于注册命令和菜单
        """
        # 调用业务逻辑注册命令
        self.business.register_commands(menu_system)
        
        # 更新主菜单计数
        self.main_menus_registered += 1
        self.main_menu_id = "{{ cookiecutter.plugin_name.lower() }}_main_menu"
    
    def get_manual(self) -> str:
        """获取插件手册，返回Markdown格式的帮助内容
        
        Returns:
            str: Markdown格式的插件手册，从manual.md文件中读取
        """
        try:
            # 获取插件目录路径
            if self.plugin_path:
                manual_path = os.path.join(self.plugin_path, "manual.md")
                if os.path.exists(manual_path):
                    with open(manual_path, "r", encoding="utf-8") as f:
                        return f.read()
            # 如果文件不存在或plugin_path未设置，返回默认内容
            return "# 插件手册\n\n该插件未提供帮助文档。"
        except Exception as e:
            self.log_error(f"读取插件手册失败: {e}")
            return "# 插件手册\n\n读取帮助文档失败。"
    
    def get_config_schema(self) -> Dict[str, Any]:
        """获取插件配置模式，从config_schema.json文件中读取
        
        Returns:
            Dict[str, Any]: 配置项模式，包含配置名、类型、默认值、说明、可选值等
        """
        try:
            # 获取插件目录路径
            if self.plugin_path:
                config_schema_path = os.path.join(self.plugin_path, "config_schema.json")
                if os.path.exists(config_schema_path):
                    with open(config_schema_path, "r", encoding="utf-8") as f:
                        return json.load(f)
            # 如果文件不存在或plugin_path未设置，返回默认配置
            return {
                "enabled": {
                    "type": "boolean",
                    "default": True,
                    "description": "是否启用该插件",
                    "required": True
                }
            }
        except Exception as e:
            self.log_error(f"读取配置模式失败: {e}")
            # 返回默认配置
            return {
                "enabled": {
                    "type": "boolean",
                    "default": True,
                    "description": "是否启用该插件",
                    "required": True
                }
            }
    
    def get_binary_path(self) -> str:
        """获取插件二进制文件路径
        
        可选实现此方法，用于返回插件二进制文件的路径
        """
        # 示例：返回bin目录下的{{ cookiecutter.plugin_name.lower() }}二进制文件
        return self.get_resource_path("../bin/{{ cookiecutter.plugin_name.lower() }}")
    
    def get_resource_path(self, resource_name: str) -> str:
        """获取插件资源文件路径
        
        可选实现此方法，用于返回插件资源文件的路径
        
        参数：
        - resource_name: 资源文件名或相对路径
        
        返回：
        - 资源文件的绝对路径
        """
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(plugin_dir, resource_name)
    
    def example_command(self):
        """示例命令实现，已迁移到业务逻辑类
        
        此方法已废弃，业务逻辑请参考 {{ cookiecutter.plugin_name }}_business.py
        """
        self.log_warning("example_command方法已废弃，请使用业务逻辑类中的实现")
        return "命令已迁移到业务逻辑类"