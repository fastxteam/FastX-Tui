#!/usr/bin/env python3
"""
搜索功能模块
"""
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import box
from core.menu_system import MenuSystem, MenuItem, MenuNode

class SearchFeature:
    """搜索功能"""
    
    def __init__(self, menu_system: MenuSystem, console: Console, config_manager=None):
        self.menu_system = menu_system
        self.console = console
        self.config_manager = config_manager
        self.max_history = 20
        
        # 从配置加载搜索历史
        if self.config_manager:
            self.search_history = self.config_manager.get_search_history()
        else:
            self.search_history: List[str] = []
    
    def search_items(self, keyword: str, 
                    search_name: bool = True,
                    search_description: bool = True,
                    search_category: bool = False) -> List[MenuItem]:
        """搜索菜单项"""
        results = []
        keyword_lower = keyword.lower()
        
        for item in self.menu_system.items.values():
            if not item.enabled:
                continue
            
            match = False
            
            # 搜索名称
            if search_name and keyword_lower in item.name.lower():
                match = True
            
            # 搜索描述
            if not match and search_description and keyword_lower in item.description.lower():
                match = True
            
            # 搜索分类
            if not match and search_category and hasattr(item, 'category'):
                if keyword_lower in item.category.lower():
                    match = True
            
            if match:
                results.append(item)
        
        # 添加到搜索历史
        if keyword and keyword not in self.search_history:
            if self.config_manager:
                self.config_manager.add_search_history(keyword)
                # 更新本地历史记录
                self.search_history = self.config_manager.get_search_history()
            else:
                self.search_history.append(keyword)
                if len(self.search_history) > self.max_history:
                    self.search_history.pop(0)
        
        return results
    
    def show_search_interface(self):
        """显示搜索界面"""
        self.console.clear()
        
        self.console.print("\n" + "=" * 70, style="cyan")
        self.console.print("🔍 菜单项搜索".center(70), style="cyan bold")
        self.console.print("=" * 70 + "\n", style="cyan")
        
        # 显示搜索历史
        if self.search_history:
            self.console.print("[dim]最近搜索:[/dim]", end=" ")
            self.console.print(" | ".join(self.search_history[-5:]), style="dim")
            self.console.print()
        
        # 获取搜索关键词
        keyword = Prompt.ask("[bold cyan]请输入搜索关键词[/bold cyan]")
        
        if not keyword:
            self.console.print("\n[yellow]搜索已取消[/yellow]")
            input("\n按任意键返回...")
            return
        
        # 执行搜索
        results = self.search_items(keyword)
        
        # 显示结果
        self.console.print("\n" + "=" * 70, style="green")
        self.console.print(f"搜索结果: '{keyword}'".center(70), style="green bold")
        self.console.print("=" * 70 + "\n", style="green")
        
        if results:
            self._display_search_results(results, keyword)
        else:
            self.console.print(f"[yellow]未找到包含 '{keyword}' 的菜单项[/yellow]")
            self.console.print("\n💡 提示:")
            self.console.print("  • 尝试不同的关键词")
            self.console.print("  • 检查拼写是否正确")
            self.console.print("  • 搜索范围包括名称和描述")
        
        self.console.print("\n" + "─" * 70, style="dim")
        self.console.print("[yellow]按任意键返回...[/yellow]")
        input()
    
    def _display_search_results(self, results: List[MenuItem], keyword: str):
        """显示搜索结果"""
        table = Table(
            title=f"找到 {len(results)} 个结果",
            box=box.SIMPLE,
            show_header=True,
            header_style="bold white",
            expand=True,
            show_lines=True,
            width=120  # 增加整体表格宽度
        )
        
        table.add_column("ID", style="cyan bold")
        # table.add_column("图标", style="white", justify="center")
        table.add_column("名称", style="white")
        table.add_column("类型", style="green")
        table.add_column("描述", style="yellow")
        
        for item in results[:20]:  # 只显示前20个结果
            # 高亮关键词
            name = self._highlight_keyword(item.name, keyword)
            description = self._highlight_keyword(item.description, keyword)
            
            # 确定类型
            if isinstance(item, MenuNode):
                item_type = "[菜单]"
                style = "bold cyan"
            else:
                item_type = "[命令]"
                style = ""
            
            table.add_row(
                item.id,
                # item.icon,
                name,
                item_type,
                description,
                style=style
            )
        
        self.console.print(table)
        
        if len(results) > 20:
            self.console.print(f"\n[yellow]... 还有 {len(results) - 20} 个结果未显示[/yellow]")
        
        # 显示操作提示
        self.console.print(f"\n💡 操作提示:")
        self.console.print(f"  输入 ID 可直接执行或跳转到该项目")
        self.console.print(f"  输入 'b' 返回搜索")
        self.console.print(f"  输入 'q' 退出")
        
        # 处理选择
        while True:
            choice = Prompt.ask(
                "\n[bold cyan]输入ID执行，或按回车返回[/bold cyan]",
                default=""
            ).strip()
            
            if not choice:
                break
            elif choice.lower() == 'q':
                self.console.print("\n[green]再见！[/green]\n")
                import sys
                sys.exit(0)
            elif choice.lower() == 'b':
                self.show_search_interface()
                break
            
            # 查找并执行项目
            for item in results:
                if item.id == choice:
                    self._execute_search_result(item)
                    return
            
            self.console.print(f"[red]未找到ID为 '{choice}' 的项目[/red]")
    
    def _highlight_keyword(self, text: str, keyword: str) -> str:
        """高亮显示关键词"""
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
        """执行搜索结果"""
        from core.menu_system import MenuNode, ActionItem
        
        if isinstance(item, MenuNode):
            # 如果是菜单，导航到该菜单
            self.menu_system.navigate_to_menu(item.id)
            self.console.print(f"\n✅ 已跳转到: {item.name}")
            input("\n按任意键继续...")
        
        elif isinstance(item, ActionItem):
            # 如果是动作项，执行它
            self.console.print(f"\n🚀 执行: {item.name}")
            self.console.print(f"📝 描述: {item.description}")
            self.console.print(f"\n⏳ 正在执行...\n")
            
            output = self.menu_system.execute_action(item)
            
            self.console.print("\n" + "=" * 70, style="green")
            self.console.print(f"执行完成: {item.name}".center(70), style="green bold")
            self.console.print("=" * 70 + "\n", style="green")
            self.console.print(output)
            
            self.console.print("\n" + "─" * 70, style="dim")
            self.console.print("[yellow]按任意键返回...[/yellow]")
            input()
    
    def quick_search(self, keyword: str) -> Optional[MenuItem]:
        """快速搜索（返回第一个匹配项）"""
        results = self.search_items(keyword)
        if results:
            return results[0]
        return None
    
    def show_search_history(self):
        """显示搜索历史"""
        self.console.print("\n" + "=" * 70, style="cyan")
        self.console.print("📜 搜索历史".center(70), style="cyan bold")
        self.console.print("=" * 70 + "\n", style="cyan")
        
        if not self.search_history:
            self.console.print("[yellow]暂无搜索历史[/yellow]")
        else:
            for i, keyword in enumerate(reversed(self.search_history), 1):
                self.console.print(f"{i:2d}. {keyword}")
        
        self.console.print("\n" + "─" * 70, style="dim")
        self.console.print("[yellow]按任意键返回...[/yellow]")
        input()
    
    def clear_search_history(self):
        """清除搜索历史"""
        if self.config_manager:
            self.config_manager.clear_search_history()
            # 更新本地历史记录
            self.search_history = self.config_manager.get_search_history()
        else:
            self.search_history.clear()
        self.console.print("\n✅ 搜索历史已清除")
        input("\n按任意键继续...")