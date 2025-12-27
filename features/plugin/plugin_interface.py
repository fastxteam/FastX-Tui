#!/usr/bin/env python3
"""
FastX-Tui 插件管理界面模块
"""
import os
import sys
from typing import Optional
from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from core.plugin_manager import PluginManager, PluginRepository
from core.menu_system import MenuSystem, MenuNode
from core.config_manager import ConfigManager


class PluginInterface:
    """插件管理界面管理器"""

    def __init__(self, console: Console, plugin_manager: PluginManager, menu_system: MenuSystem,
                 config_manager: ConfigManager):
        self.console = console
        self.plugin_manager = plugin_manager
        self.menu_system = menu_system
        self.config_manager = config_manager
        # 初始化插件仓库管理器
        self.plugin_repo = PluginRepository()
        # 面板宽度
        self.panel_width = 136

    def show_plugin_interface(self, view_manager=None) -> bool:
        """显示插件管理界面"""
        while True:
            self.console.clear()
            self._show_plugin_menu()
            choice = self._get_user_choice()
            if choice == '0':
                self.console.clear()
                return True
            elif choice == 'q':
                return False
            self._handle_choice(choice, view_manager)

    def _show_plugin_menu(self):
        """显示插件管理菜单"""
        # 主标题
        title_panel = Panel(
            Text("插件管理中心", style="bold cyan"),
            box=box.SIMPLE,
            border_style="cyan",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 获取插件列表
        plugins = self.plugin_manager.list_plugins()

        # 获取插件目录
        plugin_dir = self.config_manager.get_config("plugin_directory", "plugins")
        plugin_dir_path = os.path.abspath(plugin_dir)

        # 创建插件信息表格 - 调整Table设置减少行间距
        plugin_table = Table(
            show_header=True,
            show_footer=False,
            header_style="bold magenta",
            box=box.SIMPLE,
            border_style="blue",
            show_lines=False,  # 移除行间线条
            collapse_padding=True,  # 减少内边距
            pad_edge=False,  # 移除边缘填充
            padding=(0, 0),  # 最小内边距
            width=self.panel_width - 2
        )

        # 计算列宽（总计134字符）
        plugin_table.add_column("编号", style="cyan", justify="center", width=8)
        plugin_table.add_column("状态", justify="center", width=8)
        plugin_table.add_column("名称", style="bold white", width=30)
        plugin_table.add_column("版本", style="green", justify="center", width=12)
        plugin_table.add_column("作者", style="yellow", width=25)
        plugin_table.add_column("描述", style="dim", no_wrap=True, width=51)

        plugin_count = 0
        if plugins:
            for i, plugin_info in enumerate(plugins, 1):
                status = "●" if plugin_info["enabled"] and plugin_info["loaded"] else "○" if plugin_info[
                    "enabled"] else "×"
                status_style = "green" if plugin_info["enabled"] and plugin_info["loaded"] else "yellow" if plugin_info[
                    "enabled"] else "red"

                # 处理过长的文本 - 截断而不是换行
                name = plugin_info["display_name"]
                if len(name) > 30:
                    name = name[:27] + "..."

                author = plugin_info["author"]
                if len(author) > 25:
                    author = author[:22] + "..."

                description = plugin_info["description"]
                if len(description) > 30:
                    description = description[:27] + "..."

                plugin_table.add_row(
                    f"{i}",
                    Text(status, style=status_style),
                    name,
                    f"v{plugin_info['version']}",
                    author,
                    description
                )
                plugin_count += 1
        else:
            # 没有插件时的显示
            plugin_table.add_row("", "", "暂无插件", "", "", "")

        # 插件列表面板
        plugin_title = Text(f"已发现插件 ({plugin_count})", style="bold blue")

        plugin_panel = Panel(
            plugin_table,
            title=plugin_title,
            subtitle=f"插件目录: {plugin_dir_path}",
            subtitle_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
            width=self.panel_width
        )
        self.console.print(plugin_panel)
        self.console.print()

        # 创建操作命令表格 - 调整Table设置减少行间距
        command_table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
            border_style="green",
            show_lines=False,
            collapse_padding=True,
            pad_edge=False,
            padding=(0, 0),
            width=self.panel_width - 2
        )
        command_table.add_column("命令", style="bold cyan", width=8)
        command_table.add_column("具体操作", style="white", width=128)

        commands = [
            ("1", "重新加载所有插件"),
            ("2", "刷新插件列表"),
            ("3", "显示插件目录"),
            ("4", "启用/禁用插件"),
            ("5", "浏览在线插件"),
            ("6", "安装在线插件"),
            ("7", "创建新插件"),
            ("8", "更新插件"),
            ("9", "卸载插件")
        ]

        for cmd, desc in commands:
            command_table.add_row(cmd, desc)

        # 操作面板
        operation_panel = Panel(
            command_table,
            title="操作命令",
            subtitle="0: 返回主菜单 | q: 退出程序",
            subtitle_align="left",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1),
            width=self.panel_width
        )

        self.console.print(operation_panel)

        # 分隔线
        self.console.print()
        self.console.print("─" * self.panel_width, style="dim")

        # 输入提示
        self.console.print("\n请输入命令编号: ", style="bold green", end="")

    def _get_user_choice(self) -> str:
        """获取用户选择"""
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
        elif choice == '5':
            self._browse_online_plugins()
        elif choice == '6':
            self._install_online_plugin()
        elif choice == '7':
            self._create_new_plugin()
        elif choice == '8':
            self._update_plugins()
        elif choice == '9':
            self._uninstall_plugin()

        if choice != '0' and choice != 'q':
            self._wait_for_keypress()

    def _wait_for_keypress(self):
        """等待按键继续"""
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

    def _browse_online_plugins(self):
        """浏览在线插件"""
        self.console.clear()

        title_panel = Panel(
            Text("浏览在线插件", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 支持搜索功能
        search_query = self.console.input("搜索插件 (直接回车跳过): ")

        self.console.print("\n正在获取插件信息...")
        plugins = self.plugin_repo.get_plugins(search=search_query)

        if plugins['plugins']:
            # 创建插件表格 - 调整Table设置
            table = Table(
                show_header=True,
                header_style="bold magenta",
                box=box.SIMPLE,
                border_style="blue",
                show_lines=False,
                collapse_padding=True,
                pad_edge=False,
                padding=(0, 0),
                width=self.panel_width - 2
            )
            # 重新计算列宽
            table.add_column("编号", style="cyan", justify="center", width=8)
            table.add_column("名称", style="bold white", width=40)
            table.add_column("版本", style="green", justify="center", width=12)
            table.add_column("作者", style="yellow", width=30)
            table.add_column("评分", style="blue", justify="center", width=10)
            table.add_column("下载量", style="dim", justify="right", width=12)

            for i, plugin in enumerate(plugins['plugins'], 1):
                # 处理过长的文本
                name = plugin.get("name", "未知")
                if len(name) > 40:
                    name = name[:37] + "..."

                author = plugin.get("author", "未知")
                if len(author) > 30:
                    author = author[:27] + "..."

                table.add_row(
                    f"{i}",
                    name,
                    plugin.get("version", "0.0.0"),
                    author,
                    f"{plugin.get('rating', 0.0):.1f}",
                    f"{plugin.get('downloads', 0):,}"
                )

            # 结果面板
            result_panel = Panel(
                table,
                title=f"找到 {plugins['total']} 个插件",
                subtitle=f"第 {plugins['page']}/{(plugins['total'] + plugins['per_page'] - 1) // plugins['per_page']} 页",
                subtitle_align="left",
                border_style="blue",
                box=box.ROUNDED,
                padding=(0, 1),
                width=self.panel_width
            )

            self.console.print(result_panel)
        else:
            no_result_panel = Panel(
                Text("没有找到匹配的插件", style="yellow", justify="center"),
                border_style="yellow",
                box=box.ROUNDED,
                width=self.panel_width
            )
            self.console.print(no_result_panel)

    def _install_online_plugin(self):
        """安装在线插件"""
        self.console.clear()

        title_panel = Panel(
            Text("安装在线插件", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 安装选项表格
        options_table = Table(
            show_header=False,
            box=box.SIMPLE,
            border_style="blue",
            show_lines=False,
            collapse_padding=True,
            pad_edge=False,
            padding=(0, 0),
            width=self.panel_width - 2
        )
        options_table.add_column("编号", style="bold cyan", width=8)
        options_table.add_column("安装方式", style="white", width=128)

        options_table.add_row("1", "从官方仓库安装 (输入插件ID)")
        options_table.add_row("2", "从GitHub安装 (输入仓库URL)")

        options_panel = Panel(
            options_table,
            subtitle="0: 返回",
            subtitle_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
            width=self.panel_width
        )

        self.console.print(options_panel)
        self.console.print()

        self.console.print("请选择安装方式: ", style="bold green", end="")
        install_choice = input().strip()

        if install_choice == '0':
            return
        elif install_choice == '1':
            # 从官方仓库安装
            plugin_id = input("请输入插件ID: ").strip()
            if plugin_id:
                self.console.print("\n正在安装插件...")
                success = self.plugin_repo.install_plugin(plugin_id, self.plugin_manager)
                if success:
                    self._show_message("插件安装成功", "green")
                    # 重新加载插件
                    self._reload_plugins()
                else:
                    self._show_message("插件安装失败", "red")
        elif install_choice == '2':
            # 从GitHub直接安装
            github_url = input("请输入GitHub仓库URL: ").strip()
            if github_url:
                self.console.print("\n正在安装插件...")
                success = self.plugin_manager.install_plugin_from_github(github_url)
                if success:
                    self._show_message("插件安装成功", "green")
                    # 重新加载插件
                    self._reload_plugins()
                else:
                    self._show_message("插件安装失败", "red")
        else:
            self._show_message("无效的选择", "red")

    def _update_plugins(self):
        """更新插件"""
        self.console.clear()

        title_panel = Panel(
            Text("更新插件", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 获取已安装的插件
        installed_plugins = self.plugin_manager.list_plugins()

        if not installed_plugins:
            self._show_message("暂无已安装的插件", "yellow")
            return

        # 创建更新表格
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
            border_style="blue",
            show_lines=False,
            collapse_padding=True,
            pad_edge=False,
            padding=(0, 0),
            width=self.panel_width - 2
        )
        table.add_column("序号", style="cyan", justify="center", width=8)
        table.add_column("插件", style="bold white", width=55)
        table.add_column("当前版本", style="green", justify="center", width=15)
        table.add_column("库上版本", style="blue", justify="center", width=15)
        table.add_column("状态", style="yellow", justify="center", width=12)

        for i, plugin_info in enumerate(installed_plugins, 1):
            # 模拟获取库上版本
            repo_version = plugin_info['version']  # 模拟数据
            status = "最新" if plugin_info['version'] == repo_version else "可更新"

            # 处理插件名称
            name = plugin_info['name']
            if len(name) > 55:
                name = name[:52] + "..."

            table.add_row(
                f"{i}",
                name,
                plugin_info['version'],
                repo_version,
                status
            )

        table_panel = Panel(
            table,
            title=f"已安装插件 ({len(installed_plugins)})",
            subtitle="0: 返回 | a: 更新所有插件",
            subtitle_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
            width=self.panel_width
        )

        self.console.print(table_panel)
        self.console.print()

        self.console.print("请选择要更新的插件编号: ", style="bold green", end="")
        choice = input().strip()

        if choice == '0':
            return
        elif choice.lower() == 'a':
            # 更新所有插件
            self.console.print("\n正在更新所有插件...")
            updated_count = 0
            for plugin_info in installed_plugins:
                self.console.print(f"更新 {plugin_info['name']}...")
                self.console.print(f"  {plugin_info['name']} 已是最新版本")
                updated_count += 1
            self._show_message(f"更新完成! 共检查了 {updated_count} 个插件", "green")
        else:
            # 更新单个插件
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(installed_plugins):
                    plugin_info = installed_plugins[idx]
                    self.console.print(f"\n正在更新 {plugin_info['name']}...")
                    self.console.print(f"  {plugin_info['name']} 已是最新版本")
                else:
                    self._show_message("无效的插件编号", "red")
            except ValueError:
                self._show_message("无效的输入", "red")

    def _reload_plugins(self):
        """重新加载插件"""
        self.console.print()
        title_panel = Panel(
            Text("重新加载插件", style="bold green"),
            subtitle="正在重新加载插件...",
            subtitle_align="center",
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        # 清空所有插件相关的菜单和命令
        self.plugin_manager.cleanup_all()

        # 获取主菜单
        main_menu = self.menu_system.get_item_by_id("main_menu")
        if isinstance(main_menu, MenuNode):
            # 保存系统内置菜单项和插件主菜单
            new_main_menu_items = []
            for item_id in main_menu.items[:]:
                menu_item = self.menu_system.get_item_by_id(item_id)
                if menu_item:
                    # 保留系统内置菜单项
                    if getattr(menu_item, 'is_system', False):
                        new_main_menu_items.append(item_id)
                    else:
                        # 检查是否是插件主菜单，保留插件主菜单
                        plugin_name = item_id.replace('_menu', '')
                        if plugin_name in self.plugin_manager.all_plugins:
                            new_main_menu_items.append(item_id)
            main_menu.items = new_main_menu_items

        # 清空所有非系统内置的菜单项和非插件主菜单
        items_to_remove = []
        for item_id, item in self.menu_system.items.items():
            # 保留系统内置项
            if getattr(item, 'is_system', False):
                continue
            
            # 保留插件主菜单
            if isinstance(item, MenuNode) and item_id.endswith('_menu'):
                plugin_name = item_id.replace('_menu', '')
                if plugin_name in self.plugin_manager.all_plugins:
                    continue
            
            # 其他项都移除
            items_to_remove.append(item_id)
        
        # 从菜单系统中移除所有非系统菜单项和非插件主菜单
        for item_id in items_to_remove:
            self.menu_system.remove_item(item_id)

        # 重新加载插件
        self.plugin_manager.load_all_plugins()
        self.plugin_manager.register_all_plugins(self.menu_system)

        # 直接在PluginInterface中重建插件菜单
        self._rebuild_plugin_menu()

        # 等待所有日志输出完成
        import time
        time.sleep(0.1)  # 短暂等待确保日志输出完成

        # 显示结果
        self._show_message(f"成功重新加载 {len(self.plugin_manager.plugins)} 个插件", "green")

    def _rebuild_plugin_menu(self):
        """重建插件菜单，与AppManager保持一致的逻辑"""
        from core.menu_system import MenuNode, MenuType, MenuItem, ActionItem

        # 获取主菜单
        main_menu = self.menu_system.get_item_by_id("main_menu")
        if not isinstance(main_menu, MenuNode):
            return

        # 从主菜单中移除插件菜单（如果存在）
        if "plugins_menu" in main_menu.items:
            main_menu.items.remove("plugins_menu")

        # 检查并移除plugins_menu菜单
        if "plugins_menu" in self.menu_system.items:
            del self.menu_system.items["plugins_menu"]

        # 自动统计所有插件命令
        plugin_items_added = False

        # 收集要从主菜单移除的插件命令
        commands_to_remove = []

        for item_id, item in self.menu_system.items.items():
            # 跳过系统内置项目和菜单
            if getattr(item, 'is_system', False):
                continue
                
            # 检查是否是插件生成的命令或菜单
            if isinstance(item, (MenuItem, ActionItem, MenuNode)):
                if isinstance(item, MenuNode):
                    # 是插件生成的菜单，检查是否直接注册到了主菜单
                    is_in_main_menu = item_id in main_menu.items

                    if is_in_main_menu:
                        # 保留在主菜单中，因为有些插件可能需要直接添加菜单到主菜单
                        # 但我们可以在禁用插件时清理这些菜单
                        plugin_items_added = True
                else:
                    # 是插件命令，检查是否直接注册到了主菜单
                    is_in_main_menu = item_id in main_menu.items

                    # 如果是直接注册到主菜单的命令，从主菜单移除
                    if is_in_main_menu:
                        commands_to_remove.append(item_id)

        # 从主菜单中移除插件命令
        for item_id in commands_to_remove:
            if item_id in main_menu.items:
                main_menu.items.remove(item_id)

    def _refresh_plugins(self):
        """刷新插件列表"""
        self.console.print()
        title_panel = Panel(
            Text("刷新插件列表", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        discovered = self.plugin_manager.discover_plugins()
        loaded = list(self.plugin_manager.plugins.keys())

        if discovered:
            self.console.print()

            # 创建插件详情表格
            plugins_table = Table(
                show_header=True,
                header_style="bold magenta",
                box=box.SIMPLE,
                border_style="cyan",
                show_lines=False,
                collapse_padding=True,
                pad_edge=False,
                padding=(0, 0),
                width=self.panel_width - 2
            )
            plugins_table.add_column("插件名称", style="cyan bold", width=100)
            plugins_table.add_column("状态", style="yellow", justify="center", width=34)

            for plugin in discovered:
                status = "已加载" if plugin in loaded else "未加载"
                status_style = "green" if plugin in loaded else "red"
                plugins_table.add_row(
                    plugin,
                    Text(status, style=status_style)
                )

            plugins_panel = Panel(
                plugins_table,
                title="发现的插件",
                subtitle=f"发现插件: {len(discovered)} 已加载插件:{len(loaded)}",
                subtitle_align="left",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(0, 1),
                width=self.panel_width
            )

            self.console.print(plugins_panel)

    def _show_plugin_directory(self):
        """显示插件目录"""
        self.console.print()
        title_panel = Panel(
            Text("插件目录", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        plugin_dir = self.config_manager.get_config("plugin_directory", "plugins")
        abs_plugin_dir = os.path.abspath(plugin_dir)

        if os.path.exists(abs_plugin_dir):
            files = os.listdir(abs_plugin_dir)
            if files:
                self.console.print()

                # 使用Tree组件显示目录结构
                tree = Tree(f"📁 {os.path.basename(abs_plugin_dir)}", style="bold cyan")

                # 分类显示文件和目录
                directories = []
                python_files = []
                other_files = []

                for file in files:
                    file_path = os.path.join(abs_plugin_dir, file)
                    if os.path.isdir(file_path):
                        directories.append(file)
                    elif file.endswith('.py') and file != '__init__.py':
                        python_files.append(file)
                    else:
                        other_files.append(file)

                # 添加目录
                if directories:
                    dir_branch = tree.add("📁 目录", style="bold yellow")
                    for dir_name in sorted(directories):
                        dir_branch.add(f"📁 {dir_name}/", style="cyan")

                # 添加Python文件
                if python_files:
                    py_branch = tree.add("🐍 Python插件文件", style="bold green")
                    for py_file in sorted(python_files):
                        py_branch.add(f"📄 {py_file}", style="green")

                # 添加其他文件
                if other_files:
                    other_branch = tree.add("📄 其他文件", style="bold dim")
                    for other_file in sorted(other_files):
                        other_branch.add(f"📄 {other_file}", style="dim")

                # 创建Tree面板
                tree_panel = Panel(
                    tree,
                    title="目录内容",
                    subtitle=f"插件目录路径: {abs_plugin_dir}",
                    subtitle_align="center",
                    border_style="cyan",
                    box=box.ROUNDED,
                    padding=(1, 2),
                    width=self.panel_width
                )

                self.console.print(tree_panel)
            else:
                self._show_message("目录为空", "yellow")
        else:
            self._show_message("目录不存在", "red")

    def _toggle_plugin(self):
        """启用/禁用插件"""
        plugins = self.plugin_manager.list_plugins()

        if not plugins:
            self._show_message("暂无插件", "yellow")
            return

        self.console.print()
        title_panel = Panel(
            Text("启用/禁用插件", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        # 显示插件列表供选择 - 调整Table设置
        select_table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
            border_style="blue",
            show_lines=False,
            collapse_padding=True,
            pad_edge=False,
            padding=(0, 0),
            width=self.panel_width - 2
        )
        select_table.add_column("编号", style="cyan", justify="center", width=8)
        select_table.add_column("插件名称", style="bold white", width=80)
        select_table.add_column("状态", style="yellow", justify="center", width=20)

        for i, plugin_info in enumerate(plugins, 1):
            status = "已启用" if plugin_info["enabled"] else "已禁用"
            select_table.add_row(
                f"{i}",
                plugin_info['name'],
                status
            )

        select_panel = Panel(
            select_table,
            subtitle="0: 返回",
            subtitle_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
            width=self.panel_width
        )

        self.console.print(select_panel)
        self.console.print()

        self.console.print("请输入插件编号: ", style="bold green", end="")
        choice = input().strip()

        if choice == '0':
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(plugins):
                plugin_info = plugins[idx]
                plugin_name = plugin_info["name"]

                if plugin_info["enabled"]:
                    # 禁用插件
                    success = self.plugin_manager.disable_plugin(plugin_name)
                    if success:
                        self._show_message(f"插件 {plugin_info['name']} 已成功禁用", "green")
                        # 重新加载插件并重建菜单
                        self._reload_plugins()
                    else:
                        self._show_message(f"禁用插件 {plugin_info['name']} 失败", "red")
                else:
                    # 启用插件
                    success = self.plugin_manager.enable_plugin(plugin_name)
                    if success:
                        self._show_message(f"插件 {plugin_info['name']} 已成功启用", "green")
                        # 重新加载插件并重建菜单
                        self._reload_plugins()
                    else:
                        self._show_message(f"启用插件 {plugin_info['name']} 失败", "red")
            else:
                self._show_message("无效的插件编号", "red")
        except ValueError:
            self._show_message("无效的输入", "red")

    def _create_new_plugin(self):
        """创建新插件"""
        self.console.clear()

        title_panel = Panel(
            Text("创建新插件", style="bold cyan"),
            box=box.SIMPLE,
            border_style="cyan",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 导入PythonOperations
        from core.operations import PythonOperations

        # 获取用户输入
        plugin_name = self.console.input("请输入插件名称 (英文): ").strip()
        if not plugin_name:
            self._show_message("插件名称不能为空", "red")
            return

        plugin_display_name = self.console.input("请输入插件显示名称 (直接回车使用插件名称): ").strip()

        # 创建插件
        self.console.print(f"\n正在创建插件 '{plugin_name}'...")
        result = PythonOperations.create_plugin(plugin_name, plugin_display_name)

        if "成功" in result:
            self._show_message(result, "green")
        else:
            self._show_message(result, "yellow")

        self.console.print("\n正在刷新插件列表...")
        self._reload_plugins()

    def _uninstall_plugin(self):
        """卸载插件"""
        plugins = self.plugin_manager.list_plugins()

        if not plugins:
            self._show_message("暂无插件", "yellow")
            return

        self.console.print()
        title_panel = Panel(
            Text("卸载插件", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        # 显示插件列表供选择 - 调整Table设置
        select_table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
            border_style="blue",
            show_lines=False,
            collapse_padding=True,
            pad_edge=False,
            padding=(0, 0),
            width=self.panel_width - 2
        )
        select_table.add_column("编号", style="cyan", justify="center", width=8)
        select_table.add_column("插件名称", style="bold white", width=80)
        select_table.add_column("版本", style="green", justify="center", width=20)

        for i, plugin_info in enumerate(plugins, 1):
            select_table.add_row(
                f"{i}",
                plugin_info['name'],
                f"v{plugin_info['version']}"
            )

        select_panel = Panel(
            select_table,
            subtitle="0: 返回",
            subtitle_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
            width=self.panel_width
        )

        self.console.print(select_panel)
        self.console.print()

        self.console.print("请输入插件编号: ", style="bold green", end="")
        choice = input().strip()

        if choice == '0':
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(plugins):
                plugin_info = plugins[idx]
                plugin_name = plugin_info["name"]

                # 确认卸载
                from rich.prompt import Confirm
                confirm = Confirm.ask(f"\n是否确定要卸载插件 {plugin_info['name']}?")
                if confirm:
                    success = self.plugin_manager.uninstall_plugin(plugin_name)
                    if success:
                        self._show_message(f"插件 {plugin_info['name']} 已成功卸载", "green")
                        # 重新加载插件并重建菜单
                        self._reload_plugins()
                    else:
                        self._show_message(f"卸载插件 {plugin_info['name']} 失败", "red")
                else:
                    self._show_message(f"已取消卸载插件 {plugin_info['name']}", "yellow")
            else:
                self._show_message("无效的插件编号", "red")
        except ValueError:
            self._show_message("无效的输入", "red")

    def _show_message(self, message: str, color: str = "white"):
        """显示消息面板"""
        message_panel = Panel(
            Text(message, justify="center"),
            border_style=color,
            box=box.ROUNDED,
            padding=(1, 2),
            width=self.panel_width
        )
        self.console.print(message_panel)