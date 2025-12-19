#!/usr/bin/env python3
"""
FastX-Tui 帮助功能模块
"""
from typing import Dict, Any
from rich.console import Console

class HelpFeature:
    """帮助功能实现"""
    
    def __init__(self, console: Console):
        self.console = console
    
    def show_help(self):
        """显示帮助信息"""
        self.console.print("=" * 70, style="cyan")
        self.console.print("FastX-Tui 帮助信息".center(70), style="cyan bold")
        self.console.print("=" * 70, style="cyan")
        
        # 基本信息
        self.console.print("\n[bold]基本信息[/bold]")
        self.console.print("├─ FastX-Tui: 一个功能强大的终端工具集")
        self.console.print("├─ 版本: v0.1.0")
        self.console.print("└─ 作者: FastXTeam")
        
        # 快捷键
        self.console.print("\n[bold]常用快捷键[/bold]")
        shortcuts = [
            ("q", "退出程序"),
            ("h", "显示帮助信息"),
            ("c", "清除屏幕"),
            ("s", "搜索功能"),
            ("0", "返回上一级菜单")
        ]
        
        for key, desc in shortcuts:
            self.console.print(f"├─ [yellow]{key}[/yellow]: {desc}")
        
        # 菜单导航
        self.console.print("\n[bold]菜单导航[/bold]")
        self.console.print("├─ 输入数字选择菜单项")
        self.console.print("├─ 在非主菜单中输入0返回上一级")
        self.console.print("└─ 按回车键继续操作")
        
        # 功能说明
        self.console.print("\n[bold]主要功能[/bold]")
        features = [
            ("系统工具", "查看系统信息、网络信息、进程列表等"),
            ("文件工具", "管理文件系统、查看目录内容、搜索文件等"),
            ("Python工具", "Python环境信息、包管理、模块导入检查等"),
            ("配置管理", "查看和修改应用配置"),
            ("插件管理", "安装、卸载和管理插件")
        ]
        
        for name, desc in features:
            self.console.print(f"├─ [green]{name}[/green]: {desc}")
        
        self.console.print("\n" + "─" * 70, style="dim")
        self.console.print("[yellow]按回车键继续...[/yellow]")
        input()
