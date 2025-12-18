#!/usr/bin/env python3
"""
FastX TUI - 基于pyi18n的国际化版本
"""
import os
import sys
import time
import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from typing import List, Optional, Dict, Any

# 导入按键获取模块（跨平台）
if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.panel import Panel
from rich import box

from core.logger import get_logger

from core.menu_system import (
    MenuSystem, MenuNode, ActionItem, MenuType, CommandType
)
from core.operations import SystemOperations, FileOperations, PythonOperations
from core.plugin_manager import PluginManager
from core.logger import (
    get_current_log_level, set_log_level, get_available_log_levels
)
from core.network_tools import NetworkToolsPlugin
from features.search import SearchFeature
from config.config_manager import ConfigManager, UserPreferences
from locales.pyi18n_manager import PyI18nLocaleManager, LanguageInfo


class FastXPyI18nTUI:
    """基于pyi18n的FastX TUI"""

    def __init__(self):
        # 初始化控制台
        self.console = Console()

        # 初始化日志
        self.logger = get_logger(self.__class__.__name__)

        # 初始化配置管理器
        self.config_manager = ConfigManager()

        # 初始化国际化管理器（使用pyi18n）
        self.locale_manager = PyI18nLocaleManager(
            locale_dir="locales",
            default_locale=self.config_manager.get_config("language", "zh_CN")
        )

        # 注册语言变更回调
        self.locale_manager.register_change_callback(self._on_language_changed)

        # 应用配置的语言
        configured_lang = self.config_manager.get_config("language", "zh_CN")
        self.locale_manager.set_locale(configured_lang, notify=False)

        # 初始化菜单系统（传入国际化管理器）
        self.menu_system = MenuSystem(self.console)
        # 设置本地化管理器
        self.menu_system.set_locale_manager(self.locale_manager)

        # 初始化插件管理器
        self.plugin_manager = PluginManager(
            self.config_manager.get_config("plugin_directory", "plugins")
        )

        # 初始化网络工具插件（用于版本检查）
        self.network_tools = NetworkToolsPlugin()
        self.network_tools.initialize()

        # 初始化搜索功能
        self.search_feature = SearchFeature(self.menu_system, self.console, self.config_manager)

        # 初始化操作类
        self.operations = {
            'system': SystemOperations(),
            'file': FileOperations(),
            'python': PythonOperations()
        }

        # 性能监控
        self.start_time = time.time()
        self.command_count = 0

        # 版本检查相关
        self.current_version = self.t("app.version")
        self.latest_version = None
        self.update_available = False
        self.version_check_failed = False

        # 初始化系统
        self._init_system()
        
        # 根据配置检查版本更新
        if self.config_manager.get_config("auto_check_updates", True):
            self._check_version_update()

    def t(self, key: str, default: str = None, **kwargs) -> str:
        """翻译文本的便捷方法"""
        return self.locale_manager.t(key, default, **kwargs)

    def _on_language_changed(self, old_locale: str, new_locale: str):
        """语言变更回调"""
        self.console.print(f"\n🌐 {self.t('language.changed', old=old_locale, new=new_locale)}")
        self.console.print(f"🔄 {self.t('language.reinitializing')}")

        # 保存当前状态
        current_menu_id = self.menu_system.current_menu.id if self.menu_system.current_menu else "main_menu"

        # 重新初始化菜单
        self._reinitialize_menus()

        # 清除菜单历史记录，避免路径叠加
        self.menu_system.menu_history.clear()

        # 恢复之前的菜单状态
        # 只有当需要恢复的菜单不是主菜单时才导航，避免重复添加主菜单到历史记录
        if current_menu_id != "main_menu":
            self.menu_system.navigate_to_menu(current_menu_id)

    def _check_version_update(self):
        """检查GitHub上的版本更新"""
        self.version_check_failed = False
        try:
            # 调试信息
            self.logger.debug(f"当前版本: {self.current_version}")
            self.logger.debug(f"自动检查更新设置: {self.config_manager.get_config('auto_check_updates', True)}")
            
            # 使用网络工具插件检查版本更新
            result = self.network_tools.check_github_version(
                current_version=self.current_version.lstrip('v'),
                repo="fastxteam/FastX-Tui"
            )
            
            self.logger.debug(f"版本检查结果: {result}")
            
            if result['success']:
                self.latest_version = result['latest_version']
                self.update_available = result['update_available']
            else:
                self.version_check_failed = True
                self.logger.debug(f"版本检查失败: {result.get('error', '未知错误')}")
        except Exception:
            # Set flag on any error
            self.version_check_failed = True
    
    def _show_update_prompt(self):
        """显示版本更新提示"""
        if self.update_available and self.latest_version:
            current_version = self.current_version.lstrip('v')
            latest_version = self.latest_version
            
            # 创建格式化的更新消息
            update_message = Text.from_markup(
                f"[#F9E2AF]FastX-Tui update available! {current_version} -> {latest_version}[/#F9E2AF]\n"
                f"[#F9E2AF]Check the latest release at: https://github.com/fastxteam/FastX-Tui/releases/latest[/#F9E2AF]"
            )
            
            # 使用Panel显示更新消息
            self.console.print(
                Panel(
                    update_message,
                    border_style="#F9E2AF",
                    expand=True,
                    width=120
                )
            )

    def _reinitialize_menus(self):
        """重新初始化菜单（使用新语言）"""
        # 清除现有菜单项
        self.menu_system.items.clear()

        # 重新初始化菜单结构（包括基础菜单创建）
        self._init_menu()

        # 重新初始化固定项
        self.menu_system._init_fixed_items()

        # 重新注册插件命令
        self.plugin_manager.register_all_plugins(self.menu_system)

        # 重新填充插件菜单
        self._rebuild_plugin_menu()

        # 重新应用用户偏好
        self._apply_user_preferences()

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

        # 显示欢迎信息（根据配置决定）
        if self.config_manager.get_config("show_welcome_page", True):
            self._show_welcome_message()
            # 等待用户确认后再进入主菜单
            input(f"\n{self.t('app.confirm')}...")
            # 清除屏幕，进入主菜单
            self.menu_system.clear_screen()

    def _init_menu(self):
        """初始化菜单结构"""
        # 创建主菜单
        main_menu = MenuNode(
            id="main_menu",
            name=self.t("menu.main"),
            description=self.t("app.description"),
            menu_type=MenuType.MAIN,
            icon="🏠"
        )

        # 系统工具菜单
        system_menu = MenuNode(
            id="system_tools_menu",
            name=self.t("menu.system"),
            description=self.t("system.info_desc"),
            menu_type=MenuType.SUB,
            icon="🖥️"
        )

        # 文件工具菜单
        file_menu = MenuNode(
            id="file_tools_menu",
            name=self.t("menu.file"),
            description=self.t("file.list_desc"),
            menu_type=MenuType.SUB,
            icon="📁"
        )

        # Python工具菜单
        python_menu = MenuNode(
            id="python_tools_menu",
            name=self.t("menu.python"),
            description=self.t("python.info_desc"),
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
            name=self.t("system.info"),
            description=self.t("system.info_desc"),
            icon="📊",
            command_type=CommandType.PYTHON,
            python_func=self.operations['system'].get_system_info
        ))

        system_menu.add_item(ActionItem(
            id="network_info",
            name=self.t("system.network"),
            description=self.t("system.network_desc"),
            icon="🌐",
            command_type=CommandType.PYTHON,
            python_func=self.operations['system'].get_network_info
        ))

        system_menu.add_item(ActionItem(
            id="process_list",
            name=self.t("system.process"),
            description=self.t("system.process_desc"),
            icon="📋",
            command_type=CommandType.PYTHON,
            python_func=self.operations['system'].list_processes
        ))

        system_menu.add_item(ActionItem(
            id="disk_space",
            name=self.t("system.disk"),
            description=self.t("system.disk_desc"),
            icon="💾",
            command_type=CommandType.PYTHON,
            python_func=self.operations['system'].get_disk_space
        ))

        system_menu.add_item(ActionItem(
            id="system_uptime",
            name=self.t("system.uptime"),
            description=self.t("system.uptime_desc"),
            icon="⏰",
            command_type=CommandType.PYTHON,
            python_func=self.operations['system'].get_system_uptime
        ))

        # 文件工具
        file_menu.add_item(ActionItem(
            id="list_directory",
            name=self.t("file.list"),
            description=self.t("file.list_desc"),
            icon="📄",
            command_type=CommandType.PYTHON,
            python_func=self.operations['file'].list_directory
        ))

        file_menu.add_item(ActionItem(
            id="file_tree",
            name=self.t("file.tree"),
            description=self.t("file.tree_desc"),
            icon="🌳",
            command_type=CommandType.PYTHON,
            python_func=self.operations['file'].show_file_tree
        ))

        file_menu.add_item(ActionItem(
            id="search_files",
            name=self.t("file.search"),
            description=self.t("file.search_desc"),
            icon="🔍",
            command_type=CommandType.PYTHON,
            python_func=self.operations['file'].search_files
        ))

        # Python工具
        python_menu.add_item(ActionItem(
            id="python_info",
            name=self.t("python.info"),
            description=self.t("python.info_desc"),
            icon="🐍",
            command_type=CommandType.PYTHON,
            python_func=self.operations['python'].get_python_info
        ))

        python_menu.add_item(ActionItem(
            id="python_packages",
            name=self.t("python.packages"),
            description=self.t("python.packages_desc"),
            icon="📦",
            command_type=CommandType.PYTHON,
            python_func=self.operations['python'].list_packages
        ))

        python_menu.add_item(ActionItem(
            id="check_imports",
            name=self.t("python.imports"),
            description=self.t("python.imports_desc"),
            icon="🔍",
            command_type=CommandType.PYTHON,
            python_func=self.operations['python'].check_imports
        ))

        # 将子菜单添加到主菜单
        main_menu.add_item("system_tools_menu")
        main_menu.add_item("file_tools_menu")
        main_menu.add_item("python_tools_menu")

        # 添加配置功能
        main_menu.add_item(ActionItem(
            id="show_config",
            name=self.t("menu.config"),
            description=self.t("config.view_desc"),
            icon="⚙️",
            command_type=CommandType.PYTHON,
            python_func=self.show_config_interface
        ))

        # 添加插件管理
        main_menu.add_item(ActionItem(
            id="plugin_manager",
            name=self.t("menu.plugin"),
            description=self.t("plugin.list_desc"),
            icon="🔌",
            command_type=CommandType.PYTHON,
            python_func=self.show_plugin_interface
        ))

        # 创建插件主菜单（但不添加内容，内容将在插件注册后由_rebuild_plugin_menu处理）
        plugins_menu = MenuNode(
            id="plugins_menu",
            name=self.t("plugin.menu"),
            description=self.t("plugin.menu_desc"),
            menu_type=MenuType.SUB,
            icon="🔌"
        )
        self.menu_system.register_item(plugins_menu)

        # 设置当前菜单
        self.menu_system.current_menu = main_menu

    def _rebuild_plugin_menu(self):
        """重建插件菜单"""
        # 获取插件菜单
        plugins_menu = self.menu_system.get_item_by_id("plugins_menu")
        if not isinstance(plugins_menu, MenuNode):
            # 如果插件菜单不存在，创建它
            plugins_menu = MenuNode(
                id="plugins_menu",
                name=self.t("plugin.menu"),
                description=self.t("plugin.menu_desc"),
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

        # 添加所有已注册的插件命令到插件主菜单
        plugin_items_added = False
        for item_id, item in self.menu_system.items.items():
            # 跳过已经添加过的项目、固定项和插件自己创建的子菜单
            if item_id not in ["main_menu", "system_tools_menu", "file_tools_menu", "python_tools_menu", "show_config", "plugin_manager", "clear_screen", "show_help", "exit_app", "plugins_menu"]:
                # 只添加真正的插件命令（MenuItem或ActionItem），不添加MenuNode类型的子菜单
                if not isinstance(item, MenuNode):
                    plugins_menu.add_item(item_id)
                    plugin_items_added = True

        # 如果有插件命令，将插件菜单重新添加到主菜单
        if plugin_items_added:
            main_menu.add_item("plugins_menu")

    def _apply_user_preferences(self):
        """应用用户偏好"""
        # 设置默认菜单
        default_menu = self.config_manager.get_preference("preferred_menu", "main_menu")
        menu_item = self.menu_system.get_item_by_id(default_menu)
        if isinstance(menu_item, MenuNode):
            self.menu_system.current_menu = menu_item

    def _show_welcome_message(self):
        """显示欢迎信息"""
        self.menu_system.clear_screen()

        # 显示横幅
        banner_style = self.config_manager.get_config("banner_style", "default")
        self.menu_system.show_banner(version=self.current_version, banner_style=banner_style)

        # 显示版本信息
        self.console.print("\n" + "=" * 70, style="cyan")
        welcome_msg = self.t("app.welcome", "欢迎使用 {app_name} {version}")
        welcome_msg = welcome_msg.format(
            app_name=self.t("app.name"),
            version=self.t("app.version")
        )
        self.console.print(welcome_msg.center(70), style="cyan bold")
        self.console.print("=" * 70 + "\n", style="cyan")

        # 显示系统信息
        import platform
        self.console.print(f"💻 {self.t('system.info')}: {platform.system()} {platform.version()}")
        self.console.print(f"🐍 Python: {platform.python_version()}")
        self.console.print(f"🌐 {self.t('config.language_display')}: {self.locale_manager.get_locale()}")
        self.console.print(f"🔌 {self.t('plugin.list')}: {len(self.plugin_manager.plugins)}")

        # 显示提示
        self.console.print(f"\n💡 {self.t('help.title')}:")
        self.console.print(f"  • {self.t('hint.help')} - {self.t('app.help')}")
        self.console.print(f"  • {self.t('hint.search')} - {self.t('app.search')}")
        self.console.print(f"  • {self.t('hint.exit')} - {self.t('app.exit')}")

        self.console.print("\n" + "─" * 70, style="dim")

    def show_language_interface(self):
        """显示语言切换界面"""
        self.menu_system.clear_screen()

        while True:
            self.console.print("\n" + "=" * 70, style="cyan")
            title = self.t("config.language") + " - " + self.t("config.title")
            self.console.print(title.center(70), style="cyan bold")
            self.console.print("=" * 70 + "\n", style="cyan")

            # 显示当前语言
            current = self.locale_manager.get_locale()
            lang_info = self.locale_manager.language_info.get(current)
            current_name = lang_info.native_name if lang_info else current

            self.console.print(f"🌐 {self.t('config.current')}: {current_name} ({current})")
            self.console.print()

            # 显示可用语言
            available_langs = self.locale_manager.get_available_locales()

            self.console.print(f"📚 {self.t('config.languages')}:")
            for i, lang_info in enumerate(available_langs, 1):
                current_mark = " ← " if lang_info.code == current else "   "
                status = "✅" if lang_info.enabled else "⭕"
                self.console.print(f"  {i}.{current_mark} {status} {lang_info.native_name} ({lang_info.code})")

            self.console.print(f"\n  b. {self.t('app.back')}")
            self.console.print(f"  r. {self.t('plugin.reload')}")

            self.console.print("\n" + "─" * 70, style="dim")
            choice = Prompt.ask(f"[bold cyan]{self.t('app.confirm')}[/bold cyan]")

            if choice.lower() == 'b':
                # 返回主菜单
                self.menu_system.clear_screen()
                break

            elif choice.lower() == 'r':
                self.locale_manager.reload()
                self.console.print(f"\n✅ {self.t('plugin.reloaded')}")
                input(f"\n{self.t('app.back')}...")
                continue

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_langs):
                    lang_info = available_langs[idx]

                    # 切换到新语言
                    if self.locale_manager.set_locale(lang_info.code):
                        # 更新配置
                        self.config_manager.set_config("language", lang_info.code)

                        self.console.print(f"\n✅ {self.t('success.config_saved')}")
                        input(f"\n{self.t('app.back')}...")

                        # 语言切换后需要重新显示界面
                        return
                    else:
                        self.console.print(f"[red]❌ {self.t('error.config_load')}[/red]")
                        input(f"\n{self.t('app.back')}...")
                else:
                    self.console.print(f"[red]❌ {self.t('error.invalid_choice')}[/red]")
                    input(f"\n{self.t('app.back')}...")
            except ValueError:
                self.console.print(f"[red]❌ {self.t('error.invalid_input')}[/red]")
                input(f"\n{self.t('app.back')}...")

    def show_config_interface(self):
        """显示配置界面"""
        self.menu_system.clear_screen()

        while True:
            self.console.print("\n" + "=" * 70, style="cyan")
            self.console.print(f"{self.t('config.title')}".center(70), style="cyan bold")
            self.console.print("=" * 70 + "\n", style="cyan")

            # 显示配置选项
            options = [
                ("1", self.t("config.view"), self._show_current_config),
                ("2", self.t("config.theme"), self._change_theme),
                ("3", self.t("config.language"), self.show_language_interface),
                ("4", self.t("config.advanced"), self._show_advanced_settings),
                ("5", self.t("config.reset"), self._reset_config),
                ("6", self.t("config.export"), self._export_config),
                ("7", self.t("config.import"), self._import_config),
                ("b", self.t("app.back_main"), None),
                ("q", self.t("app.exit"), None)
            ]

            for key, description, _ in options:
                self.console.print(f"  {key}. {description}")

            self.console.print("\n" + "─" * 70, style="dim")
            choice = Prompt.ask(f"[bold cyan]{self.t('app.confirm')}[/bold cyan]")

            if choice == 'b':
                # 返回主菜单
                self.menu_system.go_to_root()
                break
            elif choice == 'q':
                self.handle_exit()
                return

            # 执行选择的操作
            for key, description, action in options:
                if choice == key and action:
                    action()
                    break
            else:
                self.console.print(f"[red]❌ {self.t('error.invalid_choice')}[/red]")
                input(f"\n{self.t('app.back')}...")

    def _show_current_config(self):
        """显示当前配置"""
        config_summary = self.config_manager.show_config_summary()
        self.console.print(f"\n{config_summary}")

        # 显示语言信息
        self.console.print(f"\n🌐 {self.t('config.language')}:")
        current = self.locale_manager.get_locale()
        lang_info = self.locale_manager.language_info.get(current)
        if lang_info:
            self.console.print(f"  • {self.t('config.current')}: {lang_info.native_name} ({current})")

        available = self.locale_manager.get_available_locales()
        self.console.print(f"  • {self.t('config.languages')}: {len(available)}")

        input(f"\n{self.t('app.back')}...")

    def _change_theme(self):
        """修改主题"""
        themes = ["default", "dark", "light", "blue", "green"]
        
        self.console.print(f"\n🎨 {self.t('theme.available')}")
        for i, theme in enumerate(themes, 1):
            self.console.print(f"  {i}. {theme}")
        
        choice = Prompt.ask(f"\n[bold cyan]{self.t('theme.select_prompt', count=len(themes))}[/bold cyan]")
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(themes):
                self.config_manager.set_config("theme", themes[idx])
                self.console.print(f"\n✅ {self.t('success.theme_switched', theme=themes[idx])}")
            else:
                self.console.print(f"[red]❌ {self.t('error.invalid_choice')}: {choice}[/red]")
        except ValueError:
            self.console.print(f"[red]❌ {self.t('error.invalid_input')}: {choice}[/red]")
        
        input(f"\n{self.t('app.continue')}")
    
    def _change_language(self):
        """修改语言"""
        languages = [
            ("zh_CN", "简体中文"),
            ("en_US", "English"),
            ("ja_JP", "日本語")
        ]
        
        self.console.print(f"\n🌐 可用语言:")
        for i, (code, name) in enumerate(languages, 1):
            self.console.print(f"  {i}. {name} ({code})")
        
        choice = Prompt.ask("\n[bold cyan]请选择语言 (1-3)[/bold cyan]")
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(languages):
                self.config_manager.set_config("language", languages[idx][0])
                self.console.print(f"\n✅ 语言已切换为: {languages[idx][1]}")
            else:
                self.console.print(f"[red]{self.t('error.invalid_choice', choice=choice)}[/red]")
        except ValueError:
            self.console.print(f"[red]{self.t('error.invalid_input', choice=choice)}[/red]")
        
        input(f"\n{self.t('app.continue')}")
    
    def _show_advanced_settings(self):
        """显示高级设置界面"""
        self.menu_system.clear_screen()
        
        while True:
            self.console.print("\n" + "=" * 70, style="cyan")
            self.console.print(f"⚙️  {self.t('config.advanced')}".center(70), style="cyan bold")
            self.console.print("=" * 70 + "\n", style="cyan")
            
            # 获取当前设置
            show_welcome = self.config_manager.get_config("show_welcome_page", True)
            auto_check_updates = self.config_manager.get_config("auto_check_updates", True)
            banner_style = self.config_manager.get_config("banner_style", "default")
            
            # 显示高级设置选项
            self.console.print(f"📋 {self.t('config.advanced_settings')}:")
            self.console.print(f"1. {self.t('config.show_welcome')}: {'✅' if show_welcome else '❌'}")
            self.console.print(f"2. {self.t('config.auto_check_updates')}: {'✅' if auto_check_updates else '❌'}")
            self.console.print(f"3. {self.t('config.banner_style')}: {banner_style}")
            self.console.print()
            self.console.print(f"b. {self.t('app.back')}")
            self.console.print(f"q. {self.t('app.exit')}")
            
            self.console.print("\n" + "─" * 70, style="dim")
            choice = Prompt.ask(f"[bold cyan]{self.t('app.confirm')}[/bold cyan]")
            
            if choice == 'b':
                break
            elif choice == 'q':
                self.handle_exit()
                return
            elif choice == '1':
                # 切换显示欢迎页面设置
                new_value = not show_welcome
                self.config_manager.set_config("show_welcome_page", new_value)
                status = self.t('config.enabled') if new_value else self.t('config.disabled')
                self.console.print(f"\n✅ {self.t('config.show_welcome')} {status}")
                input(f"\n{self.t('app.continue')}")
            elif choice == '2':
                # 切换自动检查更新设置
                new_value = not auto_check_updates
                self.config_manager.set_config("auto_check_updates", new_value)
                status = self.t('config.enabled') if new_value else self.t('config.disabled')
                self.console.print(f"\n✅ {self.t('config.auto_check_updates')} {status}")
                input(f"\n{self.t('app.continue')}")
            elif choice == '3':
                # 切换横幅样式
                new_style = "gradient" if banner_style == "default" else "default"
                self.config_manager.set_config("banner_style", new_style)
                self.console.print(f"\n✅ {self.t('config.banner_style')} {self.t('config.set_to')} {new_style}")
                input(f"\n{self.t('app.continue')}")
            else:
                self.console.print(f"[red]❌ {self.t('error.invalid_choice')}[/red]")
                input(f"\n{self.t('app.continue')}")
    
    def _reset_config(self):
        """重置配置"""
        confirm = Prompt.ask(
            f"[bold red]{self.t('config.reset_confirm')}[/bold red]",
            choices=["y", "n", "Y", "N"],
            default="n"
        )
        
        if confirm.lower() == 'y':
            self.config_manager.reset_to_defaults()
            self.console.print(f"\n✅ {self.t('success.config_reset')}")
        else:
            self.console.print(f"\n❌ {self.t('config.reset_canceled')}")
        
        input(f"\n{self.t('app.continue')}")
    
    def _export_config(self):
        """导出配置"""
        filename = Prompt.ask(
            f"[bold cyan]{self.t('config.export_prompt')}[/bold cyan]",
            default="fastx_config.json"
        )
        
        if self.config_manager.export_config(filename):
            self.console.print(f"\n✅ {self.t('success.config_exported', filename=filename)}")
        else:
            self.console.print(f"\n❌ {self.t('config.export_failed')}")
        
        input(f"\n{self.t('app.continue')}")
    
    def _import_config(self):
        """导入配置"""
        filename = Prompt.ask(
            f"[bold cyan]{self.t('config.import_prompt')}[/bold cyan]",
            default="fastx_config.json"
        )
        
        if os.path.exists(filename):
            if self.config_manager.import_config(filename):
                self.console.print(f"\n✅ {self.t('success.imported')}")
            else:
                self.console.print(f"\n❌ {self.t('config.import_failed')}")
        else:
            self.console.print(f"\n❌ {self.t('error.file_not_found')}: {filename}")
        
        input(f"\n{self.t('app.continue')}")
    
    def show_plugin_interface(self):
        """显示插件管理界面"""
        self.menu_system.clear_screen()
        
        while True:
            self.console.print("\n" + "=" * 70, style="cyan")
            self.console.print(f"🔌 {self.t('plugin.title')}".center(70), style="cyan bold")
            self.console.print("=" * 70 + "\n", style="cyan")
            
            # 显示插件列表
            plugins = self.plugin_manager.list_plugins()
            
            if plugins:
                self.console.print(f"📦 {self.t('plugin.loaded_plugins')} ({len(plugins)}):\n")
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
                self.console.print(f"[yellow]{self.t('plugin.no_plugins')}[/yellow]\n")
            
            # 显示操作选项
            self.console.print(f"🛠️  {self.t('plugin.operations')}:")
            self.console.print(f"  1. {self.t('plugin.reload_all')}")
            self.console.print(f"  2. {self.t('plugin.refresh_list')}")
            self.console.print(f"  3. {self.t('plugin.view_directory')}")
            self.console.print(f"  b. {self.t('plugin.back_menu')}")
            self.console.print(f"  q. {self.t('app.exit')}")
            
            self.console.print("\n" + "─" * 70, style="dim")
            choice = Prompt.ask(f"[bold cyan]{self.t('app.confirm')}[/bold cyan]")
            
            if choice == '1':
                self._reload_plugins()
            elif choice == '2':
                self._refresh_plugins()
            elif choice == '3':
                self._show_plugin_directory()
            elif choice == 'b':
                # 返回主菜单
                self.menu_system.go_to_root()
                break
            elif choice == 'q':
                self.console.print(f"\n[green]{self.t('app.exit_thanks')}[/green]\n")
                sys.exit(0)
            else:
                self.console.print(f"[red]{self.t('error.invalid_choice')}: {choice}[/red]")
                input(f"\n{self.t('app.continue')}")
    
    def _reload_plugins(self):
        """重新加载插件"""
        self.console.print(f"\n🔄 {self.t('plugin.loading')}")
        
        # 清理现有插件
        self.plugin_manager.cleanup_all()
        
        # 重新加载
        self.plugin_manager.load_all_plugins()
        self.plugin_manager.register_all_plugins(self.menu_system)
        
        self.console.print(f"✅ {self.t('plugin.reload_success', count=len(self.plugin_manager.plugins))}")
        input(f"\n{self.t('app.continue')}")
    
    def _refresh_plugins(self):
        """刷新插件列表"""
        self.console.print(f"\n🔄 {self.t('plugin.loading')}")
        
        discovered = self.plugin_manager.discover_plugins()
        loaded = list(self.plugin_manager.plugins.keys())
        
        self.console.print(f"📁 {self.t('plugin.refresh_info.discovered')}: {len(discovered)}")
        self.console.print(f"🔌 {self.t('plugin.refresh_info.loaded')}: {len(loaded)}")
        
        if discovered:
            self.console.print(f"\n📋 {self.t('plugin.refresh_info.discovered')}:")
            for plugin in discovered:
                status = "✅" if plugin in loaded else "❌"
                self.console.print(f"  {status} {plugin}")
        
        input(f"\n{self.t('app.continue')}")
    
    def _show_plugin_directory(self):
        """显示插件目录"""
        plugin_dir = self.config_manager.get_config("plugin_directory", "plugins")
        
        self.console.print(f"\n📁 {self.t('plugin.directory')}: {os.path.abspath(plugin_dir)}")
        
        if os.path.exists(plugin_dir):
            files = os.listdir(plugin_dir)
            if files:
                self.console.print(f"\n📋 {self.t('plugin.directory')}:")
                for file in files:
                    if file.endswith('.py') and file != '__init__.py':
                        self.console.print(f"  📄 {file}")
                    else:
                        self.console.print(f"  📁 {file}")
            else:
                self.console.print(f"[yellow]{self.t('plugin.directory_empty')}[/yellow]")
        else:
            self.console.print(f"[yellow]{self.t('plugin.directory_not_exists')}[/yellow]")
        
        input("\n按任意键继续...")

    def display_interface(self):
        """显示完整界面"""
        # 清屏
        if self.config_manager.get_config("auto_clear_screen", True):
            self.menu_system.clear_screen()

        # 显示横幅
        if self.config_manager.get_config("show_banner", True):
            banner_style = self.config_manager.get_config("banner_style", "default")
            self.menu_system.show_banner(version=self.current_version, banner_style=banner_style)
        
        # 显示版本更新提示（如果有更新）
        self._show_update_prompt()

        # 显示当前菜单
        self.menu_system.show_current_menu()

        # 显示提示
        if self.config_manager.get_config("show_hints", True):
            self.show_hints()

    def show_hints(self):
        """显示快捷键提示"""
        # 快捷键提示
        shortcuts = []
        
        # 导航提示
        if self.menu_system.current_menu.menu_type != MenuType.MAIN:
            shortcuts.append(f"0:{self.t('hint.back')}")
        else:
            shortcuts.append(f"q:{self.t('hint.exit')}")

        # 功能提示
        shortcuts.extend([
            f"c:{self.t('hint.clear')}",
            f"h:{self.t('hint.help')}",
            f"s:{self.t('hint.search')}",
            f"l:{self.t('config.language_display')}",  # 语言切换快捷键
            f"k:{self.t('logger.title', '日志')}"  # 日志管理快捷键
        ])

        # 使用分隔线分割
        self.console.print("─" * 120, style="dim")

        # 显示快捷键行
        shortcuts_text = f"[dim]{self.t('hint.shortcuts')}: " + " | ".join(shortcuts) + "[/dim]"
        self.console.print(shortcuts_text)

        # 使用分隔线分割
        self.console.print("─" * 120, style="dim")

        # 状态栏信息
        status_bar = []
        
        # 显示运行统计
        uptime = time.time() - self.start_time
        status_bar.append(f"⏱️: {int(uptime)} {self.t('format.time_seconds', '秒')}")
        
        # 命令计数
        status_bar.append(f"📊: {self.command_count}")
        
        # 添加日志级别
        current_log_level = get_current_log_level()
        status_bar.append(f"📋: {current_log_level}")
        
        # 添加版本更新信息
        if self.version_check_failed:
            # 版本检查失败 - 红色圆点
            status_bar.append(f"📦: {self.current_version} [red]⚡[/red]")
        elif self.update_available and self.latest_version:
            # 有更新 - 黄色圆点并显示新版本号
            status_bar.append(f"📦: {self.current_version} → {self.latest_version} [yellow]⚡[/yellow]")
        else:
            # 最新版本 - 绿色圆点
            status_bar.append(f"📦: {self.current_version} [green]⚡[/green]")

        # 构建当前位置路径
        path_parts = []
        # 只处理有效的MenuNode对象，避免NoneType错误
        for menu in self.menu_system.menu_history:
            if hasattr(menu, 'name'):
                path_parts.append(menu.name)
        if self.menu_system.current_menu and hasattr(self.menu_system.current_menu, 'name'):
            path_parts.append(self.menu_system.current_menu.name)
        current_path = " > ".join(path_parts) if path_parts else "主菜单"

        # 构建状态栏文本
        status_text = f"[dim] | ".join(status_bar) + "[/dim]"
        
        # 构建完整的状态栏（左侧：当前位置，右侧：状态信息）
        # 计算左侧和右侧的宽度，确保总宽度为120
        total_width = 160
        left_text = f"[dim] > {current_path}[/dim]"
        right_text = status_text
        
        # 计算中间空格数量
        middle_spaces = total_width - len(left_text) - len(right_text)
        if middle_spaces < 1:
            middle_spaces = 1
        
        # 构建完整的状态栏
        full_status = f"{left_text}{' ' * middle_spaces}{right_text}"
        
        # 打印固定宽度的状态栏
        self.console.print(full_status)
        self.console.print("─" * 120, style="dim")

    def get_user_choice(self) -> str:
        """获取用户选择"""
        display_items = self.menu_system.current_menu.get_display_items(self.menu_system)

        # 构建可用选项
        available_choices = [str(i) for i in range(1, len(display_items) + 1)]

        # 添加快捷键
        shortcut_choices = ['c', 'h', 's', 'l', 'k', 'q']  # l表示语言切换，k表示日志管理

        # 根据当前菜单类型添加返回/退出选项
        if self.menu_system.current_menu.menu_type != MenuType.MAIN:
            shortcut_choices.append('0')  # 0表示返回上级

        # 添加0到可用选择
        if '0' in shortcut_choices:
            available_choices.append('0')

        choice = Prompt.ask(
            f"\n[bold cyan]{self.t('app.confirm')}[/bold cyan]",
            choices=available_choices + shortcut_choices,
            show_choices=False
        ).lower()

        return choice

    def process_choice(self, choice: str):
        """处理用户选择"""
        # 处理快捷键
        if choice == 'q':
            self.handle_exit()
            return

        elif choice == 'h':
            self.show_help()
            return

        elif choice == 'c':
            self.menu_system.clear_screen()
            return

        elif choice == 's':
            self.search_feature.show_search_interface()
            return

        elif choice == 'l':  # 语言切换快捷键
            self.show_language_interface()
            return
        elif choice == 'k':  # 日志管理快捷键
            self.show_logger_interface()
            return

        elif choice == '0':
            # 统一处理返回逻辑
            if self.menu_system.current_menu.menu_type != MenuType.MAIN:
                # 返回上级菜单
                if self.menu_system.go_back():
                    return
                else:
                    # 如果已经在主菜单，则退出
                    self.handle_exit()
            else:
                # 在主菜单时，0表示退出
                self.handle_exit()
            return

        elif choice == 'b':
            # 返回主菜单
            self.menu_system.go_to_root()
            return

        # 处理数字选择
        try:
            idx = int(choice) - 1
            display_items = self.menu_system.current_menu.get_display_items(self.menu_system)

            if 0 <= idx < len(display_items):
                selected_item = display_items[idx]
                self.handle_selected_item(selected_item)
            elif choice == '0':
                # 数字0的处理已经在上面处理过
                pass
            else:
                self.console.print(f"[red]❌ {self.t('error.invalid_choice')}[/red]")
                input(f"\n{self.t('app.back')}...")
        except ValueError:
            self.console.print(f"[red]❌ {self.t('error.invalid_input')}[/red]")
            input(f"\n{self.t('app.back')}...")

    def handle_selected_item(self, item):
        """处理选中的项目"""
        from core.menu_system import MenuNode, ActionItem

        if isinstance(item, MenuNode):
            # 导航到菜单
            self.menu_system.navigate_to_menu(item.id)

        elif isinstance(item, ActionItem):
            # 特殊命令处理
            if item.id == "clear_screen":
                self.menu_system.clear_screen()
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
            self.menu_system.clear_screen()

            # 显示执行信息
            self.console.print("\n" + "=" * 70, style="yellow")
            execute_msg = self.t("app.executing") + ": " + item.name
            self.console.print(execute_msg.center(70), style="yellow bold")
            self.console.print("=" * 70 + "\n", style="yellow")

            self.console.print(f"📝 {self.t('app.description')}: {item.description}")

            if item.command_type == CommandType.SHELL and item.command:
                self.console.print(f"💻 {self.t('app.command')}: {item.command}")

            self.console.print(f"\n⏳ {self.t('app.loading')}\n")

            # 执行命令
            self.command_count += 1
            output = self.menu_system.execute_action(item)

            # 显示结果
            self.console.print("\n" + "=" * 70, style="green")
            complete_msg = self.t("app.completed") + ": " + item.name
            self.console.print(complete_msg.center(70), style="green bold")
            self.console.print("=" * 70 + "\n", style="green")
            self.console.print(output)

            self.console.print("\n" + "─" * 70, style="dim")
            self.console.print(f"[yellow]{self.t('app.back')}...[/yellow]")
            input()

            # 返回后重新显示界面
            self.menu_system.display_interface(clear=True)

    def show_logger_interface(self):
        """显示日志管理界面"""
        self.menu_system.clear_screen()

        while True:
            self.console.print("\n" + "=" * 70, style="cyan")
            title = self.t("logger.title", "日志管理") + " - " + self.t("config.title")
            self.console.print(title.center(70), style="cyan bold")
            self.console.print("=" * 70 + "\n", style="cyan")

            # 显示当前日志级别
            current_level = get_current_log_level()
            self.console.print(f"🔍 {self.t('logger.current_level')}: {current_level}")
            self.console.print()

            # 显示可用日志级别
            available_levels = get_available_log_levels()

            self.console.print(f"📚 {self.t('logger.available_levels')}:")
            for i, level in enumerate(available_levels, 1):
                current_mark = " ← " if level == current_level else "   "
                self.console.print(f"  {i}.{current_mark} {level}")

            self.console.print(f"\n  v. {self.t('logger.view_logs')} - {self.t('logger.view_logs_desc')}")
            self.console.print(f"\n  b. {self.t('app.back')}")

            self.console.print("\n" + "─" * 70, style="dim")
            choice = Prompt.ask(f"[bold cyan]{self.t('app.confirm')}[/bold cyan]")

            if choice.lower() == 'b':
                break
            elif choice.lower() == 'v':
                # 查看日志
                self.show_logs()
                continue

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_levels):
                    new_level = available_levels[idx]

                    # 切换到新日志级别
                    set_log_level(new_level)
                    self.console.print(f"\n✅ {self.t('logger.level_changed')}: {new_level}")
                    input(f"\n{self.t('app.back')}...")

                    # 返回后重新显示界面
                    return
                else:
                    self.console.print(f"[red]❌ {self.t('error.invalid_choice')}[/red]")
                    input(f"\n{self.t('app.back')}...")
            except ValueError:
                self.console.print(f"[red]❌ {self.t('error.invalid_input')}[/red]")
                input(f"\n{self.t('app.back')}...")

    def _get_char(self):
        """获取单个按键（跨平台）"""
        if sys.platform == 'win32':
            return msvcrt.getch().decode('utf-8')
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    def show_logs(self):
        """显示日志内容"""
        log_file = "logs/fastx.log"
        
        if not os.path.exists(log_file):
            self.console.print(f"[red]❌ {self.t('logger.log_file_not_found')}: {log_file}[/red]")
            input(f"\n{self.t('app.back')}...")
            return
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()
        except Exception as e:
            self.console.print(f"[red]❌ {self.t('logger.read_log_error')}: {str(e)}[/red]")
            input(f"\n{self.t('app.back')}...")
            return
        
        if not logs:
            self.console.print(f"[yellow]⚠️ {self.t('logger.no_logs_available')}[/yellow]")
            input(f"\n{self.t('app.back')}...")
            return
        
        # 显示日志界面
        page_size = 500
        current_page = 0
        total_pages = (len(logs) + page_size - 1) // page_size
        
        while True:
            self.menu_system.clear_screen()
            
            self.console.print("\n" + "=" * 70, style="cyan")
            title = self.t("logger.view_logs") + " - " + self.t("app.title")
            self.console.print(title.center(70), style="cyan bold")
            self.console.print("=" * 70 + "\n", style="cyan")
            
            # 显示当前页码
            self.console.print(f"📄 {self.t('logger.page')} {current_page + 1}/{total_pages}")
            self.console.print(f"📊 {self.t('logger.total_logs')}: {len(logs)}")
            self.console.print()
            
            # 显示日志内容
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(logs))
            
            for i in range(start_idx, end_idx):
                line = logs[i].strip()
                if line:
                    # 根据日志级别显示不同颜色
                    if "[DEBUG]" in line:
                        self.console.print(line, style="dim")
                    elif "[INFO]" in line:
                        self.console.print(line)
                    elif "[WARNING]" in line:
                        self.console.print(line, style="yellow")
                    elif "[ERROR]" in line:
                        self.console.print(line, style="red")
                    elif "[CRITICAL]" in line:
                        self.console.print(line, style="bold red")
                    else:
                        self.console.print(line)
            
            # 显示操作选项
            self.console.print("\n" + "─" * 70, style="dim")
            self.console.print(f"  [bold cyan]n[/bold cyan] - {self.t('logger.next_page')} | [bold cyan]p[/bold cyan] - {self.t('logger.prev_page')} | [bold cyan]b[/bold cyan] - {self.t('app.back')}")
            self.console.print(f"  [dim]{self.t('logger.press_key')}[/dim]")
            
            choice = self._get_char().lower()
            
            if choice == 'b':
                break
            elif choice == 'n' and current_page < total_pages - 1:
                current_page += 1
            elif choice == 'p' and current_page > 0:
                current_page -= 1
            # 支持方向键导航
            elif choice == '\x1b':  # ESC 序列开始
                second_char = self._get_char()
                if second_char == '[':
                    third_char = self._get_char()
                    if third_char == 'B' and current_page < total_pages - 1:  # 下箭头
                        current_page += 1
                    elif third_char == 'A' and current_page > 0:  # 上箭头
                        current_page -= 1

    def show_help(self):
        """显示帮助信息"""
        self.menu_system.clear_screen()

        help_text = f"""
        {self.t('help.title')}
        ============

        {self.t('help.basic')}
        --------
        {self.t('help.basic_desc')}

        {self.t('help.menu')}
        --------
        {self.t('help.menu_desc')}

        {self.t('help.icons')}
        --------
        {self.t('help.icons_desc')}

        {self.t('help.note')}
        --------
        {self.t('help.note_desc')}

        {self.t('hint.shortcuts')}
        ------------
        • 0 - {self.t('hint.back')}/{self.t('hint.exit')}
        • c - {self.t('hint.clear')}
        • h - {self.t('hint.help')}
        • s - {self.t('hint.search')}
        • l - {self.t('config.language')}
        • k - {self.t('logger.title')}
        """

        self.console.print("\n" + "=" * 70, style="green")
        self.console.print(f"{self.t('app.help')}".center(70), style="green bold")
        self.console.print("=" * 70 + "\n", style="green")
        self.console.print(help_text)

        self.console.print("\n" + "─" * 70, style="dim")
        self.console.print(f"[yellow]{self.t('app.back')}...[/yellow]")
        input()

        # 返回后重新显示界面
        self.menu_system.display_interface(clear=True)

    def handle_exit(self):
        """处理退出"""
        if self.config_manager.get_config("confirm_exit", True):
            confirm = Prompt.ask(
                f"[bold red]{self.t('app.exit_confirm')}[/bold red]",
                choices=["y", "n", "Y", "N"],
                default="n"
            )

            if confirm.lower() != 'y':
                return

        # 显示退出信息
        uptime = time.time() - self.start_time
        minutes = uptime / 60
        hours = minutes / 60

        self.console.print(f"\n📊 {self.t('stats.title')}:")

        if hours >= 1:
            self.console.print(f"  ⏱️  {self.t('stats.uptime')}: {hours:.1f} {self.t('format.time_hours', '小时')}")
        elif minutes >= 1:
            self.console.print(f"  ⏱️  {self.t('stats.uptime')}: {minutes:.1f} {self.t('format.time_minutes', '分钟')}")
        else:
            self.console.print(f"  ⏱️  {self.t('stats.uptime')}: {uptime:.1f} {self.t('format.time_seconds', '秒')}")

        self.console.print(f"  📝 {self.t('stats.commands')}: {self.command_count}")
        self.console.print(f"  🔌 {self.t('stats.plugins')}: {len(self.plugin_manager.plugins)}")

        # 清理资源
        self.plugin_manager.cleanup_all()

        # 注销回调
        self.locale_manager.unregister_change_callback(self._on_language_changed)

        self.console.print(f"\n[green]{self.t('app.exit_thanks')}[/green]\n")
        sys.exit(0)

    def run(self):
        """运行主程序"""
        try:
            # 主循环
            while True:
                # 显示界面
                self.display_interface()

                # 获取用户选择并处理
                choice = self.get_user_choice()
                self.process_choice(choice)

        except KeyboardInterrupt:
            self.handle_exit()
        except Exception as e:
            self.menu_system.clear_screen()
            self.console.print(f"\n[red]❌ {self.t('error.command_failed')}: {str(e)}[/red]\n")
            import traceback
            self.console.print(traceback.format_exc())
            input(f"\n{self.t('app.back')}...")


def check_dependencies():
    """检查依赖"""
    required = ["psutil", "rich"]
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"缺少依赖包: {', '.join(missing)}")
        print("正在安装依赖...")

        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("✅ 依赖安装完成!")
        except Exception as e:
            print(f"❌ 依赖安装失败: {str(e)}")
            print(f"请手动执行: pip install {' '.join(missing)}")
            return False

    return True


def main():
    """主函数"""
    print("🚀 启动 FastX TUI (pyi18n版本)...")

    # 检查依赖
    if not check_dependencies():
        return

    # 运行应用
    app = FastXPyI18nTUI()
    app.run()


if __name__ == "__main__":
    main()