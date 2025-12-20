#!/usr/bin/env python3
"""
FastX-Tui Example Plugin - 入口文件
这个文件是插件的入口，包含插件的配置信息和基本结构
业务逻辑请参考 example_business.py
"""

from typing import List, Dict
from core.plugin_manager import Plugin, PluginInfo
from core.menu_system import MenuSystem
from example_business import ExampleBusiness

class ExamplePlugin(Plugin):
    """示例插件
    
    这是FastX-Tui插件的入口类，所有插件必须继承自Plugin类并实现所有抽象方法。
    
    必须实现的方法：
    - get_info(): 返回插件信息
    - initialize(): 初始化插件
    - cleanup(): 清理插件资源
    - register(): 注册插件命令到菜单系统
    
    可选实现的方法：
    - get_binary_path(): 获取插件二进制文件路径
    - get_resource_path(): 获取插件资源文件路径
    """
    
    def __init__(self):
        """初始化插件"""
        super().__init__()
        self.business = None
    
    def get_info(self) -> PluginInfo:
        """获取插件信息
        
        必须实现此方法，返回插件的详细信息
        """
        return PluginInfo(
            name="示例插件",
            version="1.0.0",
            author="FastX Team",
            description="这是一个FastX-Tui插件系统的示例插件，展示了插件的基本功能和最佳实践。",
            category="开发",  # 插件分类
            tags=["示例", "开发", "模板"],  # 插件标签
            compatibility={"fastx-tui": ">=0.1.13"},  # 兼容性要求
            dependencies=["requests>=2.31.0"],  # 依赖项
            repository="https://github.com/fastxteam/FastX-Tui-Plugin-Example",  # 插件仓库
            homepage="https://github.com/fastxteam/FastX-Tui-Plugin-Example",  # 插件主页
            license="MIT",  # 许可证
            last_updated="2025-12-21",  # 最后更新时间
            rating=4.8,  # 评分
            downloads=1000  # 下载次数
        )
    
    def initialize(self):
        """初始化插件
        
        必须实现此方法，用于初始化插件的资源、连接数据库等
        """
        # 初始化业务逻辑
        self.business = ExampleBusiness(self)
        self.log_info("示例插件初始化完成")
    
    def cleanup(self):
        """清理插件资源
        
        必须实现此方法，用于清理插件使用的资源，如关闭连接、释放内存等
        """
        self.log_info("示例插件清理完成")
        # 清理业务逻辑资源
        self.business = None
    
    def register(self, menu_system: MenuSystem):
        """注册插件命令到菜单系统
        
        必须实现此方法，用于将插件命令注册到菜单系统中
        
        参数：
        - menu_system: 菜单系统实例，用于注册命令和菜单
        """
        # 调用业务逻辑注册命令
        self.business.register_commands(menu_system)
    
    def get_binary_path(self) -> str:
        """获取插件二进制文件路径
        
        可选实现此方法，用于返回插件二进制文件的路径
        """
        # 示例：返回bin目录下的example_binary文件
        return self.get_resource_path("../bin/example_binary")
