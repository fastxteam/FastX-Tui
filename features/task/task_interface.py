#!/usr/bin/env python3
"""
任务管理界面模块 - 提供任务列表和结果查看功能
"""
import time
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED, SIMPLE
from core.task_manager import TaskStatus


class TaskInterface:
    """任务管理界面"""
    
    def __init__(self, console, task_manager, config_manager):
        self.console = console
        self.task_manager = task_manager
        self.config_manager = config_manager
    
    def show_task_list(self):
        """显示任务列表"""
        while True:
            # 清屏
            self._clear_screen()
            
            # 获取所有任务
            tasks = self.task_manager.get_all_tasks()
            
            # 创建任务统计信息
            task_count = self.task_manager.get_task_count()
            
            # 创建统计信息Table
            stat_table = Table(
                box=SIMPLE,
                show_header=False,
                expand=True,
                padding=(0, 2)
            )
            stat_table.add_column(justify="left")
            stat_table.add_column(justify="left")
            stat_table.add_column(justify="left")
            stat_table.add_column(justify="left")
            stat_table.add_column(justify="left")
            
            stat_table.add_row(
                f"[bold]总任务:[/bold] [cyan]{task_count['total']}[/cyan]",
                f"[bold]等待中:[/bold] [yellow]{task_count['pending']}[/yellow]",
                f"[bold]运行中:[/bold] [green]{task_count['running']}[/green]",
                f"[bold]已完成:[/bold] [blue]{task_count['completed']}[/blue]",
                f"[bold]已失败:[/bold] [red]{task_count['failed']}[/red]"
            )
            
            # 显示统计信息
            self.console.print(Panel(
                stat_table,
                title="任务统计",
                title_align="left",
                border_style="cyan",
                box=ROUNDED,
                padding=(0, 2)
            ))
            
            # 创建任务列表Table
            task_table = Table(
                box=SIMPLE,
                show_header=True,
                header_style="bold white",
            )
            
            task_table.add_column("编号", style="cyan bold", justify="center")
            task_table.add_column("名称", style="white")
            task_table.add_column("状态", style="green")
            task_table.add_column("类型", style="yellow")
            task_table.add_column("创建时间", style="magenta")
            task_table.add_column("执行时间", style="blue")
            
            # 状态样式映射
            status_styles = {
                TaskStatus.PENDING: "yellow",
                TaskStatus.RUNNING: "green",
                TaskStatus.COMPLETED: "blue",
                TaskStatus.FAILED: "red",
                TaskStatus.CANCELLED: "dim"
            }
            
            # 状态显示文本映射
            status_texts = {
                TaskStatus.PENDING: "等待执行",
                TaskStatus.RUNNING: "正在执行",
                TaskStatus.COMPLETED: "执行完成",
                TaskStatus.FAILED: "执行失败",
                TaskStatus.CANCELLED: "已取消"
            }
            
            if not tasks:
                # 如果没有任务，显示提示
                self.console.print(Panel(
                    Text("当前没有任务", style="yellow bold"),
                    title="任务列表",
                    title_align="left",
                    border_style="cyan",
                    box=ROUNDED,
                    padding=(2, 2)
                ))
            else:
                # 添加任务到表格
                for i, task in enumerate(tasks, 1):
                    # 格式化时间
                    create_time = time.strftime("%H:%M:%S", time.localtime()) if task.start_time else "-"
                    exec_time = f"{task.execution_time:.2f}s" if task.execution_time else "-"
                    
                    # 获取状态样式和文本
                    status_style = status_styles.get(task.status, "white")
                    status_text = status_texts.get(task.status, "未知")
                    
                    # 添加未查看标记
                    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and not task.is_viewed:
                        status_text += " [UN-VIEW]"
                    
                    task_table.add_row(
                        f"[bold]{i}[/bold]",
                        task.name,
                        f"[{status_style}]{status_text}[/{status_style}]",
                        task.command_type,
                        create_time,
                        exec_time
                    )
                
                # 显示任务列表
                self.console.print(Panel(
                    task_table,
                    title="任务列表",
                    title_align="left",
                    border_style="cyan",
                    box=ROUNDED,
                    padding=(0, 2)
                ))
            
            # 显示操作提示
            actions = [
                "输入任务编号查看详情",
                "c - 清空已完成任务",
                "r - 刷新列表",
                "q - 返回"
            ]
            
            self.console.print("\n" + "─" * 125, style="dim")
            self.console.print("操作提示: " + " | ".join(actions), style="dim bold")
            
            # 获取用户选择
            from rich.prompt import Prompt
            
            available_choices = [str(i) for i in range(1, len(tasks) + 1)] + ['c', 'r', 'q']
            
            choice = Prompt.ask(
                f"\n[bold cyan]请选择[/bold cyan]",
                choices=available_choices,
                show_choices=False
            ).lower()
            
            # 处理选择
            if choice == 'q':
                # 返回
                self._clear_screen()
                break
            elif choice == 'r':
                # 刷新列表，继续循环
                continue
            elif choice == 'c':
                # 清空已完成任务
                self.task_manager.clear_completed_tasks()
                self.console.print("\n[green]✅ 已清空所有已完成任务[/green]")
                input(f"\n按回车键继续...")
            else:
                # 查看任务详情
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(tasks):
                        self._show_task_result(tasks[idx])
                except ValueError:
                    self.console.print(f"[red]❌ 无效的输入[/red]")
                    input(f"\n按回车键继续...")
    
    def _show_task_result(self, task):
        """显示任务结果"""
        # 标记任务为已查看
        self.task_manager.mark_task_as_viewed(task.id)
        
        while True:
            # 清屏
            self._clear_screen()
            
            # 创建任务信息Table
            info_table = Table(
                box=SIMPLE,
                show_header=True,
                header_style="bold magenta",
                expand=True,
                padding=(0, 2)
            )
            info_table.add_column(header="属性", justify="left")
            info_table.add_column(header="值", justify="left")
            
            # 状态样式映射
            status_styles = {
                TaskStatus.PENDING: "yellow",
                TaskStatus.RUNNING: "green",
                TaskStatus.COMPLETED: "blue",
                TaskStatus.FAILED: "red",
                TaskStatus.CANCELLED: "dim"
            }
            
            # 状态显示文本映射
            status_texts = {
                TaskStatus.PENDING: "等待执行",
                TaskStatus.RUNNING: "正在执行",
                TaskStatus.COMPLETED: "执行完成",
                TaskStatus.FAILED: "执行失败",
                TaskStatus.CANCELLED: "已取消"
            }
            
            # 获取状态样式和文本
            status_style = status_styles.get(task.status, "white")
            status_text = status_texts.get(task.status, "未知")
            
            # 格式化时间
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(task.start_time)) if task.start_time else "-"
            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(task.end_time)) if task.end_time else "-"
            exec_time = f"{task.execution_time:.2f}秒" if task.execution_time else "-"
            
            # 添加任务信息
            info_table.add_row("任务ID", task.id[:8] + "...")
            info_table.add_row("任务名称", task.name)
            info_table.add_row("任务描述", task.description)
            info_table.add_row("命令类型", task.command_type)
            if task.command:
                info_table.add_row("命令", task.command)
            info_table.add_row("状态", f"[{status_style}]{status_text}[/{status_style}]")
            info_table.add_row("开始时间", start_time)
            info_table.add_row("结束时间", end_time)
            info_table.add_row("执行时间", exec_time)
            
            # 显示任务信息
            self.console.print(Panel(
                info_table,
                title=f"> {task.name} | 任务详情",
                title_align="center",
                border_style="cyan",
                box=ROUNDED,
                padding=(1, 2)
            ))
            
            # 显示任务结果
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                result_content = task.result if task.status == TaskStatus.COMPLETED else task.error
                result_style = "green" if task.status == TaskStatus.COMPLETED else "red"
                
                self.console.print(Panel(
                    result_content,
                    title="任务结果",
                    title_align="left",
                    border_style=result_style,
                    box=ROUNDED,
                    padding=(1, 2)
                ))
            
            # 显示操作提示
            actions = [
                "r - 刷新状态",
                "q - 返回任务列表"
            ]
            
            self.console.print("\n" + "─" * 125, style="dim")
            self.console.print("操作提示: " + " | ".join(actions), style="dim bold")
            
            # 获取用户选择
            from rich.prompt import Prompt
            
            choice = Prompt.ask(
                f"\n[bold cyan]请选择[/bold cyan]",
                choices=['r', 'q'],
                show_choices=False
            ).lower()
            
            # 处理选择
            if choice == 'q':
                # 返回任务列表
                break
            elif choice == 'r':
                # 刷新状态，重新获取任务
                task = self.task_manager.get_task(task.id)
                if not task:
                    self.console.print("\n[red]❌ 任务已不存在[/red]")
                    input(f"\n按回车键继续...")
                    break
    
    def _clear_screen(self):
        """清屏操作"""
        import os
        import sys
        os.system('cls' if sys.platform == 'win32' else 'clear')
