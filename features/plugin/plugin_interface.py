#!/usr/bin/env python3
"""
FastX-Tui 插件管理界面模块
"""
import os
import sys
from typing import Optional

from rich.console import Console
from rich.table import Table

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
    
    def show_plugin_interface(self, view_manager=None) -> bool:
        """显示插件管理界面"""
        while True:
            self.console.clear()
            self._show_plugin_menu()
            choice = self._get_user_choice()
            if choice == 'b':
                return True
            elif choice == 'q':
                return False
            self._handle_choice(choice, view_manager)
    
    def _show_plugin_menu(self):
        """显示插件管理菜单"""
        self.console.print("=" * 80)
        self.console.print("🧩 插件管理中心".center(80), style="bold cyan")
        self.console.print("=" * 80)
        self.console.print()
        
        # 显示插件列表
        plugins = self.plugin_manager.list_plugins()
        
        if plugins:
            self.console.print(f"📦 已加载插件 ({len(plugins)}):")
            
            # 创建表格显示插件信息
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("编号", style="cyan bold", justify="center")
            table.add_column("状态", justify="center")
            table.add_column("名称", style="white")
            table.add_column("版本", style="green")
            table.add_column("作者", style="yellow")
            
            for i, plugin_info in enumerate(plugins, 1):
                status = "✅" if plugin_info.enabled else "❌"
                table.add_row(
                    f"{i}",
                    status,
                    plugin_info.name,
                    f"v{plugin_info.version}",
                    plugin_info.author
                )
            
            self.console.print(table)
            self.console.print()
            
            # 显示插件详细信息
            for i, plugin_info in enumerate(plugins, 1):
                self.console.print(f"{i}. {plugin_info.name} 描述:")
                self.console.print(f"   {plugin_info.description}")
                self.console.print()
        else:
            self.console.print(f"[yellow]暂无已加载的插件[/yellow]")
            self.console.print()
        
        # 显示插件操作选项
        menu_items = [
            "1. 重新加载所有插件",
            "2. 刷新插件列表",
            "3. 显示插件目录",
            "4. 启用/禁用插件",
            "b. 返回主菜单",
            "q. 退出"
        ]
        
        for item in menu_items:
            self.console.print(item, style="white")
        
        self.console.print()
        plugin_dir = self.config_manager.get_config("plugin_directory", "plugins")
        self.console.print(f"📁 插件目录: {os.path.abspath(plugin_dir)}", style="bold yellow")
        self.console.print()
    
    def _get_user_choice(self) -> str:
        """获取用户选择"""
        self.console.print("请输入您的选择 (1-4, b, q): ", style="bold green", end="")
        
        # 使用无缓冲输入
        if sys.platform == "win32":
            import msvcrt
            choice = msvcrt.getch().decode('utf-8').lower()
            self.console.print(choice)
        else:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                choice = sys.stdin.read(1).lower()
                self.console.print(choice)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        return choice
    
    def _handle_choice(self, choice: str, view_manager=None):
        """处理用户选择"""
        if choice == '1':
            self._reload_plugins()
        elif choice == '2':
            self._refresh_plugins()
        elif choice == '3':
            self._show_plugin_directory()
        elif choice == '4':
            self._toggle_plugin()
        
        if choice != 'b' and choice != 'q':
            self.console.print("\n按任意键继续...", style="dim")
            if sys.platform == "win32":
                import msvcrt
                msvcrt.getch()
            else:
                import termios
                import tty
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def _reload_plugins(self):
        """重新加载插件"""
        self.console.print("\n" + "-" * 80)
        self.console.print("🔄 重新加载插件".center(80), style="bold green")
        self.console.print("-" * 80)
        
        self.console.print(f"正在重新加载插件...")
        
        # 清理现有插件
        self.plugin_manager.cleanup_all()
        
        # 重新加载
        self.plugin_manager.load_all_plugins()
        self.plugin_manager.register_all_plugins(self.menu_system)
        
        self.console.print(f"✅ 成功重新加载 {len(self.plugin_manager.plugins)} 个插件", style="bold green")
    
    def _refresh_plugins(self):
        """刷新插件列表"""
        self.console.print("\n" + "-" * 80)
        self.console.print("🔍 刷新插件列表".center(80), style="bold green")
        self.console.print("-" * 80)
        
        discovered = self.plugin_manager.discover_plugins()
        loaded = list(self.plugin_manager.plugins.keys())
        
        self.console.print(f"📁 发现插件: {len(discovered)}")
        self.console.print(f"🔌 已加载插件: {len(loaded)}")
        
        if discovered:
            self.console.print(f"\n📋 发现的插件:")
            for plugin in discovered:
                status = "✅ 已加载" if plugin in loaded else "❌ 未加载"
                self.console.print(f"  {plugin}: {status}")
    
    def _show_plugin_directory(self):
        """显示插件目录"""
        self.console.print("\n" + "-" * 80)
        self.console.print("📁 插件目录".center(80), style="bold green")
        self.console.print("-" * 80)
        
        plugin_dir = self.config_manager.get_config("plugin_directory", "plugins")
        abs_plugin_dir = os.path.abspath(plugin_dir)
        
        self.console.print(f"插件目录路径: {abs_plugin_dir}")
        
        if os.path.exists(abs_plugin_dir):
            files = os.listdir(abs_plugin_dir)
            if files:
                self.console.print(f"\n目录内容:")
                for file in files:
                    file_path = os.path.join(abs_plugin_dir, file)
                    if os.path.isfile(file_path) and file.endswith('.py') and file != '__init__.py':
                        self.console.print(f"  📄 {file}")
                    elif os.path.isdir(file_path):
                        self.console.print(f"  📁 {file}/")
                    else:
                        self.console.print(f"  📄 {file}")
            else:
                self.console.print(f"\n[yellow]目录为空[/yellow]")
        else:
            self.console.print(f"\n[red]目录不存在[/red]")
    
    def _toggle_plugin(self):
        """启用/禁用插件"""
        plugins = self.plugin_manager.list_plugins()
        
        if not plugins:
            self.console.print(f"\n[yellow]暂无已加载的插件[/yellow]")
            return
        
        self.console.print("\n" + "-" * 80)
        self.console.print("⚙️  启用/禁用插件".center(80), style="bold green")
        self.console.print("-" * 80)
        
        # 显示插件列表供选择
        for i, plugin_info in enumerate(plugins, 1):
            status = "✅ 已启用" if plugin_info.enabled else "❌ 已禁用"
            self.console.print(f"{i}. {plugin_info.name} - {status}")
        
        self.console.print("0. 返回")
        self.console.print()
        
        self.console.print("请输入插件编号: ", style="bold green", end="")
        choice = input().strip()
        
        if choice == '0':
            return
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(plugins):
                plugin_info = plugins[idx]
                self.console.print(f"\n暂不支持动态启用/禁用插件", style="yellow")
                self.console.print(f"插件 {plugin_info.name} 当前状态: {'启用' if plugin_info.enabled else '禁用'}")
            else:
                self.console.print(f"\n[red]无效的插件编号[/red]")
        except ValueError:
            self.console.print(f"\n[red]无效的输入[/red]")
