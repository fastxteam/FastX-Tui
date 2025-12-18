#!/usr/bin/env python3
"""
基于pyi18n的语言管理器
"""
import os
import json
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass

@dataclass
class LanguageInfo:
    """语言信息"""
    code: str           # 语言代码，如 zh_CN, en_US
    name: str           # 显示名称
    native_name: str    # 本地名称
    enabled: bool = True
    rtl: bool = False   # 从右到左

class PyI18nLocaleManager:
    """基于pyi18n的语言管理器"""
    
    def __init__(self, 
                 locale_dir: str = "locales",
                 default_locale: str = "zh_CN",
                 available_locales: tuple = ("zh_CN", "en_US")):
        
        self.locale_dir = locale_dir
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.available_locales = available_locales
        
        # 语言信息映射
        self.language_info: Dict[str, LanguageInfo] = {}
        self._init_language_info()
        
        # 回调函数列表
        self.on_change_callbacks: List[Callable[[str, str], None]] = []
        
        # 创建目录
        os.makedirs(locale_dir, exist_ok=True)
        
        # 检查并创建默认语言文件
        self._ensure_default_locales()
        
        # 初始化pyi18n
        self.i18n = self._init_pyi18n()
        
        print(f"[i18n] 初始化完成，当前语言: {self.current_locale}")
    
    def _init_language_info(self):
        """初始化语言信息"""
        self.language_info = {
            "zh_CN": LanguageInfo(
                code="zh_CN",
                name="Chinese (Simplified)",
                native_name="简体中文",
                enabled=True
            ),
            "en_US": LanguageInfo(
                code="en_US",
                name="English (US)",
                native_name="English",
                enabled=True
            ),
            "ja_JP": LanguageInfo(
                code="ja_JP",
                name="Japanese",
                native_name="日本語",
                enabled=True
            ),
            "ko_KR": LanguageInfo(
                code="ko_KR",
                name="Korean",
                native_name="한국어",
                enabled=True
            ),
            "fr_FR": LanguageInfo(
                code="fr_FR",
                name="French",
                native_name="Français",
                enabled=False  # 默认禁用，需要翻译文件
            ),
            "es_ES": LanguageInfo(
                code="es_ES",
                name="Spanish",
                native_name="Español",
                enabled=False
            )
        }
    
    def _ensure_default_locales(self):
        """确保默认语言文件存在"""
        default_translations = {
            "zh_CN": self._get_zh_cn_translations(),
            "en_US": self._get_en_us_translations(),
            "ja_JP": self._get_ja_jp_translations(),
            "ko_KR": self._get_ko_kr_translations()
        }
        
        for locale_code, translations in default_translations.items():
            filepath = os.path.join(self.locale_dir, f"{locale_code}.json")
            if not os.path.exists(filepath):
                print(f"[i18n] 创建默认语言文件: {locale_code}")
                self._save_locale_file(locale_code, translations)
    
    def _init_pyi18n(self):
        """初始化国际化实例（使用内置回退实现）"""
        print(f"[i18n] 使用内置回退实现")
        return self._create_fallback_i18n()
    
    def _create_fallback_i18n(self):
        """创建回退的i18n实现"""
        class FallbackI18n:
            def __init__(self, manager):
                self.manager = manager
                self.translations = {}
                self._load_fallback_translations()
            
            def _load_fallback_translations(self):
                """加载回退翻译"""
                for locale_code in self.manager.available_locales:
                    filepath = os.path.join(self.manager.locale_dir, f"{locale_code}.json")
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            self.translations[locale_code] = json.load(f)
            
            def gettext(self, locale: str, key: str, **kwargs) -> str:
                """获取翻译文本"""
                def _get_translation(locale_code):
                    """内部函数：获取指定语言的翻译"""
                    if locale_code not in self.translations:
                        return None
                    
                    # 支持嵌套键 (如 "app.menu.main")
                    keys = key.split('.')
                    value = self.translations[locale_code]
                    
                    try:
                        for k in keys:
                            if isinstance(value, dict) and k in value:
                                value = value[k]
                            else:
                                return None
                        return value
                    except Exception as e:
                        print(f"[i18n] 翻译键解析失败: {key} ({locale_code}): {e}")
                        return None
                
                # 首先尝试获取当前语言的翻译
                value = _get_translation(locale)
                
                # 如果当前语言没有翻译，尝试默认语言
                if value is None and locale != self.manager.default_locale:
                    value = _get_translation(self.manager.default_locale)
                
                # 如果还是没有翻译，返回键本身
                if value is None:
                    print(f"[i18n] 翻译键未找到: {key} ({locale})")
                    return key
                
                # 格式化参数
                if kwargs and isinstance(value, str):
                    try:
                        return value.format(**kwargs)
                    except KeyError as e:
                        print(f"[i18n] 翻译格式化失败 - 缺少参数: {e} ({key}): {value}")
                        return value
                    except ValueError as e:
                        print(f"[i18n] 翻译格式化失败 - 格式错误: {e} ({key}): {value}")
                        return value
                    except Exception as e:
                        print(f"[i18n] 翻译格式化失败: {e} ({key}): {value}")
                        return value
                return str(value)
        
        return FallbackI18n(self)
    
    def _locale_file_exists(self, locale_code: str) -> bool:
        """检查语言文件是否存在"""
        filepath = os.path.join(self.locale_dir, f"{locale_code}.json")
        return os.path.exists(filepath)
    
    def _save_locale_file(self, locale_code: str, translations: Dict):
        """保存语言文件"""
        filepath = os.path.join(self.locale_dir, f"{locale_code}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(translations, f, indent=2, ensure_ascii=False)
    
    def t(self, key: str, default: str = None, **kwargs) -> str:
        """翻译文本（主方法）"""
        try:
            result = self.i18n.gettext(self.current_locale, key, **kwargs)
            # 如果返回的是键本身（未找到翻译），尝试默认语言
            if result == key and self.current_locale != self.default_locale:
                result = self.i18n.gettext(self.default_locale, key, **kwargs)
            
            # 如果还是未找到，使用默认值
            if result == key and default is not None:
                result = default
            
            return result
        except Exception as e:
            # 出错时返回默认值或键本身
            print(f"[i18n] 翻译失败 key='{key}': {str(e)}")
            return default if default is not None else key
    
    def translate(self, key: str, default: str = None, **kwargs) -> str:
        """翻译文本（别名）"""
        return self.t(key, default, **kwargs)
    
    def set_locale(self, locale_code: str, notify: bool = True) -> bool:
        """设置当前语言"""
        old_locale = self.current_locale
        
        # 检查语言是否可用
        if not self._is_locale_available(locale_code):
            print(f"[i18n] 语言不可用: {locale_code}")
            return False
        
        # 检查语言文件是否存在
        if not self._locale_file_exists(locale_code):
            print(f"[i18n] 语言文件不存在: {locale_code}")
            return False
        
        # 更新当前语言
        self.current_locale = locale_code
        
        # 通知回调
        if notify and old_locale != locale_code:
            self._notify_locale_change(old_locale, locale_code)
        
        print(f"[i18n] 语言切换: {old_locale} -> {locale_code}")
        return True
    
    def _is_locale_available(self, locale_code: str) -> bool:
        """检查语言是否可用"""
        if locale_code in self.language_info:
            return self.language_info[locale_code].enabled
        return False
    
    def _notify_locale_change(self, old_locale: str, new_locale: str):
        """通知语言变更"""
        for callback in self.on_change_callbacks:
            try:
                callback(old_locale, new_locale)
            except Exception as e:
                print(f"[i18n] 回调执行失败: {str(e)}")
    
    def register_change_callback(self, callback: Callable[[str, str], None]):
        """注册语言变更回调"""
        self.on_change_callbacks.append(callback)
    
    def unregister_change_callback(self, callback: Callable[[str, str], None]):
        """注销语言变更回调"""
        if callback in self.on_change_callbacks:
            self.on_change_callbacks.remove(callback)
    
    def get_locale(self) -> str:
        """获取当前语言"""
        return self.current_locale
    
    def get_available_locales(self) -> List[LanguageInfo]:
        """获取可用语言列表"""
        return [
            info for info in self.language_info.values() 
            if info.enabled and self._locale_file_exists(info.code)
        ]
    
    def get_enabled_locales(self) -> List[str]:
        """获取启用的语言代码列表"""
        return [info.code for info in self.get_available_locales()]
    
    def reload(self):
        """重新加载语言文件"""
        try:
            # 重新初始化pyi18n
            self.i18n = self._init_pyi18n()
            print(f"[i18n] 重新加载完成")
        except Exception as e:
            print(f"[i18n] 重新加载失败: {str(e)}")
    
    def get_translation(self, locale_code: str, key: str, **kwargs) -> str:
        """获取指定语言的翻译"""
        try:
            return self.i18n.gettext(locale_code, key, **kwargs)
        except:
            return key
    
    def has_translation(self, key: str, locale_code: str = None) -> bool:
        """检查是否有翻译"""
        check_locale = locale_code or self.current_locale
        try:
            result = self.i18n.gettext(check_locale, key)
            return result != key
        except:
            return False
    
    # 默认翻译数据
    def _get_zh_cn_translations(self) -> Dict:
        return {
            "app": {
                "name": "FastX TUI",
                "version": "v3.0",
                "description": "终端工具集",
                "author": "FastX Team",
                "welcome": "欢迎使用 {app_name} {version}",
                "exit": "退出程序",
                "exit_confirm": "确定要退出吗? (y/N)",
                "exit_thanks": "感谢使用，再见！",
                "help": "帮助",
                "clear": "清屏",
                "search": "搜索",
                "back": "返回",
                "back_upper": "返回上级",
                "back_main": "返回主菜单",
                "confirm": "确认",
                "cancel": "取消",
                "save": "保存",
                "load": "加载",
                "reset": "重置",
                "yes": "是",
                "no": "否",
                "ok": "确定",
                "error": "错误",
                "warning": "警告",
                "info": "信息",
                "success": "成功",
                "failed": "失败",
                "loading": "加载中...",
                "executing": "执行中...",
                "completed": "完成",
                "time": "时间",
                "size": "大小",
                "count": "数量",
                "total": "总计",
                "available": "可用",
                "used": "已用",
                "free": "空闲",
                "percent": "百分比"
            },
            "menu": {
                "main": "主菜单",
                "system": "系统工具",
                "file": "文件工具",
                "python": "Python工具",
                "network": "网络工具",
                "plugin": "插件管理",
                "config": "配置管理",
                "search": "搜索功能",
                "favorites": "我的收藏",
                "history": "历史记录"
            },
            "system": {
                "info": "系统信息",
                "info_desc": "显示详细的系统硬件和软件信息",
                "network": "网络信息",
                "network_desc": "显示网络接口和连接信息",
                "process": "进程列表",
                "process_desc": "显示当前运行的进程",
                "disk": "磁盘空间",
                "disk_desc": "显示磁盘使用情况",
                "uptime": "运行时间",
                "uptime_desc": "显示系统运行时间"
            },
            "file": {
                "list": "目录列表",
                "list_desc": "列出当前目录内容",
                "tree": "文件树",
                "tree_desc": "显示目录树结构",
                "search": "文件搜索",
                "search_desc": "搜索指定类型的文件"
            },
            "python": {
                "info": "Python信息",
                "info_desc": "显示Python版本和环境信息",
                "packages": "包列表",
                "packages_desc": "显示已安装的Python包",
                "imports": "包检查",
                "imports_desc": "检查常用Python包的导入状态"
            },
            "config": {
                "title": "配置管理",
                "view": "查看配置",
                "view_desc": "查看当前配置信息",
                "theme": "修改主题",
                "theme_desc": "更改界面主题",
                "language": "修改语言",
                "language_desc": "更改显示语言",
                "reset": "重置配置",
                "reset_desc": "恢复默认配置",
                "export": "导出配置",
                "export_desc": "导出当前配置到文件",
                "import": "导入配置",
                "import_desc": "从文件导入配置",
                "current": "当前",
                "languages": "可用语言",
                "reset_confirm": "确定要重置所有配置吗? (y/N)",
                "reset_canceled": "操作已取消",
                "export_prompt": "请输入导出文件名",
                "export_failed": "导出失败",
                "import_prompt": "请输入导入文件名",
                "import_failed": "导入失败",
                "continue": "按任意键继续...",
                "language_display": "语言"
            },
            "plugin": {
                "menu": "插件菜单",
                "menu_desc": "所有已加载的插件命令",
                "title": "插件管理",
                "list": "插件列表",
                "list_desc": "查看已安装的插件",
                "reload": "重新加载插件",
                "reload_desc": "重新加载所有插件",
                "refresh": "刷新插件列表",
                "refresh_desc": "刷新插件目录",
                "directory": "插件目录",
                "directory_desc": "查看插件目录内容",
                "loading": "重新加载插件...",
                "loaded_plugins": "已加载插件",
                "no_plugins": "暂无已加载的插件",
                "operations": "操作",
                "reload_all": "重新加载所有插件",
                "refresh_list": "刷新插件列表",
                "view_directory": "查看插件目录",
                "back_menu": "返回主菜单",
                "exit_program": "退出程序",
                "plugin_info": {
                    "name": "名称",
                    "version": "版本",
                    "author": "作者",
                    "description": "描述",
                    "status": "状态",
                    "enabled": "已启用",
                    "disabled": "已禁用"
                },
                "reload_success": "已重新加载 {count} 个插件",
                "refresh_info": {
                    "discovered": "发现插件文件",
                    "loaded": "已加载插件"
                },
                "directory_not_exists": "插件目录不存在",
                "directory_empty": "插件目录为空"
            },
            "hint": {
                "shortcuts": "快捷键",
                "back": "返回上级",
                "clear": "清屏",
                "help": "帮助",
                "search": "搜索",
                "exit": "退出"
            },
            "error": {
                "invalid_choice": "无效的选择",
                "invalid_input": "无效的输入",
                "file_not_found": "文件不存在",
                "permission_denied": "权限不足",
                "command_failed": "命令执行失败",
                "command_timeout": "命令执行超时",
                "plugin_load": "插件加载失败",
                "config_load": "配置加载失败"
            },
            "success": {
                "command": "命令执行成功",
                "config_saved": "配置已保存",
                "plugin_loaded": "插件加载成功",
                "plugin_reloaded": "插件已重新加载",
                "exported": "导出成功",
                "imported": "导入成功",
                "theme_switched": "主题已切换为: {theme}",
                "language_switched": "语言已切换为: {language}",
                "config_reset": "配置已重置为默认值",
                "config_exported": "配置已导出到: {filename}"
        },
        "language": {
            "changed": "语言已切换: {old} → {new}",
            "reinitializing": "重新初始化界面...",
            "available": "可用语言:",
            "select_prompt": "请选择语言 (1-{count})",
            "invalid_choice": "无效的选择: {choice}",
            "invalid_input": "无效的输入: {choice}",
            "continue": "按任意键继续..."
        },
        "theme": {
            "available": "可用主题:",
            "select_prompt": "请选择主题 (1-{count})",
            "invalid_choice": "无效的选择: {choice}",
            "invalid_input": "无效的输入: {choice}",
            "continue": "按任意键继续..."
        },
        "logger": {
            "title": "日志管理",
            "current_level": "当前日志级别",
            "available_levels": "可用日志级别",
            "view_logs": "查看日志",
            "view_logs_desc": "查看系统日志文件",
            "level_changed": "日志级别已更改为",
            "log_file_not_found": "日志文件不存在",
            "read_log_error": "读取日志失败",
            "no_logs_available": "暂无日志记录",
            "page": "页码",
            "total_logs": "日志总数"
        },
        "help": {
            "title": "使用说明",
            "basic": "基本操作",
            "basic_desc": "• 输入数字选择对应菜单项\n• 0 - 返回上级菜单 (不在主菜单时)\n• 0 - 退出程序 (在主菜单时)\n• c - 清屏\n• h - 显示帮助信息\n• s - 搜索菜单项",
            "menu": "菜单导航",
            "menu_desc": "• 使用数字选择菜单项\n• 使用0返回上一级菜单\n• 在主菜单按0退出程序",
            "icons": "图标说明",
            "icons_desc": "📁 菜单    ▶ 命令\n📊 系统    🌐 网络\n📁 文件    🐍 Python\n🔍 搜索    ⚙️  配置",
            "note": "注意",
            "note_desc": "如果图标显示不正常，请在终端设置中启用Unicode支持"
        },
        "stats": {
            "title": "运行统计",
            "uptime": "运行时间",
            "commands": "执行命令",
            "plugins": "加载插件"
        },
        "format": {
            "time_seconds": "秒",
            "time_minutes": "分钟",
            "time_hours": "小时",
            "size_bytes": "{bytes} B",
            "size_kb": "{kb:.1f} KB",
            "size_mb": "{mb:.1f} MB",
            "size_gb": "{gb:.1f} GB"
        }
        }
    
    def _get_en_us_translations(self) -> Dict:
        return {
            "app": {
                "name": "FastX TUI",
                "version": "v3.0",
                "description": "Terminal Toolset",
                "author": "FastX Team",
                "exit": "Exit Program",
                "exit_confirm": "Are you sure you want to exit? (y/N)",
                "exit_thanks": "Thank you for using, goodbye!",
                "help": "Help",
                "clear": "Clear Screen",
                "search": "Search",
                "back": "Back",
                "back_upper": "Back to Upper",
                "back_main": "Back to Main Menu",
                "confirm": "Confirm",
                "cancel": "Cancel",
                "save": "Save",
                "load": "Load",
                "reset": "Reset",
                "yes": "Yes",
                "no": "No",
                "ok": "OK",
                "error": "Error",
                "warning": "Warning",
                "info": "Info",
                "success": "Success",
                "failed": "Failed",
                "loading": "Loading...",
                "executing": "Executing...",
                "completed": "Completed",
                "time": "Time",
                "size": "Size",
                "count": "Count",
                "total": "Total",
                "available": "Available",
                "used": "Used",
                "free": "Free",
                "percent": "Percent"
            },
            "menu": {
                "main": "Main Menu",
                "system": "System Tools",
                "file": "File Tools",
                "python": "Python Tools",
                "network": "Network Tools",
                "plugin": "Plugin Management",
                "config": "Configuration",
                "search": "Search Function",
                "favorites": "My Favorites",
                "history": "History"
            },
            "system": {
                "info": "System Information",
                "info_desc": "Display detailed system hardware and software information",
                "network": "Network Information",
                "network_desc": "Display network interfaces and connection information",
                "process": "Process List",
                "process_desc": "Display currently running processes",
                "disk": "Disk Space",
                "disk_desc": "Display disk usage information",
                "uptime": "Uptime",
                "uptime_desc": "Display system uptime"
            },
            "file": {
                "list": "Directory Listing",
                "list_desc": "List contents of current directory",
                "tree": "File Tree",
                "tree_desc": "Display directory tree structure",
                "search": "File Search",
                "search_desc": "Search for files by type"
            },
            "python": {
                "info": "Python Information",
                "info_desc": "Display Python version and environment information",
                "packages": "Package List",
                "packages_desc": "Display installed Python packages",
                "imports": "Package Check",
                "imports_desc": "Check import status of common Python packages"
            },
            "config": {
                "title": "Configuration Management",
                "view": "View Config",
                "view_desc": "View current configuration information",
                "theme": "Change Theme",
                "theme_desc": "Change interface theme",
                "language": "Change Language",
                "language_desc": "Change display language",
                "reset": "Reset Config",
                "reset_desc": "Restore default configuration",
                "export": "Export Config",
                "export_desc": "Export current configuration to file",
                "import": "Import Config",
                "import_desc": "Import configuration from file",
                "current": "Current",
                "languages": "Available Languages",
                "reset_confirm": "Are you sure you want to reset all configurations? (y/N)",
                "reset_canceled": "Operation canceled",
                "export_prompt": "Please enter export filename",
                "export_failed": "Export failed",
                "import_prompt": "Please enter import filename",
                "import_failed": "Import failed",
                "continue": "Press any key to continue...",
                "language_display": "Language"
            },
            "plugin": {
                "menu": "Plugin Menu",
                "menu_desc": "All loaded plugin commands",
                "title": "Plugin Management",
                "list": "Plugin List",
                "list_desc": "View installed plugins",
                "reload": "Reload Plugins",
                "reload_desc": "Reload all plugins",
                "refresh": "Refresh Plugin List",
                "refresh_desc": "Refresh plugin directory",
                "directory": "Plugin Directory",
                "directory_desc": "View plugin directory contents",
                "loading": "Reloading plugins...",
                "loaded_plugins": "Loaded Plugins",
                "no_plugins": "No plugins loaded yet",
                "operations": "Operations",
                "reload_all": "Reload All Plugins",
                "refresh_list": "Refresh Plugin List",
                "view_directory": "View Plugin Directory",
                "back_menu": "Back to Menu",
                "exit_program": "Exit Program",
                "plugin_info": {
                    "name": "Name",
                    "version": "Version",
                    "author": "Author",
                    "description": "Description",
                    "status": "Status",
                    "enabled": "Enabled",
                    "disabled": "Disabled"
                },
                "reload_success": "Reloaded {count} plugins",
                "refresh_info": {
                    "discovered": "Discovered plugin files",
                    "loaded": "Loaded plugins"
                },
                "directory_not_exists": "Plugin directory does not exist",
                "directory_empty": "Plugin directory is empty"
            },
            "hint": {
                "shortcuts": "Shortcuts",
                "back": "Back",
                "clear": "Clear",
                "help": "Help",
                "search": "Search",
                "exit": "Exit"
            },
            "error": {
                "invalid_choice": "Invalid choice",
                "invalid_input": "Invalid input",
                "file_not_found": "File not found",
                "permission_denied": "Permission denied",
                "command_failed": "Command execution failed",
                "command_timeout": "Command execution timeout",
                "plugin_load": "Plugin load failed",
                "config_load": "Configuration load failed"
            },
            "success": {
                "command": "Command executed successfully",
                "config_saved": "Configuration saved",
                "plugin_loaded": "Plugin loaded successfully",
                "plugin_reloaded": "Plugin reloaded",
                "exported": "Exported successfully",
                "imported": "Imported successfully",
                "theme_switched": "Theme switched to: {theme}",
                "language_switched": "Language switched to: {language}",
                "config_reset": "Configuration reset to default values",
                "config_exported": "Configuration exported to: {filename}"
            },
            "language": {
                "changed": "Language changed: {old} → {new}",
                "reinitializing": "Reinitializing interface...",
                "available": "Available languages:",
                "select_prompt": "Please select language (1-{count})",
                "invalid_choice": "Invalid choice: {choice}",
                "invalid_input": "Invalid input: {choice}",
                "continue": "Press any key to continue..."
            },
            "theme": {
                "available": "Available themes:",
                "select_prompt": "Please select theme (1-{count})",
                "invalid_choice": "Invalid choice: {choice}",
                "invalid_input": "Invalid input: {choice}",
                "continue": "Press any key to continue..."
            },
            "help": {
                "title": "Usage Instructions",
                "basic": "Basic Operations",
                "basic_desc": "• Enter numbers to select menu items\n• 0 - Back to upper menu (when not in main menu)\n• 0 - Exit program (when in main menu)\n• c - Clear screen\n• h - Show help information\n• s - Search menu items",
                "menu": "Menu Navigation",
                "menu_desc": "• Use numbers to select menu items\n• Use 0 to go back to previous menu\n• Press 0 in main menu to exit program",
                "icons": "Icon Guide",
                "icons_desc": "📁 Menu    ▶ Command\n📊 System    🌐 Network\n📁 File    🐍 Python\n🔍 Search    ⚙️  Configuration",
                "note": "Note",
                "note_desc": "If icons don't display properly, enable Unicode support in terminal settings"
            },
            "stats": {
                "title": "Runtime Statistics",
                "uptime": "Uptime",
                "commands": "Commands executed",
                "plugins": "Plugins loaded"
            },
            "format": {
                "time_seconds": "seconds",
                "time_minutes": "minutes",
                "time_hours": "hours",
                "size_bytes": "{bytes} B",
                "size_kb": "{kb:.1f} KB",
                "size_mb": "{mb:.1f} MB",
                "size_gb": "{gb:.1f} GB"
            }
        }
    
    def _get_ja_jp_translations(self) -> Dict:
        return {
            "app": {
                "name": "FastX TUI",
                "description": "ターミナルツールセット",
                "exit": "終了",
                "help": "ヘルプ"
            },
            "menu": {
                "main": "メインメニュー",
                "system": "システムツール"
            }
        }
    
    def _get_ko_kr_translations(self) -> Dict:
        return {
            "app": {
                "name": "FastX TUI",
                "description": "터미널 도구 모음",
                "exit": "종료",
                "help": "도움말"
            },
            "menu": {
                "main": "메인 메뉴",
                "system": "시스템 도구"
            }
        }