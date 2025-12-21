#!/usr/bin/env python3
"""
日志管理功能模块
"""
import os
import sys
import re
from typing import List, Dict, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.text import Text
from core.logger import (
    set_log_level,
    get_current_log_level,
    get_available_log_levels
)
from config.config_manager import ConfigManager

class LogManager:
    """日志管理器"""
    
    def __init__(self, console: Console, config_manager: ConfigManager):
        self.console = console
        self.config_manager = config_manager
        # 使用绝对路径确保日志文件路径正确
        self.log_file = os.path.join(os.getcwd(), "logs", "fastx-tui.log")
        self.page_size = 500
        self.current_page = 1
        self.filter_level = None
        self.filter_plugin = None
        self.display_size = self.page_size
    
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
        self.console.print("=" * 80)
        self.console.print("📊 日志管理中心".center(80), style="bold cyan")
        self.console.print("=" * 80)
        self.console.print()
        
        menu_items = [
            "1. 查看当前日志等级",
            "2. 设置日志等级",
            "3. 查看日志记录",
            "4. 打开日志文件",
            "5. 设置日志显示大小",
            "6. 配置日志筛选条件",
            "0. 返回主菜单",
            "q. 退出"
        ]
        
        for item in menu_items:
            self.console.print(item, style="white")
        
        self.console.print()
        self.console.print("🔍 当前日志等级: {}".format(get_current_log_level()), style="bold yellow")
        self.console.print("📄 日志文件: {}".format(self.log_file), style="bold yellow")
        self.console.print("📋 显示大小: {} 条/页".format(self.display_size), style="bold yellow")
        
        if self.filter_level:
            self.console.print("⚙️  等级筛选: {}".format(self.filter_level), style="bold yellow")
        if self.filter_plugin:
            self.console.print("🧩 插件筛选: {}".format(self.filter_plugin), style="bold yellow")
        
        self.console.print()
    
    def _get_user_choice(self) -> str:
        """获取用户选择"""
        self.console.print("请输入您的选择 (1-6, 0, q): ", style="bold green", end="")
        
        # 使用类似app_manager中的无缓冲输入
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
        self.console.print("\n" + "-" * 80)
        self.console.print("📊 当前日志配置".center(80), style="bold green")
        self.console.print("-" * 80)
        self.console.print(f"当前日志等级: {get_current_log_level()}", style="white")
        self.console.print(f"可用日志等级: {', '.join(get_available_log_levels())}", style="white")
    
    def _set_log_level(self):
        """设置日志等级"""
        self.console.print("\n" + "-" * 80)
        self.console.print("⚙️ 设置日志等级".center(80), style="bold green")
        self.console.print("-" * 80)
        
        available_levels = get_available_log_levels()
        for i, level in enumerate(available_levels, 1):
            self.console.print(f"{i}. {level}", style="white")
        
        self.console.print("0. 返回", style="white")
        
        while True:
            choice = self._get_user_choice()
            if choice == '0':
                return
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(available_levels):
                    selected_level = available_levels[index]
                    set_log_level(selected_level)
                    self.config_manager.set_config("log_level", selected_level)
                    self.console.print(f"\n✅ 日志等级已设置为: {selected_level}", style="bold green")
                    break
                else:
                    self.console.print("❌ 无效的选择，请重试", style="bold red")
            except ValueError:
                self.console.print("❌ 无效的输入，请重试", style="bold red")
    
    def _view_log_records(self):
        """查看日志记录"""
        if not os.path.exists(self.log_file):
            self.console.print(f"❌ 日志文件不存在: {self.log_file}", style="bold red")
            return
        
        self.current_page = 1
        while True:
            self.console.clear()
            self.console.print("📄 日志记录查看".center(80), style="bold cyan")
            self.console.print("-" * 80)
            
            logs = self._read_logs()
            total_pages = (len(logs) + self.display_size - 1) // self.display_size
            
            if total_pages == 0:
                self.console.print("📭 没有日志记录", style="dim")
            else:
                start = (self.current_page - 1) * self.display_size
                end = start + self.display_size
                page_logs = logs[start:end]
                
                self._display_logs(page_logs)
                self._show_pagination(total_pages)
            
            self.console.print()
            self.console.print("快捷键: ← 上一页 | → 下一页 | 0 返回", style="dim")
            
            choice = self._get_navigation_choice()
            if choice == 'left':
                if self.current_page > 1:
                    self.current_page -= 1
            elif choice == 'right':
                if self.current_page < total_pages:
                    self.current_page += 1
            elif choice == '0':
                break
    
    def _read_logs(self) -> List[Dict[str, str]]:
        """读取日志文件"""
        logs = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    log_entry = self._parse_log_line(line.strip())
                    if log_entry:
                        logs.append(log_entry)
        except Exception as e:
            self.console.print(f"❌ 读取日志失败: {str(e)}", style="bold red")
        
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
    
    def _parse_log_line(self, line: str) -> Optional[Dict[str, str]]:
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
    
    def _display_logs(self, logs: List[Dict[str, str]]):
        """显示日志记录"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("时间", width=20, style="cyan")
        table.add_column("等级", width=10, style="green")
        table.add_column("来源", width=20, style="yellow")
        table.add_column("消息", style="white")
        
        for log in logs:
            # 根据日志等级设置样式
            level_style = {
                "DEBUG": "dim blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold red"
            }.get(log['level'], "white")
            
            # 插件日志特殊标识
            name_style = "bold cyan" if "." in log['name'] else "yellow"
            
            table.add_row(
                log['time'],
                log['level'],
                log['name'],
                log['message'],
                style=level_style
            )
        
        self.console.print(table)
    
    def _show_pagination(self, total_pages: int):
        """显示分页信息"""
        pagination = f"第 {self.current_page} / {total_pages} 页"
        self.console.print(pagination.center(80), style="bold blue")
    
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
            self.console.print(f"❌ 日志文件不存在: {self.log_file}", style="bold red")
            return
        
        self.console.print(f"\n📂 正在打开日志文件: {self.log_file}", style="bold green")
        
        try:
            if sys.platform == "win32":
                os.startfile(self.log_file)
            elif sys.platform == "darwin":
                os.system(f"open {self.log_file}")
            else:
                os.system(f"xdg-open {self.log_file}")
            self.console.print("✅ 日志文件已打开", style="bold green")
        except Exception as e:
            self.console.print(f"❌ 打开日志文件失败: {str(e)}", style="bold red")
    
    def _set_display_size(self):
        """设置日志显示大小"""
        self.console.print("\n" + "-" * 80)
        self.console.print("⚙️ 设置日志显示大小".center(80), style="bold green")
        self.console.print("-" * 80)
        
        self.console.print("当前显示大小: {} 条/页".format(self.display_size), style="white")
        self.console.print("请输入新的显示大小 (10-1000): ", style="white", end="")
        
        new_size = input().strip()
        try:
            size = int(new_size)
            if 10 <= size <= 1000:
                self.display_size = size
                self.config_manager.set_config("log_display_size", size)
                self.console.print(f"✅ 显示大小已设置为: {size}", style="bold green")
            else:
                self.console.print("❌ 显示大小必须在 10-1000 之间", style="bold red")
        except ValueError:
            self.console.print("❌ 无效的输入，请输入数字", style="bold red")
    
    def _configure_filter(self):
        """配置日志筛选条件"""
        while True:
            self.console.clear()
            self.console.print("⚙️  配置日志筛选条件".center(80), style="bold cyan")
            self.console.print("-" * 80)
            
            filter_menu = [
                "1. 设置日志等级筛选",
                "2. 设置插件日志筛选",
                "3. 清除所有筛选条件",
                "0. 返回"
            ]
            
            for item in filter_menu:
                self.console.print(item, style="white")
            
            choice = self._get_user_choice()
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
        self.console.print("\n" + "-" * 80)
        self.console.print("🔍 设置日志等级筛选".center(80), style="bold green")
        self.console.print("-" * 80)
        
        available_levels = get_available_log_levels()
        available_levels.append("全部")
        
        for i, level in enumerate(available_levels, 1):
            self.console.print(f"{i}. {level}", style="white")
        
        self.console.print("0. 返回", style="white")
        
        while True:
            choice = self._get_user_choice()
            if choice == '0':
                return
            try:
                index = int(choice) - 1
                if 0 <= index < len(available_levels):
                    selected_level = available_levels[index]
                    self.filter_level = selected_level if selected_level != "全部" else None
                    self.console.print(f"✅ 等级筛选已设置为: {selected_level}", style="bold green")
                    break
                else:
                    self.console.print("❌ 无效的选择，请重试", style="bold red")
            except ValueError:
                self.console.print("❌ 无效的输入，请重试", style="bold red")
    
    def _set_plugin_filter(self):
        """设置插件日志筛选"""
        self.console.print("\n" + "-" * 80)
        self.console.print("🔍 设置插件日志筛选".center(80), style="bold green")
        self.console.print("-" * 80)
        
        self.console.print("输入插件名称（留空表示清除插件筛选）: ", style="white", end="")
        plugin_name = input().strip()
        
        if plugin_name:
            self.filter_plugin = plugin_name
            self.console.print(f"✅ 插件筛选已设置为: {plugin_name}", style="bold green")
        else:
            self.filter_plugin = None
            self.console.print("✅ 插件筛选已清除", style="bold green")
    
    def _clear_filters(self):
        """清除所有筛选条件"""
        self.filter_level = None
        self.filter_plugin = None
        self.console.print("✅ 所有筛选条件已清除", style="bold green")
    
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
