#!/usr/bin/env python3
"""
菜单系统核心模块
"""
import os
import time
import subprocess
import sys
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich import box


class MenuType(Enum):
    """菜单类型"""
    MAIN = "main"
    SUB = "sub"


class CommandType(Enum):
    """命令类型"""
    SHELL = "shell"
    PYTHON = "python"


@dataclass
class MenuItem:
    """菜单项基类"""
    id: str
    name: str
    description: str = ""
    enabled: bool = True
    icon: str = "▶"
    category: str = "general"


@dataclass
class ActionItem(MenuItem):
    """可执行的动作项"""
    command_type: CommandType = CommandType.SHELL
    command: Optional[str] = None
    python_func: Optional[Callable] = None
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    timeout: int = 30

    def execute(self) -> str:
        """执行命令/函数"""
        if self.command_type == CommandType.PYTHON and self.python_func:
            try:
                return self.python_func(*self.args, **self.kwargs)
            except Exception as e:
                return f"Python函数执行错误: {str(e)}"

        elif self.command_type == CommandType.SHELL and self.command:
            try:
                result = subprocess.run(
                    self.command.split() if not self.args else self.args,
                    capture_output=True,
                    text=True,
                    shell=True,
                    encoding='gbk' if sys.platform == 'win32' else 'utf-8',
                    timeout=self.timeout
                )
                output = result.stdout if result.stdout else result.stderr
                if result.returncode != 0:
                    return f"命令执行失败 (代码: {result.returncode}):\n{output}"
                return output
            except subprocess.TimeoutExpired:
                return f"命令执行超时 ({self.timeout}秒)"
            except Exception as e:
                return f"命令执行错误: {str(e)}"

        return "此命令没有可执行的内容"


@dataclass
class MenuNode(MenuItem):
    """菜单节点"""
    menu_type: MenuType = MenuType.SUB
    parent_id: Optional[str] = None
    items: List[Union[str, MenuItem, 'MenuNode']] = field(default_factory=list)
    icon: str = "📁"

    def add_item(self, item: Union[str, MenuItem, 'MenuNode']):
        """添加菜单项"""
        self.items.append(item)

    def get_display_items(self, menu_system: 'MenuSystem') -> List[MenuItem]:
        """获取显示的项目列表"""
        display_items = []
        for item in self.items:
            if isinstance(item, str):
                menu_item = menu_system.get_item_by_id(item)
                if menu_item and menu_item.enabled:
                    display_items.append(menu_item)
            elif isinstance(item, (MenuItem, MenuNode)) and item.enabled:
                display_items.append(item)
        return display_items


class MenuSystem:
    """菜单系统管理类"""
    
    def __init__(self, console: Console):
        self.console = console
        self.current_menu: Optional[MenuNode] = None
        self.menu_history: List[MenuNode] = []
        self.items: Dict[str, Union[MenuItem, MenuNode]] = {}
        self.start_time = time.time()

        # 本地化管理器（稍后设置）
        self.locale_manager = None

        # 图标映射（使用等宽友好的图标）
        self.icon_map = {
            'main': '🏠',
            'system': '⚙️',
            'file': '📁',
            'python': '🐍',
            'network': '🌐',
            'search': '🔍',
            'config': '⚙️',
            'plugin': '🔌',
            'help': '❓',
            'exit': '🚪',
            'clear': '🧹',
            'process': '📋',
            'disk': '💾',
            'time': '⏰',
            'tree': '🌳',
            'package': '📦'
        }

        # 初始化固定快捷键项
        self._init_fixed_items()

    def set_locale_manager(self, locale_manager):
        """设置本地化管理器"""
        self.locale_manager = locale_manager

    def t(self, key: str, default: str = None, **kwargs) -> str:
        """翻译文本"""
        if self.locale_manager and hasattr(self.locale_manager, 't'):
            return self.locale_manager.t(key, default, **kwargs)
        return default if default is not None else key

    def _init_fixed_items(self):
        """初始化固定项目"""
        # 清屏
        self.register_item(ActionItem(
            id="clear_screen",
            name=self.t("app.clear", "清屏"),
            description=self.t("app.clear", "清除屏幕内容"),
            icon="🧹",
            command_type=CommandType.SHELL,
            command="cls" if sys.platform == 'win32' else "clear"
        ))

        # 帮助
        self.register_item(MenuItem(
            id="show_help",
            name=self.t("app.help", "帮助"),
            description=self.t("app.help", "显示帮助信息"),
            icon="📚"
        ))

        # 退出
        self.register_item(ActionItem(
            id="exit_app",
            name=self.t("app.exit", "退出程序"),
            description=self.t("app.exit", "安全退出程序"),
            icon="⚡",
            command_type=CommandType.SHELL,
            command="echo " + self.t("app.exit", "正在退出...")
        ))

    def register_item(self, item: Union[MenuItem, MenuNode]):
        """注册菜单项"""
        self.items[item.id] = item
        return item

    def get_item_by_id(self, item_id: str) -> Optional[Union[MenuItem, MenuNode]]:
        """根据ID获取菜单项"""
        return self.items.get(item_id)

    def navigate_to_menu(self, menu_id: str) -> bool:
        """导航到指定菜单"""
        menu = self.get_item_by_id(menu_id)
        if isinstance(menu, MenuNode):
            if self.current_menu:
                self.menu_history.append(self.current_menu)
            self.current_menu = menu
            self.clear_screen()  # 清除屏幕显示新菜单
            return True
        return False

    def go_back(self) -> bool:
        """返回上一级菜单"""
        if self.menu_history:
            self.current_menu = self.menu_history.pop()
            self.clear_screen()  # 清除屏幕显示上一级菜单
            return True
        return False

    def go_to_root(self):
        """返回主菜单"""
        while self.go_back():
            pass
        self.clear_screen()  # 清除屏幕显示主菜单

    def clear_screen(self):
        """清除屏幕"""
        os.system('cls' if sys.platform == 'win32' else 'clear')

    def show_banner(self, version=""):
        """显示横幅"""
        banner = f"""
╔═══════════════════════════════════════════════════════════════════════════╗═══════════════════════════════════════╗
║                                                                           ║                                       ║
║    ███████╗ █████╗ ███████╗████████╗██╗  ██╗     ████████╗██╗   ██╗██╗    ║      ███                              ║
║    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝╚██╗██╔╝     ╚══██╔══╝██║   ██║██║    ║         ███                           ║
║    █████╗  ███████║███████╗   ██║    ╚███╔╝         ██║   ██║   ██║██║    ║           ███                         ║
║    ██╔══╝  ██╔══██║╚════██║   ██║    ██╔██╗         ██║   ██║   ██║██║    ║         ███                           ║
║    ██║     ██║  ██║███████║   ██║   ██╔╝ ██╗        ██║   ╚██████╔╝██║    ║      ███                              ║
║    ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝        ╚═╝    ╚═════╝ ╚═╝    ║                                       ║
║                                                                           ║                                       ║
║                   Terminal ToolSets For MCU                               ║                                       ║
║                                                                           ║                                       ║
║    Built with FastXTeam/TUI, Architect Developed By @wanqiang.liu         ║                                       ║
╚═══════════════════════════════════════════════════════════════════════════╝═══════════════════════════════════════╝
        """
        self.console.print(banner, style="cyan")

    def get_icon(self, item_type: str, default: str = '▶') -> str:
        """获取图标，确保宽度一致"""
        # 对于特定类型的项目使用映射的图标
        for key, icon in self.icon_map.items():
            if key in item_type.lower():
                return icon

        # 对于菜单和命令使用固定图标
        if item_type.lower() in ['menu', 'sub', 'main']:
            return '📁'
        return '▶'

    def show_current_menu(self):
        """显示当前菜单 - 修复图标对齐问题"""
        if not self.current_menu:
            return


        # 获取要显示的项目
        if not self.current_menu:
            return
        
        display_items = self.current_menu.get_display_items(self)
        if not display_items:
            self.console.print(f"[yellow]{self.t('error.no_items', '此菜单当前没有可用的项目')}[/yellow]\n")
            return

        # 创建表格显示菜单项 - 修复图标对齐和宽度
        table = Table(
            box=box.SIMPLE,  # 使用简单的边框避免对齐问题
            show_header=True,
            header_style="bold white",
            width=120  # 增加整体表格宽度
        )

        # 使用更合理的固定宽度列
        table.add_column(self.t("table.number", "编号"), style="cyan bold", justify="center")
        # table.add_column(self.t("table.icon", "图标"), style="white", width=10, justify="center")  # 增加图标列宽度
        table.add_column(self.t("table.name", "名称"), style="white",)  # 增加名称列宽度
        table.add_column(self.t("table.type", "类型"), style="green")  # 增加类型列宽度
        table.add_column(self.t("table.description", "描述"), style="yellow")  # 增加描述列宽度

        for i, item in enumerate(display_items, 1):
            # 确定项目类型
            if isinstance(item, MenuNode):
                item_type = self.t("menu.type_menu", "[菜单]")
                style = "bold cyan"
            else:
                item_type = self.t("menu.type_command", "[命令]")
                style = ""

            # 使用固定宽度的图标或占位符
            icon = item.icon if hasattr(item, 'icon') and item.icon else self.get_icon(item_type)

            table.add_row(
                f"[bold]{i}[/bold]",
                # icon,
                f"{item.name}",
                item_type,
                item.description,
                style=style
            )

        self.console.print(table)
        self.console.print()

    def show_shortcut_hints(self):
        """显示快捷键提示"""
        hints = []

        # 导航提示 - 统一使用0返回上一级
        if self.current_menu and self.current_menu.menu_type != MenuType.MAIN:
            hints.append(f"0:{self.t('hint.back', '返回上级')}")
        else:
            hints.append(f"q:{self.t('hint.exit', '退出')}")

        # 功能提示
        hints.extend([
            f"c:{self.t('hint.clear', '清屏')}",
            f"h:{self.t('hint.help', '帮助')}",
            f"s:{self.t('hint.search', '搜索')}"
        ])

        self.console.print("─" * 70, style="dim")
        self.console.print(f"[dim]{self.t('hint.shortcuts', '快捷键')}: " + " | ".join(hints) + "[/dim]")

    def display_interface(self, clear: bool = True):
        """显示完整界面"""
        if clear:
            self.clear_screen()

        # 显示横幅
        self.show_banner()

        # 显示当前菜单
        self.show_current_menu()

        # 显示快捷键提示
        self.show_shortcut_hints()

    def execute_action(self, action: ActionItem) -> str:
        """执行动作"""
        try:
            start_time = time.time()
            output = action.execute()
            execution_time = time.time() - start_time

            unit = self.t("format.time_seconds", "秒")
            time_msg = f"执行时间: {execution_time:.2f}{unit}"
            result = f"⏱️  {time_msg}\n"
            result += "─" * 70 + "\n\n"
            result += output

            return result
        except Exception as e:
            error_msg = self.t("error.command_failed", "执行过程中发生错误")
            return f"{error_msg}:\n\n[red]{str(e)}[/red]"

    def create_submenu(self, menu_id: str, name: str, description: str = "", icon: str = "📁") -> MenuNode:
        """创建子菜单"""
        submenu = MenuNode(id=menu_id, name=name, description=description, menu_type=MenuType.SUB, icon=icon)
        self.register_item(submenu)
        return submenu

    def add_item_to_menu(self, menu_id: str, item: Union[str, MenuItem, MenuNode]) -> bool:
        """将菜单项添加到指定菜单"""
        menu = self.get_item_by_id(menu_id)
        if isinstance(menu, MenuNode):
            menu.add_item(item)
            return True
        return False

    def add_item_to_main_menu(self, item: Union[str, MenuItem, MenuNode]) -> bool:
        """将菜单项添加到主菜单"""
        main_menu = self.get_item_by_id("main_menu")
        if isinstance(main_menu, MenuNode):
            main_menu.add_item(item)
            return True
        return False