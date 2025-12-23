#!/usr/bin/env python3
"""
更新功能界面模块
"""
from typing import Dict, Optional, Tuple
from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm

from core.update_manager import UpdateManager
from core.logger import get_logger

logger = get_logger(__name__)


class UpdateInterface:
    """
    更新功能界面类，负责处理更新相关的UI渲染和用户交互
    """

    def __init__(self, update_manager: UpdateManager, console: Console):
        """
        初始化更新功能界面

        Args:
            update_manager: 更新管理器实例，提供底层核心逻辑
            console: Rich控制台实例，用于UI渲染
        """
        self.update_manager = update_manager
        self.console = console
        self.panel_width = 136  # 标准面板宽度

    def check_for_updates(self, force_check: bool = False) -> Tuple[bool, Optional[str]]:
        """
        检查版本更新（UI包装）

        Args:
            force_check: 是否强制检查，忽略缓存时间

        Returns:
            Tuple[bool, Optional[str]]: (是否有更新, 最新版本号)
        """
        return self.update_manager.check_version_update(force_check)

    def get_update_message(self) -> str:
        """
        获取更新提示消息

        Returns:
            str: 更新提示消息
        """
        return self.update_manager.get_update_message()

    def update_app(self) -> bool:
        """
        自动更新应用程序（UI包装）

        Returns:
            bool: 更新是否成功
        """
        if not self.update_manager.update_available or not self.update_manager.latest_version:
            logger.info("没有可用更新")
            self.console.print("[yellow]没有可用更新[/yellow]")
            return False

        logger.info(
            f"开始更新应用，当前版本: {self.update_manager.current_version}, 最新版本: {self.update_manager.latest_version}")
        self.console.print("[green]开始更新应用...[/green]")
        self.console.print(f"当前版本: {self.update_manager.current_version}")
        self.console.print(f"最新版本: {self.update_manager.latest_version}")

        return self.update_manager.update_app()

    def handle_update_command(self, args=None) -> bool:
        """
        处理更新命令，提供用户交互界面

        Args:
            args: 命令参数

        Returns:
            bool: 命令执行是否成功
        """
        self.console.clear()

        # 1. 显示标题面板
        title_panel = Panel(
            Text("📦: FastX-Tui 更新管理", style="bold cyan", justify="center"),
            box=box.SIMPLE,
            border_style="cyan",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 2. 显示当前版本信息
        self.console.print(f"当前版本: {self.update_manager.current_version}", style="bold white")
        self.console.print()

        # 3. 获取所有可用版本
        info_panel = Panel(
            Text("正在获取可用版本...", style="yellow", justify="center"),
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2),
            width=self.panel_width
        )
        self.console.print(info_panel)
        self.console.print()

        versions_result = self.update_manager.get_available_versions(per_page=10)

        if not versions_result['success']:
            error_panel = Panel(
                Text(f"获取可用版本失败: {versions_result['error']}", style="red", justify="center"),
                border_style="red",
                box=box.ROUNDED,
                padding=(1, 2),
                width=self.panel_width
            )
            self.console.print(error_panel)
            self._wait_for_keypress()
            return False

        # 4. 过滤出比当前版本更新的版本
        current_version = self.update_manager.current_version.lstrip('v')
        available_versions = []

        for release in versions_result['releases']:
            from core.network_tools import NetworkToolsPlugin
            if NetworkToolsPlugin()._compare_versions(current_version, release['version']):
                available_versions.append(release)

        if not available_versions:
            no_update_panel = Panel(
                Text("当前已是最新版本，无需更新", style="green", justify="center"),
                subtitle="按任意键返回...",
                subtitle_align="center",
                border_style="green",
                box=box.ROUNDED,
                padding=(1, 2),
                width=self.panel_width
            )
            self.console.print(no_update_panel)
            self._wait_for_keypress()
            return True

        # 5. 使用Table显示可用版本
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
            border_style="blue",
            show_lines=False,
            collapse_padding=True,
            padding=(0, 0),
            width=self.panel_width - 2
        )

        # 计算列宽（总计134字符）
        table.add_column("序号", style="cyan", justify="center", width=8)
        table.add_column("版本号", style="bold white", width=30)
        table.add_column("发布时间", style="green", width=20)
        table.add_column("版本名称", style="yellow", width=76)

        for index, release in enumerate(available_versions, 1):
            # 格式化发布时间
            published_at = release['published_at'].split('T')[0] if release['published_at'] else "未知"
            version_name = release['name'] or "无名称"

            # 缩短过长的版本名称
            if len(version_name) > 70:
                version_name = version_name[:67] + "..."

            table.add_row(
                str(index),
                release['version'],
                published_at,
                version_name
            )

        # 6. 显示版本选择面板
        version_panel = Panel(
            table,
            title=f"可用更新版本 (共 {len(available_versions)} 个)",
            subtitle="0: 返回主菜单 | Enter: 直接返回",
            subtitle_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
            width=self.panel_width
        )

        while True:
            self.console.clear()
            self.console.print(title_panel)
            self.console.print()
            self.console.print(f"当前版本: {self.update_manager.current_version}", style="bold white")
            self.console.print()
            self.console.print(version_panel)
            self.console.print()

            # 7. 让用户选择要更新的版本
            self.console.print("请输入版本序号: ", style="bold green", end="")
            choice_input = input().strip()

            if not choice_input:
                return True

            try:
                choice = int(choice_input)

                if choice == 0:
                    return True

                if 1 <= choice <= len(available_versions):
                    selected_release = available_versions[choice - 1]
                    return self._show_version_detail(title_panel, selected_release)
                else:
                    # 无效序号 - 在当前界面下方显示错误提示
                    error_panel = Panel(
                        Text(f"无效的序号，请输入 0-{len(available_versions)}", style="red", justify="center"),
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(1, 1),
                        width=self.panel_width
                    )
                    self.console.print()
                    self.console.print(error_panel)
                    self.console.print()
                    self.console.print("按任意键重新选择...", style="dim", end="")
                    self._wait_for_keypress()
                    continue

            except ValueError:
                # 无效输入 - 在当前界面下方显示错误提示
                error_panel = Panel(
                    Text("请输入有效的数字序号", style="red", justify="center"),
                    border_style="red",
                    box=box.ROUNDED,
                    padding=(1, 1),
                    width=self.panel_width
                )
                self.console.print()
                self.console.print(error_panel)
                self.console.print()
                self.console.print("按任意键重新选择...", style="dim", end="")
                self._wait_for_keypress()
                continue
            except KeyboardInterrupt:
                return True

        return True

    def _show_version_detail(self, title_panel: Panel, selected_release: Dict) -> bool:
        """
        显示版本详情并处理更新

        Args:
            title_panel: 标题面板
            selected_release: 选择的版本信息

        Returns:
            bool: 更新是否成功
        """
        while True:
            self.console.clear()
            self.console.print(title_panel)
            self.console.print()

            # 1. 版本详情面板
            detail_table = Table(
                show_header=False,
                box=box.SIMPLE,
                border_style="cyan",
                show_lines=False,
                collapse_padding=True,
                padding=(0, 0),
                width=self.panel_width - 2
            )
            detail_table.add_column("属性", style="cyan bold", width=20)
            detail_table.add_column("值", style="white", width=114)

            detail_table.add_row("版本号", selected_release['version'])
            detail_table.add_row("版本名称", selected_release['name'] or "无名称")
            detail_table.add_row("发布时间", selected_release['published_at'].split('T')[0] if selected_release[
                'published_at'] else "未知")
            detail_table.add_row("发布链接", selected_release['html_url'])

            detail_panel = Panel(
                detail_table,
                title="版本详情",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(0, 1),
                width=self.panel_width
            )

            self.console.print(detail_panel)
            self.console.print()

            # 2. 显示更新日志
            if selected_release['body']:
                changelog_text = Text("更新日志:\n", style="bold yellow")
                lines = selected_release['body'].split('\n')[:5]
                for line in lines:
                    if line.strip():
                        changelog_text.append(f"  • {line.strip()}\n")
                if len(selected_release['body'].split('\n')) > 5:
                    changelog_text.append("  • ... 更多日志请访问发布链接查看\n", style="dim")

                changelog_panel = Panel(
                    changelog_text,
                    border_style="yellow",
                    box=box.ROUNDED,
                    padding=(1, 2),
                    width=self.panel_width
                )
                self.console.print(changelog_panel)
                self.console.print()

            # 3. 确认更新
            self.console.print("确认更新到此版本吗？ (y/N): ", style="bold green", end="")
            confirm = input().strip().lower()

            if confirm in ['y', 'yes', '是']:
                # 4. 执行更新
                self.console.clear()
                self.console.print(title_panel)
                self.console.print()

                # 设置要更新到的版本
                self.update_manager.latest_version = selected_release['version']
                self.update_manager.update_available = True

                # 执行更新
                success = self.update_app()

                if success:
                    success_panel = Panel(
                        Text(f"√ 更新到版本 {selected_release['version']} 成功!", style="bold green", justify="center"),
                        subtitle="建议重启应用以应用所有更新",
                        subtitle_align="center",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(1, 2),
                        width=self.panel_width
                    )
                    self.console.print(success_panel)
                else:
                    error_panel = Panel(
                        Text("× 更新失败", style="bold red", justify="center"),
                        subtitle="请检查网络连接或日志信息",
                        subtitle_align="center",
                        border_style="red",
                        box=box.ROUNDED,
                        padding=(1, 2),
                        width=self.panel_width
                    )
                    self.console.print(error_panel)

                self._wait_for_keypress()
                return success
            else:
                # 取消更新 - 在当前界面下方显示提示
                cancel_panel = Panel(
                    Text("已取消更新", style="yellow", justify="center"),
                    border_style="yellow",
                    box=box.ROUNDED,
                    padding=(1, 1),
                    width=self.panel_width
                )
                self.console.print()
                self.console.print(cancel_panel)
                self.console.print()
                self.console.print("按任意键返回版本列表...", style="dim", end="")
                self._wait_for_keypress()
                break

        return True

    def _wait_for_keypress(self):
        """
        等待用户按键继续
        """
        import sys

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

        self.console.print()