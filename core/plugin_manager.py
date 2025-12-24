#!/usr/bin/env python3
"""
插件管理器模块
"""
import os
import importlib
import sys
import subprocess
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from .menu_system import MenuSystem, ActionItem, CommandType
from .logger import get_logger
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from models.plugin_schema import PluginInfoSchema

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
    """插件基类
    
    所有FastX-Tui插件必须继承自此类并实现所有抽象方法。
    
    属性：
    - logger: 插件日志器
    - plugin_path: 插件目录路径（由PluginManager设置）
    - main_menus_registered: 跟踪主菜单注册数量，用于限制每个插件只能注册一个主菜单
    - main_menu_id: 插件注册的主菜单ID，用于跟踪
    """
    
    def __init__(self):
        """初始化插件，设置日志器
        
        初始化插件的基本属性，包括日志器、插件路径、主菜单注册数量等。
        """
        # 获取插件名称作为日志器名称
        self.logger = get_logger(self.__class__.__name__)
        # 插件目录路径，在加载时由PluginManager设置
        self.plugin_path = None
        # 跟踪主菜单注册数量，用于限制每个插件只能注册一个主菜单
        self.main_menus_registered = 0
        # 插件注册的主菜单ID，用于跟踪
        self.main_menu_id = None
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """获取插件信息
        
        必须实现此方法，返回插件的详细信息，包括名称、版本、作者、描述等。
        
        Returns:
            PluginInfo: 插件信息对象，包含插件的详细信息
        """
        pass
    
    @abstractmethod
    def register(self, menu_system: MenuSystem):
        """注册插件到菜单系统
        
        必须实现此方法，用于将插件的命令和菜单注册到菜单系统中。
        
        Args:
            menu_system: 菜单系统实例，用于注册插件的命令和菜单
        """
        pass
    
    @abstractmethod
    def initialize(self):
        """初始化插件
        
        必须实现此方法，用于初始化插件的资源、连接数据库、加载配置等。
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理插件资源
        
        必须实现此方法，用于清理插件使用的资源，如关闭连接、释放内存等。
        """
        pass
    
    def get_binary_path(self) -> str:
        """获取插件二进制文件路径
        
        可选实现此方法，用于返回插件二进制文件的路径。
        
        Returns:
            str: 插件二进制文件路径
        """
        return ""
    
    def get_resource_path(self, resource_name: str) -> str:
        """获取插件资源文件路径
        
        获取插件资源文件的完整路径，资源文件通常存放在插件的resources目录下。
        
        Args:
            resource_name: 资源文件名称
        
        Returns:
            str: 资源文件的完整路径
        """
        if self.plugin_path:
            return os.path.join(self.plugin_path, "resources", resource_name)
        return resource_name
    
    def get_manual(self) -> str:
        """获取插件手册，返回Markdown格式的帮助内容
        
        可选实现此方法，返回插件的帮助文档，使用Markdown格式编写。
        
        Returns:
            str: Markdown格式的插件手册
        """
        return "# 插件手册\n\n该插件未提供帮助文档。"
    
    def get_config_schema(self) -> Dict[str, Any]:
        """获取插件配置模式，定义插件的配置项及约束
        
        可选实现此方法，返回插件的配置项模式，包含配置名、类型、默认值、说明、可选值等。
        
        Returns:
            Dict[str, Any]: 配置项模式，包含配置名、类型、默认值、说明、可选值等
        """
        return {
            "enabled": {
                "type": "boolean",
                "default": True,
                "description": "是否启用该插件",
                "required": True
            }
        }
    
    def get_config(self, config_name: str, default: Any = None) -> Any:
        """获取插件配置值
        
        获取插件的配置值，如果配置不存在则返回默认值。
        此方法将在PluginManager中被重写，使用配置管理器获取配置。
        
        Args:
            config_name: 配置项名称
            default: 默认值，配置不存在时返回
            
        Returns:
            Any: 配置值
        """
        # 该方法将在PluginManager中被重写，使用配置管理器获取配置
        return default
    
    def set_config(self, config_name: str, value: Any):
        """设置插件配置值
        
        设置插件的配置值，此方法将在PluginManager中被重写，使用配置管理器设置配置。
        
        Args:
            config_name: 配置项名称
            value: 配置值
        """
        # 该方法将在PluginManager中被重写，使用配置管理器设置配置
        pass
    
    def log_debug(self, msg: str, *args, **kwargs):
        """记录调试日志
        
        记录调试级别的日志信息，通常用于开发和调试阶段。
        
        Args:
            msg: 日志消息
            *args: 消息格式化参数
            **kwargs: 额外的日志参数
        """
        self.logger.debug(msg, *args, **kwargs)
    
    def log_info(self, msg: str, *args, **kwargs):
        """记录信息日志
        
        记录信息级别的日志信息，通常用于正常的运行状态。
        
        Args:
            msg: 日志消息
            *args: 消息格式化参数
            **kwargs: 额外的日志参数
        """
        self.logger.info(msg, *args, **kwargs)
    
    def log_warning(self, msg: str, *args, **kwargs):
        """记录警告日志
        
        记录警告级别的日志信息，通常用于可能的问题或异常情况。
        
        Args:
            msg: 日志消息
            *args: 消息格式化参数
            **kwargs: 额外的日志参数
        """
        self.logger.warning(msg, *args, **kwargs)
    
    def log_error(self, msg: str, *args, **kwargs):
        """记录错误日志
        
        记录错误级别的日志信息，通常用于错误和异常情况。
        
        Args:
            msg: 日志消息
            *args: 消息格式化参数
            **kwargs: 额外的日志参数
        """
        self.logger.error(msg, *args, **kwargs)
    
    def log_critical(self, msg: str, *args, **kwargs):
        """记录严重错误日志
        
        记录严重错误级别的日志信息，通常用于严重的系统错误和崩溃情况。
        
        Args:
            msg: 日志消息
            *args: 消息格式化参数
            **kwargs: 额外的日志参数
        """
        self.logger.critical(msg, *args, **kwargs)

class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: str = "plugins", config_manager=None):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Plugin] = {}  # 已加载的插件
        self.loaded_plugins: List[str] = []   # 已加载插件名称列表
        self.all_plugins: List[str] = []      # 所有发现的插件，包括未加载的
        self.plugin_configs: Dict[str, Dict] = {}  # 插件配置，包括启用状态等
        
        # 初始化日志器
        self.logger = get_logger("PluginManager")
        
        # 创建插件目录
        os.makedirs(plugin_dir, exist_ok=True)
        
        # 配置管理器，用于持久化插件配置
        self.config_manager = config_manager
        
        # 加载插件配置
        self._load_plugin_configs()
        
        # 初始化虚拟环境管理器
        from .venv_manager import VenvManager
        self.venv_manager = VenvManager()
        
    def _load_plugin_configs(self):
        """加载插件配置"""
        if self.config_manager:
            self.plugin_configs = self.config_manager.list_plugin_configs()
        else:
            # 没有配置管理器时使用默认配置
            self.plugin_configs = {}
    
    def _save_plugin_configs(self):
        """保存插件配置"""
        if self.config_manager:
            # 插件配置已通过config_manager的update_plugin_config等方法保存，无需额外操作
            pass
    
    def get_plugin_config(self, plugin_name: str) -> Dict:
        """获取插件配置"""
        return self.plugin_configs.get(plugin_name, {})
    
    def set_plugin_config(self, plugin_name: str, config: Dict):
        """设置插件配置"""
        self.plugin_configs[plugin_name] = config
        if self.config_manager:
            self.config_manager.set_plugin_config(plugin_name, config)
        self._save_plugin_configs()
    
    def discover_plugins(self) -> List[str]:
        """发现插件文件和GitHub仓库插件"""
        plugin_files = []
        
        for item in os.listdir(self.plugin_dir):
            item_path = os.path.join(self.plugin_dir, item)
            
            # 处理单个.py文件插件（兼容旧版本） - 只允许FastX-Tui-Plugin-开头的命名
            if os.path.isfile(item_path) and item.endswith('.py') and item != '__init__.py':
                # 单个.py文件插件也必须以FastX-Tui-Plugin-开头
                if item.startswith('FastX-Tui-Plugin-'):
                    plugin_files.append(item[:-3])  # 移除.py扩展名
            
            # 处理GitHub仓库插件
            elif os.path.isdir(item_path):
                # 检查是否是FastX-Tui插件仓库（命名格式：FastX-Tui-Plugin-{PluginName}）
                if item.startswith('FastX-Tui-Plugin-'):
                    # 检查仓库中是否有fastx_tui_plugin.py入口文件
                    if os.path.isfile(os.path.join(item_path, 'fastx_tui_plugin.py')):
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
                entry_file = os.path.join(plugin_path, 'fastx_tui_plugin.py')
                module_name = f"fastx_tui_plugin_{plugin_name}"
            else:
                # 单个.py文件插件（兼容旧版本）
                entry_file = os.path.join(self.plugin_dir, f"{plugin_name}.py")
                module_name = plugin_name
            
            # 检查插件入口文件是否存在
            if not os.path.exists(entry_file):
                self.logger.warning(f"无法找到插件 {plugin_name} 的入口文件")
                return None
            
            # 为插件创建虚拟环境
            if not self.venv_manager.venv_exists(plugin_name):
                if not self.venv_manager.create_venv(plugin_name, plugin_path):
                    self.logger.error(f"无法为插件 {plugin_name} 创建虚拟环境")
                    return None
            else:
                # 更新虚拟环境依赖
                if not self.venv_manager.update_venv(plugin_name, plugin_path):
                    self.logger.error(f"无法更新插件 {plugin_name} 的虚拟环境依赖")
                    return None
            
            # 使用插件虚拟环境中的Python解释器来加载插件信息
            venv_python_path = self.venv_manager.get_venv_python_path(plugin_name)
            
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(
                module_name,
                entry_file,
                # 使用插件虚拟环境中的Python解释器
                loader=importlib.machinery.SourceFileLoader(module_name, entry_file)
            )
            if spec is None:
                self.logger.warning(f"无法找到插件 {plugin_name} 的入口文件")
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            
            # 将插件目录添加到模块的搜索路径中，以便插件可以导入自己的子模块
            if is_repo_plugin:
                sys.path.insert(0, plugin_path)
            
            # 获取虚拟环境的site-packages路径
            result = subprocess.run(
                [venv_python_path, "-c", "import sys; print('\\n'.join(sys.path))"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # 将虚拟环境的site-packages路径添加到模块的搜索路径中
                venv_sys_path = result.stdout.strip().split('\n')
                for path in venv_sys_path:
                    # 检查路径是否已经在sys.path中，避免重复添加
                    if path not in sys.path:
                        sys.path.insert(0, path)
            
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
            
            # 动态替换插件的配置访问方法
            def plugin_get_config(config_name, default=None):
                """动态生成的获取配置方法"""
                plugin_config = self.plugin_configs.get(plugin_name, {})
                return plugin_config.get(config_name, default)
            
            def plugin_set_config(config_name, value):
                """动态生成的设置配置方法"""
                if plugin_name not in self.plugin_configs:
                    self.plugin_configs[plugin_name] = {}
                self.plugin_configs[plugin_name][config_name] = value
                if self.config_manager:
                    self.config_manager.update_plugin_config(plugin_name, config_name, value)
                self._save_plugin_configs()
            
            # 替换插件的配置访问方法
            plugin_instance.get_config = plugin_get_config
            plugin_instance.set_config = plugin_set_config
            
            plugin_info = plugin_instance.get_info()
            
            # 使用PluginInfoSchema验证插件信息
            try:
                # 将PluginInfo转换为字典
                plugin_info_dict = {
                    "name": plugin_info.name,
                    "version": plugin_info.version,
                    "author": plugin_info.author,
                    "description": plugin_info.description,
                    "homepage": plugin_info.homepage,
                    "repository": plugin_info.repository,
                    "license": plugin_info.license,
                    "dependencies": plugin_info.dependencies,
                    "category": plugin_info.category
                }
                
                # 使用PluginInfoSchema验证
                schema = PluginInfoSchema(**plugin_info_dict)
                self.logger.info(f"插件信息验证通过: {plugin_info.name} v{plugin_info.version}")
            except Exception as e:
                self.logger.error(f"插件 {plugin_name} 信息验证失败: {str(e)}")
                return None
            
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
    
    def load_all_plugins(self, console=None) -> Dict[str, Plugin]:
        """加载所有插件"""
        plugin_names = self.discover_plugins()
        self.all_plugins = plugin_names
        
        if console:
            # 使用rich.progress显示多任务进度
            console.print("\n📌 [bold]多任务进度:[/bold]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            ) as progress:
                # 创建进度任务
                tasks = [
                    progress.add_task("[red]发现插件...", total=len(plugin_names)),
                    progress.add_task("[green]加载插件...", total=len(plugin_names)),
                    progress.add_task("[blue]初始化...", total=len(plugin_names)),
                ]
                
                # 模拟进度更新
                for i, plugin_name in enumerate(plugin_names):
                    # 更新发现进度
                    progress.update(tasks[0], advance=1)
                    
                    # 检查插件是否被启用
                    plugin_config = self.get_plugin_config(plugin_name)
                    enabled = plugin_config.get("enabled", True)
                    
                    if enabled:
                        self.load_plugin(plugin_name)
                        # 更新加载进度
                        progress.update(tasks[1], advance=1)
                    else:
                        self.logger.info(f"插件 {plugin_name} 已被禁用，跳过加载")
                    
                    # 更新初始化进度
                    progress.update(tasks[2], advance=1)
        else:
            # 无console时的原始逻辑
            for plugin_name in plugin_names:
                # 检查插件是否被启用
                plugin_config = self.get_plugin_config(plugin_name)
                enabled = plugin_config.get("enabled", True)
                
                if enabled:
                    self.load_plugin(plugin_name)
                else:
                    self.logger.info(f"插件 {plugin_name} 已被禁用，跳过加载")
        
        return self.plugins
    
    def register_all_plugins(self, menu_system: MenuSystem):
        """注册所有插件到菜单系统"""
        for plugin_name, plugin in self.plugins.items():
            try:
                # 重置主菜单计数
                plugin.main_menus_registered = 0
                plugin.main_menu_id = None
                
                # 注册插件
                plugin.register(menu_system)
                
                # 检查是否注册了多个主菜单
                if plugin.main_menus_registered > 1:
                    self.logger.warning(f"插件 {plugin_name} 注册了 {plugin.main_menus_registered} 个主菜单，根据规范只能注册一个主菜单")
            except Exception as e:
                self.logger.error(f"注册插件 {plugin_name} 失败: {str(e)}")
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """列出所有插件信息，包括已加载和未加载的"""
        plugin_list = []
        
        for plugin_name in self.all_plugins:
            plugin_info = {
                "name": plugin_name,
                "loaded": plugin_name in self.plugins,
                "enabled": self.get_plugin_config(plugin_name).get("enabled", True)
            }
            
            # 如果插件已加载，获取详细信息
            if plugin_name in self.plugins:
                try:
                    plugin = self.plugins[plugin_name]
                    detailed_info = plugin.get_info()
                    plugin_info.update({
                        "display_name": detailed_info.name,
                        "version": detailed_info.version,
                        "author": detailed_info.author,
                        "description": detailed_info.description,
                        "category": detailed_info.category,
                        "tags": detailed_info.tags,
                        "compatibility": detailed_info.compatibility
                    })
                except Exception as e:
                    self.logger.warning(f"获取插件 {plugin_name} 详细信息失败: {str(e)}")
            else:
                # 未加载的插件，只显示基本信息
                plugin_info.update({
                    "display_name": plugin_name,
                    "version": "未知",
                    "author": "未知",
                    "description": "插件未加载"
                })
            
            plugin_list.append(plugin_info)
        
        return plugin_list
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        try:
            # 先禁用插件
            self.disable_plugin(plugin_name)
            
            # 删除插件目录或文件
            plugin_path = os.path.join(self.plugin_dir, plugin_name)
            if os.path.isdir(plugin_path):
                import shutil
                import stat
                
                def remove_readonly(func, path, excinfo):
                    """处理只读文件的删除回调"""
                    # 将文件设置为可写
                    os.chmod(path, stat.S_IWRITE)
                    # 重新尝试删除
                    func(path)
                
                try:
                    # 尝试删除目录，处理只读文件
                    shutil.rmtree(plugin_path, onerror=remove_readonly)
                    self.logger.info(f"已删除插件目录: {plugin_path}")
                except Exception as e:
                    # 如果删除失败，尝试手动删除目录内容
                    self.logger.warning(f"使用shutil.rmtree删除目录失败，尝试手动删除: {str(e)}")
                    
                    # 手动删除文件，跳过可能锁定的文件
                    for root, dirs, files in os.walk(plugin_path, topdown=False):
                        for name in files:
                            try:
                                file_path = os.path.join(root, name)
                                os.chmod(file_path, stat.S_IWRITE)
                                os.remove(file_path)
                            except Exception as file_e:
                                self.logger.warning(f"无法删除文件 {file_path}: {str(file_e)}")
                        for name in dirs:
                            try:
                                dir_path = os.path.join(root, name)
                                os.rmdir(dir_path)
                            except Exception as dir_e:
                                self.logger.warning(f"无法删除目录 {dir_path}: {str(dir_e)}")
                    
                    # 最后尝试删除根目录
                    try:
                        os.rmdir(plugin_path)
                        self.logger.info(f"已删除插件目录: {plugin_path}")
                    except Exception as root_e:
                        self.logger.error(f"无法删除插件根目录 {plugin_path}: {str(root_e)}")
            elif os.path.isfile(plugin_path + ".py"):
                os.remove(plugin_path + ".py")
                self.logger.info(f"已删除插件文件: {plugin_path}.py")
            else:
                self.logger.warning(f"插件 {plugin_name} 不存在")
                return False
            
            # 删除插件的虚拟环境
            self.venv_manager.delete_venv(plugin_name)
            
            # 从插件列表中移除
            if plugin_name in self.all_plugins:
                self.all_plugins.remove(plugin_name)
            
            # 从已加载插件中移除
            if plugin_name in self.plugins:
                del self.plugins[plugin_name]
            
            # 从已加载插件名称列表中移除
            if plugin_name in self.loaded_plugins:
                self.loaded_plugins.remove(plugin_name)
            
            # 移除插件配置
            if plugin_name in self.plugin_configs:
                del self.plugin_configs[plugin_name]
                if self.config_manager:
                    self.config_manager.remove_plugin_config(plugin_name)
                self._save_plugin_configs()
            
            return True
        except Exception as e:
            self.logger.error(f"卸载插件 {plugin_name} 失败: {str(e)}")
            return False
    
    def enable_plugin(self, plugin_name: str, menu_system=None) -> bool:
        """启用插件"""
        try:
            # 更新插件配置
            plugin_config = self.get_plugin_config(plugin_name)
            plugin_config["enabled"] = True
            self.set_plugin_config(plugin_name, plugin_config)
            
            # 加载插件
            plugin = self.load_plugin(plugin_name)
            
            # 如果提供了menu_system，重新注册所有插件
            if menu_system and plugin:
                plugin.register(menu_system)
            
            return plugin is not None
        except Exception as e:
            self.logger.error(f"启用插件 {plugin_name} 失败: {str(e)}")
            return False
    
    def disable_plugin(self, plugin_name: str, menu_system=None) -> bool:
        """禁用插件"""
        try:
            # 更新插件配置
            plugin_config = self.get_plugin_config(plugin_name)
            plugin_config["enabled"] = False
            self.set_plugin_config(plugin_name, plugin_config)
            
            # 如果插件已加载，清理插件
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                try:
                    plugin.cleanup()
                except Exception as e:
                    self.logger.warning(f"清理插件 {plugin_name} 失败: {str(e)}")
                
                del self.plugins[plugin_name]
                if plugin_name in self.loaded_plugins:
                    self.loaded_plugins.remove(plugin_name)
            
            return True
        except Exception as e:
            self.logger.error(f"禁用插件 {plugin_name} 失败: {str(e)}")
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
        
        # 清理虚拟环境管理器
        self.venv_manager.cleanup()
    
    def install_plugin_from_github(self, repo_url: str) -> bool:
        """从GitHub仓库安装插件"""
        import subprocess
        import os
        import shutil
        
        # 提取仓库名
        if repo_url.endswith('.git'):
            repo_name = repo_url.split('/')[-1][:-4]
        else:
            repo_name = repo_url.split('/')[-1]
        
        # 初始化插件路径
        plugin_path = os.path.join(self.plugin_dir, repo_name)
        
        try:
            # 检查repo_url是否是有效的GitHub仓库URL
            if not repo_url.startswith('https://github.com/') and not repo_url.startswith('git@github.com:'):
                self.logger.error(f"无效的GitHub仓库URL: {repo_url}")
                return False
            
            # 检查仓库名是否符合FastX-Tui插件命名规范
            if not repo_name.startswith('FastX-Tui-Plugin-'):
                self.logger.error(f"GitHub仓库名必须以'FastX-Tui-Plugin-'开头: {repo_name}")
                return False
            
            # 检查插件目录是否已存在
            if os.path.exists(plugin_path):
                # 检查目录是否包含有效的插件文件
                fastx_plugin_file = os.path.join(plugin_path, 'fastx_tui_plugin.py')
                if os.path.isfile(fastx_plugin_file):
                    # 目录包含有效的插件文件，认为插件已存在
                    self.logger.error(f"插件 {repo_name} 已存在")
                    return False
                else:
                    # 目录存在但不包含有效的插件文件，删除空目录或无效目录
                    self.logger.warning(f"发现无效的插件目录 {repo_name}，将删除后重新安装")
                    try:
                        shutil.rmtree(plugin_path)
                    except Exception as e:
                        self.logger.error(f"删除无效插件目录失败: {str(e)}")
                        self.logger.error(f"请手动删除目录 {plugin_path} 后重试")
                        return False
            
            # 使用git clone命令下载仓库
            self.logger.info(f"正在从GitHub下载插件: {repo_url}")
            subprocess.run(
                ['git', 'clone', repo_url, plugin_path],
                check=True,
                capture_output=True,
                text=True
            )
            
            # 检查仓库中是否有fastx_tui_plugin.py入口文件
            if not os.path.isfile(os.path.join(plugin_path, 'fastx_tui_plugin.py')):
                self.logger.error(f"插件 {repo_name} 缺少fastx_tui_plugin.py入口文件")
                # 清理已下载的仓库
                shutil.rmtree(plugin_path)
                return False
            
            self.logger.info(f"插件 {repo_name} 安装成功")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git克隆失败: {e.stderr}")
            # 清理已创建的目录
            if os.path.exists(plugin_path):
                try:
                    shutil.rmtree(plugin_path)
                except Exception as cleanup_e:
                    self.logger.error(f"清理已创建目录失败: {str(cleanup_e)}")
                    self.logger.error(f"请手动删除目录 {plugin_path} 后重试")
            return False
        except Exception as e:
            self.logger.error(f"安装插件失败: {str(e)}")
            # 清理已创建的目录
            if os.path.exists(plugin_path):
                try:
                    shutil.rmtree(plugin_path)
                except Exception as cleanup_e:
                    self.logger.error(f"清理已创建目录失败: {str(cleanup_e)}")
                    self.logger.error(f"请手动删除目录 {plugin_path} 后重试")
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
            
            # 重新创建或更新虚拟环境
            plugin_path = os.path.join(self.plugin_dir, plugin_name)
            if os.path.exists(plugin_path):
                # 删除旧的虚拟环境
                self.venv_manager.delete_venv(plugin_name)
                
                # 重新创建虚拟环境
                if not self.venv_manager.create_venv(plugin_name, plugin_path):
                    self.logger.error(f"无法为插件 {plugin_name} 重新创建虚拟环境")
                    return False
            
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
        
        # 示例插件仓库列表，只包含仓库地址，信息通过get_plugin_info_from_github动态获取
        self.example_plugin_repos = [
            "https://github.com/fastxteam/FastX-Tui-Plugin-Example.git",
            "https://github.com/fastxteam/FastX-Tui-Plugin-DEMFaultAnalyzer.git"
        ]
        
        # 缓存插件信息
        self.plugin_info_cache = {}
    
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
            self.logger.debug(f"获取插件列表失败: {str(e)}")
            # 从示例插件仓库动态获取插件信息
            plugins = []
            
            for repo_url in self.example_plugin_repos:
                # 检查缓存中是否已有该插件信息
                if repo_url in self.plugin_info_cache:
                    plugin_info = self.plugin_info_cache[repo_url]
                else:
                    # 从GitHub获取插件信息
                    plugin_info = self.get_plugin_info_from_github(repo_url)
                    if plugin_info:
                        # 缓存插件信息
                        self.plugin_info_cache[repo_url] = plugin_info
                
                if plugin_info:
                    plugins.append(plugin_info)
            
            # 按分类过滤
            if category:
                plugins = [p for p in plugins if p["category"] == category]
            
            # 按搜索关键词过滤
            if search:
                search_lower = search.lower()
                plugins = [p for p in plugins if 
                          search_lower in p["name"].lower() or 
                          search_lower in p["description"].lower() or 
                          any(search_lower in tag.lower() for tag in p["tags"])]
            
            # 分页处理
            start = (page - 1) * per_page
            end = start + per_page
            paginated_plugins = plugins[start:end]
            
            return {
                "plugins": paginated_plugins,
                "total": len(plugins),
                "page": page,
                "per_page": per_page
            }
    
    def get_plugin_info_from_github(self, repo_url: str) -> Optional[Dict[str, Any]]:
        """从GitHub仓库获取插件信息，自动读取fastx_plugin.py"""
        try:
            import tempfile
            import os
            import sys
            import subprocess
            import importlib.util
            import requests
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # 克隆仓库到临时目录
                repo_name = repo_url.rstrip('.git').split('/')[-1]
                clone_dir = os.path.join(temp_dir, repo_name)
                
                # 执行git clone命令
                subprocess.run([
                    'git', 'clone', 
                    '--depth', '1',  # 只克隆最新的提交，加快速度
                    repo_url, 
                    clone_dir
                ], check=True, timeout=30, capture_output=True, text=True)
                
                # 检查fastx_tui_plugin.py是否存在
                fastx_plugin_path = os.path.join(clone_dir, 'fastx_tui_plugin.py')
                if not os.path.exists(fastx_plugin_path):
                    self.logger.error(f"仓库 {repo_url} 中没有找到fastx_tui_plugin.py")
                    return None
                
                # 添加克隆目录到sys.path，这样插件的依赖模块才能被找到
                sys.path.insert(0, clone_dir)
                
                try:
                    # 动态导入插件模块
                    spec = importlib.util.spec_from_file_location(
                        "temp_plugin",
                        fastx_plugin_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # 查找插件类
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                hasattr(attr, "get_info") and 
                                callable(getattr(attr, "get_info"))):
                                # 实例化插件并获取信息
                                plugin_instance = attr()
                                plugin_info = plugin_instance.get_info()
                                
                                # 提取用户名和仓库名用于生成ID
                                repo_url_clean = repo_url.rstrip('.git')
                                if 'github.com/' in repo_url_clean:
                                    parts = repo_url_clean.split('github.com/')[1].split('/')
                                    if len(parts) >= 2:
                                        user = parts[0]
                                        repo = parts[1]
                                        
                                        # 从GitHub API获取动态数据
                                        rating = plugin_info.rating
                                        downloads = plugin_info.downloads
                                        
                                        try:
                                            # 使用GitHub API获取仓库信息
                                            api_url = f"https://api.github.com/repos/{user}/{repo}"
                                            headers = {
                                                "Accept": "application/vnd.github.v3+json"
                                            }
                                            response = requests.get(api_url, headers=headers, timeout=5)
                                            if response.status_code == 200:
                                                repo_data = response.json()
                                                # 使用仓库星级作为评分（转换为0-5分制）
                                                rating = round(repo_data.get("stargazers_count", 0) / 20, 1)  # 假设最多100星，转换为5分制
                                                if rating > 5.0:
                                                    rating = 5.0
                                                # 使用仓库forks_count作为下载量（GitHub API没有直接的下载量字段）
                                                downloads = repo_data.get("forks_count", 0)
                                        except Exception as api_e:
                                            self.logger.debug(f"获取GitHub API数据失败: {str(api_e)}")
                                            # 如果API调用失败，使用插件中定义的默认值
                                        
                                        # 转换为字典
                                        return {
                                            "id": f"{user}-{repo}",
                                            "name": plugin_info.name,
                                            "version": plugin_info.version,
                                            "author": plugin_info.author,
                                            "description": plugin_info.description,
                                            "category": plugin_info.category,
                                            "tags": plugin_info.tags,
                                            "rating": rating,
                                            "downloads": downloads,
                                            "repository": repo_url,
                                            "homepage": repo_url,
                                            "license": plugin_info.license,
                                            "last_updated": plugin_info.last_updated
                                        }
                except Exception as e:
                    self.logger.error(f"解析GitHub插件信息失败: {str(e)}")
                finally:
                    # 从sys.path中移除克隆目录
                    sys.path.pop(0)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"克隆GitHub仓库失败: {e.stderr}")
        except Exception as e:
            self.logger.error(f"从GitHub获取插件信息失败: {str(e)}")
        
        # 如果没有fastx_plugin.py或解析失败，返回None
        return None
    
    def get_plugin_details(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """获取插件详情"""
        try:
            import requests
            
            response = requests.get(f"{self.base_url}/details/{plugin_id}", timeout=5)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            self.logger.debug(f"获取插件详情失败: {str(e)}")
            
            # 先确保插件信息已加载
            for repo_url in self.example_plugin_repos:
                if repo_url not in self.plugin_info_cache:
                    plugin_info = self.get_plugin_info_from_github(repo_url)
                    if plugin_info:
                        self.plugin_info_cache[repo_url] = plugin_info
            
            # 从缓存中查找插件详情
            plugins = list(self.plugin_info_cache.values())
            
            # 按ID查找
            for plugin in plugins:
                if plugin["id"] == plugin_id:
                    return plugin
            
            # 如果插件ID是数字，可能是用户输入的编号，尝试转换
            try:
                idx = int(plugin_id) - 1
                if 0 <= idx < len(plugins):
                    return plugins[idx]
            except ValueError:
                pass
            
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
            self.logger.debug(f"获取插件分类失败: {str(e)}")
            # 从动态获取的插件信息中提取分类
            categories = set()
            
            # 先确保插件信息已加载
            for repo_url in self.example_plugin_repos:
                if repo_url not in self.plugin_info_cache:
                    plugin_info = self.get_plugin_info_from_github(repo_url)
                    if plugin_info:
                        self.plugin_info_cache[repo_url] = plugin_info
                
                if repo_url in self.plugin_info_cache:
                    categories.add(self.plugin_info_cache[repo_url].get("category", "其他"))
            
            # 添加默认分类并转为列表
            default_categories = ["其他", "工具", "主题", "集成", "开发"]
            # 合并分类，去重并排序
            all_categories = sorted(list(set(default_categories + list(categories))))
            return all_categories
    
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