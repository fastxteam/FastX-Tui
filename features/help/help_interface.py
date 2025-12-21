#!/usr/bin/env python3
"""
FastX-Tui 帮助功能界面模块
"""
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED
from rich import box
from rich.columns import Columns

class HelpFeature:
    """帮助功能实现"""
    
    def __init__(self, console: Console):
        self.console = console
    
    def show_help(self):
        """显示帮助信息"""
        self.console.clear()
        
        # 创建主面板
        self.console.print(Panel(
            self._create_help_content(),
            title="FastX-Tui 帮助信息",
            title_align="center",
            subtitle="按回车键继续...",
            subtitle_align="center",
            border_style="cyan",
            box=ROUNDED,
            expand=False,
            padding=(1, 2)
        ))
        
        # 等待用户按回车继续
        input()
        self.console.clear()
    
    def _create_help_content(self) -> str:
        """创建帮助内容"""
        content = ""
        
        # 基本信息
        content += "基本信息\n"
        content += "─" * 40 + "\n"
        basic_info = [
            ("名称", "FastX-Tui"),
            ("版本", "v0.1.0"),
            ("作者", "FastXTeam"),
            ("描述", "一个功能强大的终端工具集")
        ]
        
        for key, value in basic_info:
            content += f"[bold]{key}:[/bold] {value}\n"
        
        content += "\n\n"
        
        # 常用快捷键
        content += "常用快捷键\n"
        content += "─" * 40 + "\n"
        shortcuts = [
            ("q", "退出程序"),
            ("h", "显示帮助信息"),
            ("c", "清除屏幕"),
            ("s", "搜索功能"),
            ("l", "日志管理"),
            ("0", "返回上一级菜单")
        ]
        
        for key, desc in shortcuts:
            content += f"[yellow]{key}[/yellow]: {desc}\n"
        
        content += "\n\n"
        
        # 菜单导航
        content += "菜单导航\n"
        content += "─" * 40 + "\n"
        navigation = [
            "输入数字选择菜单项",
            "在非主菜单中输入0返回上一级",
            "按回车键继续操作"
        ]
        
        for item in navigation:
            content += f"{item}\n"
        
        content += "\n\n"
        
        # 主要功能
        content += "主要功能\n"
        content += "─" * 40 + "\n"
        features = [
            ("系统工具", "查看系统信息、网络信息、进程列表等"),
            ("文件工具", "管理文件系统、查看目录内容、搜索文件等"),
            ("Python工具", "Python环境信息、包管理、模块导入检查等"),
            ("配置管理", "查看和修改应用配置"),
            ("插件管理", "安装、卸载和管理插件"),
            ("日志管理", "查看和管理应用日志")
        ]
        
        for name, desc in features:
            content += f"[green]{name}[/green]: {desc}\n"
        
        return content