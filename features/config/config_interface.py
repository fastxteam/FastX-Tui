#!/usr/bin/env python3
"""
FastX-Tui 配置界面管理模块
"""
import os
import sys
from typing import Optional
from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from core.config_manager import ConfigManager


class ConfigInterface:
    """配置界面管理器"""

    def __init__(self, console: Console, config_manager: ConfigManager, plugin_manager=None):
        self.console = console
        self.config_manager = config_manager
        self.plugin_manager = plugin_manager
        # 面板宽度
        self.panel_width = 120

    def show_config_interface(self, view_manager=None) -> bool:
        """显示配置界面"""
        while True:
            self.console.clear()
            self._show_config_menu()
            choice = self._get_user_choice()
            if choice == '0':
                self.console.clear()
                return True
            elif choice == 'q':
                return False
            self._handle_choice(choice, view_manager)

    def _show_config_menu(self):
        """显示配置管理菜单"""
        # 主标题
        title_panel = Panel(
            Text("配置管理中心", style="bold cyan"),
            box=box.SIMPLE,
            border_style="cyan",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 当前配置信息 - 在操作命令上方
        current_theme = self.config_manager.get_config("theme", "default")
        current_language = self.config_manager.get_config("language", "zh_CN")
        auto_updates = self.config_manager.get_config("auto_check_updates", True)

        # 创建配置状态表格
        config_table = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(0, 1)
        )

        # 使用三列布局
        config_table.add_column("项目", style="cyan bold", width=25)
        config_table.add_column("当前设置", style="white", width=65)
        config_table.add_column("", width=30)  # 空列用于对齐

        config_table.add_row("主题", current_theme, "")
        config_table.add_row("语言", current_language, "")
        config_table.add_row("自动检查更新", "已开启" if auto_updates else "已关闭", "")

        config_panel = Panel(
            config_table,
            title="当前配置状态",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )

        self.console.print(config_panel)
        self.console.print()

        # 创建操作命令表格
        command_table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(0, 1)
        )

        # 一列显示所有命令，命令和描述分开
        command_table.add_column("命令", style="bold cyan", width=8)
        command_table.add_column("具体操作", style="white", width=112)

        # 命令列表 - 直接显示所有命令
        commands = [
            ("1", "查看当前配置"),
            ("2", "更换主题"),
            ("3", "高级设置"),
            ("4", "插件配置"),
            ("5", "重置配置"),
            ("6", "导出配置"),
            ("7", "导入配置")
        ]

        # 直接添加所有命令到表格
        for cmd, desc in commands:
            command_table.add_row(cmd, desc)

        command_panel = Panel(
            command_table,
            title="操作命令",
            subtitle="0: 返回主菜单 | q: 退出程序",
            subtitle_align="left",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )

        self.console.print(command_panel)

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
            self._show_current_config()
        elif choice == '2':
            self._change_theme()
        elif choice == '3':
            self._show_advanced_settings()
        elif choice == '4':
            self._show_plugin_config()
        elif choice == '5':
            self._reset_config()
        elif choice == '6':
            self._export_config()
        elif choice == '7':
            self._import_config()

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

    def _show_current_config(self):
        """显示当前配置"""
        self.console.print()
        title_panel = Panel(
            Text("当前配置", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        config_summary = self.config_manager.show_config_summary()

        # 创建配置详情面板
        config_panel = Panel(
            config_summary,
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
            width=self.panel_width
        )
        self.console.print(config_panel)

    def _change_theme(self):
        """修改主题"""
        self.console.print()
        title_panel = Panel(
            Text("更换主题", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        themes = ["default", "dark", "light", "blue", "green"]
        theme_info = {
            "default": "默认主题",
            "dark": "深色主题",
            "light": "浅色主题",
            "blue": "蓝色主题",
            "green": "绿色主题"
        }

        # 创建主题选择表格
        theme_table = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(0, 1)
        )

        # 一列显示所有主题选项
        theme_table.add_column("编号", style="bold cyan", width=8)
        theme_table.add_column("主题名称", style="white", width=25)
        theme_table.add_column("说明", style="dim", width=87)

        # 添加主题选项
        for i, theme in enumerate(themes, 1):
            theme_table.add_row(str(i), theme, theme_info.get(theme, ""))

        theme_panel = Panel(
            theme_table,
            subtitle="0: 返回",
            subtitle_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )

        self.console.print(theme_panel)
        self.console.print()

        self.console.print("请选择主题编号: ", style="bold green", end="")
        choice = input().strip()

        if choice == '0':
            return

        try:
            index = int(choice) - 1
            if 0 <= index < len(themes):
                selected_theme = themes[index]
                self.config_manager.set_config("theme", selected_theme)
                self._show_message(f"主题已切换为: {selected_theme}", "green")
            else:
                self._show_message("无效的选择", "red")
        except ValueError:
            self._show_message("无效的输入", "red")

    def _show_advanced_settings(self):
        """显示高级设置界面"""
        while True:
            self.console.clear()

            title_panel = Panel(
                Text("高级设置", style="bold cyan"),
                box=box.SIMPLE,
                border_style="cyan",
                padding=(0, 0),
                width=self.panel_width
            )
            self.console.print(title_panel)
            self.console.print()

            # 获取当前设置
            show_welcome = self.config_manager.get_config("show_welcome_page", True)
            auto_check_updates = self.config_manager.get_config("auto_check_updates", True)
            banner_style = self.config_manager.get_config("banner_style", "default")
            use_async = self.config_manager.get_config("use_async_tasks", True)

            # 创建设置表格
            settings_table = Table(
                show_header=True,
                header_style="bold magenta",
                box=box.SIMPLE,
                border_style="blue",
                show_lines=True,
                width=self.panel_width - 2
            )
            settings_table.add_column("编号", style="cyan", justify="center", width=8)
            settings_table.add_column("设置项", style="bold white", width=25)
            settings_table.add_column("当前状态", style="yellow", justify="center", width=15)
            settings_table.add_column("说明", style="dim", width=72)

            settings_table.add_row(
                "1",
                "显示欢迎页面",
                "√ 开启" if show_welcome else "× 关闭",
                "启动时显示欢迎页面"
            )
            settings_table.add_row(
                "2",
                "自动检查更新",
                "√ 开启" if auto_check_updates else "× 关闭",
                "启动时自动检查更新"
            )
            settings_table.add_row(
                "3",
                "横幅样式",
                banner_style,
                "标题横幅的显示样式"
            )
            settings_table.add_row(
                "4",
                "使用异步任务",
                "√ 开启" if use_async else "× 关闭",
                "使用异步方式执行命令，提高系统响应性"
            )

            settings_panel = Panel(
                settings_table,
                subtitle="0: 返回",
                subtitle_align="left",
                border_style="blue",
                box=box.ROUNDED,
                padding=(0, 0),
                width=self.panel_width
            )

            self.console.print(settings_panel)
            self.console.print()

            self.console.print("请选择设置项编号: ", style="bold green", end="")
            choice = input().strip()

            if choice == '0':
                break
            elif choice == '1':
                # 切换显示欢迎页面设置
                new_value = not show_welcome
                self.config_manager.set_config("show_welcome_page", new_value)
                status = "开启" if new_value else "关闭"
                self._show_message(f"显示欢迎页面: {status}", "green")
                self._wait_for_keypress()
            elif choice == '2':
                # 切换自动检查更新设置
                new_value = not auto_check_updates
                self.config_manager.set_config("auto_check_updates", new_value)
                status = "开启" if new_value else "关闭"
                self._show_message(f"自动检查更新: {status}", "green")
                self._wait_for_keypress()
            elif choice == '3':
                # 切换横幅样式
                new_style = "gradient" if banner_style == "default" else "default"
                self.config_manager.set_config("banner_style", new_style)
                self._show_message(f"横幅样式已设置为: {new_style}", "green")
                self._wait_for_keypress()
            elif choice == '4':
                # 切换使用异步任务设置
                new_value = not use_async
                self.config_manager.set_config("use_async_tasks", new_value)
                status = "开启" if new_value else "关闭"
                self._show_message(f"使用异步任务: {status}", "green")
                self._wait_for_keypress()
            else:
                self._show_message("无效的选择", "red")
                self._wait_for_keypress()

    def _reset_config(self):
        """重置配置"""
        self.console.print()
        title_panel = Panel(
            Text("重置配置", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        warning_table = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(1, 2)
        )
        warning_table.add_column("警告", style="bold red", justify="center")
        warning_table.add_row("这将重置所有配置到默认值！")

        warning_panel = Panel(
            warning_table,
            border_style="red",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )

        self.console.print(warning_panel)
        self.console.print()

        self.console.print("确定要重置吗？(y/n): ", style="bold red", end="")

        if sys.platform == "win32":
            import msvcrt
            confirm = msvcrt.getch().decode('utf-8').lower()
            self.console.print(confirm)
        else:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                confirm = sys.stdin.read(1).lower()
                self.console.print(confirm)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if confirm.lower() == 'y':
            self.config_manager.reset_to_defaults()
            self._show_message("配置已重置为默认值", "green")
        else:
            self._show_message("重置已取消", "yellow")

    def _export_config(self):
        """导出配置"""
        self.console.print()
        title_panel = Panel(
            Text("导出配置", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        # 说明面板
        info_table = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(1, 2)
        )
        info_table.add_column("", style="white")
        info_table.add_row("请输入导出文件名 (默认: fastx-tui_config.json)")

        info_panel = Panel(
            info_table,
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(info_panel)
        self.console.print()

        self.console.print("文件名: ", style="white", end="")
        filename = input().strip()

        if not filename:
            filename = "fastx-tui_config.json"

        if self.config_manager.export_config(filename):
            filepath = os.path.abspath(filename)
            self._show_message(f"配置已成功导出到: {filepath}", "green")
        else:
            self._show_message("配置导出失败", "red")

    def _import_config(self):
        """导入配置"""
        self.console.print()
        title_panel = Panel(
            Text("导入配置", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        # 说明面板
        info_table = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(1, 2)
        )
        info_table.add_column("", style="white")
        info_table.add_row("请输入导入文件名")

        info_panel = Panel(
            info_table,
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(info_panel)
        self.console.print()

        self.console.print("文件名: ", style="white", end="")
        filename = input().strip()

        if filename:
            if os.path.exists(filename):
                if self.config_manager.import_config(filename):
                    self._show_message("配置已成功导入", "green")
                else:
                    self._show_message("配置导入失败", "red")
            else:
                self._show_message(f"文件不存在: {filename}", "red")
        else:
            self._show_message("文件名不能为空", "red")

    def _show_plugin_config(self):
        """显示插件配置界面"""
        if not self.plugin_manager:
            self._show_message("插件管理器未初始化", "red")
            return
        
        plugins = self.plugin_manager.list_plugins()
        plugin_list = [plugin for plugin in plugins if plugin["loaded"]]
        
        if not plugin_list:
            self._show_message("没有加载的插件", "red")
            return
        
        while True:
            # 显示插件列表供选择
            self.console.clear()
            title_panel = Panel(
                Text("插件配置", style="bold cyan"),
                box=box.SIMPLE,
                border_style="cyan",
                padding=(0, 0),
                width=self.panel_width
            )
            self.console.print(title_panel)
            self.console.print()
            
            # 创建插件选择表格
            plugin_table = Table(
                show_header=True,
                header_style="bold magenta",
                box=box.SIMPLE,
                show_edge=True,
                width=self.panel_width - 2,
                padding=(0, 1)
            )
            
            plugin_table.add_column("编号", style="bold cyan", width=8)
            plugin_table.add_column("插件名称", style="white", width=40)
            plugin_table.add_column("版本", style="dim", width=15)
            plugin_table.add_column("描述", style="dim", width=57)
            
            for i, plugin_info in enumerate(plugin_list, 1):
                plugin_table.add_row(
                    str(i),
                    plugin_info["display_name"],
                    plugin_info["version"],
                    plugin_info["description"]
                )
            
            plugin_panel = Panel(
                plugin_table,
                subtitle="0: 返回",
                subtitle_align="left",
                border_style="blue",
                box=box.ROUNDED,
                padding=(0, 0),
                width=self.panel_width
            )
            
            self.console.print(plugin_panel)
            self.console.print()
            
            self.console.print("请选择要配置的插件编号: ", style="bold green", end="")
            
            # 获取用户选择
            choice = input().strip()
            
            if choice == '0':
                return
            
            try:
                plugin_index = int(choice) - 1
                if 0 <= plugin_index < len(plugin_list):
                    # 获取插件名称和实例
                    plugin_info = plugin_list[plugin_index]
                    plugin_name = plugin_info["name"]
                    plugin = self.plugin_manager.get_plugin(plugin_name)
                    
                    if plugin:
                        # 显示插件配置
                        self._show_single_plugin_config(plugin, plugin_info)
                else:
                    self._show_message("无效的选择", "red")
                    self._wait_for_keypress()
            except ValueError:
                self._show_message("无效的输入", "red")
                self._wait_for_keypress()
    
    def _show_single_plugin_config(self, plugin, plugin_info):
        """显示单个插件的配置"""
        # 获取插件配置模式
        config_schema = plugin.get_config_schema()
        
        # 获取插件配置
        plugin_config = self.config_manager.get_config(f"plugin_{plugin_info['name']}", {})
        
        while True:
            # 显示插件配置
            self.console.clear()
            title_panel = Panel(
                Text(f"插件配置 - {plugin_info['display_name']}", style="bold cyan"),
                box=box.SIMPLE,
                border_style="cyan",
                padding=(0, 0),
                width=self.panel_width
            )
            self.console.print(title_panel)
            self.console.print()
            
            # 创建配置表格
            config_table = Table(
                show_header=True,
                header_style="bold magenta",
                box=box.SIMPLE,
                show_edge=True,
                width=self.panel_width - 2,
                padding=(0, 1)
            )
            
            config_table.add_column("编号", style="bold cyan", width=8)
            config_table.add_column("配置项", style="white", width=25)
            config_table.add_column("当前值", style="yellow", width=25)
            config_table.add_column("说明", style="dim", width=62)
            
            config_items = list(config_schema.items())
            for i, (config_name, config_info) in enumerate(config_items, 1):
                current_value = plugin_config.get(config_name, config_info.get("default"))
                config_table.add_row(
                    str(i),
                    config_name,
                    str(current_value),
                    config_info.get("description", "")
                )
            
            config_panel = Panel(
                config_table,
                subtitle="0: 返回 | 输入配置项编号修改值",
                subtitle_align="left",
                border_style="blue",
                box=box.ROUNDED,
                padding=(0, 0),
                width=self.panel_width
            )
            
            self.console.print(config_panel)
            self.console.print()
            
            self.console.print("请选择操作: ", style="bold green", end="")
            
            # 获取用户选择
            choice = input().strip()
            
            if choice == '0':
                return
            
            try:
                config_index = int(choice) - 1
                if 0 <= config_index < len(config_items):
                    # 获取配置项信息
                    config_name, config_info = config_items[config_index]
                    current_value = plugin_config.get(config_name, config_info.get("default"))
                    
                    # 显示修改界面
                    self.console.clear()
                    title_panel = Panel(
                        Text(f"修改配置 - {config_name}", style="bold cyan"),
                        box=box.SIMPLE,
                        border_style="cyan",
                        padding=(0, 0),
                        width=self.panel_width
                    )
                    self.console.print(title_panel)
                    self.console.print()
                    
                    self.console.print(f"配置项: {config_name}")
                    self.console.print(f"当前值: {current_value}")
                    self.console.print(f"说明: {config_info.get('description', '')}")
                    
                    if "choices" in config_info:
                        self.console.print(f"可选值: {', '.join(map(str, config_info['choices']))}")
                    
                    self.console.print()
                    self.console.print("请输入新值 (直接回车保持当前值): ", style="bold green", end="")
                    
                    new_value = input().strip()
                    
                    if new_value:
                        # 根据配置类型转换值
                        config_type = config_info.get("type", "string")
                        
                        try:
                            if config_type == "boolean":
                                # 处理布尔值
                                if new_value.lower() in ["true", "1", "yes", "y"]:
                                    parsed_value = True
                                elif new_value.lower() in ["false", "0", "no", "n"]:
                                    parsed_value = False
                                else:
                                    raise ValueError("无效的布尔值")
                            elif config_type == "integer":
                                parsed_value = int(new_value)
                            elif config_type == "float":
                                parsed_value = float(new_value)
                            else:
                                parsed_value = new_value
                            
                            # 验证可选值
                            if "choices" in config_info and parsed_value not in config_info["choices"]:
                                raise ValueError(f"值必须是以下之一: {', '.join(map(str, config_info['choices']))}")
                            
                            # 更新配置
                            plugin_config[config_name] = parsed_value
                            self.config_manager.set_config(f"plugin_{plugin_info['name']}", plugin_config)
                            
                            self._show_message(f"配置项 {config_name} 已更新为: {parsed_value}", "green")
                            self._wait_for_keypress()
                        except ValueError as e:
                            self._show_message(f"无效的输入: {e}", "red")
                            self._wait_for_keypress()
                else:
                    self._show_message("无效的选择", "red")
                    self._wait_for_keypress()
            except ValueError:
                self._show_message("无效的输入", "red")
                self._wait_for_keypress()
    

    
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