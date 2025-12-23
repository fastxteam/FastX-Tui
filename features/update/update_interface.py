#!/usr/bin/env python3
"""
更新功能界面模块
"""
from typing import Dict, Optional, Tuple

from core.update_manager import UpdateManager
from core.logger import get_logger

logger = get_logger(__name__)


class UpdateInterface:
    """
    更新功能界面类，负责处理更新相关的UI渲染和用户交互
    """
    
    def __init__(self, update_manager: UpdateManager, console=None):
        """
        初始化更新功能界面
        
        Args:
            update_manager: 更新管理器实例，提供底层核心逻辑
            console: Rich控制台实例，用于UI渲染
        """
        self.update_manager = update_manager
        self.console = console
    
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
            if self.console:
                self.console.print("[yellow]没有可用更新[/yellow]")
            return False
        
        logger.info(f"开始更新应用，当前版本: {self.update_manager.current_version}, 最新版本: {self.update_manager.latest_version}")
        if self.console:
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
        if not self.console:
            logger.error("控制台实例不可用，无法显示更新界面")
            return False
        
        # 显示当前版本信息
        self.console.print("=" * 70, style="green")
        self.console.print("📦 FastX-Tui 更新管理".center(70), style="green bold")
        self.console.print("=" * 70, style="green")
        self.console.print(f"当前版本: {self.update_manager.current_version}")
        
        # 获取所有可用版本
        self.console.print("\n🔍 正在获取可用版本...")
        versions_result = self.update_manager.get_available_versions(per_page=10)
        
        if not versions_result['success']:
            self.console.print(f"[red]获取可用版本失败: {versions_result['error']}[/red]")
            input("\n按回车键返回...")
            return False
        
        # 过滤出比当前版本更新的版本
        current_version = self.update_manager.current_version.lstrip('v')
        available_versions = []
        
        for release in versions_result['releases']:
            # 比较版本号，只保留比当前版本更新的版本
            from core.network_tools import NetworkToolsPlugin
            if NetworkToolsPlugin()._compare_versions(current_version, release['version']):
                available_versions.append(release)
        
        if not available_versions:
            self.console.print("\n[yellow]当前已是最新版本，无需更新[/yellow]")
            input("\n按回车键返回...")
            return True
        
        # 使用Table显示可用版本
        from rich.table import Table
        
        table = Table(title="可用更新版本", show_header=True, header_style="bold magenta")
        table.add_column("序号", style="dim", width=6)
        table.add_column("版本号", style="cyan")
        table.add_column("发布时间", style="green")
        table.add_column("版本名称", style="yellow")
        
        for index, release in enumerate(available_versions, 1):
            # 格式化发布时间
            published_at = release['published_at'].split('T')[0] if release['published_at'] else "未知"
            
            table.add_row(
                str(index),
                release['version'],
                published_at,
                release['name'] or "无名称"
            )
        
        self.console.print("")
        self.console.print(table)
        
        # 让用户选择要更新的版本
        from rich.prompt import Prompt
        
        self.console.print("\n💡 提示: 输入序号选择要更新的版本，输入0返回主菜单")
        
        try:
            choice = Prompt.ask("\n请选择要更新到的版本序号", choices=[str(i) for i in range(0, len(available_versions) + 1)], show_choices=False)
            choice = int(choice)
            
            if choice == 0:
                self.console.print("\n[yellow]已取消更新[/yellow]")
                input("\n按回车键返回...")
                return True
            
            if 1 <= choice <= len(available_versions):
                selected_release = available_versions[choice - 1]
                
                # 显示选择的版本信息
                self.console.print("\n" + "=" * 70, style="cyan")
                self.console.print(f"📋 版本详情: {selected_release['version']}".center(70), style="cyan bold")
                self.console.print("=" * 70, style="cyan")
                self.console.print(f"版本名称: {selected_release['name']}")
                self.console.print(f"发布时间: {selected_release['published_at'].split('T')[0]}")
                self.console.print(f"发布链接: {selected_release['html_url']}")
                
                # 显示更新日志（前5行）
                if selected_release['body']:
                    self.console.print("\n📝 更新日志:")
                    lines = selected_release['body'].split('\n')[:5]
                    for line in lines:
                        if line.strip():
                            self.console.print(f"  • {line.strip()}")
                    if len(selected_release['body'].split('\n')) > 5:
                        self.console.print("  • ... 更多日志请访问发布链接查看")
                
                # 询问用户是否确认更新
                from rich.prompt import Confirm
                
                confirm_update = Confirm.ask("\n是否确认更新到该版本", default=False)
                
                if confirm_update:
                    # 更新到选定版本
                    self.console.print(f"\n[green]开始更新到版本 {selected_release['version']}...[/green]")
                    
                    # 设置要更新到的版本
                    self.update_manager.latest_version = selected_release['version']
                    self.update_manager.update_available = True
                    
                    # 执行更新
                    success = self.update_app()
                    
                    if success:
                        self.console.print(f"\n[green]✅ 更新到版本 {selected_release['version']} 成功![/green]")
                        self.console.print("💡 提示: 建议重启应用以应用所有更新")
                    else:
                        self.console.print(f"\n[red]❌ 更新失败[/red]")
                    
                    input("\n按回车键返回...")
                    return success
                else:
                    self.console.print("\n[yellow]已取消更新[/yellow]")
                    input("\n按回车键返回...")
                    return True
            else:
                self.console.print(f"\n[red]❌ 无效的选择: {choice}[/red]")
                input("\n按回车键返回...")
                return False
                
        except ValueError:
            self.console.print(f"\n[red]❌ 无效的输入[/red]")
            input("\n按回车键返回...")
            return False
        except KeyboardInterrupt:
            self.console.print(f"\n\n[yellow]已取消更新[/yellow]")
            input("\n按回车键返回...")
            return True
        
        return True
