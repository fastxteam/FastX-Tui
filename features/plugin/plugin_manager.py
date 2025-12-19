#!/usr/bin/env python3
"""
FastX-Tui 插件管理界面模块
"""
import os
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt

from core.plugin_manager import PluginManager
from core.menu_system import MenuSystem
from config.config_manager import ConfigManager


class PluginInterface:
    """插件管理界面管理器"""
    
    def __init__(self, console: Console, plugin_manager: PluginManager, menu_system: MenuSystem, config_manager: ConfigManager):
        self.console = console
        self.plugin_manager = plugin_manager
        self.menu_system = menu_system
        self.config_manager = config_manager
    
    def show_plugin_interface(self):
        """显示插件管理界面"""
        while True:
            self.console.print("\n" + "=" * 70, style="cyan")
            self.console.print("插件管理".center(70), style="cyan bold")
            self.console.print("=" * 70 + "\n", style="cyan")
            
            # 显示插件列表
            plugins = self.plugin_manager.list_plugins()
            
            if plugins:
                self.console.print(f"📦 已加载插件 ({len(plugins)}):\n")
                for i, plugin_info in enumerate(plugins, 1):
                    status = "✅" if plugin_info.enabled else "❌"
                    self.console.print(
                        f"  {i}. {status} {plugin_info.name} "
                        f"v{plugin_info.version}"
                    )
                    self.console.print(f"     作者: {plugin_info.author}")
                    self.console.print(f"     描述: {plugin_info.description}")
                    self.console.print()
            else:
                self.console.print(f"[yellow]暂无已加载的插件[/yellow]\n")
            
            # 显示操作选项
            self.console.print(f"🛠️  插件操作:")
            self.console.print(f"  1. 重新加载所有插件")
            self.console.print(f"  2. 刷新插件列表")
            self.console.print(f"  3. 显示插件目录")
            self.console.print(f"  b. 返回主菜单")
            self.console.print(f"  q. 退出程序")
            
            self.console.print("\n" + "─" * 70, style="dim")
            choice = Prompt.ask(f"[bold cyan]请选择[/bold cyan]")
            
            if choice == '1':
                self._reload_plugins()
            elif choice == '2':
                self._refresh_plugins()
            elif choice == '3':
                self._show_plugin_directory()
            elif choice == 'b':
                # 返回主菜单前清屏
                self.console.print("\n" + "─" * 70, style="dim")
                self.console.print(f"[yellow]返回主菜单...[/yellow]")
                return
            elif choice == 'q':
                # 退出程序
                from sys import exit
                self.console.print(f"\n[green]感谢使用 FastX-Tui[/green]")
                exit(0)
            else:
                self.console.print(f"[red]❌ 无效的选择[/red]")
                input(f"\n按回车键继续...")
    
    def _reload_plugins(self):
        """重新加载插件"""
        self.console.print(f"\n🔄 正在重新加载插件...")
        
        # 清理现有插件
        self.plugin_manager.cleanup_all()
        
        # 重新加载
        self.plugin_manager.load_all_plugins()
        self.plugin_manager.register_all_plugins(self.menu_system)
        
        self.console.print(f"✅ 成功重新加载 {len(self.plugin_manager.plugins)} 个插件")
        input(f"\n按回车键继续...")
    
    def _refresh_plugins(self):
        """刷新插件列表"""
        self.console.print(f"\n🔄 正在刷新插件列表...")
        
        discovered = self.plugin_manager.discover_plugins()
        loaded = list(self.plugin_manager.plugins.keys())
        
        self.console.print(f"📁 发现插件: {len(discovered)}")
        self.console.print(f"🔌 已加载插件: {len(loaded)}")
        
        if discovered:
            self.console.print(f"\n📋 发现的插件:")
            for plugin in discovered:
                status = "✅" if plugin in loaded else "❌"
                self.console.print(f"  {status} {plugin}")
        
        input(f"\n按回车键继续...")
    
    def _show_plugin_directory(self):
        """显示插件目录"""
        plugin_dir = self.config_manager.get_config("plugin_directory", "plugins")
        
        self.console.print(f"\n📁 插件目录: {os.path.abspath(plugin_dir)}")
        
        if os.path.exists(plugin_dir):
            files = os.listdir(plugin_dir)
            if files:
                self.console.print(f"\n📋 目录内容:")
                for file in files:
                    if file.endswith('.py') and file != '__init__.py':
                        self.console.print(f"  📄 {file}")
                    else:
                        self.console.print(f"  📁 {file}")
            else:
                self.console.print(f"[yellow]目录为空[/yellow]")
        else:
            self.console.print(f"[yellow]目录不存在[/yellow]")
        
        input(f"\n按回车键继续...")


# 导出插件管理界面实例
plugin_interface = None

def get_plugin_interface(console: Optional[Console] = None, plugin_manager: Optional[PluginManager] = None, menu_system: Optional[MenuSystem] = None, config_manager: Optional[ConfigManager] = None) -> PluginInterface:
    """获取插件管理界面实例"""
    global plugin_interface
    if plugin_interface is None:
        if not console or not plugin_manager or not menu_system or not config_manager:
            raise ValueError("初始化时必须提供所有参数")
        plugin_interface = PluginInterface(console, plugin_manager, menu_system, config_manager)
    return plugin_interface
