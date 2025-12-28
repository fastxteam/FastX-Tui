from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, List, Optional
import re

class AppConfigSchema(BaseModel):
    """应用配置模型"""
    model_config = ConfigDict(
        extra='allow',
        validate_assignment=True,
        strict=False
    )
    
    # 显示设置
    show_banner: bool = Field(default=True, description="是否显示横幅")
    show_hints: bool = Field(default=True, description="是否显示提示")
    show_icons: bool = Field(default=True, description="是否显示图标")
    animation_enabled: bool = Field(default=True, description="是否启用动画")
    banner_style: str = Field(default="default", description="横幅样式", pattern=r'^(default|gradient)$')
    
    # 行为设置
    auto_clear_screen: bool = Field(default=True, description="是否自动清屏")
    confirm_exit: bool = Field(default=False, description="退出时是否确认")
    confirm_dangerous_commands: bool = Field(default=True, description="危险命令是否确认")
    
    # 性能设置
    command_timeout: int = Field(default=30, ge=5, le=300, description="命令超时时间")
    max_history_items: int = Field(default=50, ge=10, le=200, description="最大历史记录数")
    max_search_results: int = Field(default=20, ge=5, le=100, description="最大搜索结果数")
    
    # 主题设置
    theme: str = Field(default="default", description="主题名称")
    color_scheme: str = Field(default="auto", description="配色方案", pattern=r'^(auto|light|dark)$')
    
    # 插件设置
    plugin_auto_load: bool = Field(default=True, description="是否自动加载插件")
    plugin_directory: str = Field(default="plugins", description="插件目录")
    
    # 其他设置
    language: str = Field(default="zh_CN", description="语言")
    log_level: str = Field(default="INFO", description="日志级别", pattern=r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$')
    enable_analytics: bool = Field(default=False, description="是否启用分析")
    show_welcome_page: bool = Field(default=True, description="是否显示欢迎页面")
    auto_check_updates: bool = Field(default=True, description="是否自动检查版本更新")
    use_async_tasks: bool = Field(default=False, description="是否使用异步任务")

    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """验证语言代码格式"""
        if not re.match(r'^[a-zA-Z]{2}(_[A-Z]{2})?$', v):
            raise ValueError("语言代码格式无效，应为 xx 或 xx_XX 格式")
        return v

class UserPreferencesSchema(BaseModel):
    """用户偏好设置模型"""
    model_config = ConfigDict(
        validate_assignment=True,
        strict=False
    )
    
    # 常用功能
    favorite_items: List[str] = Field(default_factory=list, description="收藏项目")
    recently_used: List[str] = Field(default_factory=list, description="最近使用")
    search_history: List[str] = Field(default_factory=list, description="搜索历史")
    
    # 快捷键自定义
    custom_shortcuts: Dict[str, str] = Field(default_factory=lambda: {
        "search": "ctrl+f",
        "history": "ctrl+h",
        "favorites": "ctrl+b"
    }, description="自定义快捷键")
    
    # 界面偏好
    preferred_menu: str = Field(default="main_menu", description="首选菜单")
    default_view: str = Field(default="table", description="默认视图", pattern=r'^(table|list|grid)$')

class ConfigFileSchema(BaseModel):
    """配置文件模型"""
    config: AppConfigSchema = Field(default_factory=AppConfigSchema, description="应用配置")
    preferences: UserPreferencesSchema = Field(default_factory=UserPreferencesSchema, description="用户偏好")

class ImportConfigRequestSchema(BaseModel):
    """导入配置请求模型"""
    filepath: str = Field(..., description="配置文件路径")

    @field_validator('filepath')
    @classmethod
    def validate_filepath(cls, v: str) -> str:
        """验证文件路径"""
        if not v:
            raise ValueError("文件路径不能为空")
        if not (v.endswith('.json') or v.endswith('.yaml') or v.endswith('.yml')):
            raise ValueError("仅支持 JSON、YAML 和 YML 格式的配置文件")
        return v

class ExportConfigRequestSchema(BaseModel):
    """导出配置请求模型"""
    filepath: str = Field(..., description="配置文件路径")

    @field_validator('filepath')
    @classmethod
    def validate_filepath(cls, v: str) -> str:
        """验证文件路径"""
        if not v:
            raise ValueError("文件路径不能为空")
        if not (v.endswith('.json') or v.endswith('.yaml') or v.endswith('.yml')):
            raise ValueError("仅支持 JSON、YAML 和 YML 格式的配置文件")
        return v

class ConfigChangeRequestSchema(BaseModel):
    """配置变更请求模型"""
    key: str = Field(..., description="配置项键名")
    value: str = Field(..., description="配置项值")

class PreferenceChangeRequestSchema(BaseModel):
    """偏好变更请求模型"""
    key: str = Field(..., description="偏好项键名")
    value: str = Field(..., description="偏好项值")