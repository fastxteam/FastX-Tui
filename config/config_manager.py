#!/usr/bin/env python3
"""
配置管理器模块
"""
import os
import json
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class AppConfig:
    """应用配置"""
    # 显示设置
    show_banner: bool = True
    show_hints: bool = True
    show_icons: bool = True
    animation_enabled: bool = True
    
    # 行为设置
    auto_clear_screen: bool = False
    confirm_exit: bool = True
    confirm_dangerous_commands: bool = True
    
    # 性能设置
    command_timeout: int = 30
    max_history_items: int = 50
    max_search_results: int = 20
    
    # 主题设置
    theme: str = "default"
    color_scheme: str = "auto"  # auto, light, dark
    
    # 插件设置
    plugin_auto_load: bool = True
    plugin_directory: str = "plugins"
    
    # 其他设置
    language: str = "zh_CN"
    log_level: str = "INFO"
    enable_analytics: bool = False

@dataclass
class UserPreferences:
    """用户偏好设置"""
    # 常用功能
    favorite_items: list = None
    recently_used: list = None
    search_history: list = None
    
    # 快捷键自定义
    custom_shortcuts: Dict[str, str] = None
    
    # 界面偏好
    preferred_menu: str = "main_menu"
    default_view: str = "table"  # table, list, grid
    
    def __post_init__(self):
        if self.favorite_items is None:
            self.favorite_items = []
        if self.recently_used is None:
            self.recently_used = []
        if self.search_history is None:
            self.search_history = []
        if self.custom_shortcuts is None:
            self.custom_shortcuts = {
                "search": "ctrl+f",
                "history": "ctrl+h",
                "favorites": "ctrl+b"
            }

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = ".fastx"):
        self.config_dir = Path.home() / config_dir
        self.config_file = self.config_dir / "config.json"
        self.prefs_file = self.config_dir / "preferences.json"
        
        # 创建配置目录
        self.config_dir.mkdir(exist_ok=True)
        
        # 初始化配置
        self.config = AppConfig()
        self.preferences = UserPreferences()
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        try:
            # 加载主配置
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
            
            # 加载用户偏好
            if self.prefs_file.exists():
                with open(self.prefs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.preferences, key):
                            setattr(self.preferences, key, value)
            
        except Exception as e:
            print(f"[警告] 加载配置失败: {str(e)}")
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        try:
            self.save_config()
            self.save_preferences()
        except Exception as e:
            print(f"[错误] 创建默认配置失败: {str(e)}")
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[错误] 保存配置失败: {str(e)}")
    
    def save_preferences(self):
        """保存用户偏好"""
        try:
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.preferences), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[错误] 保存用户偏好失败: {str(e)}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return getattr(self.config, key, default)
    
    def set_config(self, key: str, value: Any):
        """设置配置值"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save_config()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取用户偏好"""
        return getattr(self.preferences, key, default)
    
    def set_preference(self, key: str, value: Any):
        """设置用户偏好"""
        if hasattr(self.preferences, key):
            setattr(self.preferences, key, value)
            self.save_preferences()
    
    def add_favorite(self, item_id: str):
        """添加到收藏夹"""
        if item_id not in self.preferences.favorite_items:
            self.preferences.favorite_items.append(item_id)
            self.save_preferences()
    
    def remove_favorite(self, item_id: str):
        """从收藏夹移除"""
        if item_id in self.preferences.favorite_items:
            self.preferences.favorite_items.remove(item_id)
            self.save_preferences()
    
    def get_search_history(self) -> list:
        """获取搜索历史"""
        return self.preferences.search_history
    
    def add_search_history(self, keyword: str):
        """添加到搜索历史"""
        if keyword and keyword not in self.preferences.search_history:
            self.preferences.search_history.append(keyword)
            # 限制搜索历史长度
            if len(self.preferences.search_history) > 20:
                self.preferences.search_history.pop(0)
            self.save_preferences()
    
    def clear_search_history(self):
        """清除搜索历史"""
        self.preferences.search_history.clear()
        self.save_preferences()
    
    def add_recently_used(self, item_id: str):
        """添加到最近使用"""
        if item_id in self.preferences.recently_used:
            self.preferences.recently_used.remove(item_id)
        self.preferences.recently_used.insert(0, item_id)
        
        # 限制最近使用列表长度
        if len(self.preferences.recently_used) > 10:
            self.preferences.recently_used = self.preferences.recently_used[:10]
        
        self.save_preferences()
    
    def export_config(self, filepath: str):
        """导出配置到文件"""
        try:
            data = {
                "config": asdict(self.config),
                "preferences": asdict(self.preferences)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                    yaml.dump(data, f, allow_unicode=True)
                else:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"[错误] 导出配置失败: {str(e)}")
            return False
    
    def import_config(self, filepath: str):
        """从文件导入配置"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            if "config" in data:
                for key, value in data["config"].items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
            
            if "preferences" in data:
                for key, value in data["preferences"].items():
                    if hasattr(self.preferences, key):
                        setattr(self.preferences, key, value)
            
            self.save_config()
            self.save_preferences()
            
            return True
        except Exception as e:
            print(f"[错误] 导入配置失败: {str(e)}")
            return False
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.config = AppConfig()
        self.preferences = UserPreferences()
        self.save_config()
        self.save_preferences()
    
    def show_config_summary(self) -> str:
        """显示配置摘要"""
        info = []
        info.append("=" * 70)
        info.append("⚙️  配置摘要".center(70))
        info.append("=" * 70)
        
        # 显示配置
        info.append(f"\n📋 主配置:")
        info.append(f"  主题: {self.config.theme}")
        info.append(f"  语言: {self.config.language}")
        info.append(f"  命令超时: {self.config.command_timeout}秒")
        info.append(f"  自动加载插件: {'是' if self.config.plugin_auto_load else '否'}")
        
        # 显示用户偏好
        info.append(f"\n👤 用户偏好:")
        info.append(f"  收藏项目数: {len(self.preferences.favorite_items)}")
        info.append(f"  最近使用数: {len(self.preferences.recently_used)}")
        info.append(f"  自定义快捷键: {len(self.preferences.custom_shortcuts)}个")
        
        # 显示文件信息
        info.append(f"\n📁 文件信息:")
        info.append(f"  配置目录: {self.config_dir}")
        info.append(f"  配置文件: {self.config_file}")
        info.append(f"  偏好文件: {self.prefs_file}")
        
        return "\n".join(info)