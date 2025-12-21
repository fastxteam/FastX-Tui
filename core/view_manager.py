#!/usr/bin/env python3
"""
视图管理器模块 - 统一管理所有视图、路由和布局
"""
import os
import sys
import time
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich import box

from .menu_system import MenuNode, ActionItem, MenuType, CommandType
from .logger import get_current_log_level


@dataclass
class ViewRoute:
    """视图路由信息"""
    id: str
    name: str
    description: str
    handler: Callable
    parent_id: Optional[str] = None
    icon: str = "📁"
    type: str = "menu"  # menu, command, view
    requires_confirmation: bool = False
    params: Dict[str, Any] = field(default_factory=dict)


class View(ABC):
    """视图基类"""
    
    def __init__(self, view_manager: 'ViewManager', id: str, name: str):
        self.view_manager = view_manager
        self.id = id
        self.name = name
        self.console = view_manager.console
        self.config_manager = view_manager.config_manager
    
    @abstractmethod
    def render(self, *args, **kwargs):
        """渲染视图"""
        pass
    
    def before_render(self):
        """渲染前的准备工作"""
        pass
    
    def after_render(self):
        """渲染后的清理工作"""
        pass


class ViewManager:
    """视图管理器 - 统一管理所有视图、路由和布局"""
    
    def __init__(self, console: Console, config_manager, update_manager=None):
        self.console = console
        self.config_manager = config_manager
        self.update_manager = update_manager
        self.routes: Dict[str, ViewRoute] = {}
        self.view_stack: List[str] = []  # 视图栈，用于返回上一层
        self.current_view_id: Optional[str] = None
        self.views: Dict[str, View] = {}
        
        # 统计信息
        self.command_count = 0
        
        # 初始化布局
        self.layout = Layout()
        self._init_layout()
        
        # 性能监控
        self.start_time = time.time()
    
    def _init_layout(self):
        """初始化布局结构"""
        # 主布局：顶部banner、中间内容区、底部状态栏和快捷栏
        self.layout.split(
            Layout(name="banner", size=15),
            Layout(name="main", ratio=1),
            Layout(name="shortcut", size=1),
            Layout(name="statusbar", size=1)
        )
        
        # 中间内容区可进一步分割
        self.layout["main"].split_column(
            Layout(name="content", ratio=1),
            Layout(name="sidebar", size=20, visible=False)
        )
    
    def register_route(self, route: ViewRoute):
        """注册路由"""
        self.routes[route.id] = route
    
    def register_view(self, view: View):
        """注册视图"""
        self.views[view.id] = view
    
    def navigate(self, route_id: str, *args, **kwargs):
        """导航到指定路由"""
        if route_id not in self.routes:
            self.console.print(f"[red]错误: 路由 {route_id} 不存在[/red]")
            return False
        
        # 清屏 - 每一次跳转都清屏
        self.clear_screen()
        
        # 保存当前视图到栈中（如果不是返回操作）
        if self.current_view_id and route_id != self.current_view_id:
            self.view_stack.append(self.current_view_id)
        
        # 更新当前视图
        self.current_view_id = route_id
        
        # 获取路由并执行处理函数
        route = self.routes[route_id]
        
        # 渲染布局
        self._render_layout(route, *args, **kwargs)
        
        return True
    
    def back(self):
        """返回上一层视图"""
        if not self.view_stack:
            # 如果已经在顶层，返回主菜单
            self.navigate("main_menu")
            return True
        
        # 清屏
        self.clear_screen()
        
        # 从栈中弹出上一个视图
        prev_view_id = self.view_stack.pop()
        
        # 更新当前视图并渲染
        self.current_view_id = prev_view_id
        route = self.routes[prev_view_id]
        self._render_layout(route)
        
        return True
    
    def go_home(self):
        """返回主菜单"""
        # 清屏
        self.clear_screen()
        
        # 清空视图栈
        self.view_stack.clear()
        
        # 导航到主菜单
        self.navigate("main_menu")
    
    def clear_screen(self):
        """清屏操作 - 在原子端调用"""
        os.system('cls' if sys.platform == 'win32' else 'clear')
    
    def _render_layout(self, route: ViewRoute, *args, **kwargs):
        """渲染完整布局"""
        # 渲染banner
        # 获取版本信息，如果kwargs中没有提供则使用默认值
        version = kwargs.get('version', None)
        self._render_banner(version=version)
        
        # 渲染更新提示（在banner下方）
        if 'update_manager' in kwargs:
            self._render_update_prompt(kwargs['update_manager'])
        
        # 渲染内容区
        self._render_content(route, *args, **kwargs)
        
        # 渲染设置栏
        self._render_settings()
        
        # 渲染快捷栏
        self._render_shortcut()
        
        # 渲染状态栏（位于快捷栏下方）
        self._render_statusbar()
    
    def _render_banner(self, version: Optional[str] = None, banner_style: Optional[str] = None):
        """渲染banner
        
        Args:
            version: 当前版本号
            banner_style: 横幅样式
        """
        # 使用传入的版本号或默认版本号
        display_version = version if version else "v0.1.0"
        
        # 使用传入的样式或从配置获取
        display_style = banner_style if banner_style else self.config_manager.get_config("banner_style", "default")
        
        banner = f"""
╔═════════════════════════════════════════════════════════════════════════╗════════════════════════════════════════════╗
║                                                                         ║                                            ║
║   ███████╗ █████╗ ███████╗████████╗██╗  ██╗     ████████╗██╗   ██╗██╗   ║   ████                                     ║
║   ██╔════╝██╔══██╗██╔════╝╚══██╔══╝╚██╗██╔╝     ╚══██╔══╝██║   ██║██║   ║      ███         +------------+            ║
║   █████╗  ███████║███████╗   ██║    ╚███╔╝         ██║   ██║   ██║██║   ║         ███      |  TERMINAL  |            ║
║   ██╔══╝  ██╔══██║╚════██║   ██║    ██╔██╗         ██║   ██║   ██║██║   ║           ███    |   > _      |            ║
║   ██║     ██║  ██║███████║   ██║   ██╔╝ ██╗        ██║   ╚██████╔╝██║   ║         ███      +------^-----+            ║
║   ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝        ╚═╝    ╚═════╝ ╚═╝   ║      ███                                   ║
║                                                                         ║   ███            ██████████████            ║
║                  Terminal ToolSets For MCU                              ║                                            ║
║══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════║
║   Built with FastXTeam/TUI, Architect Developed By @wanqiang.liu        ║ https://github.com/fastxteam/FastX-Tui.git ║
╚═════════════════════════════════════════════════════════════════════════╝════════════════════════════════════════════╝
        """
        
        if display_style == "gradient":
            # 转换横幅为行列表
            banner_lines = banner.strip().split('\n')
            self._print_with_gradient(banner_lines, ["#00ffff", "#ff00ff"])
        else:
            # 默认样式
            self.console.print(banner, style="cyan")
    
    def _print_with_gradient(self, lines: List[str], colors: List[str]):
        """使用渐变效果打印文本"""
        from rich.color import parse_rgb_hex
        
        r1, g1, b1 = parse_rgb_hex(colors[0].lstrip('#'))
        r2, g2, b2 = parse_rgb_hex(colors[1].lstrip('#'))

        for line in lines:
            main_text = Text()
            if not line:  # 跳过空行
                self.console.print()
                continue
                
            for j, char in enumerate(line):
                if char != ' ':
                    ratio = j / (len(line) - 1) if len(line) > 1 else 0
                    r = int(r1 + (r2 - r1) * ratio)
                    g = int(g1 + (g2 - g1) * ratio)
                    b = int(b1 + (b2 - b1) * ratio)
                    main_text.append(char, style=f"bold rgb({r},{g},{b})")
                else:
                    main_text.append(char)
            self.console.print(main_text)
    
    def _render_content(self, route: ViewRoute, *args, **kwargs):
        """渲染内容区"""
        # 执行路由处理函数
        try:
            result = None
            if route.type == "menu":
                # 如果是菜单路由，直接渲染菜单（假设handler返回MenuNode或已处理渲染）
                route.handler(*args, **kwargs)
            else:
                # 如果是命令路由，直接执行处理函数
                result = route.handler(*args, **kwargs)
            
            if result and route.type != "menu":
                self.console.print(result)
        except Exception as e:
            self.console.print(f"[red]错误: {str(e)}[/red]")
    
    def _render_statusbar(self):
        """渲染状态栏"""
        # 计算运行时间
        uptime = time.time() - self.start_time
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # 获取当前视图信息
        current_view = self.routes.get(self.current_view_id)
        view_name = current_view.name if current_view else "未知视图"
        
        # 获取版本信息
        version = self.update_manager.current_version if self.update_manager else "v0.1.0"
        
        # 添加版本更新指示器
        if self.update_manager:
            if self.update_manager.version_check_failed:
                # 版本检查失败 - 红色圆点
                version_info = f"🏷️: {version} [red]⚡[/red]"
            elif self.update_manager.update_available and self.update_manager.latest_version:
                # 有更新 - 黄色圆点
                version_info = f"🏷️: {version} [yellow]⚡[/yellow]"
            else:
                # 最新版本 - 绿色圆点
                version_info = f"🏷️: {version} [green]⚡[/green]"
        else:
            version_info = f"🏷️: {version}"
        
        # 构建面包屑/路由 - 格式：主菜单 > 子菜单
        # 确保面包屑始终以主菜单开头
        breadcrumb = []
        
        # 始终将主菜单添加到面包屑开头
        main_menu = self.routes.get("main_menu")
        if main_menu:
            breadcrumb.append(main_menu.name)
        
        # 如果当前视图不是主菜单，添加当前视图路径
        if self.current_view_id and self.current_view_id != "main_menu":
            # 从视图栈和当前视图构建完整路径
            full_path = self.view_stack + [self.current_view_id]
            for route_id in full_path:
                route = self.routes.get(route_id)
                if route and route.id != "main_menu":  # 避免重复添加主菜单
                    breadcrumb.append(route.name)
        
        # 构建面包屑字符串
        breadcrumb_str = " > ".join(breadcrumb)
        
        # 获取当前日志等级
        current_log_level = get_current_log_level()
        
        # 根据日志等级选择图标
        log_level_icons = {
            "DEBUG": "🔍",
            "INFO": "📝",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "💥"
        }
        log_level_icon = log_level_icons.get(current_log_level, "📝")
        
        # 构建状态栏右侧内容 - 格式：图标：运行s | 指令统计图标：n | 日志等级图标：xx | 版本图标：vx.x.x ⚡
        # 使用固定宽度120(135 跟 "─" * 120差不多)，与菜单宽度对齐
        menu_width = 130
        
        # 右侧状态信息
        runtime_str = f"⏱️: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        commands_str = f"💻: {self.command_count}"
        log_str = f"{log_level_icon}: {current_log_level}"
        version_str = version_info
        
        # 构建右侧内容
        right_content = f"{runtime_str} | {commands_str} | {log_str} | {version_str}"
        
        # 左侧面包屑 + 右侧状态信息，总宽度120
        status_content = f"{breadcrumb_str}".ljust(menu_width - len(right_content) - 1) + right_content
        
        # 渲染状态栏 - 添加分隔线和特效
        self.console.print("─" * 120, style="bold white")
        self.console.print(status_content, style="bold white")
    
    def _render_update_prompt(self, update_manager=None):
        """渲染版本更新提示"""
        from rich.text import Text
        from rich.panel import Panel
        
        if update_manager and update_manager.should_show_update_prompt():
            
            current_version = update_manager.current_version.lstrip('v') if (update_manager and hasattr(update_manager, 'current_version')) else "0.0.1"
            latest_version = update_manager.latest_version if (update_manager and hasattr(update_manager, 'latest_version') and update_manager.latest_version) else "0.1.0"
            
            # 创建格式化的更新消息
            update_message = Text.from_markup(
                f"[#F9E2AF]FastX-Tui update available! {current_version} -> {latest_version}[/#F9E2AF]\n"
                f"[#F9E2AF]Check the latest release at: `https://github.com/fastxteam/FastX-Tui/releases/latest[/#F9E2AF]` "
            )
            
            # 使用Panel显示更新消息
            self.console.print(
                Panel(
                    update_message,
                    box = box.DOUBLE,
                    border_style="#F9E2AF",
                    expand=True,
                    width=120
                )
            )
            # 添加空行分隔
            self.console.print()
    
    def _render_settings(self):
        """渲染设置栏"""
        settings = []
        
        # 设置相关功能及快捷键
        settings.extend([
            "m: 配置",
            "p: 插件",
            "l: 日志"
        ])
        
        # 渲染设置栏
        settings_text = "设置栏: " + " | ".join(settings)
        # 添加分隔线和特效
        self.console.print("─" * 120, style="dim")
        self.console.print(settings_text, style="dim bold")
    
    def _render_shortcut(self):
        """渲染快捷栏"""
        shortcuts = []
        
        # 导航快捷键
        if self.view_stack:
            shortcuts.append("0: 返回")
        shortcuts.append("0: 主菜单/返回")
        
        # 功能快捷键
        shortcuts.extend([
            "q: 退出",
            "c: 清屏",
            "s: 搜索",
            "h: 帮助",
            "u: 更新"
        ])

        # 渲染快捷栏
        shortcut_text = "快捷栏: " + " | ".join(shortcuts)
        # 添加分隔线和特效
        self.console.print("─" * 120, style="dim")
        self.console.print(shortcut_text, style="dim bold")
    
    def get_current_route(self) -> Optional[ViewRoute]:
        """获取当前路由"""
        if not self.current_view_id:
            return None
        return self.routes.get(self.current_view_id)
    
    def get_route_by_id(self, route_id: str) -> Optional[ViewRoute]:
        """根据ID获取路由"""
        return self.routes.get(route_id)
    
    def get_all_routes(self) -> Dict[str, ViewRoute]:
        """获取所有路由"""
        return self.routes
    
    def get_view_stack(self) -> List[str]:
        """获取视图栈"""
        return self.view_stack
    
    def set_update_manager(self, update_manager):
        """设置更新管理器实例"""
        self.update_manager = update_manager
        
    def set_command_count(self, count):
        """设置指令运行统计次数"""
        self.command_count = count
    
    def render_menu(self, menu_node: MenuNode, menu_system=None):
        """渲染菜单"""
        if not menu_node:
            return
        
        # 获取要显示的项目
        display_items = menu_node.get_display_items(menu_system)
        if not display_items:
            self.console.print("[yellow]此菜单当前没有可用的项目[/yellow]\n")
            return
        
        # 创建表格显示菜单项
        from rich.table import Table
        from rich.panel import Panel
        
        
        # 显示菜单标题、描述和面包屑
        self.console.print(Panel(
            f"[bold]{menu_node.name}[/bold]\n{menu_node.description}",
            box=box.ROUNDED,
            style="cyan",
            width=120
        ))
        self.console.print()
        
        table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style="bold white",
            width=120
        )
        
        table.add_column("编号", style="cyan bold", justify="center")
        table.add_column("名称", style="white")
        table.add_column("类型", style="green")
        table.add_column("描述", style="yellow")
        
        for i, item in enumerate(display_items, 1):
            # 确定项目类型
            if isinstance(item, MenuNode):
                item_type = "[菜单]"
                style = "bold cyan"
            else:
                item_type = "[命令]"
                style = ""
            
            # 取消显示图标
            table.add_row(
                f"[bold]{i}[/bold]",
                item.name,
                item_type,
                item.description,
                style=style
            )
        
        self.console.print(table)
