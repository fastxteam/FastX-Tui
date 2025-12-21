#!/usr/bin/env python3
"""
FastX-Tui 帮助功能界面模块 - 修复版
"""
from typing import Dict, Any
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.layout import Layout
from rich.text import Text
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.columns import Columns
from rich.console import Group
from rich.prompt import Prompt, Confirm, IntPrompt
from rich import box
from rich.style import Style
from rich.box import ROUNDED, HEAVY
from rich.live import Live

# 平台兼容：根据操作系统选择不同的键盘输入处理方式
if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty


class HelpFeature:
    """帮助功能实现"""

    def __init__(self, console: Console):
        self.console = console
        self.current_page = "basic"  # 当前页面
        self.sections = {
            "basic": {"name": "基本信息", "icon": ""},
            "short": {"name": "常用快捷键", "icon": ""},
            "navi": {"name": "菜单导航", "icon": ""},
            "feat": {"name": "主要功能", "icon": ""},
            "plug": {"name": "插件开发", "icon": ""},
            "plapi": {"name": "插件API", "icon": ""}
        }
        self.running = True

    def get_version(self) -> str:
        """获取版本信息"""
        try:
            from core.version import FULL_VERSION
            return FULL_VERSION
        except ImportError:
            return "v0.1.0"

    def create_layout(self) -> Layout:
        """创建基础布局"""
        layout = Layout()

        # 创建主内容区域，不显示边距区域名称
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )

        # 使用1:3的比例设置侧边栏和内容区，确保侧边栏占1/4，内容区占3/4
        layout["main"].split_row(
            Layout(name="sidebar", ratio=1),
            Layout(name="content", ratio=3)
        )

        return layout

    def update_header(self) -> Panel:
        """创建头部Panel"""
        title = f"FastX-Tui 帮助系统"
        section_name = self.sections[self.current_page]["name"]

        return Panel(
            f"{title} - {section_name}",
            style="bold blue",
            subtitle="按数字键或方向键切换帮助部分",
            box=HEAVY
        )

    def update_sidebar(self) -> Panel:
        """创建侧边栏Panel"""
        nav_text = "[bold]导航菜单[/bold]\n\n"

        # 生成导航项目
        for i, (page_key, section) in enumerate(self.sections.items(), 1):
            name = section['name']
            shortcut = str(i)

            if page_key == self.current_page:
                nav_text += f"[bold green]> {shortcut} - {name}[/bold green]\n"
            else:
                nav_text += f"  {shortcut} - {name}\n"

        # 添加退出选项
        nav_text += f"  q - 退出\n"

        return Panel(
            nav_text.strip(),
            title="帮助目录",
            border_style="green",
            box=ROUNDED
        )

    def update_content(self) -> Panel:
        """根据当前页面创建内容Panel"""
        if self.current_page == "basic":
            return self._create_basic_info()
        elif self.current_page == "short":
            return self._create_shortcuts()
        elif self.current_page == "navi":
            return self._create_navigation()
        elif self.current_page == "feat":
            return self._create_features()
        elif self.current_page == "plug":
            return self._create_plugin_development()
        elif self.current_page == "plapi":
            return self._create_plugin_api()
        else:
            return Panel("未知页面", border_style="red")

    def update_footer(self) -> Panel:
        """创建底部状态栏Panel"""
        status = f"当前页面: {self.current_page} | 快捷键: 1-{len(self.sections)}切换, q退出"
        return Panel(
            status,
            style="dim",
            box=ROUNDED
        )

    def create_full_display(self) -> Layout:
        """创建完整的显示布局"""
        layout = self.create_layout()
        layout["header"].update(self.update_header())
        layout["sidebar"].update(self.update_sidebar())
        layout["content"].update(self.update_content())
        layout["footer"].update(self.update_footer())
        return layout

    def _getch(self) -> str:
        """获取单个按键输入，兼容Windows和Unix系统"""
        if sys.platform == 'win32':
            # Windows平台使用msvcrt
            ch = msvcrt.getch()
            if ch == b'\x03':  # Ctrl+C
                raise KeyboardInterrupt
            if ch == b'\xe0':  # Windows方向键前缀
                ch2 = msvcrt.getch()
                if ch2 == b'K':  # 左
                    return 'left'
                elif ch2 == b'M':  # 右
                    return 'right'
                elif ch2 == b'H':  # 上
                    return 'up'
                elif ch2 == b'P':  # 下
                    return 'down'
                else:
                    return ch.decode('latin-1', errors='ignore')
            # 使用latin-1编码处理特殊字符
            return ch.decode('latin-1', errors='ignore')
        else:
            # Unix平台使用termios/tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)

                # 处理方向键
                if ch == '\x1b':  # ESC键
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':  # CSI序列
                        ch3 = sys.stdin.read(1)
                        if ch3 == 'D':
                            return 'left'
                        elif ch3 == 'C':
                            return 'right'
                        elif ch3 == 'A':
                            return 'up'
                        elif ch3 == 'B':
                            return 'down'
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def handle_input(self):
        """处理用户输入"""
        # 使用Live实现无闪屏更新
        with Live(self.create_full_display(), console=self.console, refresh_per_second=10, screen=True) as live:
            while self.running:
                # 更新显示
                live.update(self.create_full_display())

                # 获取按键输入
                ch = self._getch()

                # 退出处理
                if ch in ['q', 'Q', '\x03']:  # q或Ctrl+C
                    self.running = False
                    break

                # 数字键处理
                if ch.isdigit():
                    section_index = int(ch) - 1
                    if 0 <= section_index < len(self.sections):
                        self.current_page = list(self.sections.keys())[section_index]

                # 方向键处理
                elif ch == 'left':
                    current_index = list(self.sections.keys()).index(self.current_page)
                    new_index = (current_index - 1) % len(self.sections)
                    self.current_page = list(self.sections.keys())[new_index]

                elif ch == 'right':
                    current_index = list(self.sections.keys()).index(self.current_page)
                    new_index = (current_index + 1) % len(self.sections)
                    self.current_page = list(self.sections.keys())[new_index]

                elif ch == 'up':
                    # 上箭头暂时不用
                    pass

                elif ch == 'down':
                    # 下箭头暂时不用
                    pass

    def show_help(self):
        """显示帮助信息"""
        self.console.clear()
        self.handle_input()
        self.console.clear()

    def _create_basic_info(self) -> Panel:
        """创建基本信息Panel"""
        # 创建基本信息表格
        table = Table(box=ROUNDED, border_style="green")
        table.add_column("项目", style="bold", width=10)
        table.add_column("信息")

        table.add_row("名称", "FastX-Tui")
        table.add_row("版本", self.get_version())
        table.add_row("作者", "FastXTeam")
        table.add_row("描述", "一个功能强大的终端工具集")

        return Panel(
            table,
            border_style="green",
            box=ROUNDED,
            padding=(1, 2),
            title="基本信息"
        )

    def _create_shortcuts(self) -> Panel:
        """创建快捷键Panel"""
        # 创建快捷键表格
        table = Table(box=ROUNDED, border_style="yellow")
        table.add_column("按键", style="bold yellow", width=10)
        table.add_column("功能描述")

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
            table.add_row(f"[yellow]{key}[/yellow]", desc)

        return Panel(
            table,
            border_style="yellow",
            box=ROUNDED,
            padding=(1, 2),
            title="常用快捷键"
        )

    def _create_navigation(self) -> Panel:
        """创建导航帮助Panel"""
        # 创建导航指南树
        tree = Tree("菜单导航指南", guide_style="cyan")
        tree.expand = True

        tree.add("输入数字选择菜单项").add("在每个菜单中，输入对应的数字来选择功能")
        tree.add("返回上一级菜单").add("在非主菜单中输入 0 返回上一级菜单")
        tree.add("继续操作").add("执行命令后，按回车键继续回到菜单")
        tree.add("直接访问功能").add("使用快捷键可以直接访问相应功能，无需通过菜单导航")

        return Panel(
            tree,
            border_style="blue",
            box=ROUNDED,
            padding=(1, 2),
            title="菜单导航"
        )

    def _create_features(self) -> Panel:
        """创建主要功能Panel"""
        # 创建各个功能模块的Panel
        platform_panel = Panel(
            "平台提供的通用工具集，包含系统工具、文件工具、Python工具",
            title="平台工具",
            border_style="cyan",
            box=ROUNDED,
            padding=(1, 2)
        )

        system_panel = Panel(
            "查看系统信息、网络信息、进程列表、磁盘空间、系统运行时间",
            title="系统工具",
            border_style="green",
            box=ROUNDED,
            padding=(1, 2)
        )

        file_panel = Panel(
            "目录列表、文件树、文件搜索",
            title="文件工具",
            border_style="yellow",
            box=ROUNDED,
            padding=(1, 2)
        )

        python_panel = Panel(
            "Python环境信息、已安装包列表、检查导入",
            title="Python工具",
            border_style="purple",
            box=ROUNDED,
            padding=(1, 2)
        )

        config_panel = Panel(
            "查看和修改应用配置",
            title="配置管理",
            border_style="yellow",
            box=ROUNDED,
            padding=(1, 2)
        )

        plugin_panel = Panel(
            "安装、卸载和管理插件",
            title="插件管理",
            border_style="green",
            box=ROUNDED,
            padding=(1, 2)
        )

        # 使用Columns布局排列这些Panel
        columns = Columns(
            [platform_panel, system_panel, file_panel, python_panel, config_panel, plugin_panel],
            equal=True,
            expand=True
        )

        # 创建主Panel
        return Panel(
            columns,
            border_style="green",
            box=ROUNDED,
            padding=(1, 2),
            title="主要功能"
        )

    def _create_plugin_development(self) -> Panel:
        """创建插件开发帮助Panel"""

        # 创建主树结构
        main_tree = Tree("📚 FastX-Tui 插件开发指南", guide_style="cyan")
        main_tree.expand = True

        # 1. 概述部分
        overview_branch = main_tree.add("📖 概述")
        overview_branch.add("• FastX-Tui 插件系统支持多文件结构、二进制文件和在线安装")
        overview_branch.add("• 为开发者提供了强大的扩展能力")
        overview_branch.add("• 本文档将指导您如何开发 FastX-Tui 插件")

        # 2. 插件结构部分
        structure_branch = main_tree.add("📁 插件结构")

        # 2.1 命名规范
        naming_branch = structure_branch.add("📝 命名规范")
        naming_branch.add("• 插件仓库必须使用格式: FastX-Tui-Plugin-{PluginName}")
        naming_branch.add("• PluginName 建议使用驼峰命名法 (如: MyAwesomePlugin)")

        # 2.2 目录结构
        dir_branch = structure_branch.add("🗂️ 目录结构")

        dir_structure = Tree("FastX-Tui-Plugin-{PluginName}/", guide_style="green")
        dir_structure.add("├── fastx_plugin.py          # 插件入口文件（必须）")
        dir_structure.add("├── pyproject.toml           # 插件元数据和依赖")
        dir_structure.add("├── README.md                # 插件说明文档")
        dir_structure.add("├── LICENSE                  # 许可证文件")
        dir_structure.add("├── resources/               # 资源文件目录（可选）")
        dir_structure.add("└── bin/                     # 二进制文件目录（可选）")

        dir_branch.add(dir_structure)

        # 3. 插件开发部分
        development_branch = main_tree.add("🛠️ 插件开发")

        # 3.1 创建插件目录
        create_branch = development_branch.add("1. 创建插件目录")
        create_branch.add("mkdir -p plugins/FastX-Tui-Plugin-{PluginName}")

        # 3.2 创建入口文件
        entry_branch = development_branch.add("2. 创建入口文件 (fastx_plugin.py)")
        entry_code = """#!/usr/bin/env python3
    from core.plugin_manager import Plugin, PluginInfo
    from core.menu_system import MenuSystem

    class {PluginName}Plugin(Plugin):
        \"\"\"{PluginName} 插件\"\"\"

        def get_info(self) -> PluginInfo:
            \"\"\"获取插件信息\"\"\"
            return PluginInfo(
                name="{PluginName}",
                version="1.0.0",
                author="Your Name",
                description="插件描述",
                category="插件分类",
                tags=["标签1", "标签2"]
            )

        def initialize(self):
            \"\"\"初始化插件\"\"\"
            pass

        def cleanup(self):
            \"\"\"清理插件资源\"\"\"
            pass

        def register(self, menu_system: MenuSystem):
            \"\"\"注册插件命令到菜单系统\"\"\"
            pass"""

        syntax = Syntax(
            entry_code,
            "python",
            theme="one-dark",
            line_numbers=True,
            word_wrap=True
        )
        entry_branch.add(syntax)

        # 3.3 必须实现的方法
        methods_branch = development_branch.add("3. 必须实现的方法")

        # 创建方法表格
        methods_table = Table(box=box.SIMPLE, show_header=True)
        methods_table.add_column("方法名", style="cyan")
        methods_table.add_column("描述", style="green")
        methods_table.add_column("必须实现", style="bold")

        methods_table.add_row("get_info()", "返回插件信息 (PluginInfo 对象)", "✅ 是")
        methods_table.add_row("initialize()", "初始化插件资源", "✅ 是")
        methods_table.add_row("cleanup()", "清理插件资源", "✅ 是")
        methods_table.add_row("register(menu_system)", "注册插件到菜单系统", "✅ 是")

        methods_branch.add(methods_table)

        # 3.4 注册菜单和命令
        register_branch = development_branch.add("4. 注册菜单和命令")

        register_code = """from core.menu_system import ActionItem, CommandType

    def register_commands(self, menu_system):
        # 创建子菜单
        submenu = menu_system.create_submenu(
            menu_id="plugin_submenu",
            name="插件菜单",
            description="插件的专属菜单"
        )

        # 注册命令
        menu_system.register_item(ActionItem(
            id="plugin_command",
            name="命令名称",
            description="命令描述",
            command_type=CommandType.PYTHON,
            python_func=self.my_command
        ))

        # 将命令添加到子菜单
        submenu.add_item("plugin_command")

    def my_command(self):
        return "命令执行结果"
        """

        register_branch.add(Syntax(register_code, "python", theme="one-dark", line_numbers=True))

        # 4. 插件信息部分
        info_branch = main_tree.add("📋 插件信息 (PluginInfo)")

        # 创建插件信息表格
        info_table = Table(title="PluginInfo 字段说明", box=box.ROUNDED, show_header=True)
        info_table.add_column("字段名", style="cyan")
        info_table.add_column("类型", style="dim")
        info_table.add_column("描述", style="green")
        info_table.add_column("默认值", style="yellow")

        info_fields = [
            ("name", "str", "插件名称", "[red]必填[/red]"),
            ("version", "str", "插件版本", "[red]必填[/red]"),
            ("author", "str", "插件作者", "[red]必填[/red]"),
            ("description", "str", "插件描述", "[red]必填[/red]"),
            ("enabled", "bool", "是否启用", "True"),
            ("category", "str", "插件分类", "\"其他\""),
            ("tags", "List[str]", "插件标签", "[]"),
            ("dependencies", "List[str]", "依赖项", "[]"),
            ("license", "str", "许可证", "\"MIT\""),
        ]

        for field, type_, desc, default in info_fields:
            info_table.add_row(field, type_, desc, default)

        info_branch.add(info_table)

        # 5. 依赖管理部分
        deps_branch = main_tree.add("📦 依赖管理")

        deps_code = """# pyproject.toml
    [project]
    name = "FastX-Tui-Plugin-MyPlugin"
    version = "1.0.0"
    description = "我的插件"
    dependencies = [
        "requests>=2.31.0",
        "numpy>=1.21.0",
    ]"""

        deps_branch.add(Syntax(deps_code, "toml", theme="one-dark", line_numbers=True))

        # 6. 最佳实践部分
        best_practices_branch = main_tree.add("📚 最佳实践")
        practices = [
            "分离关注点: 将配置和业务逻辑分离到不同的文件中",
            "使用类型提示: 为所有方法和参数添加类型提示",
            "编写文档: 为所有方法和类编写详细的文档字符串",
            "错误处理: 在插件中添加适当的错误处理",
            "资源管理: 及时清理插件使用的资源",
            "日志记录: 使用系统提供的日志接口",
            "兼容性: 在 compatibility 字段中声明兼容性要求",
            "依赖管理: 在 pyproject.toml 中声明依赖项"
        ]

        for practice in practices:
            best_practices_branch.add(f"• {practice}")

        # 7. 发布插件部分
        publish_branch = main_tree.add("🚀 发布插件")

        publish_steps = Tree("发布步骤:", guide_style="yellow")
        publish_steps.add("1. 确保插件命名符合规范")
        publish_steps.add("2. 包含所有必要文件")
        publish_steps.add("3. 声明依赖项 (pyproject.toml)")
        publish_steps.add("4. 编写详细 README.md")
        publish_steps.add("5. 推送到 GitHub 仓库")
        publish_steps.add("6. 联系官方添加到插件仓库")

        publish_branch.add(publish_steps)

        # 8. 示例部分
        example_branch = main_tree.add("📖 插件示例")
        example_branch.add("• 参考: plugins/FastX-Tui-Plugin-Example")
        example_branch.add("• 包含完整结构和实现方式")

        # 9. 联系方式
        contact_branch = main_tree.add("📞 联系方式")
        contacts = Tree("获取帮助:", guide_style="magenta")
        contacts.add("GitHub Issues: https://github.com/fastxteam/FastX-Tui/issues")
        contacts.add("邮件: team@fastx-tui.com")
        contacts.add("社区: https://discord.gg/fastx-tui")

        contact_branch.add(contacts)

        # 创建主面板
        return Panel(
            main_tree,
            border_style="green",
            box=ROUNDED,
            padding=(1, 2),
            title="插件开发指南",
            subtitle="使用方向键展开/折叠节点"
        )

    def _create_plugin_api(self) -> Panel:
        """创建插件API接口Panel - 修复版"""

        # 创建左侧内容（API文档）
        # API方法表格
        api_table = Table(title="插件API方法", box=ROUNDED, border_style="cyan")
        api_table.add_column("方法", style="bold cyan", width=15)
        api_table.add_column("说明", style="green")

        api_methods = [
            ("get_info()", "返回插件元数据信息"),
            ("register()", "注册插件功能到菜单系统"),
            ("initialize()", "插件初始化，准备资源"),
            ("cleanup()", "插件清理，释放资源")
        ]

        for method, desc in api_methods:
            api_table.add_row(method, desc)

        # PluginInfo属性表格
        info_table = Table(title="PluginInfo属性", box=ROUNDED, border_style="magenta")
        info_table.add_column("属性", style="bold magenta", width=15)
        info_table.add_column("类型", style="dim")
        info_table.add_column("说明", style="green")

        info_props = [
            ("name", "str", "插件名称"),
            ("version", "str", "插件版本"),
            ("author", "str", "插件作者"),
            ("description", "str", "插件描述"),
            ("enabled", "bool", "启用状态"),
            ("category", "str", "插件分类"),
            ("tags", "List[str]", "插件标签")
        ]

        for prop, type_, desc in info_props:
            info_table.add_row(prop, type_, desc)

        # 左侧面板内容 - 使用Group组成可渲染目标
        group = Group(
            api_table,
            "\n",  # 添加空行分隔
            info_table,
            "\n",
            f"""[bold]使用说明：[/bold]
1. 继承 [cyan]Plugin[/cyan] 基类
2. 实现所有必需方法
3. 在 [cyan]register()[/cyan] 中添加菜单项
4. 正确处理初始化和清理"""
        )

        # 右侧：代码示例
        example_code = """# 示例插件代码
    from core.plugin_manager import Plugin, PluginInfo
    from core.menu_system import MenuSystem
    from typing import Dict, Any


    class DemoPlugin(Plugin):
        \"\"\"演示插件\"\"\"

        def get_info(self) -> PluginInfo:
            \"\"\"返回插件信息\"\"\"
            return PluginInfo(
                name="演示插件",
                version="1.0.0",
                author="开发者",
                description="一个功能演示插件",
                enabled=True,
                category="工具",
                tags=["demo", "example"]
            )

        def register(self, menu_system: MenuSystem) -> None:
            \"\"\"注册菜单项\"\"\"
            # 创建主菜单
            main_menu = menu_system.add_menu(
                name="演示插件",
                description="插件功能演示"
            )

            # 添加菜单项
            main_menu.add_item(
                name="运行演示",
                description="运行插件功能",
                action=self.run_demo
            )

            main_menu.add_item(
                name="查看帮助",
                description="查看插件帮助",
                action=self.show_help
            )

        def initialize(self) -> None:
            \"\"\"初始化插件\"\"\"
            self.logger.info("演示插件初始化")

        def cleanup(self) -> None:
            \"\"\"清理插件\"\"\"
            self.logger.info("演示插件清理")

        def run_demo(self) -> None:
            \"\"\"运行演示功能\"\"\"
            self.console.print("[bold green]演示功能运行中...[/bold green]")

        def show_help(self) -> None:
            \"\"\"显示帮助\"\"\"
            self.console.print("[bold yellow]这里是帮助信息...[/bold yellow]")
    """

        # 使用Syntax渲染代码
        syntax = Syntax(
            example_code,
            "python",
            theme="material",
            line_numbers=True,
            word_wrap=False,  # 关闭自动换行，让横向滚动
            indent_guides=True,
            padding=(0, 0)
        )

        # 创建左右面板
        left_panel = Panel(
            group,
            title="API参考",
            border_style="cyan",
            box=ROUNDED,
            padding=(1, 1)
        )

        right_panel = Panel(
            syntax,
            title="代码示例",
            border_style="green",
            box=ROUNDED,
            padding=(0, 0)
        )

        # 使用Columns布局，指定宽度比例
        columns = Columns(
            [left_panel, right_panel],
            expand=True,
            equal=False
        )

        return Panel(
            columns,
            border_style="purple",
            box=ROUNDED,
            padding=(0, 0),
            title="插件API接口"
        )

# 测试代码
if __name__ == "__main__":
    console = Console()
    help_feature = HelpFeature(console)
    help_feature.show_help()