#!/usr/bin/env python3
"""
插件管理器模块
"""
import os
import importlib
import sys
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from .menu_system import MenuSystem, ActionItem, CommandType
from .logger import get_logger

@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    version: str
    author: str
    description: str
    enabled: bool = True

class Plugin(ABC):
    """插件基类"""
    
    def __init__(self):
        """初始化插件，设置日志器"""
        # 获取插件名称作为日志器名称
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        pass
    
    @abstractmethod
    def register(self, menu_system: MenuSystem):
        """注册插件到菜单系统"""
        pass
    
    @abstractmethod
    def initialize(self):
        """初始化插件"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理插件资源"""
        pass
    
    def log_debug(self, msg: str, *args, **kwargs):
        """记录调试日志"""
        self.logger.debug(msg, *args, **kwargs)
    
    def log_info(self, msg: str, *args, **kwargs):
        """记录信息日志"""
        self.logger.info(msg, *args, **kwargs)
    
    def log_warning(self, msg: str, *args, **kwargs):
        """记录警告日志"""
        self.logger.warning(msg, *args, **kwargs)
    
    def log_error(self, msg: str, *args, **kwargs):
        """记录错误日志"""
        self.logger.error(msg, *args, **kwargs)
    
    def log_critical(self, msg: str, *args, **kwargs):
        """记录严重错误日志"""
        self.logger.critical(msg, *args, **kwargs)

class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Plugin] = {}
        self.loaded_plugins: List[str] = []
        
        # 初始化日志器
        self.logger = get_logger("PluginManager")
        
        # 创建插件目录
        os.makedirs(plugin_dir, exist_ok=True)
    
    def discover_plugins(self) -> List[str]:
        """发现插件文件"""
        plugin_files = []
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                plugin_files.append(filename[:-3])  # 移除.py扩展名
        return plugin_files
    
    def load_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """加载单个插件"""
        try:
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(
                plugin_name,
                os.path.join(self.plugin_dir, f"{plugin_name}.py")
            )
            if spec is None:
                self.logger.warning(f"无法找到插件 {plugin_name}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Plugin) and 
                    attr != Plugin):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                self.logger.warning(f"插件 {plugin_name} 没有找到 Plugin 子类")
                return None
            
            # 实例化插件
            plugin_instance = plugin_class()
            plugin_info = plugin_instance.get_info()
            
            if not plugin_info.enabled:
                self.logger.info(f"插件 {plugin_name} 已被禁用")
                return None
            
            # 初始化插件
            plugin_instance.initialize()
            
            self.plugins[plugin_name] = plugin_instance
            self.loaded_plugins.append(plugin_name)
            
            self.logger.info(f"加载插件: {plugin_info.name} v{plugin_info.version}")
            return plugin_instance
            
        except Exception as e:
            self.logger.error(f"加载插件 {plugin_name} 失败: {str(e)}")
            return None
    
    def load_all_plugins(self) -> Dict[str, Plugin]:
        """加载所有插件"""
        plugin_names = self.discover_plugins()
        for plugin_name in plugin_names:
            self.load_plugin(plugin_name)
        return self.plugins
    
    def register_all_plugins(self, menu_system: MenuSystem):
        """注册所有插件到菜单系统"""
        for plugin in self.plugins.values():
            try:
                plugin.register(menu_system)
            except Exception as e:
                self.logger.error(f"注册插件失败: {str(e)}")
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[PluginInfo]:
        """列出所有插件信息"""
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """启用插件"""
        # 这里可以实现动态启用/禁用逻辑
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """禁用插件"""
        # 这里可以实现动态启用/禁用逻辑
        return False
    
    def cleanup_all(self):
        """清理所有插件"""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                self.logger.warning(f"清理插件失败: {str(e)}")
        
        self.plugins.clear()
        self.loaded_plugins.clear()