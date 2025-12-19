#!/usr/bin/env python3
"""
FastX-Tui 配置界面管理模块
"""
import os
import json
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from config.config_manager import ConfigManager


class ConfigInterface:
    """配置界面管理器"""
    
    def __init__(self, console: Console, config_manager: ConfigManager):
        self.console = console
        self.config_manager = config_manager
    
    def show_config_interface(self):
        """显示配置界面"""
        while True:
            self.console.print("\n" + "=" * 70, style="cyan")
            self.console.print("配置管理".center(70), style="cyan bold")
            self.console.print("=" * 70 + "\n", style="cyan")
    
            # 显示配置选项
            options = [
                ("1", "查看当前配置", self._show_current_config),
                ("2", "更换主题", self._change_theme),
                ("3", "高级设置", self._show_advanced_settings),
                ("4", "重置配置", self._reset_config),
                ("5", "导出配置", self._export_config),
                ("6", "导入配置", self._import_config),
                ("b", "返回主菜单", None),
                ("q", "退出程序", None)
            ]
    
            for key, description, _ in options:
                self.console.print(f"  {key}. {description}")
    
            self.console.print("\n" + "─" * 70, style="dim")
            choice = Prompt.ask(f"[bold cyan]请选择[/bold cyan]")
    
            if choice == 'b':
                # 返回主菜单前清屏
                self.console.print("\n" + "─" * 70, style="dim")
                self.console.print(f"[yellow]返回主菜单...[/yellow]")
                return
            elif choice == 'q':
                from sys import exit
                self.console.print(f"\n[green]感谢使用 FastX-Tui[/green]")
                exit(0)
                return
    
            # 执行选择的操作
            for key, description, action in options:
                if choice == key and action:
                    action()
                    break
            else:
                self.console.print(f"[red]❌ 无效的选择[/red]")
                input(f"\n按回车键继续...")
    
    def _show_current_config(self):
        """显示当前配置"""
        config_summary = self.config_manager.show_config_summary()
        self.console.print(f"\n{config_summary}")
        input(f"\n按回车键继续...")
    
    def _change_theme(self):
        """修改主题"""
        themes = ["default", "dark", "light", "blue", "green"]
        
        self.console.print(f"\n🎨 可用主题:")
        for i, theme in enumerate(themes, 1):
            self.console.print(f"  {i}. {theme}")
        
        choice = Prompt.ask(f"\n[bold cyan]请选择主题 (1-{len(themes)})[/bold cyan]")
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(themes):
                self.config_manager.set_config("theme", themes[idx])
                self.console.print(f"\n✅ 主题已切换为: {themes[idx]}")
            else:
                self.console.print(f"[red]❌ 无效的选择: {choice}[/red]")
        except ValueError:
            self.console.print(f"[red]❌ 无效的输入: {choice}[/red]")
        
        input(f"\n按回车键继续...")
    
    def _show_advanced_settings(self):
        """显示高级设置界面"""
        while True:
            self.console.print("\n" + "=" * 70, style="cyan")
            self.console.print(f"⚙️  高级设置".center(70), style="cyan bold")
            self.console.print("=" * 70 + "\n", style="cyan")
            
            # 获取当前设置
            show_welcome = self.config_manager.get_config("show_welcome_page", True)
            auto_check_updates = self.config_manager.get_config("auto_check_updates", True)
            banner_style = self.config_manager.get_config("banner_style", "default")
            
            # 显示高级设置选项
            self.console.print(f"📋 高级设置:")
            self.console.print(f"1. 显示欢迎页面: {'✅' if show_welcome else '❌'}")
            self.console.print(f"2. 自动检查更新: {'✅' if auto_check_updates else '❌'}")
            self.console.print(f"3. 横幅样式: {banner_style}")
            self.console.print()
            self.console.print(f"b. 返回")
            self.console.print(f"q. 退出")
            
            self.console.print("\n" + "─" * 70, style="dim")
            choice = Prompt.ask(f"[bold cyan]请选择[/bold cyan]")
            
            if choice == 'b':
                break
            elif choice == 'q':
                from sys import exit
                self.console.print(f"\n[green]感谢使用 FastX-Tui[/green]")
                exit(0)
                return
            elif choice == '1':
                # 切换显示欢迎页面设置
                new_value = not show_welcome
                self.config_manager.set_config("show_welcome_page", new_value)
                status = "已启用" if new_value else "已禁用"
                self.console.print(f"\n✅ 显示欢迎页面: {status}")
                input(f"\n按回车键继续...")
            elif choice == '2':
                # 切换自动检查更新设置
                new_value = not auto_check_updates
                self.config_manager.set_config("auto_check_updates", new_value)
                status = "已启用" if new_value else "已禁用"
                self.console.print(f"\n✅ 自动检查更新: {status}")
                input(f"\n按回车键继续...")
            elif choice == '3':
                # 切换横幅样式
                new_style = "gradient" if banner_style == "default" else "default"
                self.config_manager.set_config("banner_style", new_style)
                self.console.print(f"\n✅ 横幅样式已设置为: {new_style}")
                input(f"\n按回车键继续...")
            else:
                self.console.print(f"[red]❌ 无效的选择[/red]")
                input(f"\n按回车键继续...")
    
    def _reset_config(self):
        """重置配置"""
        confirm = Prompt.ask(
            f"[bold red]确定要重置所有配置到默认值吗？[/bold red]",
            choices=["y", "n", "Y", "N"],
            default="n"
        )
        
        if confirm.lower() == 'y':
            self.config_manager.reset_to_defaults()
            self.console.print(f"\n✅ 配置已重置为默认值")
        else:
            self.console.print(f"\n❌ 重置已取消")
        
        input(f"\n按回车键继续...")
    
    def _export_config(self):
        """导出配置"""
        filename = Prompt.ask(
            f"[bold cyan]请输入导出文件名[/bold cyan]",
            default="fastx_config.json"
        )
        
        if self.config_manager.export_config(filename):
            self.console.print(f"\n✅ 配置已成功导出到: {filename}")
        else:
            self.console.print(f"\n❌ 配置导出失败")
        
        input(f"\n按回车键继续...")
    
    def _import_config(self):
        """导入配置"""
        filename = Prompt.ask(
            f"[bold cyan]请输入导入文件名[/bold cyan]",
            default="fastx_config.json"
        )
        
        if os.path.exists(filename):
            if self.config_manager.import_config(filename):
                self.console.print(f"\n✅ 配置已成功导入")
            else:
                self.console.print(f"\n❌ 配置导入失败")
        else:
            self.console.print(f"\n❌ 文件不存在: {filename}")
        
        input(f"\n按回车键继续...")


# 导出配置界面实例
config_interface = None

def get_config_interface(console: Optional[Console] = None, config_manager: Optional[ConfigManager] = None) -> ConfigInterface:
    """获取配置界面实例"""
    global config_interface
    if config_interface is None:
        if not console or not config_manager:
            raise ValueError("初始化时必须提供console和config_manager")
        config_interface = ConfigInterface(console, config_manager)
    return config_interface
