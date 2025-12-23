#!/usr/bin/env python3
"""
搜索功能模块
提供菜单项的搜索、历史记录管理功能
"""
from typing import List, Dict, Optional
from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from core.menu_system import MenuSystem, MenuItem, MenuNode


class SearchInterface:
    """搜索功能接口类

    主要功能：
    1. 搜索菜单项（支持名称、描述、分类搜索）
    2. 管理搜索历史记录
    3. 显示搜索结果并执行跳转
    4. 提供快速搜索功能
    """

    def __init__(self, menu_system: MenuSystem, console: Console, config_manager=None):
        """初始化搜索接口

        Args:
            menu_system: 菜单系统实例，包含所有菜单项
            console: Rich Console实例，用于输出美化内容
            config_manager: 配置管理器，可选，用于持久化搜索历史
        """
        self.menu_system = menu_system
        self.console = console
        self.config_manager = config_manager
        self.panel_width = 136  # 面板宽度，适应标准终端
        self.max_history = 20  # 最大历史记录数

        # 从配置加载搜索历史
        if self.config_manager:
            self.search_history = self.config_manager.get_search_history()
        else:
            self.search_history: List[str] = []  # 本地历史记录

    def search_items(self, keyword: str,
                     search_name: bool = True,
                     search_description: bool = True,
                     search_category: bool = False) -> List[MenuItem]:
        """搜索菜单项

        Args:
            keyword: 搜索关键词
            search_name: 是否搜索名称（默认True）
            search_description: 是否搜索描述（默认True）
            search_category: 是否搜索分类（默认False）

        Returns:
            List[MenuItem]: 匹配的菜单项列表

        Note:
            搜索结果会自动添加到搜索历史记录中
        """
        results = []
        keyword_lower = keyword.lower()

        # 遍历所有启用的菜单项
        for item in self.menu_system.items.values():
            if not item.enabled:
                continue

            match = False

            # 搜索名称（不区分大小写）
            if search_name and keyword_lower in item.name.lower():
                match = True

            # 搜索描述（不区分大小写）
            if not match and search_description and keyword_lower in item.description.lower():
                match = True

            # 搜索分类（不区分大小写）
            if not match and search_category and hasattr(item, 'category'):
                if keyword_lower in item.category.lower():
                    match = True

            if match:
                results.append(item)

        # 保存到搜索历史（去重）
        if keyword and keyword not in self.search_history:
            if self.config_manager:
                self.config_manager.add_search_history(keyword)
                # 更新本地历史记录
                self.search_history = self.config_manager.get_search_history()
            else:
                self.search_history.append(keyword)
                # 限制历史记录数量
                if len(self.search_history) > self.max_history:
                    self.search_history.pop(0)

        return results

    def show_search_interface(self):
        """显示搜索主界面

        功能：
        1. 显示搜索历史
        2. 接收用户输入的关键词
        3. 执行搜索并显示结果
        4. 提供搜索提示

        UI布局：
        - 标题面板
        - 历史记录面板（如果有历史）
        - 搜索输入面板
        - 搜索结果面板（如果有结果）
        """
        self.console.clear()

        # 1. 主标题面板
        title_panel = Panel(
            Text("菜单项搜索", style="bold cyan"),
            box=box.SIMPLE,
            border_style="cyan",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 2. 搜索历史面板（如果存在历史记录）
        if self.search_history:
            history_table = Table(
                show_header=False,
                box=box.SIMPLE,
                border_style="blue",
                show_edge=True,
                width=self.panel_width - 2,
                padding=(1, 2)
            )
            history_table.add_column("", style="dim", width=self.panel_width - 6)
            # 只显示最近5条历史
            history_text = "最近搜索: " + " | ".join(self.search_history[-5:])
            history_table.add_row(history_text)

            history_panel = Panel(
                history_table,
                title="搜索历史",
                border_style="blue",
                box=box.ROUNDED,
                padding=(0, 0),
                width=self.panel_width
            )

            self.console.print(history_panel)
            self.console.print()

        # 3. 搜索输入面板
        input_panel = Panel(
            Text("请输入搜索关键词", style="bold white", justify="center"),
            subtitle="输入关键词开始搜索，直接回车返回",
            subtitle_align="left",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
            width=self.panel_width
        )
        self.console.print(input_panel)
        self.console.print()

        # 4. 获取搜索关键词
        self.console.print("搜索关键词: ", style="bold cyan", end="")
        keyword = input().strip()

        # 空输入返回上级
        if not keyword:
            return

        # 5. 执行搜索
        results = self.search_items(keyword)

        # 6. 显示结果或无结果提示
        if results:
            self._display_search_results(results, keyword)
        else:
            self._show_search_no_results(keyword)

    def _display_search_results(self, results: List[MenuItem], keyword: str):
        """显示搜索结果

        Args:
            results: 搜索结果列表
            keyword: 搜索关键词

        UI布局：
        - 结果标题面板
        - 结果表格（显示前20个结果）
        - 操作提示

        用户操作：
        - 输入编号：跳转到对应菜单项
        - 输入ID：跳转到对应菜单项
        - b：返回搜索界面
        - h：查看搜索历史
        - 回车：返回上级
        """
        self.console.clear()

        # 1. 结果标题面板
        title_panel = Panel(
            Text(f"搜索结果: '{keyword}'", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 2. 创建结果表格
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
            border_style="blue",
            show_lines=False,
            collapse_padding=True,
            pad_edge=False,
            padding=(0, 0),
            width=self.panel_width - 2
        )

        # 计算列宽（总计134字符）
        table.add_column("编号", style="cyan", justify="center", width=8)
        table.add_column("ID", style="cyan bold", width=25)
        table.add_column("名称", style="bold white", width=30)
        table.add_column("类型", style="green", justify="center", width=12)
        table.add_column("描述", style="yellow", width=59)

        # 3. 填充表格数据（最多显示20个）
        display_count = min(len(results), 20)
        for i, item in enumerate(results[:display_count], 1):
            # 高亮关键词
            name = self._highlight_keyword(item.name, keyword)
            description = self._highlight_keyword(item.description, keyword)

            # 确定类型
            if isinstance(item, MenuNode):
                item_type = "菜单"
                type_style = "bold cyan"
            else:
                item_type = "命令"
                type_style = "green"

            # 缩短过长的描述
            if len(description) > 70:
                description = description[:67] + "..."

            table.add_row(
                f"{i}",
                item.id,
                name,
                Text(item_type, style=type_style),
                description
            )

        # 4. 构建副标题信息
        subtitle_parts = []
        if len(results) > 20:
            subtitle_parts.append(f"还有 {len(results) - 20} 个结果未显示")
        subtitle_parts.append("输入编号或ID执行，b: 返回搜索，h: 查看历史，直接回车返回")

        # 5. 创建结果面板
        results_panel = Panel(
            table,
            title=f"找到 {len(results)} 个结果 (显示前 {display_count} 个)",
            subtitle=" | ".join(subtitle_parts),
            subtitle_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
            width=self.panel_width
        )

        self.console.print(results_panel)
        self.console.print()

        # 6. 处理用户选择
        while True:
            self.console.print("请输入选择: ", style="bold green", end="")
            choice = input().strip()

            if not choice:
                # 回车返回上级
                break
            elif choice.lower() == 'b':
                # 返回搜索界面
                self.show_search_interface()
                return
            elif choice.lower() == 'h':
                # 查看搜索历史
                self.show_search_history_interface()
                # 返回当前搜索结果
                self._display_search_results(results, keyword)
                continue

            try:
                # 尝试按编号选择
                idx = int(choice) - 1
                if 0 <= idx < len(results):
                    selected_item = results[idx]
                    # 直接执行跳转
                    self._execute_search_result(selected_item)
                    return  # 跳转后不会返回这里
                else:
                    self.console.print(f"[red]无效的编号，请输入 1-{min(len(results), 20)}[/red]")
                    continue
            except ValueError:
                # 尝试按ID选择
                for item in results:
                    if item.id == choice:
                        # 直接执行跳转
                        self._execute_search_result(item)
                        return  # 跳转后不会返回这里

                self.console.print(f"[red]未找到ID为 '{choice}' 的项目[/red]")

    def _show_search_no_results(self, keyword: str):
        """显示无搜索结果

        Args:
            keyword: 搜索关键词

        UI布局：
        - 无结果提示面板
        - 搜索提示信息
        """
        self.console.clear()

        # 1. 标题面板
        title_panel = Panel(
            Text(f"搜索结果: '{keyword}'", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 2. 创建提示表格
        tips_table = Table(
            show_header=False,
            box=box.SIMPLE,
            border_style="yellow",
            show_lines=False,
            collapse_padding=True,
            pad_edge=False,
            padding=(0, 0),
            width=self.panel_width - 2
        )
        tips_table.add_column("", style="yellow", width=self.panel_width - 2)
        tips_table.add_row(f"未找到包含 '{keyword}' 的菜单项")
        tips_table.add_row("")
        tips_table.add_row("💡 搜索提示:")
        tips_table.add_row("  • 尝试不同的关键词")
        tips_table.add_row("  • 检查拼写是否正确")
        tips_table.add_row("  • 搜索范围包括名称和描述")

        # 3. 创建提示面板
        tips_panel = Panel(
            tips_table,
            title="搜索结果",
            subtitle="b: 返回搜索 | h: 查看搜索历史 | 直接回车返回",
            subtitle_align="left",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(0, 1),
            width=self.panel_width
        )

        self.console.print(tips_panel)
        self.console.print()

        # 4. 处理用户输入
        self.console.print("请输入命令: ", style="bold green", end="")
        choice = input().strip().lower()

        if choice == 'b':
            # 返回搜索界面
            self.show_search_interface()
        elif choice == 'h':
            # 查看搜索历史
            self.show_search_history_interface()
            # 返回无结果界面
            self._show_search_no_results(keyword)

    def _highlight_keyword(self, text: str, keyword: str) -> str:
        """高亮显示关键词

        Args:
            text: 原始文本
            keyword: 需要高亮的关键词

        Returns:
            str: 包含Rich格式的高亮文本

        Example:
            text = "Hello World"
            keyword = "world"
            return "[bold yellow]World[/bold yellow]" (部分)
        """
        if not keyword:
            return text

        keyword_lower = keyword.lower()
        text_lower = text.lower()

        # 查找所有匹配位置
        positions = []
        start = 0
        while True:
            pos = text_lower.find(keyword_lower, start)
            if pos == -1:
                break
            positions.append((pos, pos + len(keyword_lower)))
            start = pos + 1

        if not positions:
            return text

        # 构建高亮文本
        result = []
        last_pos = 0

        for start, end in positions:
            # 添加前面的文本
            if start > last_pos:
                result.append(text[last_pos:start])

            # 添加高亮的关键词
            result.append(f"[bold yellow]{text[start:end]}[/bold yellow]")
            last_pos = end

        # 添加剩余的文本
        if last_pos < len(text):
            result.append(text[last_pos:])

        return "".join(result)

    def _execute_search_result(self, item: MenuItem):
        """执行搜索结果（直接跳转/执行）

        Args:
            item: 要执行的菜单项

        功能：
        1. 如果是菜单项：直接导航到对应菜单
        2. 如果是命令项：直接执行命令
        3. 不显示确认面板，直接跳转

        Note:
            这是修改后的核心逻辑，移除了确认面板和等待输入
        """
        from core.menu_system import MenuNode, ActionItem
        import time  # 用于短暂延迟显示信息

        self.console.clear()

        # 1. 显示跳转标题
        title_panel = Panel(
            Text(f"跳转到: {item.name}", style="bold green"),
            box=box.SIMPLE,
            border_style="green",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 2. 显示简要跳转信息（不等待确认）
        if isinstance(item, MenuNode):
            # 菜单项跳转信息
            info_text = Text(f"正在导航到菜单: ", style="cyan") + \
                        Text(item.name, style="bold white")
        else:
            # 命令项执行信息
            info_text = Text(f"正在执行命令: ", style="cyan") + \
                        Text(item.name, style="bold white")

        info_panel = Panel(
            info_text,
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
            width=self.panel_width
        )

        self.console.print(info_panel)
        self.console.print()

        # 3. 短暂延迟让用户看到跳转信息（300ms）
        time.sleep(0.3)

        # 4. 执行跳转或命令
        if isinstance(item, MenuNode):
            # 4.1 菜单项：直接导航
            # menu_system会自动显示目标菜单内容
            self.menu_system.navigate_to_menu(item.id)
            # 导航后停留在目标菜单，不需要返回

        elif hasattr(item, 'execute') and callable(item.execute):
            # 4.2 命令项：执行并返回结果
            try:
                # 执行命令
                output = item.execute()

                if output:
                    # 显示执行结果
                    self.console.clear()
                    self.console.print(title_panel)
                    self.console.print()

                    # 创建结果面板
                    result_panel = Panel(
                        Text(output, style="white"),
                        title="执行结果",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(1, 2),
                        width=self.panel_width
                    )
                    self.console.print(result_panel)
                    self.console.print()

                    # 显示返回提示
                    self.console.print("命令执行完成，1秒后返回搜索界面...", style="yellow")
                    time.sleep(1)

                # 命令执行完成后返回搜索界面
                self.show_search_interface()

            except Exception as e:
                # 命令执行失败
                self.console.clear()
                self.console.print(title_panel)
                self.console.print()

                # 显示错误信息
                error_panel = Panel(
                    Text(f"执行失败: {str(e)}", style="red"),
                    title="执行错误",
                    border_style="red",
                    box=box.ROUNDED,
                    padding=(1, 2),
                    width=self.panel_width
                )
                self.console.print(error_panel)
                self.console.print()

                # 显示返回提示
                self.console.print("按任意键返回搜索界面...", style="yellow")
                self._wait_for_keypress()
                self.show_search_interface()

    def show_search_history_interface(self):
        """显示搜索历史界面

        功能：
        1. 显示所有搜索历史记录
        2. 支持从历史记录重新搜索
        3. 支持清除历史记录

        UI布局：
        - 历史记录标题
        - 历史记录表格
        - 操作提示
        """
        self.console.clear()

        # 1. 标题面板
        title_panel = Panel(
            Text("搜索历史", style="bold cyan"),
            box=box.SIMPLE,
            border_style="cyan",
            padding=(0, 0),
            width=self.panel_width
        )
        self.console.print(title_panel)
        self.console.print()

        # 2. 检查是否有历史记录
        if not self.search_history:
            no_history_panel = Panel(
                Text("暂无搜索历史", style="yellow", justify="center"),
                border_style="yellow",
                box=box.ROUNDED,
                padding=(2, 2),
                width=self.panel_width
            )
            self.console.print(no_history_panel)
            self.console.print()
            self._wait_for_keypress()
            return

        # 3. 创建历史记录表格
        history_table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
            border_style="blue",
            show_lines=False,
            collapse_padding=True,
            pad_edge=False,
            padding=(0, 0),
            width=self.panel_width - 2
        )

        # 计算列宽
        history_table.add_column("编号", style="cyan", justify="center", width=8)
        history_table.add_column("搜索关键词", style="bold white", width=80)
        history_table.add_column("操作", style="green", justify="center", width=46)

        # 4. 填充历史记录（逆序显示，最新的在最上面）
        for i, keyword in enumerate(reversed(self.search_history), 1):
            # 操作按钮文本
            actions = Text("🔍 搜索", style="green")

            history_table.add_row(
                f"{i}",
                keyword,
                actions
            )

        # 5. 创建历史记录面板
        history_panel = Panel(
            history_table,
            title=f"共 {len(self.search_history)} 条搜索历史",
            subtitle="输入编号执行搜索 | c: 清除历史 | 直接回车返回",
            subtitle_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
            width=self.panel_width
        )

        self.console.print(history_panel)
        self.console.print()

        # 6. 处理用户选择
        while True:
            self.console.print("请输入选择: ", style="bold green", end="")
            choice = input().strip().lower()

            if not choice:
                # 回车返回
                return
            elif choice == 'c':
                # 清除历史
                if Confirm.ask("确定要清除所有搜索历史吗？"):
                    self.clear_search_history()
                    # 重新显示历史界面（会显示"暂无历史"）
                    self.show_search_history_interface()
                return
            else:
                try:
                    # 尝试按编号选择
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.search_history):
                        # 从历史记录中获取关键词（逆序）
                        keyword = list(reversed(self.search_history))[idx]
                        # 执行搜索
                        results = self.search_items(keyword)

                        if results:
                            # 显示搜索结果
                            self._display_search_results(results, keyword)
                        else:
                            # 显示无结果
                            self._show_search_no_results(keyword)
                        return
                    else:
                        self.console.print(f"[red]无效的编号，请输入 1-{len(self.search_history)}[/red]")
                except ValueError:
                    # 检查是否为有效的关键词
                    if choice in self.search_history:
                        # 直接按关键词搜索
                        results = self.search_items(choice)

                        if results:
                            self._display_search_results(results, choice)
                        else:
                            self._show_search_no_results(choice)
                        return
                    else:
                        self.console.print("[red]无效的选择[/red]")

    def clear_search_history(self):
        """清除搜索历史记录

        功能：
        1. 清除本地历史记录
        2. 如果配置管理器存在，清除持久化历史
        3. 显示清除成功消息
        """
        if self.config_manager:
            # 清除持久化存储
            self.config_manager.clear_search_history()
            # 更新本地记录
            self.search_history = self.config_manager.get_search_history()
        else:
            # 清除本地记录
            self.search_history.clear()

        # 显示成功消息
        success_panel = Panel(
            Text("搜索历史已清除", style="green", justify="center"),
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
            width=self.panel_width
        )
        self.console.print(success_panel)
        self.console.print()

        # 短暂显示消息
        import time
        time.sleep(0.5)

    def quick_search(self, keyword: str) -> Optional[MenuItem]:
        """快速搜索（返回第一个匹配项）

        Args:
            keyword: 搜索关键词

        Returns:
            Optional[MenuItem]: 第一个匹配的菜单项，无匹配返回None

        Note:
            用于程序内部调用的快速搜索，不保存历史记录
        """
        results = self.search_items(keyword)
        if results:
            return results[0]
        return None

    def _wait_for_keypress(self):
        """等待用户按键继续

        功能：
        1. 跨平台的按键等待
        2. Windows使用msvcrt
        3. Linux/Mac使用termios

        Note:
            只在需要用户确认的场景调用
        """
        import sys

        if sys.platform == "win32":
            # Windows平台
            import msvcrt
            msvcrt.getch()
        else:
            # Unix/Linux/Mac平台
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _show_message(self, message: str, color: str = "white"):
        """显示消息面板（传统方法）

        Args:
            message: 消息内容
            color: 边框颜色

        Note:
            已弃用，在新逻辑中不推荐使用
            保留用于兼容性
        """
        message_panel = Panel(
            Text(message, justify="center"),
            subtitle="按任意键继续...",
            subtitle_align="left",
            border_style=color,
            box=box.ROUNDED,
            padding=(1, 2),
            width=self.panel_width
        )
        self.console.print(message_panel)
        self._wait_for_keypress()