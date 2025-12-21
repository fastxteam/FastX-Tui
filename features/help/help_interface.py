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
        # 动态获取版本信息
        try:
            from core.version import FULL_VERSION
            version = FULL_VERSION
        except ImportError:
            version = "v0.1.0"
        
        basic_info = [
            ("名称", "FastX-Tui"),
            ("版本", version),
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
            ("m", "配置管理"),
            ("p", "插件管理"),
            ("u", "检查更新"),
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
        
        # 插件开发
        content += "插件开发\n"
        content += "─" * 40 + "\n"
        content += "插件开发接口说明:\n"
        content += "1. 实现Plugin类，继承自core.plugin_manager.Plugin\n"
        content += "2. 实现get_info()方法返回插件信息\n"
        content += "3. 实现initialize()和cleanup()方法\n"
        content += "4. 在register()方法中注册菜单和命令\n"
        content += "5. 示例: plugins/FastX-Tui-Plugin-Example/fastx_plugin.py\n"
        content += "\n"

        
        # 主要功能
        content += "主要功能\n"
        content += "─" * 40 + "\n"
        features = [
            ("平台工具", "平台提供的通用工具集，包含系统工具、文件工具、Python工具"),
            ("系统工具", "查看系统信息、网络信息、进程列表、磁盘空间、系统运行时间"),
            ("文件工具", "目录列表、文件树、文件搜索"),
            ("Python工具", "Python环境信息、已安装包列表、检查导入"),
            ("配置管理", "查看和修改应用配置"),
            ("插件管理", "安装、卸载和管理插件"),
            ("日志管理", "查看和管理应用日志")
        ]
        
        for name, desc in features:
            content += f"[green]{name}[/green]: {desc}\n"
        
        return content