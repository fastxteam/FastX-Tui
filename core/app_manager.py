#!/usr/bin/env python3
"""
FastX-Tui 应用管理器
"""
import os
import sys
import time
from typing import Dict, Any, Optional

from rich.console import Console

from core.logger import get_logger
from core.menu_system import MenuSystem, MenuType
from core.operations import SystemOperations, FileOperations, PythonOperations
from core.plugin_manager import PluginManager
from core.view_manager import ViewManager, ViewRoute
from core.update_manager import UpdateManager
from core.network_tools import NetworkToolsPlugin
from core.version import FULL_VERSION, VERSION
from config.config_manager import ConfigManager
from features.search import SearchFeature
from features.help import HelpFeature
from features.config.config_interface import ConfigInterface
from features.plugin.plugin_interface import PluginInterface
from features.log_management import LogManager

class AppManager:
    """应用管理器"""
    
    def __init__(self):
        # 初始化控制台
        self.console = Console()
        
        # 初始化日志
        self.logger = get_logger(self.__class__.__name__)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化菜单系统
        self.menu_system = MenuSystem(self.console)
        
        # 初始化视图管理器
        self.view_manager = ViewManager(self.console, self.config_manager)
        
        # 初始化插件管理器
        self.plugin_manager = PluginManager(
            self.config_manager.get_config("plugin_directory", "plugins")
        )
        
        # 初始化搜索功能
        self.search_feature = SearchFeature(self.menu_system, self.console, self.config_manager)
        
        # 初始化帮助功能
        self.help_feature = HelpFeature(self.console)
        
        # 初始化配置功能
        self.config_interface = ConfigInterface(self.console, self.config_manager)
        
        # 初始化插件功能
        self.plugin_interface = PluginInterface(self.console, self.plugin_manager, self.menu_system, self.config_manager)
        
        # 初始化日志管理功能
        self.log_manager = LogManager(self.console, self.config_manager)
        
        # 初始化操作类
        self.operations = {
            'system': SystemOperations(),
            'file': FileOperations(),
            'python': PythonOperations()
        }
        
        # 性能监控
        self.start_time = time.time()
        self.command_count = 0
        
        # 版本信息
        self.current_version = FULL_VERSION
        
        # 初始化网络工具插件
        self.network_tools = NetworkToolsPlugin()
        self.network_tools.initialize()
        
        # 初始化更新管理器
        self.update_manager = UpdateManager(self.config_manager, self.current_version, self.console)
        self.update_manager.set_network_tools(self.network_tools)
        
        # 将update_manager传递给view_manager
        self.view_manager.set_update_manager(self.update_manager)
    
    def initialize(self):
        """初始化应用"""
        try:
            # 初始化系统
            self._init_system()
            
            # 根据配置检查版本更新
            if self.config_manager.get_config("auto_check_updates", True):
                update_available, latest_version = self.update_manager.check_for_updates()
                # 不再直接显示更新提示，将由view_manager在渲染布局时自动显示
            
            # 注册所有菜单和命令为路由
            self._register_routes()
            
            return True
        except Exception as e:
            self.logger.error(f"应用初始化失败: {str(e)}")
            self.console.print(f"[red]❌ 应用初始化失败: {str(e)}[/red]")
            return False
    
    def _init_system(self):
        """初始化系统"""
        # 先初始化菜单
        self._init_menu()
        
        # 加载插件
        if self.config_manager.get_config("plugin_auto_load", True):
            self.plugin_manager.load_all_plugins()
            self.plugin_manager.register_all_plugins(self.menu_system)
            
            # 重新构建插件菜单，确保所有插件命令都被正确添加
            self._rebuild_plugin_menu()
        
        # 应用用户偏好
        self._apply_user_preferences()
        
        # 动态注册所有菜单和命令路由，包括插件生成的
        self._register_dynamic_routes()
        
        # 显示欢迎信息（根据配置决定）
        if self.config_manager.get_config("show_welcome_page", True):
            self._show_welcome_message()
    
    def _init_menu(self):
        """初始化菜单结构"""
        from core.menu_system import MenuNode, ActionItem, CommandType
        
        # 创建主菜单
        main_menu = MenuNode(
            id="main_menu",
            name="主菜单",
            description="FastX-Tui 主菜单",
            menu_type=MenuType.MAIN,
            icon="🏠"
        )
        
        # 系统工具菜单
        system_menu = MenuNode(
            id="system_tools_menu",
            name="系统工具",
            description="系统信息和管理工具",
            menu_type=MenuType.SUB,
            icon="🖥️"
        )
        
        # 文件工具菜单
        file_menu = MenuNode(
            id="file_tools_menu",
            name="文件工具",
            description="文件管理和操作工具",
            menu_type=MenuType.SUB,
            icon="📁"
        )
        
        # Python工具菜单
        python_menu = MenuNode(
            id="python_tools_menu",
            name="Python工具",
            description="Python开发和运行时工具",
            menu_type=MenuType.SUB,
            icon="🐍"
        )
        
        # 注册菜单
        self.menu_system.register_item(main_menu)
        self.menu_system.register_item(system_menu)
        self.menu_system.register_item(file_menu)
        self.menu_system.register_item(python_menu)
        
        # 系统工具
        system_menu.add_item(ActionItem(
            id="system_info",
            name="系统信息",
            description="显示系统详细信息",
            icon="📊",
            command_type=CommandType.PYTHON,
            python_func=self.operations['system'].get_system_info
        ))
        
        system_menu.add_item(ActionItem(
            id="network_info",
            name="网络信息",
            description="显示网络配置信息",
            icon="🌐",
            command_type=CommandType.PYTHON,
            python_func=self.operations['system'].get_network_info
        ))
        
        system_menu.add_item(ActionItem(
            id="process_list",
            name="进程列表",
            description="列出所有运行中的进程",
            icon="📋",
            command_type=CommandType.PYTHON,
            python_func=self.operations['system'].list_processes
        ))
        
        system_menu.add_item(ActionItem(
            id="disk_space",
            name="磁盘空间",
            description="显示磁盘使用情况",
            icon="💾",
            command_type=CommandType.PYTHON,
            python_func=self.operations['system'].get_disk_space
        ))
        
        system_menu.add_item(ActionItem(
            id="system_uptime",
            name="系统运行时间",
            description="显示系统运行时间",
            icon="⏰",
            command_type=CommandType.PYTHON,
            python_func=self.operations['system'].get_system_uptime
        ))
        
        # 文件工具
        file_menu.add_item(ActionItem(
            id="list_directory",
            name="目录列表",
            description="列出目录内容",
            icon="📄",
            command_type=CommandType.PYTHON,
            python_func=self.operations['file'].list_directory
        ))
        
        file_menu.add_item(ActionItem(
            id="file_tree",
            name="文件树",
            description="显示文件系统树状结构",
            icon="🌳",
            command_type=CommandType.PYTHON,
            python_func=self.operations['file'].show_file_tree
        ))
        
        file_menu.add_item(ActionItem(
            id="search_files",
            name="文件搜索",
            description="搜索文件系统中的文件",
            icon="🔍",
            command_type=CommandType.PYTHON,
            python_func=self.operations['file'].search_files
        ))
        
        # Python工具
        python_menu.add_item(ActionItem(
            id="python_info",
            name="Python信息",
            description="显示Python环境信息",
            icon="🐍",
            command_type=CommandType.PYTHON,
            python_func=self.operations['python'].get_python_info
        ))
        
        python_menu.add_item(ActionItem(
            id="python_packages",
            name="Python包",
            description="列出已安装的Python包",
            icon="📦",
            command_type=CommandType.PYTHON,
            python_func=self.operations['python'].list_packages
        ))
        
        python_menu.add_item(ActionItem(
            id="check_imports",
            name="检查导入",
            description="检查Python模块导入",
            icon="🔍",
            command_type=CommandType.PYTHON,
            python_func=self.operations['python'].check_imports
        ))
        
        # 将子菜单添加到主菜单
        main_menu.add_item("system_tools_menu")
        main_menu.add_item("file_tools_menu")
        main_menu.add_item("python_tools_menu")
        
        # 创建插件主菜单
        plugins_menu = MenuNode(
            id="plugins_menu",
            name="插件命令",
            description="所有已安装插件的命令",
            menu_type=MenuType.SUB,
            icon="🔌"
        )
        self.menu_system.register_item(plugins_menu)
        
        # 设置当前菜单
        self.menu_system.current_menu = main_menu
    
    def _register_dynamic_routes(self):
        """动态注册所有菜单和命令为路由，包括插件生成的"""
        from core.menu_system import MenuNode, MenuItem, ActionItem
        
        # 动态注册所有菜单节点
        for item_id, item in self.menu_system.items.items():
            if isinstance(item, MenuNode) and item_id not in self.view_manager.routes:
                # 注册菜单路由
                self.view_manager.register_route(ViewRoute(
                    id=item_id,
                    name=item.name,
                    description=item.description,
                    handler=self._render_menu,
                    parent_id="main_menu",  # 默认为主菜单的子菜单
                    icon=item.icon if hasattr(item, 'icon') else "📁",
                    type="menu"
                ))
        
        # 注册所有插件命令路由
        for item_id, item in self.menu_system.items.items():
            if isinstance(item, (MenuItem, ActionItem)) and item_id not in self.view_manager.routes:
                # 注册命令路由
                self.view_manager.register_route(ViewRoute(
                    id=item_id,
                    name=item.name,
                    description=item.description,
                    handler=self._render_menu,  # 使用统一的菜单渲染
                    parent_id="plugins_menu" if "plugin" in item_id.lower() else "main_menu",
                    icon=item.icon if hasattr(item, 'icon') else "▶",
                    type="command"
                ))
    
    def _rebuild_plugin_menu(self):
        """重建插件菜单"""
        from core.menu_system import MenuNode
        
        # 获取插件菜单
        plugins_menu = self.menu_system.get_item_by_id("plugins_menu")
        if not isinstance(plugins_menu, MenuNode):
            # 如果插件菜单不存在，创建它
            plugins_menu = MenuNode(
                id="plugins_menu",
                name="插件命令",
                description="所有已安装插件的命令",
                menu_type=MenuType.SUB,
                icon="🔌"
            )
            self.menu_system.register_item(plugins_menu)
        
        # 清空现有插件菜单项
        plugins_menu.items.clear()
        
        # 获取主菜单
        main_menu = self.menu_system.get_item_by_id("main_menu")
        if not isinstance(main_menu, MenuNode):
            return
        
        # 从主菜单中移除插件菜单（如果存在）
        if "plugins_menu" in main_menu.items:
            main_menu.items.remove("plugins_menu")
        
        # 添加所有已注册的插件命令和子菜单到插件主菜单
        plugin_items_added = False
        for item_id, item in self.menu_system.items.items():
            # 跳过已经添加过的项目和固定项
            if item_id not in ["main_menu", "system_tools_menu", "file_tools_menu", "python_tools_menu", "show_config", "plugin_manager", "clear_screen", "show_help", "exit_app", "plugins_menu"]:
                # 添加所有插件创建的项目，包括MenuNode类型的子菜单
                if isinstance(item, MenuNode):
                    # 插件创建的子菜单，直接添加到插件主菜单
                    plugins_menu.add_item(item_id)
                    plugin_items_added = True
                else:
                    # 插件命令，直接添加到插件主菜单
                    plugins_menu.add_item(item_id)
                    plugin_items_added = True
        
        # 如果有插件命令，将插件菜单重新添加到主菜单
        if plugin_items_added:
            main_menu.add_item("plugins_menu")
        
        # 动态注册所有菜单和命令路由，包括插件生成的
        self._register_dynamic_routes()
    
    def _apply_user_preferences(self):
        """应用用户偏好"""
        from core.menu_system import MenuNode
        
        # 设置默认菜单
        default_menu = self.config_manager.get_preference("preferred_menu", "main_menu")
        menu_item = self.menu_system.get_item_by_id(default_menu)
        if isinstance(menu_item, MenuNode):
            self.menu_system.current_menu = menu_item
    
    def _show_welcome_message(self):
        """显示欢迎信息"""
        self.view_manager.clear_screen()
        
        # 显示横幅
        self.view_manager._render_banner(version=self.current_version)
        
        # 显示版本信息
        self.console.print("\n" + "=" * 70, style="cyan")
        welcome_msg = f"欢迎使用 FastX-Tui {self.current_version}"
        self.console.print(welcome_msg.center(70), style="cyan bold")
        self.console.print("=" * 70 + "\n", style="cyan")
        
        # 显示系统信息
        import platform
        self.console.print(f"💻 系统信息: {platform.system()} {platform.version()}")
        self.console.print(f"🐍 Python: {platform.python_version()}")
        
        self.console.print(f"🔌 插件数量: {len(self.plugin_manager.plugins)}")
        
        # 显示提示
        self.console.print(f"\n💡 帮助提示:")
        self.console.print(f"  • 输入 h - 显示帮助信息")
        self.console.print(f"  • 输入 s - 搜索功能")
        self.console.print(f"  • 输入 q - 退出程序")
        
        self.console.print("\n" + "─" * 70, style="dim")
        
        # 等待用户确认后清屏
        input(f"\n按回车键继续...")
        self.view_manager.clear_screen()
    
    def _register_routes(self):
        """注册所有菜单和命令为路由"""
        # 注册主菜单路由
        self.view_manager.register_route(ViewRoute(
            id="main_menu",
            name="主菜单",
            description="FastX-Tui 主菜单",
            handler=self._render_menu,
            parent_id=None,
            icon="🏠",
            type="menu"
        ))
        
        # 注册系统工具菜单路由
        self.view_manager.register_route(ViewRoute(
            id="system_tools_menu",
            name="系统工具",
            description="系统信息和管理工具",
            handler=self._render_menu,
            parent_id="main_menu",
            icon="🖥️",
            type="menu"
        ))
        
        # 注册文件工具菜单路由
        self.view_manager.register_route(ViewRoute(
            id="file_tools_menu",
            name="文件工具",
            description="文件管理和操作工具",
            handler=self._render_menu,
            parent_id="main_menu",
            icon="📁",
            type="menu"
        ))
        
        # 注册Python工具菜单路由
        self.view_manager.register_route(ViewRoute(
            id="python_tools_menu",
            name="Python工具",
            description="Python开发和运行时工具",
            handler=self._render_menu,
            parent_id="main_menu",
            icon="🐍",
            type="menu"
        ))
        
        # 注册设置菜单路由
        self.view_manager.register_route(ViewRoute(
            id="settings_menu",
            name="设置",
            description="应用设置和管理",
            handler=self._render_menu,
            parent_id="main_menu",
            icon="⚙️",
            type="menu"
        ))
        
        # 注册配置功能路由
        self.view_manager.register_route(ViewRoute(
            id="show_config",
            name="配置管理",
            description="查看和修改应用配置",
            handler=self.show_config_interface,
            parent_id="settings_menu",
            icon="⚙️",
            type="command"
        ))
        
        # 注册插件管理路由
        self.view_manager.register_route(ViewRoute(
            id="plugin_manager",
            name="插件管理",
            description="查看和管理插件",
            handler=self.show_plugin_interface,
            parent_id="settings_menu",
            icon="🔌",
            type="command"
        ))
        
        # 注册日志管理路由
        self.view_manager.register_route(ViewRoute(
            id="log_manager",
            name="日志管理",
            description="查看和管理应用日志",
            handler=self.show_log_interface,
            parent_id="settings_menu",
            icon="📊",
            type="command"
        ))
        
        # 注册系统命令路由
        self.view_manager.register_route(ViewRoute(
            id="system_info",
            name="系统信息",
            description="显示系统详细信息",
            handler=self.operations['system'].get_system_info,
            parent_id="system_tools_menu",
            icon="📊",
            type="command"
        ))
        
        self.view_manager.register_route(ViewRoute(
            id="network_info",
            name="网络信息",
            description="显示网络配置信息",
            handler=self.operations['system'].get_network_info,
            parent_id="system_tools_menu",
            icon="🌐",
            type="command"
        ))
        
        self.view_manager.register_route(ViewRoute(
            id="process_list",
            name="进程列表",
            description="列出所有运行中的进程",
            handler=self.operations['system'].list_processes,
            parent_id="system_tools_menu",
            icon="📋",
            type="command"
        ))
        
        self.view_manager.register_route(ViewRoute(
            id="disk_space",
            name="磁盘空间",
            description="显示磁盘使用情况",
            handler=self.operations['system'].get_disk_space,
            parent_id="system_tools_menu",
            icon="💾",
            type="command"
        ))
        
        self.view_manager.register_route(ViewRoute(
            id="system_uptime",
            name="系统运行时间",
            description="显示系统运行时间",
            handler=self.operations['system'].get_system_uptime,
            parent_id="system_tools_menu",
            icon="⏰",
            type="command"
        ))
        
        # 注册文件命令路由
        self.view_manager.register_route(ViewRoute(
            id="list_directory",
            name="目录列表",
            description="列出目录内容",
            handler=self.operations['file'].list_directory,
            parent_id="file_tools_menu",
            icon="📄",
            type="command"
        ))
        
        self.view_manager.register_route(ViewRoute(
            id="file_tree",
            name="文件树",
            description="显示文件系统树状结构",
            handler=self.operations['file'].show_file_tree,
            parent_id="file_tools_menu",
            icon="🌳",
            type="command"
        ))
        
        self.view_manager.register_route(ViewRoute(
            id="search_files",
            name="文件搜索",
            description="搜索文件系统中的文件",
            handler=self.operations['file'].search_files,
            parent_id="file_tools_menu",
            icon="🔍",
            type="command"
        ))
        
        # 注册Python命令路由
        self.view_manager.register_route(ViewRoute(
            id="python_info",
            name="Python信息",
            description="显示Python环境信息",
            handler=self.operations['python'].get_python_info,
            parent_id="python_tools_menu",
            icon="🐍",
            type="command"
        ))
        
        self.view_manager.register_route(ViewRoute(
            id="python_packages",
            name="Python包",
            description="列出已安装的Python包",
            handler=self.operations['python'].list_packages,
            parent_id="python_tools_menu",
            icon="📦",
            type="command"
        ))
        
        self.view_manager.register_route(ViewRoute(
            id="check_imports",
            name="检查导入",
            description="检查Python模块导入",
            handler=self.operations['python'].check_imports,
            parent_id="python_tools_menu",
            icon="🔍",
            type="command"
        ))
        
        # 注册固定功能路由
        self.view_manager.register_route(ViewRoute(
            id="clear_screen",
            name="清屏",
            description="清除屏幕内容",
            handler=self.view_manager.clear_screen,
            parent_id=None,
            icon="🧹",
            type="command"
        ))
        
        self.view_manager.register_route(ViewRoute(
            id="show_help",
            name="帮助",
            description="显示帮助信息",
            handler=self.show_help,
            parent_id=None,
            icon="❓",
            type="command"
        ))
        
        self.view_manager.register_route(ViewRoute(
            id="update_app",
            name="检查更新",
            description="检查并更新应用到最新版本",
            handler=self.update_app,
            parent_id=None,
            icon="🔄",
            type="command"
        ))
        
        self.view_manager.register_route(ViewRoute(
            id="exit_app",
            name="退出",
            description="退出应用程序",
            handler=self.handle_exit,
            parent_id=None,
            icon="🚪",
            type="command"
        ))
        
        # 注册插件菜单路由
        self.view_manager.register_route(ViewRoute(
            id="plugins_menu",
            name="插件命令",
            description="所有已安装插件的命令",
            handler=self._render_menu,
            parent_id="main_menu",
            icon="🔌",
            type="menu"
        ))
    
    def _render_menu(self, *args, **kwargs):
        """渲染当前菜单"""
        if not self.menu_system.current_menu:
            self.menu_system.navigate_to_menu("main_menu")
        
        # 使用视图管理器渲染菜单，并传递menu_system参数
        self.view_manager.render_menu(self.menu_system.current_menu, self.menu_system)
    
    def show_config_interface(self):
        """显示配置界面"""
        self.config_interface.show_config_interface()
    
    def show_plugin_interface(self):
        """显示插件管理界面"""
        self.plugin_interface.show_plugin_interface()
    
    def show_log_interface(self):
        """显示日志管理界面"""
        self.log_manager.show_log_interface()
    
    def show_help(self, *args, **kwargs):
        """显示帮助信息"""
        self.help_feature.show_help()
    
    def update_app(self):
        """检查并更新应用到最新版本"""
        # 先检查是否有可用更新
        update_available, latest_version = self.update_manager.check_for_updates(force_check=True)
        
        if update_available:
            # 执行更新
            success = self.update_manager.update_app()
            if success:
                # 询问用户是否重启应用
                from rich.prompt import Confirm
                should_restart = Confirm.ask("\n是否立即重启应用以应用更新?")
                if should_restart:
                    import os
                    import sys
                    # 重启应用
                    self.console.print("[green]正在重启应用...[/green]")
                    self.cleanup()
                    os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            self.console.print("[yellow]当前已是最新版本，无需更新[/yellow]")
    
    def handle_exit(self):
        """处理退出"""
        # 这个方法将在后续移到features/exit模块中
        self.cleanup()
        import sys
        self.console.print(f"\n[green]感谢使用 FastX-Tui[/green]\n")
        sys.exit(0)
    
    def _show_hints(self):
        """显示快捷键提示"""
        # 此方法已过时，快捷栏和状态栏现在由ViewManager统一渲染
        pass
    
    def _get_user_choice(self) -> str:
        """获取用户选择"""
        from rich.prompt import Prompt
        
        display_items = self.menu_system.current_menu.get_display_items(self.menu_system)
        
        # 构建可用选项
        available_choices = [str(i) for i in range(1, len(display_items) + 1)]
        
        # 添加快捷键
        shortcut_choices = ['c', 'h', 'u', 's', 'l', 'q', 'm', 'p']
        
        # 根据当前菜单类型添加返回/退出选项
        from core.menu_system import MenuType
        if self.menu_system.current_menu.menu_type != MenuType.MAIN:
            shortcut_choices.append('0')  # 0表示返回上级
        
        # 添加0到可用选择
        if '0' in shortcut_choices:
            available_choices.append('0')
        
        choice = Prompt.ask(
            f"\n[bold cyan]请选择[/bold cyan]",
            choices=available_choices + shortcut_choices,
            show_choices=False
        ).lower()
        
        return choice
    
    def _process_choice(self, choice: str):
        """处理用户选择"""
        # 处理快捷键
        if choice == 'q':
            self.handle_exit()
            return
        
        elif choice == 'b':
            # 按b键直接返回主菜单
            self.view_manager.clear_screen()
            self.menu_system.navigate_to_menu("main_menu")
            return
        
        elif choice == 'h':
            self.show_help()
            return
        
        elif choice == 'c':
            self.view_manager.clear_screen()
            return
        
        elif choice == 'u':
            # 检查更新
            self.view_manager.clear_screen()
            self.update_app()
            return
        
        elif choice == 's':
            self.search_feature.show_search_interface()
            return
        
        elif choice == 'l':
            self.show_log_interface()
            return
        
        elif choice == 'm':
            # F1：配置管理
            self.show_config_interface()
            return
        
        elif choice == 'p':
            # F2：插件管理
            self.show_plugin_interface()
            return
        
        elif choice == '0':
            # 统一处理返回逻辑
            from core.menu_system import MenuType
            if self.menu_system.current_menu.menu_type != MenuType.MAIN:
                # 返回上级菜单前清屏
                self.view_manager.clear_screen()
                if self.menu_system.go_back():
                    return
                else:
                    # 如果已经在主菜单，则退出
                    self.handle_exit()
            else:
                # 在主菜单时，0表示退出
                self.handle_exit()
            return
        
        # 处理数字选择
        try:
            idx = int(choice) - 1
            display_items = self.menu_system.current_menu.get_display_items(self.menu_system)
            
            if 0 <= idx < len(display_items):
                selected_item = display_items[idx]
                self._handle_selected_item(selected_item)
            else:
                self.console.print(f"[red]❌ 无效的选择[/red]")
                input(f"\n按回车键继续...")
        except ValueError:
            self.console.print(f"[red]❌ 无效的输入[/red]")
            input(f"\n按回车键继续...")
    
    def _handle_selected_item(self, item):
        """处理选中的项目"""
        from core.menu_system import MenuNode, ActionItem
        
        if isinstance(item, MenuNode):
            # 切换菜单前清屏
            self.view_manager.clear_screen()
            # 导航到菜单
            self.menu_system.navigate_to_menu(item.id)
            
        elif isinstance(item, ActionItem):
            # 特殊命令处理
            if item.id == "clear_screen":
                self.view_manager.clear_screen()
                return
            
            if item.id == "show_help":
                self.show_help()
                return
            
            if item.id == "exit_app":
                self.handle_exit()
                return
            
            # 添加到最近使用
            self.config_manager.add_recently_used(item.id)
            
            # 清屏准备执行
            self.view_manager.clear_screen()
            
            # 显示执行信息
            self.console.print("\n" + "=" * 70, style="yellow")
            execute_msg = "正在执行: " + item.name
            self.console.print(execute_msg.center(70), style="yellow bold")
            self.console.print("=" * 70 + "\n", style="yellow")
            
            self.console.print(f"📝 描述: {item.description}")
            
            from core.menu_system import CommandType
            if item.command_type == CommandType.SHELL and item.command:
                self.console.print(f"💻 命令: {item.command}")
            
            self.console.print(f"\n⏳ 正在执行...\n")
            
            # 执行命令
            self.command_count += 1
            output = self.menu_system.execute_action(item)
            
            # 显示结果
            self.console.print("\n" + "=" * 70, style="green")
            complete_msg = "执行完成: " + item.name
            self.console.print(complete_msg.center(70), style="green bold")
            self.console.print("=" * 70 + "\n", style="green")
            self.console.print(output)
            
            self.console.print("\n" + "─" * 70, style="dim")
            self.console.print(f"[yellow]按回车键继续...[/yellow]")
            input()
            # 清屏准备返回菜单
            self.view_manager.clear_screen()
    
    def _display_interface(self):
        """显示完整界面"""
        # 清屏
        if self.config_manager.get_config("auto_clear_screen", True):
            self.view_manager.clear_screen()
        
        # 获取当前菜单的路由ID
        current_menu_id = self.menu_system.current_menu.id if self.menu_system.current_menu else "main_menu"
        
        # 获取当前路由
        current_route = self.view_manager.get_route_by_id(current_menu_id)
        
        # 使用ViewManager统一渲染布局
        if current_route:
            # 更新当前视图ID
            self.view_manager.current_view_id = current_route.id
            # 更新命令计数
            self.view_manager.set_command_count(self.command_count)
            # 渲染布局 - 已经包含了更新提示（在banner下方）
            self.view_manager._render_layout(current_route, version=self.current_version, update_manager=self.update_manager)
        else:
            # 降级处理：如果没有路由，使用原有的渲染方式
            # 显示横幅
            if self.config_manager.get_config("show_banner", True):
                banner_style = self.config_manager.get_config("banner_style", "default")
                self.view_manager._render_banner(version=self.current_version, banner_style=banner_style)
            
            # 渲染更新提示
            self.view_manager._render_update_prompt(self.update_manager)
            
            # 显示当前菜单
            self._render_menu()
            
            # 显示提示
            if self.config_manager.get_config("show_hints", True):
                self._show_hints()
    
    def start_main_loop(self):
        """启动应用主循环"""
        try:
            # 进入主循环前先清屏，确保欢迎界面内容被完全清理
            self.view_manager.clear_screen()
            
            while True:
                # 显示界面
                self._display_interface()
                
                # 获取用户选择
                choice = self._get_user_choice()
                
                # 处理选择
                self._process_choice(choice)
        except KeyboardInterrupt:
            self.handle_exit()
    
    def cleanup(self):
        """清理资源"""
        # 保存配置
        self.config_manager.save_config()
        
        # 清理插件
        self.plugin_manager.cleanup_all()
        
        # 记录退出日志
        self.logger.info("应用程序正常退出")
        
        # 显示运行统计
        import time
        uptime = time.time() - self.start_time
        self.console.print(f"\n[yellow]运行时间: {int(uptime)} 秒, 执行命令: {self.command_count} 个[/yellow]")
        self.console.print(f"[yellow]配置已保存[/yellow]")
