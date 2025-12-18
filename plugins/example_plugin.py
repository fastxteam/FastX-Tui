# plugins/example_plugin.py
from core.plugin_manager import Plugin, PluginInfo
from core.menu_system import MenuSystem, ActionItem, CommandType

class ExamplePlugin(Plugin):
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="Demo Plugin",
            version="0.1.0",
            author="wanqiang.liu",
            description="这是一个展示动态菜单注册的示例插件"
        )
    
    def initialize(self):
        self.log_info("示例插件初始化完成")
    
    def cleanup(self):
        self.log_info("示例插件清理完成")
    
    def register(self, menu_system: MenuSystem):
        """展示三种不同的菜单注册方式"""
        
        # 1. 创建自己的子菜单
        self.create_own_submenu(menu_system)
        
        # 2. 添加命令到主菜单
        self.add_to_main_menu(menu_system)
        
        # 3. 添加命令到现有子菜单
        self.add_to_existing_submenu(menu_system)
    
    def create_own_submenu(self, menu_system: MenuSystem):
        """创建自己的子菜单并添加命令"""
        # 创建子菜单
        plugin_submenu = menu_system.create_submenu(
            menu_id="example_plugin_submenu",
            name="示例插件菜单",
            description="示例插件的专属菜单",
            icon="🔌"
        )
        
        # 添加命令到自己的子菜单
        menu_system.register_item(ActionItem(
            id="plugin_hello",
            name="插件问候",
            description="这是插件自己子菜单中的问候命令",
            command_type=CommandType.PYTHON,
            python_func=lambda: "Hello from plugin's own submenu!"
        ))
        
        menu_system.register_item(ActionItem(
            id="plugin_info",
            name="插件信息",
            description="显示插件信息",
            command_type=CommandType.PYTHON,
            python_func=lambda: "示例插件 v2.0.0 - 动态菜单注册演示"
        ))
        
        # 将命令添加到子菜单
        plugin_submenu.add_item("plugin_hello")
        plugin_submenu.add_item("plugin_info")
        
        # 将子菜单添加到主菜单
        menu_system.add_item_to_main_menu("example_plugin_submenu")
    
    def add_to_main_menu(self, menu_system: MenuSystem):
        """添加命令到主菜单"""
        # 注册命令
        menu_system.register_item(ActionItem(
            id="main_menu_command",
            name="主菜单命令",
            description="这是直接添加到主菜单的插件命令",
            icon="⭐",
            command_type=CommandType.PYTHON,
            python_func=lambda: "Hello from main menu command!"
        ))
        
        # 将命令添加到主菜单
        menu_system.add_item_to_main_menu("main_menu_command")
    
    def add_to_existing_submenu(self, menu_system: MenuSystem):
        """添加命令到现有子菜单"""
        # 注册命令
        menu_system.register_item(ActionItem(
            id="system_tool_command",
            name="系统工具命令",
            description="这是添加到系统工具菜单的插件命令",
            icon="🔧",
            command_type=CommandType.PYTHON,
            python_func=lambda: "Hello from system tools command!"
        ))
        
        # 将命令添加到系统工具菜单
        if not menu_system.add_item_to_menu("system_tools_menu", "system_tool_command"):
            self.log_warning("无法将命令添加到系统工具菜单")