#!/usr/bin/env python3
"""
配置管理器模块 - 基于SQLite的配置管理系统
"""
import os
import json
import sqlite3
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import ValidationError
from models.config_schema import AppConfigSchema, UserPreferencesSchema

class ConfigManager:
    """基于SQLite的配置管理器"""
    
    def __init__(self, db_path: str = "fastx_tui.sqlite"):
        self.db_path = Path(db_path)
        self._conn = None
        
        # 初始化配置
        self.config = AppConfigSchema()
        self.preferences = UserPreferencesSchema()
        self.plugin_configs = {}  # 插件配置，key为插件名称，value为配置字典
        
        # 初始化数据库连接和表
        self._init_db()
        
        # 加载配置
        self._load_config()
    
    def _init_db(self):
        """初始化数据库连接和表"""
        try:
            # 建立数据库连接
            self._conn = sqlite3.connect(str(self.db_path))
            cursor = self._conn.cursor()
            
            # 创建配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    type TEXT NOT NULL DEFAULT 'app',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_configs_key ON configs(key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_configs_type ON configs(type)')
            
            # 提交事务
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"[错误] 初始化数据库失败: {str(e)}")
    
    def _load_config(self):
        """从SQLite加载配置"""
        try:
            cursor = self._conn.cursor()
            
            # 加载应用配置
            cursor.execute('SELECT key, value FROM configs WHERE type = ?', ('app',))
            config_data = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
            
            # 加载用户偏好
            cursor.execute('SELECT key, value FROM configs WHERE type = ?', ('preference',))
            pref_data = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
            
            # 加载插件配置
            cursor.execute('SELECT key, value FROM configs WHERE type = ?', ('plugin',))
            self.plugin_configs = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
            
            # 使用 Pydantic 验证并更新配置
            if config_data:
                self.config = AppConfigSchema(**config_data)
            
            if pref_data:
                self.preferences = UserPreferencesSchema(**pref_data)
            
        except ValidationError as e:
            print(f"[警告] 配置验证失败: {e.errors()}")
            # 重置为默认配置
            self._reset_to_defaults()
        except sqlite3.Error as e:
            print(f"[警告] 加载配置失败: {str(e)}")
            # 重置为默认配置
            self._reset_to_defaults()
        except Exception as e:
            print(f"[警告] 加载配置发生意外错误: {str(e)}")
            # 重置为默认配置
            self._reset_to_defaults()
    
    def _save_config(self):
        """保存配置到SQLite"""
        try:
            cursor = self._conn.cursor()
            
            # 保存应用配置
            config_dict = self.config.model_dump()
            for key, value in config_dict.items():
                self._upsert_config(key, value, 'app')
            
            # 保存用户偏好
            pref_dict = self.preferences.model_dump()
            for key, value in pref_dict.items():
                self._upsert_config(key, value, 'preference')
            
            # 保存插件配置
            for plugin_name, plugin_config in self.plugin_configs.items():
                self._upsert_config(plugin_name, plugin_config, 'plugin')
            
            # 提交事务
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"[错误] 保存配置失败: {str(e)}")
            self._conn.rollback()
    
    def _upsert_config(self, key: str, value: Any, config_type: str):
        """插入或更新配置项"""
        try:
            cursor = self._conn.cursor()
            cursor.execute('''
                INSERT INTO configs (key, value, type, updated_at) 
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET 
                    value = excluded.value,
                    type = excluded.type,
                    updated_at = CURRENT_TIMESTAMP
            ''', (key, json.dumps(value), config_type))
        except sqlite3.Error as e:
            print(f"[错误] 更新配置项 {key} 失败: {str(e)}")
            raise
    
    def _reset_to_defaults(self):
        """重置为默认配置"""
        try:
            # 重置配置对象
            self.config = AppConfigSchema()
            self.preferences = UserPreferencesSchema()
            self.plugin_configs = {}  # 重置插件配置
            
            # 清空数据库中的配置
            cursor = self._conn.cursor()
            cursor.execute('DELETE FROM configs')
            
            # 保存默认配置到数据库
            self._save_config()
        except sqlite3.Error as e:
            print(f"[错误] 重置默认配置失败: {str(e)}")
    
    def get_plugin_config(self, plugin_name: str, default: Any = None) -> Any:
        """获取插件配置"""
        return self.plugin_configs.get(plugin_name, default)
    
    def set_plugin_config(self, plugin_name: str, config: Dict):
        """设置插件配置"""
        self.plugin_configs[plugin_name] = config
        self._save_config()
    
    def update_plugin_config(self, plugin_name: str, key: str, value: Any):
        """更新插件配置项"""
        if plugin_name not in self.plugin_configs:
            self.plugin_configs[plugin_name] = {}
        self.plugin_configs[plugin_name][key] = value
        self._save_config()
    
    def remove_plugin_config(self, plugin_name: str):
        """删除插件配置"""
        if plugin_name in self.plugin_configs:
            del self.plugin_configs[plugin_name]
            # 同时从数据库中删除
            cursor = self._conn.cursor()
            cursor.execute('DELETE FROM configs WHERE key = ? AND type = ?', (plugin_name, 'plugin'))
            self._conn.commit()
    
    def list_plugin_configs(self) -> Dict[str, Any]:
        """列出所有插件配置"""
        return self.plugin_configs.copy()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return getattr(self.config, key, default)
    
    def set_config(self, key: str, value: Any):
        """设置配置值"""
        try:
            # 检查是否是已知配置项
            if hasattr(self.config, key):
                # 已知配置项，使用 Pydantic 验证
                config_dict = self.config.model_dump()
                config_dict[key] = value
                
                # 使用 Pydantic 验证新配置
                new_config = AppConfigSchema(**config_dict)
                
                # 如果验证通过，更新配置
                self.config = new_config
            else:
                # 额外配置项，直接添加
                setattr(self.config, key, value)
            
            # 保存到数据库
            self._save_config()
        except ValidationError as e:
            print(f"[错误] 配置值验证失败: {e.errors()}")
            raise ValueError(f"无效的配置值: {key} = {value}") from e
        except sqlite3.Error as e:
            print(f"[错误] 设置配置项 {key} 失败: {str(e)}")
            raise
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取用户偏好"""
        return getattr(self.preferences, key, default)
    
    def set_preference(self, key: str, value: Any):
        """设置用户偏好"""
        try:
            # 检查是否是已知偏好项
            if hasattr(self.preferences, key):
                # 已知偏好项，使用 Pydantic 验证
                pref_dict = self.preferences.model_dump()
                pref_dict[key] = value
                
                # 使用 Pydantic 验证新偏好
                new_preferences = UserPreferencesSchema(**pref_dict)
                
                # 如果验证通过，更新偏好
                self.preferences = new_preferences
            else:
                # 额外偏好项，直接添加
                setattr(self.preferences, key, value)
            
            # 保存到数据库
            self._save_config()
        except ValidationError as e:
            print(f"[错误] 偏好值验证失败: {e.errors()}")
            raise ValueError(f"无效的偏好值: {key} = {value}") from e
        except sqlite3.Error as e:
            print(f"[错误] 设置偏好项 {key} 失败: {str(e)}")
            raise
    
    def add_favorite(self, item_id: str):
        """添加到收藏夹"""
        if item_id not in self.preferences.favorite_items:
            self.preferences.favorite_items.append(item_id)
            self._save_config()
    
    def remove_favorite(self, item_id: str):
        """从收藏夹移除"""
        if item_id in self.preferences.favorite_items:
            self.preferences.favorite_items.remove(item_id)
            self._save_config()
    
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
            self._save_config()
    
    def clear_search_history(self):
        """清除搜索历史"""
        self.preferences.search_history.clear()
        self._save_config()
    
    def add_recently_used(self, item_id: str):
        """添加到最近使用"""
        if item_id in self.preferences.recently_used:
            self.preferences.recently_used.remove(item_id)
        self.preferences.recently_used.insert(0, item_id)
        
        # 限制最近使用列表长度
        if len(self.preferences.recently_used) > 10:
            self.preferences.recently_used = self.preferences.recently_used[:10]
        
        self._save_config()
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self._reset_to_defaults()
    
    def save_config(self):
        """保存配置 - 向后兼容方法"""
        self._save_config()
    
    def save_preferences(self):
        """保存用户偏好 - 向后兼容方法"""
        self._save_config()
    
    def show_config_summary(self) -> str:
        """显示配置摘要"""
        info = []
        info.append("=" * 70)
        info.append("配置摘要".center(70))
        info.append("=" * 70)
        
        # 显示配置
        info.append(f"\n主配置:")
        info.append(f"  主题: {getattr(self.config, 'theme', 'default')}")
        info.append(f"  语言: {getattr(self.config, 'language', 'zh_CN')}")
        info.append(f"  命令超时: {getattr(self.config, 'command_timeout', 30)}秒")
        info.append(f"  自动加载插件: {'是' if getattr(self.config, 'plugin_auto_load', True) else '否'}")
        info.append(f"  显示欢迎页面: {'是' if getattr(self.config, 'show_welcome_page', True) else '否'}")
        info.append(f"  自动检查更新: {'是' if getattr(self.config, 'auto_check_updates', True) else '否'}")
        info.append(f"  自动清屏: {'是' if getattr(self.config, 'auto_clear_screen', True) else '否'}")
        
        # 显示用户偏好
        info.append(f"\n用户偏好:")
        info.append(f"  收藏项目数: {len(getattr(self.preferences, 'favorite_items', []))}")
        info.append(f"  最近使用数: {len(getattr(self.preferences, 'recently_used', []))}")
        info.append(f"  自定义快捷键: {len(getattr(self.preferences, 'custom_shortcuts', {}))}个")
        
        # 显示插件配置
        info.append(f"\n插件配置:")
        info.append(f"  已配置插件数: {len(self.plugin_configs)}")
        if self.plugin_configs:
            enabled_plugins = sum(1 for config in self.plugin_configs.values() if config.get('enabled', True))
            info.append(f"  启用插件数: {enabled_plugins}")
        
        # 显示文件信息
        info.append(f"\n文件信息:")
        info.append(f"  配置数据库: {self.db_path}")
        
        return "\n".join(info)
    
    def __del__(self):
        """关闭数据库连接"""
        if hasattr(self, '_conn') and self._conn:
            self._conn.close()