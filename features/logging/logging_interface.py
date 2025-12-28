#!/usr/bin/env python3
"""
FastX-Tui 日志管理功能模块
"""
import os
import re
import sys

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.config_manager import ConfigManager
from core.logger import get_available_log_levels, get_current_log_level, set_log_level


class LoggingInterface:
    """日志管理器"""

    def __init__(self, console: Console, config_manager: ConfigManager):
        self.console = console
        self.config_manager = config_manager
        # 获取EXE所在目录或项目根目录
        if getattr(sys, 'frozen', False):
            # 打包后的EXE环境
            app_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # 开发环境，获取项目根目录（假设features目录在项目根目录下）
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # 使用绝对路径确保日志文件路径正确，基于EXE所在目录或项目根目录
        self.log_file = os.path.join(app_dir, "logs", "fastx-tui.log")
        self.page_size = 500
        self.current_page = 1
        self.filter_level = None
        self.filter_plugin = None
        self.display_size = self.page_size
        # 面板宽度
        self.panel_width = 120

    def show_log_interface(self, view_manager=None) -> bool:
        """显示日志管理界面"""
        while True:
            self.console.clear()
            self._show_log_menu()
            choice = self._get_user_choice()
            if choice == '0':
                self.console.clear()
                return True
            elif choice == 'q':
                return False
            self._handle_choice(choice, view_manager)

    def _show_log_menu(self):
        """显示日志管理菜单"""
        # 主标题
        title_panel = Panel(
            Text("日志管理中心", style="bold cyan"),
            box=box.SIMPLE,
            border_style="cyan",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 当前日志信息
        current_log_level = get_current_log_level()
        log_file_path = self.log_file

        # 创建日志信息表格
        info_table = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(0, 1)
        )

        info_table.add_column("项目", style="cyan bold", width=25)
        info_table.add_column("当前设置", style="white", width=65)
        info_table.add_column("", width=30)  # 空列用于对齐

        # 缩短过长的文件路径
        if len(log_file_path) > 70:
            short_path = "..." + log_file_path[-67:]
        else:
            short_path = log_file_path

        info_table.add_row("日志等级", current_log_level, "")
        info_table.add_row("日志文件", short_path, "")
        info_table.add_row("显示大小", f"{self.display_size} 条/页", "")

        # 筛选条件显示
        filter_info = ""
        if self.filter_level:
            filter_info += f"等级: {self.filter_level}"
        if self.filter_plugin:
            if filter_info:
                filter_info += " | "
            filter_info += f"插件: {self.filter_plugin}"
        info_table.add_row("筛选条件", filter_info or "无", "")

        info_panel = Panel(
            info_table,
            title="当前日志状态",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )

        self.console.print(info_panel)
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

        command_table.add_column("命令", style="bold cyan", width=8)
        command_table.add_column("具体操作", style="white", width=112)

        commands = [
            ("1", "查看当前日志等级"),
            ("2", "设置日志等级"),
            ("3", "查看日志记录"),
            ("4", "打开日志文件"),
            ("5", "设置日志显示大小"),
            ("6", "配置日志筛选条件")
        ]

        for cmd, desc in commands:
            command_table.add_row(cmd, desc)

        command_panel = Panel(
            command_table,
            title="操作命令",
            subtitle="0: 返回主菜单 | q: 退出程序 ",
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
            self._show_current_log_level()
        elif choice == '2':
            self._set_log_level()
        elif choice == '3':
            self._view_log_records()
        elif choice == '4':
            self._open_log_file()
        elif choice == '5':
            self._set_display_size()
        elif choice == '6':
            self._configure_filter()

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

    def _show_current_log_level(self):
        """显示当前日志等级"""
        self.console.print()
        title_panel = Panel(
            Text("当前日志配置", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        # 创建配置表格
        config_table = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(1, 2)
        )

        config_table.add_column("配置项", style="cyan bold", width=30)
        config_table.add_column("当前值", style="white", width=90)

        config_table.add_row("当前日志等级", get_current_log_level())

        available_levels = get_available_log_levels()
        config_table.add_row("可用日志等级", ", ".join(available_levels))

        config_panel = Panel(
            config_table,
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )

        self.console.print(config_panel)

    def _set_log_level(self):
        """设置日志等级"""
        self.console.print()
        title_panel = Panel(
            Text("设置日志等级", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        available_levels = get_available_log_levels()

        # 创建等级选择表格
        level_table = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(0, 1)
        )

        level_table.add_column("编号", style="bold cyan", width=8)
        level_table.add_column("日志等级", style="white", width=25)
        level_table.add_column("说明", style="dim", width=87)

        level_info = {
            "DEBUG": "调试信息，最详细",
            "INFO": "一般信息，默认等级",
            "WARNING": "警告信息",
            "ERROR": "错误信息",
            "CRITICAL": "严重错误信息"
        }

        for i, level in enumerate(available_levels, 1):
            level_table.add_row(str(i), level, level_info.get(level, ""))

        level_panel = Panel(
            level_table,
            subtitle="0: 返回",
            subtitle_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )

        self.console.print(level_panel)
        self.console.print()

        self.console.print("请选择日志等级编号: ", style="bold green", end="")
        choice = input().strip()

        if choice == '0':
            return

        try:
            index = int(choice) - 1
            if 0 <= index < len(available_levels):
                selected_level = available_levels[index]
                set_log_level(selected_level)
                self.config_manager.set_config("log_level", selected_level)
                self._show_message(f"日志等级已设置为: {selected_level}", "green")
            else:
                self._show_message("无效的选择", "red")
        except ValueError:
            self._show_message("无效的输入", "red")

    def _view_log_records(self):
        """查看日志记录"""
        if not os.path.exists(self.log_file):
            self._show_message(f"日志文件不存在: {self.log_file}", "red")
            return

        self.current_page = 1
        while True:
            self.console.clear()

            # 简洁的标题
            self.console.print("日志记录查看", style="bold cyan", justify="center")
            self.console.print("─" * self.panel_width, style="dim")
            self.console.print()

            logs = self._read_logs()
            total_pages = (len(logs) + self.display_size - 1) // self.display_size

            if total_pages == 0:
                self.console.print("没有日志记录", style="yellow", justify="center")
                self.console.print()
            else:
                start = (self.current_page - 1) * self.display_size
                end = start + self.display_size
                page_logs = logs[start:end]

                # 显示日志表格
                self._display_logs(page_logs)

                # 显示分页信息
                self._show_pagination(total_pages)

            # 简洁的导航提示
            nav_text = "← 上一页 | 0 返回 | → 下一页 "
            self.console.print()
            self.console.print(nav_text, style="dim", justify="center")
            self.console.print()

            self.console.print("请使用方向键导航: ", style="bold green", end="")
            choice = self._get_navigation_choice()
            if choice == 'left':
                if self.current_page > 1:
                    self.current_page -= 1
            elif choice == 'right':
                if self.current_page < total_pages:
                    self.current_page += 1
            elif choice == '0':
                break

    def _read_logs(self) -> list[dict[str, str]]:
        """读取日志文件"""
        logs = []
        try:
            with open(self.log_file, encoding='utf-8') as f:
                for line in f:
                    log_entry = self._parse_log_line(line.strip())
                    if log_entry:
                        logs.append(log_entry)
        except Exception as e:
            self._show_message(f"读取日志失败: {str(e)}", "red")

        # 应用筛选条件
        filtered_logs = []
        for log in logs:
            if self.filter_level and log['level'] != self.filter_level:
                continue
            if self.filter_plugin and not log['name'].startswith(self.filter_plugin):
                continue
            filtered_logs.append(log)

        # 按时间倒序排列，最新的日志在前
        return filtered_logs[::-1]

    def _parse_log_line(self, line: str) -> dict[str, str] | None:
        """解析日志行"""
        # 日志格式：2025-12-20 14:30:45 [INFO] [FastX] This is a log message
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] \[(.*?)\] (.*)'
        match = re.match(pattern, line)
        if match:
            return {
                'time': match.group(1),
                'level': match.group(2),
                'name': match.group(3),
                'message': match.group(4)
            }
        return None

    def _display_logs(self, logs: list[dict[str, str]]):
        """显示日志记录"""
        # 计算列宽 - 使用更大的宽度
        time_width = 20
        level_width = 8
        name_width = 25  # 增加来源列宽度
        # 消息列使用剩余宽度
        message_width = self.panel_width - time_width - level_width - name_width - 10

        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
            border_style="blue",
            show_lines=False,  # 移除行间线条
            collapse_padding=True,  # 减少内边距
            pad_edge=False,  # 移除边缘填充
            padding=(0, 1)  # 最小内边距
        )

        table.add_column("时间", width=time_width, style="cyan", overflow="fold")
        table.add_column("等级", width=level_width, overflow="fold")
        table.add_column("来源", width=name_width, style="yellow", overflow="fold")
        table.add_column("消息", width=message_width, style="white", overflow="fold")

        for log in logs:
            # 根据日志等级设置样式
            level_styles = {
                "DEBUG": ("DEBUG", "dim blue"),
                "INFO": ("INFO", "green"),
                "WARNING": ("WARN", "yellow"),
                "ERROR": ("ERROR", "red"),
                "CRITICAL": ("CRIT", "bold red")
            }

            level_text, level_style = level_styles.get(log['level'], (log['level'], "white"))

            # 缩短来源名称
            name = log['name']
            if len(name) > name_width:
                name = name[:name_width - 3] + "..."

            # 显示完整消息，让表格自动换行
            message = log['message']

            table.add_row(
                log['time'],
                Text(level_text, style=level_style),
                name,
                message
            )

        self.console.print(table)

    def _show_pagination(self, total_pages: int):
        """显示分页信息"""
        if total_pages > 0:
            # 创建分页信息
            pagination_text = f"第 {self.current_page}/{total_pages} 页"
            if self.filter_level or self.filter_plugin:
                filter_info = []
                if self.filter_level:
                    filter_info.append(f"等级: {self.filter_level}")
                if self.filter_plugin:
                    filter_info.append(f"插件: {self.filter_plugin}")
                pagination_text += f" | 筛选: {' | '.join(filter_info)}"

            self.console.print()
            self.console.print(pagination_text, style="cyan bold", justify="center")

    def _get_navigation_choice(self) -> str:
        """获取导航选择"""
        if sys.platform == "win32":
            import msvcrt
            while True:
                key = msvcrt.getch()
                if key == b'\xe0':  # 方向键前缀
                    key = msvcrt.getch()
                    if key == b'K':  # 左箭头
                        return 'left'
                    elif key == b'M':  # 右箭头
                        return 'right'
                elif key == b'0':
                    return '0'
        else:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                while True:
                    key = sys.stdin.read(1)
                    if key == '0':
                        return '0'
                    elif key == '\x1b':  # ESC
                        sys.stdin.read(1)  # 跳过 [
                        direction = sys.stdin.read(1)
                        if direction == 'D':  # 左箭头
                            return 'left'
                        elif direction == 'C':  # 右箭头
                            return 'right'
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ''

    def _open_log_file(self):
        """打开日志文件"""
        if not os.path.exists(self.log_file):
            self._show_message(f"日志文件不存在: {self.log_file}", "red")
            return

        self.console.print()
        title_panel = Panel(
            Text("打开日志文件", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        file_info = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(1, 2)
        )
        file_info.add_column("", style="white")
        file_info.add_row(f"文件路径: {self.log_file}")

        file_panel = Panel(
            file_info,
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )

        self.console.print(file_panel)
        self.console.print()

        self.console.print("正在打开日志文件...", style="bold green")

        try:
            if sys.platform == "win32":
                os.startfile(self.log_file)
            elif sys.platform == "darwin":
                os.system(f"open {self.log_file}")
            else:
                os.system(f"xdg-open {self.log_file}")
            self._show_message("日志文件已打开", "green")
        except Exception as e:
            self._show_message(f"打开日志文件失败: {str(e)}", "red")

    def _set_display_size(self):
        """设置日志显示大小"""
        self.console.print()
        title_panel = Panel(
            Text("设置日志显示大小", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        # 说明信息
        info_table = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(1, 2)
        )
        info_table.add_column("", style="white")
        info_table.add_row(f"当前显示大小: {self.display_size} 条/页")
        info_table.add_row("请输入新的显示大小 (10-1000)")

        info_panel = Panel(
            info_table,
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )

        self.console.print(info_panel)
        self.console.print()

        self.console.print("请输入新的大小: ", style="white", end="")
        new_size = input().strip()

        try:
            size = int(new_size)
            if 10 <= size <= 1000:
                self.display_size = size
                self.config_manager.set_config("log_display_size", size)
                self._show_message(f"显示大小已设置为: {size}", "green")
            else:
                self._show_message("显示大小必须在 10-1000 之间", "red")
        except ValueError:
            self._show_message("无效的输入，请输入数字", "red")

    def _configure_filter(self):
        """配置日志筛选条件"""
        while True:
            self.console.clear()

            title_panel = Panel(
                Text("配置日志筛选条件", style="bold cyan"),
                box=box.SIMPLE,
                border_style="cyan",
                padding=(0, 0),
                width=self.panel_width
            )
            self.console.print(title_panel)
            self.console.print()

            # 创建筛选菜单表格
            filter_table = Table(
                show_header=False,
                box=box.SIMPLE,
                show_edge=True,
                width=self.panel_width - 2,
                padding=(0, 1)
            )
            filter_table.add_column("命令", style="bold cyan", width=8)
            filter_table.add_column("筛选设置", style="white", width=112)

            filter_table.add_row("1", "设置日志等级筛选")
            filter_table.add_row("2", "设置插件日志筛选")
            filter_table.add_row("3", "清除所有筛选条件")

            filter_panel = Panel(
                filter_table,
                subtitle="0: 返回",
                subtitle_align="left",
                border_style="blue",
                box=box.ROUNDED,
                padding=(0, 0),
                width=self.panel_width
            )

            self.console.print(filter_panel)

            # 当前筛选状态
            if self.filter_level or self.filter_plugin:
                status_table = Table(
                    show_header=False,
                    box=box.SIMPLE,
                    show_edge=True,
                    width=self.panel_width - 2,
                    padding=(1, 2)
                )
                status_table.add_column("当前筛选条件", style="yellow bold", width=self.panel_width - 6)

                status_info = []
                if self.filter_level:
                    status_info.append(f"等级: {self.filter_level}")
                if self.filter_plugin:
                    status_info.append(f"插件: {self.filter_plugin}")

                status_table.add_row(" | ".join(status_info))

                status_panel = Panel(
                    status_table,
                    border_style="yellow",
                    box=box.ROUNDED,
                    padding=(0, 0),
                    width=self.panel_width
                )

                self.console.print()
                self.console.print(status_panel)

            self.console.print()
            self.console.print("请输入命令编号: ", style="bold green", end="")
            choice = input().strip()

            if choice == '0':
                return
            elif choice == '1':
                self._set_level_filter()
            elif choice == '2':
                self._set_plugin_filter()
            elif choice == '3':
                self._clear_filters()

    def _set_level_filter(self):
        """设置日志等级筛选"""
        self.console.print()
        title_panel = Panel(
            Text("设置日志等级筛选", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        available_levels = get_available_log_levels()
        available_levels.append("全部")

        # 创建等级选择表格
        level_table = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(0, 1)
        )
        level_table.add_column("编号", style="bold cyan", width=8)
        level_table.add_column("等级", style="white", width=25)
        level_table.add_column("说明", style="dim", width=87)

        level_info = {
            "DEBUG": "调试信息",
            "INFO": "一般信息",
            "WARNING": "警告信息",
            "ERROR": "错误信息",
            "CRITICAL": "严重错误",
            "全部": "清除等级筛选"
        }

        for i, level in enumerate(available_levels, 1):
            level_table.add_row(str(i), level, level_info.get(level, ""))

        level_panel = Panel(
            level_table,
            subtitle="0: 返回",
            subtitle_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )

        self.console.print(level_panel)
        self.console.print()

        self.console.print("请选择等级编号: ", style="bold green", end="")
        choice = input().strip()

        if choice == '0':
            return

        try:
            index = int(choice) - 1
            if 0 <= index < len(available_levels):
                selected_level = available_levels[index]
                self.filter_level = selected_level if selected_level != "全部" else None
                status = selected_level if selected_level != "全部" else "全部(清除筛选)"
                self._show_message(f"等级筛选已设置为: {status}", "green")
            else:
                self._show_message("无效的选择", "red")
        except ValueError:
            self._show_message("无效的输入", "red")

    def _set_plugin_filter(self):
        """设置插件日志筛选"""
        self.console.print()
        title_panel = Panel(
            Text("设置插件日志筛选", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)

        # 输入提示
        input_table = Table(
            show_header=False,
            box=box.SIMPLE,
            show_edge=True,
            width=self.panel_width - 2,
            padding=(1, 2)
        )
        input_table.add_column("说明", style="white", width=self.panel_width - 6)
        input_table.add_row("输入插件名称 (留空表示清除插件筛选)")

        input_panel = Panel(
            input_table,
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 0),
            width=self.panel_width
        )

        self.console.print(input_panel)
        self.console.print()

        self.console.print("插件名称: ", style="white", end="")
        plugin_name = input().strip()

        if plugin_name:
            self.filter_plugin = plugin_name
            self._show_message(f"插件筛选已设置为: {plugin_name}", "green")
        else:
            self.filter_plugin = None
            self._show_message("插件筛选已清除", "green")

    def _clear_filters(self):
        """清除所有筛选条件"""
        self.filter_level = None
        self.filter_plugin = None
        self._show_message("所有筛选条件已清除", "green")

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
