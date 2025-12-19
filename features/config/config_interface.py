#!/usr/bin/env python3
"""
FastX-Tui 配置界面管理模块
"""
import os
import sys
from typing import Optional

from rich.console import Console
from rich.table import Table

from config.config_manager import ConfigManager


class ConfigInterface:
    """配置界面管理器"""
    
    def __init__(self, console: Console, config_manager: ConfigManager):
        self.console = console
        self.config_manager = config_manager
    
    def show_config_interface(self, view_manager=None) -> bool:
        """显示配置界面"""
        while True:
            self.console.clear()
            self._show_config_menu()
            choice = self._get_user_choice()
            if choice == 'b':
                return True
            elif choice == 'q':
                return False
            self._handle_choice(choice, view_manager)
    
    def _show_config_menu(self):
        """显示配置管理菜单"""
        self.console.print("=" * 80)
        self.console.print("⚙️  配置管理中心".center(80), style="bold cyan")
        self.console.print("=" * 80)
        self.console.print()
        
        menu_items = [
            "1. 查看当前配置",
            "2. 更换主题",
            "3. 高级设置",
            "4. 重置配置",
            "5. 导出配置",
            "6. 导入配置",
            "b. 返回主菜单",
            "q. 退出"
        ]
        
        for item in menu_items:
            self.console.print(item, style="white")
        
        self.console.print()
        self.console.print("📋 当前主题: {}".format(self.config_manager.get_config("theme", "default")), style="bold yellow")
        self.console.print("🌐 语言: {}".format(self.config_manager.get_config("language", "zh_CN")), style="bold yellow")
        self.console.print("🔄 自动检查更新: {}".format("✅ 已开启" if self.config_manager.get_config("auto_check_updates", True) else "❌ 已关闭"), style="bold yellow")
        self.console.print()
    
    def _get_user_choice(self) -> str:
        """获取用户选择"""
        self.console.print("请输入您的选择 (1-6, b, q): ", style="bold green", end="")
        
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
            self._reset_config()
        elif choice == '5':
            self._export_config()
        elif choice == '6':
            self._import_config()
        
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
    
    def _show_current_config(self):
        """显示当前配置"""
        self.console.print("\n" + "-" * 80)
        self.console.print("📊 当前配置".center(80), style="bold green")
        self.console.print("-" * 80)
        
        config_summary = self.config_manager.show_config_summary()
        self.console.print(config_summary)
    
    def _change_theme(self):
        """修改主题"""
        self.console.print("\n" + "-" * 80)
        self.console.print("🎨 更换主题".center(80), style="bold green")
        self.console.print("-" * 80)
        
        themes = ["default", "dark", "light", "blue", "green"]
        
        for i, theme in enumerate(themes, 1):
            self.console.print(f"{i}. {theme}", style="white")
        
        self.console.print("b. 返回", style="white")
        
        while True:
            choice = self._get_user_choice()
            if choice == 'b':
                return
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(themes):
                    selected_theme = themes[index]
                    self.config_manager.set_config("theme", selected_theme)
                    self.console.print(f"\n✅ 主题已切换为: {selected_theme}", style="bold green")
                    break
                else:
                    self.console.print("❌ 无效的选择，请重试", style="bold red")
            except ValueError:
                self.console.print("❌ 无效的输入，请重试", style="bold red")
    
    def _show_advanced_settings(self):
        """显示高级设置界面"""
        while True:
            self.console.clear()
            self.console.print("⚙️  高级设置".center(80), style="bold cyan")
            self.console.print("-" * 80)
            
            # 获取当前设置
            show_welcome = self.config_manager.get_config("show_welcome_page", True)
            auto_check_updates = self.config_manager.get_config("auto_check_updates", True)
            banner_style = self.config_manager.get_config("banner_style", "default")
            
            # 显示高级设置选项
            self.console.print("📋 高级设置:")
            self.console.print(f"1. 显示欢迎页面: {'✅' if show_welcome else '❌'}")
            self.console.print(f"2. 自动检查更新: {'✅' if auto_check_updates else '❌'}")
            self.console.print(f"3. 横幅样式: {banner_style}")
            self.console.print()
            self.console.print("b. 返回")
            
            choice = self._get_user_choice()
            
            if choice == 'b':
                break
            elif choice == '1':
                # 切换显示欢迎页面设置
                new_value = not show_welcome
                self.config_manager.set_config("show_welcome_page", new_value)
                status = "已启用" if new_value else "已禁用"
                self.console.print(f"\n✅ 显示欢迎页面: {status}", style="bold green")
                self.console.print("按任意键继续...", style="dim")
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
            elif choice == '2':
                # 切换自动检查更新设置
                new_value = not auto_check_updates
                self.config_manager.set_config("auto_check_updates", new_value)
                status = "已启用" if new_value else "已禁用"
                self.console.print(f"\n✅ 自动检查更新: {status}", style="bold green")
                self.console.print("按任意键继续...", style="dim")
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
            elif choice == '3':
                # 切换横幅样式
                new_style = "gradient" if banner_style == "default" else "default"
                self.config_manager.set_config("banner_style", new_style)
                self.console.print(f"\n✅ 横幅样式已设置为: {new_style}", style="bold green")
                self.console.print("按任意键继续...", style="dim")
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
            else:
                self.console.print("❌ 无效的选择", style="bold red")
                self.console.print("按任意键继续...", style="dim")
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
    
    def _reset_config(self):
        """重置配置"""
        self.console.print("\n" + "-" * 80)
        self.console.print("🔄 重置配置".center(80), style="bold green")
        self.console.print("-" * 80)
        
        self.console.print("⚠️  警告: 这将重置所有配置到默认值！", style="bold red")
        self.console.print()
        
        # 使用类似app_manager中的无缓冲输入
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
            self.console.print(f"\n✅ 配置已重置为默认值", style="bold green")
        else:
            self.console.print(f"\n❌ 重置已取消", style="bold yellow")
    
    def _export_config(self):
        """导出配置"""
        self.console.print("\n" + "-" * 80)
        self.console.print("📤 导出配置".center(80), style="bold green")
        self.console.print("-" * 80)
        
        self.console.print("请输入导出文件名 (默认: fastx_config.json): ", style="white", end="")
        filename = input().strip()
        
        if not filename:
            filename = "fastx_config.json"
        
        if self.config_manager.export_config(filename):
            self.console.print(f"\n✅ 配置已成功导出到: {os.path.abspath(filename)}", style="bold green")
        else:
            self.console.print(f"\n❌ 配置导出失败", style="bold red")
    
    def _import_config(self):
        """导入配置"""
        self.console.print("\n" + "-" * 80)
        self.console.print("📥 导入配置".center(80), style="bold green")
        self.console.print("-" * 80)
        
        self.console.print("请输入导入文件名: ", style="white", end="")
        filename = input().strip()
        
        if filename:
            if os.path.exists(filename):
                if self.config_manager.import_config(filename):
                    self.console.print(f"\n✅ 配置已成功导入", style="bold green")
                else:
                    self.console.print(f"\n❌ 配置导入失败", style="bold red")
            else:
                self.console.print(f"\n❌ 文件不存在: {filename}", style="bold red")
        else:
            self.console.print(f"\n❌ 文件名不能为空", style="bold red")
