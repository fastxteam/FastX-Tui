#!/usr/bin/env python3
"""
插件管理器模块
"""
import os
import importlib
import sys
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
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
    category: str = "其他"  # 插件分类
    tags: List[str] = field(default_factory=list)  # 插件标签
    compatibility: Dict[str, str] = field(default_factory=dict)  # 兼容性信息，如fastx-tui版本要求
    dependencies: List[str] = field(default_factory=list)  # 依赖项
    repository: str = ""  # 插件仓库地址
    homepage: str = ""  # 插件主页
    license: str = "MIT"  # 许可证
    last_updated: str = ""  # 最后更新时间
    rating: float = 0.0  # 评分
    downloads: int = 0  # 下载次数

class Plugin(ABC):
    """插件基类"""
    
    def __init__(self):
        """初始化插件，设置日志器"""
        # 获取插件名称作为日志器名称
        self.logger = get_logger(self.__class__.__name__)
        # 插件目录路径，在加载时由PluginManager设置
        self.plugin_path = None
    
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
    
    def get_binary_path(self) -> str:
        """获取插件二进制文件路径（可选实现）"""
        return ""
    
    def get_resource_path(self, resource_name: str) -> str:
        """获取插件资源文件路径"""
        if self.plugin_path:
            return os.path.join(self.plugin_path, "resources", resource_name)
        return resource_name
    
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
        """发现插件文件和GitHub仓库插件"""
        plugin_files = []
        
        for item in os.listdir(self.plugin_dir):
            item_path = os.path.join(self.plugin_dir, item)
            
            # 处理单个.py文件插件（兼容旧版本）
            if os.path.isfile(item_path) and item.endswith('.py') and item != '__init__.py':
                plugin_files.append(item[:-3])  # 移除.py扩展名
            
            # 处理GitHub仓库插件
            elif os.path.isdir(item_path):
                # 检查是否是FastX-Tui插件仓库（命名格式：FastX-Tui-Plugin-{PluginName}）
                if item.startswith('FastX-Tui-Plugin-'):
                    # 检查仓库中是否有fastx_plugin.py入口文件
                    if os.path.isfile(os.path.join(item_path, 'fastx_plugin.py')):
                        # 使用仓库名作为插件名
                        plugin_files.append(item)
        
        return plugin_files
    
    def load_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """加载单个插件"""
        try:
            # 确定插件类型和入口文件路径
            plugin_path = os.path.join(self.plugin_dir, plugin_name)
            is_repo_plugin = os.path.isdir(plugin_path)
            
            if is_repo_plugin:
                # GitHub仓库插件
                entry_file = os.path.join(plugin_path, 'fastx_plugin.py')
                module_name = f"fastx_plugin_{plugin_name}"
            else:
                # 单个.py文件插件（兼容旧版本）
                entry_file = os.path.join(self.plugin_dir, f"{plugin_name}.py")
                module_name = plugin_name
            
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(
                module_name,
                entry_file
            )
            if spec is None:
                self.logger.warning(f"无法找到插件 {plugin_name} 的入口文件")
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            
            # 将插件目录添加到模块的搜索路径中，以便插件可以导入自己的子模块
            if is_repo_plugin:
                module.__path__.append(plugin_path)
                sys.path.insert(0, plugin_path)
            
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
            
            # 设置插件路径
            if is_repo_plugin:
                plugin_instance.plugin_path = plugin_path
            
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
            import traceback
            self.logger.debug(f"插件加载错误详细信息: {traceback.format_exc()}")
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
    
    def install_plugin_from_github(self, repo_url: str) -> bool:
        """从GitHub仓库安装插件"""
        try:
            import subprocess
            import os
            
            # 检查repo_url是否是有效的GitHub仓库URL
            if not repo_url.startswith('https://github.com/') and not repo_url.startswith('git@github.com:'):
                self.logger.error(f"无效的GitHub仓库URL: {repo_url}")
                return False
            
            # 提取仓库名
            if repo_url.endswith('.git'):
                repo_name = repo_url.split('/')[-1][:-4]
            else:
                repo_name = repo_url.split('/')[-1]
            
            # 检查仓库名是否符合FastX-Tui插件命名规范
            if not repo_name.startswith('FastX-Tui-Plugin-'):
                self.logger.error(f"GitHub仓库名必须以'FastX-Tui-Plugin-'开头: {repo_name}")
                return False
            
            # 检查插件目录是否已存在
            plugin_path = os.path.join(self.plugin_dir, repo_name)
            if os.path.exists(plugin_path):
                self.logger.error(f"插件 {repo_name} 已存在")
                return False
            
            # 使用git clone命令下载仓库
            self.logger.info(f"正在从GitHub下载插件: {repo_url}")
            subprocess.run(
                ['git', 'clone', repo_url, plugin_path],
                check=True,
                capture_output=True,
                text=True
            )
            
            # 检查仓库中是否有fastx_plugin.py入口文件
            if not os.path.isfile(os.path.join(plugin_path, 'fastx_plugin.py')):
                self.logger.error(f"插件 {repo_name} 缺少fastx_plugin.py入口文件")
                # 清理已下载的仓库
                import shutil
                shutil.rmtree(plugin_path)
                return False
            
            self.logger.info(f"插件 {repo_name} 安装成功")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git克隆失败: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"安装插件失败: {str(e)}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """重载指定插件"""
        try:
            # 卸载插件
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                try:
                    plugin.cleanup()
                except Exception as e:
                    self.logger.warning(f"清理插件 {plugin_name} 失败: {str(e)}")
                
                del self.plugins[plugin_name]
                if plugin_name in self.loaded_plugins:
                    self.loaded_plugins.remove(plugin_name)
                
            # 重新加载插件
            plugin = self.load_plugin(plugin_name)
            return plugin is not None
            
        except Exception as e:
            self.logger.error(f"重载插件 {plugin_name} 失败: {str(e)}")
            return False
    
    def reload_all_plugins(self) -> bool:
        """重载所有插件"""
        try:
            # 保存当前已加载的插件列表
            loaded_plugins = self.loaded_plugins.copy()
            
            # 清理所有插件
            self.cleanup_all()
            
            # 重新加载所有插件
            self.load_all_plugins()
            
            return True
            
        except Exception as e:
            self.logger.error(f"重载所有插件失败: {str(e)}")
            return False

class PluginRepository:
    """插件仓库管理器"""
    
    def __init__(self, base_url: str = "https://api.fastx-tui.com/plugins"):
        self.base_url = base_url
        self.logger = get_logger("PluginRepository")
        self.cache = {}
        self.cache_time = 0
    
    def get_plugins(self, category: str = "", search: str = "", page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """获取插件列表"""
        try:
            import requests
            
            params = {
                "category": category,
                "search": search,
                "page": page,
                "per_page": per_page
            }
            
            response = requests.get(f"{self.base_url}/list", params=params, timeout=5)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            self.logger.error(f"获取插件列表失败: {str(e)}")
            return {"plugins": [], "total": 0, "page": 1, "per_page": 20}
    
    def get_plugin_details(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """获取插件详情"""
        try:
            import requests
            
            response = requests.get(f"{self.base_url}/details/{plugin_id}", timeout=5)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            self.logger.error(f"获取插件详情失败: {str(e)}")
            return None
    
    def install_plugin(self, plugin_id: str, plugin_manager: "PluginManager") -> bool:
        """从插件仓库安装插件"""
        try:
            # 获取插件详情
            plugin_details = self.get_plugin_details(plugin_id)
            if not plugin_details:
                return False
            
            # 从GitHub安装插件
            return plugin_manager.install_plugin_from_github(plugin_details.get("repository", ""))
        except Exception as e:
            self.logger.error(f"安装插件失败: {str(e)}")
            return False
    
    def search_plugins(self, query: str) -> List[Dict[str, Any]]:
        """搜索插件"""
        result = self.get_plugins(search=query)
        return result.get("plugins", [])
    
    def get_categories(self) -> List[str]:
        """获取所有插件分类"""
        try:
            import requests
            
            response = requests.get(f"{self.base_url}/categories", timeout=5)
            response.raise_for_status()
            
            return response.json().get("categories", [])
        except Exception as e:
            self.logger.error(f"获取插件分类失败: {str(e)}")
            return ["其他", "工具", "主题", "集成", "开发"]
    
    def update_plugin(self, plugin_id: str, plugin_manager: "PluginManager") -> bool:
        """更新插件"""
        try:
            # 获取插件详情
            plugin_details = self.get_plugin_details(plugin_id)
            if not plugin_details:
                return False
            
            # 这里可以实现更复杂的更新逻辑，比如检查版本等
            return plugin_manager.install_plugin_from_github(plugin_details.get("repository", ""))
        except Exception as e:
            self.logger.error(f"更新插件失败: {str(e)}")
            return False