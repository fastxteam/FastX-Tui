#!/usr/bin/env python3
"""
视图管理器模块 - 统一管理所有视图、路由和布局
"""
import os
import sys
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .logger import get_current_log_level
from .menu_system import MenuNode


@dataclass
class ViewRoute:
    """视图路由信息"""
    id: str
    name: str
    description: str
    handler: Callable
    parent_id: str | None = None
    icon: str = "📁"
    type: str = "menu"  # menu, command, view
    requires_confirmation: bool = False
    params: dict[str, Any] = field(default_factory=dict)


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

    # 页面宽度控制变量，用于统一调整所有UI元素的宽度
    PAGE_WIDTH = 125

    def __init__(self, console: Console, config_manager, update_manager=None):
        self.console = console
        self.config_manager = config_manager
        self.update_manager = update_manager
        self.routes: dict[str, ViewRoute] = {}
        self.view_stack: list[str] = []  # 视图栈，用于返回上一层
        self.current_view_id: str | None = None
        self.views: dict[str, View] = {}

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

    def _render_banner(self, version: str | None = None, banner_style: str | None = None):
        """渲染banner
        
        Args:
            version: 当前版本号
            banner_style: 横幅样式
        """
        # 使用传入的版本号或默认版本号
        display_version = version if version else "v0.1.0"

        # 使用传入的样式或从配置获取
        display_style = banner_style if banner_style else self.config_manager.get_config("banner_style", "default")

        # 定义banner内容，确保格式正确
        banner_content = [
            "                                                                                                                           ",
            "    ████          +------------+   ███████╗ █████╗ ███████╗████████╗██╗  ██╗     ████████╗██╗   ██╗██╗                     ",
            "      ████        |  TERMINAL  |   ██╔════╝██╔══██╗██╔════╝╚══██╔══╝╚██╗██╔╝     ╚══██╔══╝██║   ██║██║                     ",
            "        ████      |       CLI  |   █████╗  ███████║███████╗   ██║    ╚███╔╝         ██║   ██║   ██║██║                     ",
            "          ████    |   > _      |   ██╔══╝  ██╔══██║╚════██║   ██║    ██╔██╗         ██║   ██║   ██║██║                     ",
            "        ████      |            |   ██║     ██║  ██║███████║   ██║   ██╔╝ ██╗        ██║   ╚██████╔╝██║                     ",
            "      ████        +------^-----+   ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝        ╚═╝    ╚═════╝ ╚═╝                     ",
            "    ████          ██████████████   FastX-TUI Terminal PluginSys, Architect Developed By @FastXTeam/WQ.L                    ",
            "                                                                                                                           "
        ]

        from rich.box import ROUNDED
        from rich.panel import Panel

        if display_style == "gradient":
            # 使用_print_with_gradient方法生成渐变文本，返回Text对象
            gradient_text = self._print_with_gradient(banner_content, ["00ffff", "ff00ff"], return_text=True)

            # 使用Panel包裹渐变文本，设置宽度为PAGE_WIDTH
            banner_panel = Panel(
                gradient_text,
                box=ROUNDED,
                style="cyan",
                expand=False,
                width=self.PAGE_WIDTH
            )
        else:
            # 默认样式，使用Panel包裹，设置宽度为PAGE_WIDTH
            # 将列表转换为字符串，添加适当的换行
            banner_str = "\n".join(banner_content)
            banner_panel = Panel(
                banner_str,
                box=ROUNDED,
                style="cyan",
                expand=False,
                width=self.PAGE_WIDTH
            )

        # 打印banner
        self.console.print(banner_panel)

    def _print_with_gradient(self, lines: list[str], colors: list[str], return_text: bool = False):
        """使用渐变效果打印文本
        
        Args:
            lines: 要打印的文本行列表
            colors: 渐变的两种颜色
            return_text: 是否返回生成的Text对象，而不是直接打印
            
        Returns:
            如果return_text为True，返回生成的Text对象；否则返回None
        """
        from rich.color import parse_rgb_hex

        r1, g1, b1 = parse_rgb_hex(colors[0].lstrip('#'))
        r2, g2, b2 = parse_rgb_hex(colors[1].lstrip('#'))

        # 创建完整的Text对象
        full_text = Text()

        for i, line in enumerate(lines):
            line_text = Text()
            if not line:  # 空行
                line_text.append("\n")
            else:
                for j, char in enumerate(line):
                    if char != ' ':
                        ratio = j / (len(line) - 1) if len(line) > 1 else 0
                        r = int(r1 + (r2 - r1) * ratio)
                        g = int(g1 + (g2 - g1) * ratio)
                        b = int(b1 + (b2 - b1) * ratio)
                        line_text.append(char, style=f"bold rgb({r},{g},{b})")
                    else:
                        line_text.append(char)
                # 除了最后一行，其他行都添加换行
                if i < len(lines) - 1:
                    line_text.append("\n")

            full_text.append(line_text)

        if return_text:
            return full_text
        else:
            self.console.print(full_text)
            return None

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
        # 右侧状态信息
        runtime_str = f"⏱️: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        commands_str = f"💻: {self.command_count}"
        log_str = f"{log_level_icon}: {current_log_level}"
        version_str = version_info

        # 构建状态内容
        status_content = f"{runtime_str} | {commands_str} | {log_str} | {version_str}"

        # 计算需要居中的宽度
        status_content = f"{' ' * (len('─' * self.PAGE_WIDTH) - len(status_content) + int(self.PAGE_WIDTH*0.12))}{status_content}"

        # 渲染状态栏 - 添加分隔线和特效
        self.console.print("─" * self.PAGE_WIDTH, style="bold white")
        self.console.print(status_content, style="bold white")

    def _render_update_prompt(self, update_manager=None):
        """渲染版本更新提示"""
        from rich.panel import Panel
        from rich.text import Text

        if update_manager and update_manager.should_show_update_prompt():

            current_version = update_manager.current_version.lstrip('v') if (update_manager and hasattr(update_manager, 'current_version')) else "0.0.1"
            latest_version = update_manager.latest_version if (update_manager and hasattr(update_manager, 'latest_version') and update_manager.latest_version) else "0.1.0"

            # 创建格式化的更新消息
            update_message = Text.from_markup(
                f"[#A3DD97]FastX-Tui update available! {current_version} -> {latest_version}[/#A3DD97]\n"
                f"[#A3DD97]Check the latest release at: `https://github.com/fastxteam/FastX-Tui/releases/latest[/#A3DD97]` "
            )

            # 使用Panel显示更新消息
            self.console.print(
                Panel(
                    update_message,
                    title="[ Notice!!! ]",
                    title_align="left",
                    box = box.ROUNDED,
                    border_style="#A3DD97",
                    expand=True,
                    width=self.PAGE_WIDTH
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
        self.console.print("─" * self.PAGE_WIDTH, style="dim")
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
            "u: 更新",
            "t: 任务"
        ])

        # 渲染快捷栏
        shortcut_text = "快捷栏: " + " | ".join(shortcuts)
        # 添加分隔线和特效
        self.console.print("─" * self.PAGE_WIDTH, style="dim")
        self.console.print(shortcut_text, style="dim bold")

    def get_current_route(self) -> ViewRoute | None:
        """获取当前路由"""
        if not self.current_view_id:
            return None
        return self.routes.get(self.current_view_id)

    def get_route_by_id(self, route_id: str) -> ViewRoute | None:
        """根据ID获取路由"""
        return self.routes.get(route_id)

    def get_all_routes(self) -> dict[str, ViewRoute]:
        """获取所有路由"""
        return self.routes

    def get_view_stack(self) -> list[str]:
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
        table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style="bold white",
            width=self.PAGE_WIDTH - 4  # 留出边框空间
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

        # 构建面包屑 - 最多显示4层关系
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

        # 限制最多显示4层关系
        if len(breadcrumb) > 4:
            # 显示主菜单 + ... + 最后两层
            breadcrumb = [breadcrumb[0], "..."] + breadcrumb[-2:]

        # 构建面包屑字符串
        breadcrumb_str = " > ".join(breadcrumb)

        # 实现Panel内部包裹菜单Table的格局，标题显示面包屑
        self.console.print(Panel(
            table,
            title=f"[bold]{breadcrumb_str}[/bold]",
            title_align= "left",
            subtitle=f"> {menu_node.description}",
            subtitle_align="center",
            box=box.ROUNDED,
            style="cyan",
            width=self.PAGE_WIDTH
        ))
