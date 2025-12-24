#!/usr/bin/env python3
"""
菜单系统核心模块 - 专注于菜单管理和命令执行
"""
import os
import time
import subprocess
import sys
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console


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
        """添加菜单项，避免重复"""
        # 检查菜单项是否已存在
        if isinstance(item, str):
            # 字符串ID
            if item not in self.items:
                self.items.append(item)
        else:
            # 菜单项对象，检查ID
            item_id = item.id
            for existing in self.items:
                if isinstance(existing, str):
                    if existing == item_id:
                        return
                else:
                    if existing.id == item_id:
                        return
            # 如果不存在，添加
            self.items.append(item)
    
    def remove_item(self, item: Union[str, MenuItem, 'MenuNode']):
        """移除菜单项"""
        if isinstance(item, str):
            # 字符串ID
            if item in self.items:
                self.items.remove(item)
        else:
            # 菜单项对象，检查ID
            item_id = item.id
            for i, existing in enumerate(self.items):
                if isinstance(existing, str):
                    if existing == item_id:
                        self.items.pop(i)
                        return
                else:
                    if existing.id == item_id:
                        self.items.pop(i)
                        return

    def get_display_items(self, menu_system: Optional['MenuSystem'] = None) -> List[MenuItem]:
        """获取显示的项目列表，确保菜单在前，命令在后"""
        menus = []
        commands = []
        
        for item in self.items:
            if isinstance(item, str):
                # 如果是字符串ID，需要从menu_system中获取实际项目
                if menu_system:
                    menu_item = menu_system.get_item_by_id(item)
                    if menu_item and menu_item.enabled:
                        if isinstance(menu_item, MenuNode):
                            menus.append(menu_item)
                        else:
                            commands.append(menu_item)
            elif isinstance(item, (MenuItem, MenuNode)) and item.enabled:
                if isinstance(item, MenuNode):
                    menus.append(item)
                else:
                    commands.append(item)
        
        # 菜单在前，命令在后
        return menus + commands


class MenuSystem:
    """菜单系统管理类"""
    
    def __init__(self, console: Console):
        self.console = console
        self.current_menu: Optional[MenuNode] = None
        self.menu_history: List[MenuNode] = []
        self.items: Dict[str, Union[MenuItem, MenuNode]] = {}
        self.start_time = time.time()

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

    def _init_fixed_items(self):
        """初始化固定项目"""
        # 清屏
        self.register_item(ActionItem(
            id="clear_screen",
            name="清屏",
            description="清除屏幕内容",
            icon="🧹",
            command_type=CommandType.SHELL,
            command="cls" if sys.platform == 'win32' else "clear"
        ))

        # 帮助
        self.register_item(MenuItem(
            id="show_help",
            name="帮助",
            description="显示帮助信息",
            icon="📚"
        ))

        # 退出
        self.register_item(ActionItem(
            id="exit_app",
            name="退出程序",
            description="安全退出程序",
            icon="⚡",
            command_type=CommandType.SHELL,
            command="echo 正在退出..."
        ))

    def register_item(self, item: Union[MenuItem, MenuNode]):
        """注册菜单项
        
        注意：每个插件只能注册一个主菜单（MenuType.MAIN）。
        """
        self.items[item.id] = item
        return item
    
    def create_main_menu(self, menu_id: str, name: str, description: str = "", icon: str = "🏠") -> MenuNode:
        """创建主菜单
        
        注意：每个插件只能注册一个主菜单。
        
        Args:
            menu_id: 菜单ID
            name: 菜单名称
            description: 菜单描述
            icon: 菜单图标
            
        Returns:
            MenuNode: 创建的主菜单节点
        """
        main_menu = MenuNode(
            id=menu_id,
            name=name,
            description=description,
            menu_type=MenuType.MAIN,
            icon=icon
        )
        self.register_item(main_menu)
        return main_menu

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
            return True
        return False

    def go_back(self) -> bool:
        """返回上一级菜单"""
        if self.menu_history:
            self.current_menu = self.menu_history.pop()
            return True
        return False

    def go_to_root(self):
        """返回主菜单"""
        while self.go_back():
            pass
        return True

    def execute_action(self, action: ActionItem) -> str:
        """执行动作"""
        try:
            start_time = time.time()
            output = action.execute()
            execution_time = time.time() - start_time

            time_msg = f"执行时间: {execution_time:.2f}秒"
            result = f"⏱️  {time_msg}\n"
            result += "─" * 70 + "\n\n"
            # 确保output是字符串，避免NoneType错误
            result += str(output) if output is not None else ""

            return result
        except Exception as e:
            return f"执行过程中发生错误:\n\n[red]{str(e)}[/red]"

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
    
    def remove_item_from_main_menu(self, item: Union[str, MenuItem, MenuNode]) -> bool:
        """从主菜单移除菜单项"""
        main_menu = self.get_item_by_id("main_menu")
        if isinstance(main_menu, MenuNode):
            main_menu.remove_item(item)
            return True
        return False
    
    def remove_item(self, item_id: str) -> bool:
        """从菜单系统中移除菜单项"""
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False
    
    def remove_item_from_menu(self, menu_id: str, item: Union[str, MenuItem, MenuNode]) -> bool:
        """从指定菜单移除菜单项"""
        menu = self.get_item_by_id(menu_id)
        if isinstance(menu, MenuNode):
            menu.remove_item(item)
            return True
        return False
    
    def add_action(self, action: ActionItem):
        """添加动作项到菜单系统，用于插件注册"""
        # 注册动作项
        self.register_item(action)
        
        # 检查是否需要创建插件分类菜单
        category = action.category
        
        # 尝试获取主菜单
        main_menu = self.get_item_by_id("main_menu")
        if not isinstance(main_menu, MenuNode):
            return
        
        # 检查是否已存在该分类的菜单
        category_menu_id = f"menu_{category.lower().replace(' ', '_')}"
        category_menu = self.get_item_by_id(category_menu_id)
        
        if not isinstance(category_menu, MenuNode):
            # 创建分类菜单
            category_menu = self.create_submenu(
                menu_id=category_menu_id,
                name=category,
                description=f"{category}相关命令",
                icon="🔌"
            )
            # 将分类菜单添加到主菜单
            self.add_item_to_main_menu(category_menu_id)
        
        # 将动作项添加到分类菜单
        self.add_item_to_menu(category_menu_id, action.id)
