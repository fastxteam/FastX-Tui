from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
import re
import validators

class PluginInfoSchema(BaseModel):
    """插件信息模型"""
    name: str = Field(..., description="插件名称")
    version: str = Field(..., description="插件版本")
    author: Optional[str] = Field(None, description="插件作者")
    description: Optional[str] = Field(None, description="插件描述")
    homepage: Optional[str] = Field(None, description="插件主页")
    repository: Optional[str] = Field(None, description="插件仓库地址")
    license: Optional[str] = Field(None, description="插件许可证")
    dependencies: Optional[List[str]] = Field(None, description="插件依赖")
    category: Optional[str] = Field(None, description="插件分类")

    @field_validator('version')
    @classmethod
    def validate_version(cls, v: str) -> str:
        """验证版本号格式"""
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError('版本号必须符合 x.y.z 格式')
        return v

    @field_validator('homepage', 'repository')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """验证URL格式"""
        if v is None:
            return v
        if not validators.url(v):
            raise ValueError(f'URL格式无效: {v}')
        return v

class PluginConfigSchema(BaseModel):
    """插件配置模式模型"""
    key: str = Field(..., description="配置项键名")
    type: str = Field(..., description="配置项类型")
    description: Optional[str] = Field(None, description="配置项描述")
    default: Any = Field(..., description="配置项默认值")
    required: bool = Field(default=False, description="是否必填")
    options: Optional[List[Any]] = Field(None, description="可选值列表")
    min: Optional[int] = Field(None, description="最小值")
    max: Optional[int] = Field(None, description="最大值")

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """验证配置项类型"""
        valid_types = ['string', 'number', 'integer', 'boolean', 'array', 'object']
        if v not in valid_types:
            raise ValueError(f'配置项类型必须是 {valid_types} 之一')
        return v

class PluginRegistrationSchema(BaseModel):
    """插件注册模型"""
    plugin_id: str = Field(..., description="插件ID")
    plugin_class: str = Field(..., description="插件类名")
    plugin_path: str = Field(..., description="插件路径")
    plugin_info: PluginInfoSchema = Field(..., description="插件信息")

class GithubPluginRepoSchema(BaseModel):
    """GitHub 插件仓库模型"""
    owner: str = Field(..., description="仓库所有者")
    name: str = Field(..., description="仓库名称")
    description: Optional[str] = Field(None, description="仓库描述")
    stars: int = Field(default=0, description="仓库星数")
    forks: int = Field(default=0, description="仓库分支数")
    watchers: int = Field(default=0, description="仓库关注数")
    issues: int = Field(default=0, description="仓库问题数")
    pulls: int = Field(default=0, description="仓库拉取请求数")
    language: Optional[str] = Field(None, description="仓库主要语言")
    last_updated: Optional[str] = Field(None, description="最后更新时间")

    @field_validator('name')
    @classmethod
    def validate_plugin_name(cls, v: str) -> str:
        """验证插件名称格式"""
        if not v.startswith('FastX-Tui-Plugin-'):
            raise ValueError('插件仓库名称必须以 FastX-Tui-Plugin- 开头')
        return v

class PluginInstallationSchema(BaseModel):
    """插件安装模型"""
    repo_url: str = Field(..., description="插件仓库URL")
    version: Optional[str] = Field(None, description="插件版本")
    force_install: bool = Field(default=False, description="是否强制安装")
    enable_after_install: bool = Field(default=True, description="安装后是否启用")

    @field_validator('repo_url')
    @classmethod
    def validate_repo_url(cls, v: str) -> str:
        """验证仓库URL格式"""
        if not validators.url(v):
            raise ValueError(f'仓库URL格式无效: {v}')
        if 'github.com' not in v:
            raise ValueError('当前仅支持 GitHub 仓库')
        return v

class PluginStatusSchema(BaseModel):
    """插件状态模型"""
    plugin_id: str = Field(..., description="插件ID")
    enabled: bool = Field(default=True, description="是否启用")
    loaded: bool = Field(default=False, description="是否已加载")
    error: Optional[str] = Field(None, description="错误信息")
    last_loaded: Optional[str] = Field(None, description="最后加载时间")

class PluginMenuItemSchema(BaseModel):
    """插件菜单项模型"""
    menu_id: str = Field(..., description="菜单项ID")
    menu_name: str = Field(..., description="菜单项名称")
    menu_category: str = Field(default="插件", description="菜单项分类")
    menu_description: Optional[str] = Field(None, description="菜单项描述")
    menu_action: str = Field(..., description="菜单项动作")
    menu_shortcut: Optional[str] = Field(None, description="菜单项快捷键")
    menu_order: int = Field(default=100, description="菜单项顺序")

    @field_validator('menu_id')
    @classmethod
    def validate_menu_id(cls, v: str) -> str:
        """验证菜单项ID格式"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('菜单项ID只能包含字母、数字、下划线和连字符')
        return v

class PluginConfigRequestSchema(BaseModel):
    """插件配置请求模型"""
    plugin_id: str = Field(..., description="插件ID")
    config_key: str = Field(..., description="配置项键名")
    config_value: Any = Field(..., description="配置项值")

class PluginOperationResponseSchema(BaseModel):
    """插件操作响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="操作结果消息")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")
    error: Optional[str] = Field(None, description="错误信息")

class PluginListResponseSchema(BaseModel):
    """插件列表响应模型"""
    total: int = Field(..., description="插件总数")
    plugins: List[Dict[str, Any]] = Field(..., description="插件列表")
    enabled_count: int = Field(..., description="已启用插件数")
    disabled_count: int = Field(..., description="已禁用插件数")

class PluginCommandSchema(BaseModel):
    """插件操作命令模型"""
    command: str = Field(..., description="命令名称")
    args: Optional[Dict[str, Any]] = Field(None, description="命令参数")
    plugin_id: Optional[str] = Field(None, description="插件ID")

    @field_validator('command')
    @classmethod
    def validate_command(cls, v: str) -> str:
        """验证命令名称"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('命令名称只能包含字母、数字、下划线和连字符')
        return v