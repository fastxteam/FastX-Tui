#!/usr/bin/env python3
"""
FastX-Tui 启动流管理器
"""
import sys
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from datetime import datetime
import time
import random
from typing import List, Dict, Any

class StartupManager:
    """启动流管理器"""
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        
        # 分割布局：日志区 + 状态栏
        self.layout.split(
            Layout(name="logs", ratio=5),  # 日志区域
            Layout(name="status", size=3)  # 状态栏
        )
        
        # 初始化日志
        self.log_content = Text()
        self.layout["logs"].update(
            Panel(
                self.log_content,
                title="[bold]系统日志[/bold]",
                border_style="green",
                padding=(1, 1)
            )
        )
        
        # 初始化状态栏
        self.update_status_bar()
        
        # 启动阶段定义
        self.stages = [
            ("初始化应用管理器", "INFO"),
            ("加载配置文件", "INFO"),
            ("初始化菜单系统", "INFO"),
            ("初始化视图管理器", "INFO"),
            ("初始化网络工具", "INFO"),
            ("开始加载插件", "INFO"),
            ("注册系统路由", "INFO"),
            ("注册插件路由", "INFO"),
            ("检查应用更新", "INFO"),
            ("启动完成", "SUCCESS")
        ]
        
        self.start_time = datetime.now()
        self.errors = 0
        self.warnings = 0
    
    def _create_status_bar(self,
                           status="准备中",
                           progress=0,
                           errors=0,
                           warnings=0):
        """创建状态栏内容"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 创建进度条
        bar_length = 30
        filled = int(bar_length * progress / 100)
        progress_bar = "█" * filled + "░" * (bar_length - filled)
        
        status_text = Text()
        status_text.append("状态: ", style="bold")
        
        # 动态状态样式
        if status == "准备中":
            status_text.append(f"{status}", style="cyan")
        elif status == "运行中":
            status_text.append(f"{status}", style="green")
        elif status == "警告":
            status_text.append(f"{status}", style="yellow")
        elif status == "错误":
            status_text.append(f"{status}", style="red")
        elif status == "完成":
            status_text.append(f"{status}", style="bold green")
        else:
            status_text.append(f"{status}", style="white")
        
        status_text.append(" | ", style="dim")
        status_text.append("进度: ", style="bold")
        status_text.append(f"{progress_bar} {progress:3d}%", style="cyan")
        status_text.append(" | ", style="dim")
        status_text.append("任务: ", style="bold")
        status_text.append(f"{progress}", style="magenta")
        status_text.append(" | ", style="dim")
        status_text.append("错误: ", style="bold red")
        status_text.append(f"{errors}", style="red")
        status_text.append(" | ", style="dim")
        status_text.append("警告: ", style="bold yellow")
        status_text.append(f"{warnings}", style="yellow")
        status_text.append(" | ", style="dim")
        status_text.append(now, style="blue")
        
        return Panel(
            status_text,
            border_style="cyan",
            title="[bold]状态监控[/bold]",
            padding=(0, 1)
        )
    
    def update_status_bar(self, **kwargs):
        """更新状态栏"""
        self.layout["status"].update(self._create_status_bar(**kwargs))
    
    def add_log(self, message, level="INFO"):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # 根据日志级别设置样式
        if level == "INFO":
            style = "green"
            prefix = "ℹ"
        elif level == "WARNING":
            style = "yellow"
            prefix = "⚠"
            self.warnings += 1
        elif level == "ERROR":
            style = "red"
            prefix = "✗"
            self.errors += 1
        elif level == "SUCCESS":
            style = "bold green"
            prefix = "✓"
        else:
            style = "white"
            prefix = "·"
        
        # 添加新日志（显示最新的在最下面）
        log_line = Text()
        log_line.append(f"[{timestamp}] ", style="dim cyan")
        log_line.append(f"{prefix} ", style=style)
        log_line.append(f"{message}\n", style=style)
        
        self.log_content.append(log_line)
        
        # 限制日志行数，防止内存过大
        lines = str(self.log_content).split('\n')
        if len(lines) > 30:  # 保留最近30行
            self.log_content = Text("\n".join(lines[-30:]) + "\n")
        
        # 更新日志面板
        self.layout["logs"].update(
            Panel(
                self.log_content,
                title="[bold]系统日志[/bold]",
                border_style="green",
                padding=(1, 1)
            )
        )
    
    def _execute_stage(self, task_index: int, message: str, app_manager: Any):
        """执行具体的启动阶段任务"""
        if message == "初始化应用管理器":
            self.add_log("创建应用管理器实例...", "INFO")
        elif message == "加载配置文件":
            self.add_log(f"配置数据库: {app_manager.config_manager.db_path}", "INFO")
        elif message == "开始加载插件":
            # 实际初始化系统
            self.add_log("初始化系统组件...", "INFO")
            # 临时禁用欢迎信息显示，避免在启动流中打印
            original_show_welcome = app_manager.config_manager.get_config("show_welcome_page", True)
            app_manager.config_manager.set_config("show_welcome_page", False)
            app_manager._init_system()
            # 恢复原配置
            app_manager.config_manager.set_config("show_welcome_page", original_show_welcome)
            if app_manager.config_manager.get_config("plugin_auto_load", True):
                plugin_count = len(app_manager.plugin_manager.plugins)
                self.add_log(f"已加载 {plugin_count} 个插件", "SUCCESS")
            else:
                self.add_log("插件自动加载已禁用", "WARNING")
        elif message == "注册插件路由":
            # 注册所有路由
            self.add_log("注册所有路由...", "INFO")
            app_manager._register_routes()
            route_count = len(app_manager.view_manager.routes)
            self.add_log(f"共注册 {route_count} 个路由", "SUCCESS")
        elif message == "检查应用更新":
            if app_manager.config_manager.get_config("auto_check_updates", True):
                update_available, latest_version = app_manager.update_manager.check_for_updates()
                if update_available:
                    self.add_log(f"发现新版本: {latest_version}", "WARNING")
                else:
                    self.add_log("当前已是最新版本", "SUCCESS")
            else:
                self.add_log("自动检查更新已禁用", "WARNING")
    
    def _update_status(self, progress: int):
        """根据进度更新状态"""
        if progress < 30:
            self.status = "准备中"
        elif progress < 80:
            self.status = "运行中"
        elif progress < 95:
            self.status = "警告"
        else:
            self.status = "完成"
    
    def run_startup(self, app_manager: Any) -> bool:
        """运行启动流程"""
        success = True
        
        # 直接禁用loguru的控制台输出，避免在启动流中打印
        from loguru import logger
        
        def loguru_sink(message):
            """自定义loguru sink，将日志静默处理"""
            pass
        
        # 移除默认的控制台sink，添加静默sink
        logger.remove()
        logger.add(loguru_sink, level="INFO")
        
        try:
            # 实时更新状态栏和日志
            # 检查是否是首次启动，或者是否需要完整的启动动画
            # 这里可以根据配置或环境变量来决定
            full_animation = False  # 默认不显示完整动画，快速启动
            
            with Live(self.layout, refresh_per_second=10, screen=True):
                task_index = 0
                
                if full_animation:
                    # 完整动画模式，适合首次启动
                    for progress in range(1, 101):
                        time.sleep(0.05)  # 加快动画速度，减少到0.05秒
                        
                        # 根据进度触发日志
                        if task_index < len(self.stages) and progress >= (task_index + 1) * (100 // len(self.stages)):
                            message, level = self.stages[task_index]
                            self.add_log(message, level)
                            
                            # 执行实际的启动任务
                            self._execute_stage(task_index, message, app_manager)
                            task_index += 1
                        
                        # 更新状态
                        self._update_status(progress)
                        
                        # 更新状态栏
                        self.update_status_bar(
                            status=self.status,
                            progress=progress,
                            errors=self.errors,
                            warnings=self.warnings
                        )
                    
                    # 最后一条完成日志
                    self.add_log("所有启动阶段已完成！", "SUCCESS")
                    time.sleep(1)  # 减少结束延迟到1秒
                else:
                    # 快速启动模式，适合后续启动
                    # 直接执行所有实际的启动任务
                    for task_index, (message, level) in enumerate(self.stages):
                        self.add_log(message, level)
                        self._execute_stage(task_index, message, app_manager)
                    
                    # 快速显示进度条
                    for progress in range(1, 101, 5):  # 每5%更新一次
                        time.sleep(0.02)  # 极短延迟
                        self._update_status(progress)
                        self.update_status_bar(
                            status=self.status,
                            progress=progress,
                            errors=self.errors,
                            warnings=self.warnings
                        )
                    
                    # 最后一条完成日志
                    self.add_log("所有启动阶段已完成！", "SUCCESS")
                    time.sleep(0.5)  # 极短的结束延迟
        finally:
            # 恢复loguru默认配置
            logger.remove()
            # 重新添加控制台handler
            logger.add(
                sys.stderr,
                format="{time:YYYY-MM-DD HH:mm:ss} [{level}] [{name}] {message}",
                level="INFO",
                enqueue=True
            )
        
        return success