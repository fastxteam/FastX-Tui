#!/usr/bin/env python3
"""
插件代理模块
用于处理插件与主程序之间的通信，确保它们可以安全地通信，同时保持环境隔离
"""
import json
from typing import Any

from .logger import get_logger


class PluginProxy:
    """插件代理类
    
    用于处理插件与主程序之间的通信，确保它们可以安全地通信，同时保持环境隔离
    """

    def __init__(self, plugin_name: str, venv_manager, plugin_path: str):
        """初始化插件代理
        
        Args:
            plugin_name: 插件名称
            venv_manager: 虚拟环境管理器实例
            plugin_path: 插件目录路径
        """
        self.plugin_name = plugin_name
        self.venv_manager = venv_manager
        self.plugin_path = plugin_path
        self.logger = get_logger(f"PluginProxy.{plugin_name}")

    def call_plugin_method(self, method_name: str, *args, **kwargs) -> Any | None:
        """调用插件方法
        
        Args:
            method_name: 要调用的方法名称
            *args: 方法参数
            **kwargs: 方法关键字参数
        
        Returns:
            Optional[Any]: 方法调用结果
        """
        try:
            # 构建调用脚本
            call_script = f"""
import sys
import json
import importlib.util
import os

# 获取插件入口文件路径
plugin_path = {json.dumps(self.plugin_path)}
entry_file = os.path.join(plugin_path, 'fastx_tui_plugin.py')

# 动态导入插件模块
spec = importlib.util.spec_from_file_location('fastx_tui_plugin', entry_file)
module = importlib.util.module_from_spec(spec)
sys.path.insert(0, plugin_path)
spec.loader.exec_module(module)

# 查找插件类
plugin_class = None
for attr_name in dir(module):
    attr = getattr(module, attr_name)
    if isinstance(attr, type) and hasattr(attr, 'get_info') and callable(getattr(attr, 'get_info')):
        plugin_class = attr
        break

if not plugin_class:
    print(json.dumps({'error': 'Plugin class not found'}))
    sys.exit(1)

# 实例化插件
plugin = plugin_class()
plugin.plugin_path = plugin_path

# 调用指定方法
try:
    if hasattr(plugin, '{method_name}'):
        method = getattr(plugin, '{method_name}')
        result = method({json.dumps(args)}, {json.dumps(kwargs)})
        print(json.dumps({'result': result}))
    else:
        print(json.dumps({'error': f'Method {method_name} not found'}))
        sys.exit(1)
except Exception as e:
    print(json.dumps({'error': str(e)}))
    sys.exit(1)
"""

            # 执行调用脚本
            result = self.venv_manager.run_in_venv(
                self.plugin_name,
                [call_script],
                self.plugin_path
            )

            if result and result['returncode'] == 0:
                # 解析结果
                output = result['stdout'].strip()
                if output:
                    try:
                        result_data = json.loads(output)
                        if 'error' in result_data:
                            self.logger.error(f"调用插件 {self.plugin_name} 方法 {method_name} 失败: {result_data['error']}")
                            return None
                        return result_data.get('result')
                    except json.JSONDecodeError as e:
                        self.logger.error(f"解析插件 {self.plugin_name} 方法调用结果失败: {str(e)}")
                        return None
            else:
                self.logger.error(f"调用插件 {self.plugin_name} 方法 {method_name} 失败: {result['stderr'] if result else 'Unknown error'}")
                return None

        except Exception as e:
            self.logger.error(f"调用插件 {self.plugin_name} 方法 {method_name} 时发生错误: {str(e)}")
            return None

    def get_plugin_info(self) -> dict[str, Any] | None:
        """获取插件信息
        
        Returns:
            Optional[Dict[str, Any]]: 插件信息
        """
        return self.call_plugin_method('get_info')

    def initialize_plugin(self) -> bool:
        """初始化插件
        
        Returns:
            bool: 是否成功初始化插件
        """
        result = self.call_plugin_method('initialize')
        return result is not None

    def cleanup_plugin(self) -> bool:
        """清理插件资源
        
        Returns:
            bool: 是否成功清理插件资源
        """
        result = self.call_plugin_method('cleanup')
        return result is not None

    def register_plugin(self, menu_system) -> bool:
        """注册插件到菜单系统
        
        Args:
            menu_system: 菜单系统实例
        
        Returns:
            bool: 是否成功注册插件
        """
        # 这里需要实现更复杂的逻辑，将菜单系统的相关方法传递给插件
        # 由于涉及到对象传递，可能需要使用更高级的序列化机制
        self.logger.warning(f"插件 {self.plugin_name} 注册到菜单系统的功能需要进一步实现")
        return True

    def execute_command(self, command: str, *args, **kwargs) -> Any | None:
        """执行插件命令
        
        Args:
            command: 要执行的命令名称
            *args: 命令参数
            **kwargs: 命令关键字参数
        
        Returns:
            Optional[Any]: 命令执行结果
        """
        try:
            # 构建命令执行脚本
            execute_script = f"""
import sys
import json
import importlib.util
import os

# 获取插件入口文件路径
plugin_path = {json.dumps(self.plugin_path)}
entry_file = os.path.join(plugin_path, 'fastx_tui_plugin.py')

# 动态导入插件模块
spec = importlib.util.spec_from_file_location('fastx_tui_plugin', entry_file)
module = importlib.util.module_from_spec(spec)
sys.path.insert(0, plugin_path)
spec.loader.exec_module(module)

# 查找插件类
plugin_class = None
for attr_name in dir(module):
    attr = getattr(module, attr_name)
    if isinstance(attr, type) and hasattr(attr, 'get_info') and callable(getattr(attr, 'get_info')):
        plugin_class = attr
        break

if not plugin_class:
    print(json.dumps({'error': 'Plugin class not found'}))
    sys.exit(1)

# 实例化插件
plugin = plugin_class()
plugin.plugin_path = plugin_path

# 执行命令
try:
    # 这里假设插件有一个execute_command方法，或者根据命令名称调用相应的方法
    if hasattr(plugin, 'execute_command'):
        result = plugin.execute_command('{command}', {json.dumps(args)}, {json.dumps(kwargs)})
        print(json.dumps({'result': result}))
    else:
        print(json.dumps({'error': f'Command {command} not supported'}))
        sys.exit(1)
except Exception as e:
    print(json.dumps({'error': str(e)}))
    sys.exit(1)
"""

            # 执行命令
            result = self.venv_manager.run_in_venv(
                self.plugin_name,
                [execute_script],
                self.plugin_path
            )

            if result and result['returncode'] == 0:
                # 解析结果
                output = result['stdout'].strip()
                if output:
                    try:
                        result_data = json.loads(output)
                        if 'error' in result_data:
                            self.logger.error(f"执行插件 {self.plugin_name} 命令 {command} 失败: {result_data['error']}")
                            return None
                        return result_data.get('result')
                    except json.JSONDecodeError as e:
                        self.logger.error(f"解析插件 {self.plugin_name} 命令执行结果失败: {str(e)}")
                        return None
            else:
                self.logger.error(f"执行插件 {self.plugin_name} 命令 {command} 失败: {result['stderr'] if result else 'Unknown error'}")
                return None

        except Exception as e:
            self.logger.error(f"执行插件 {self.plugin_name} 命令 {command} 时发生错误: {str(e)}")
            return None
