#!/usr/bin/env python3
"""
更新管理器模块
"""
import time
from typing import Dict, Optional, Tuple, Any

from core.logger import get_logger
from core.network_tools import NetworkToolsPlugin
from config.config_manager import ConfigManager

logger = get_logger(__name__)


class UpdateManager:
    """更新管理器类，负责检查版本更新和管理更新相关操作"""
    
    def __init__(self, config_manager: ConfigManager, current_version: str = "v0.1.0", console=None):
        """初始化更新管理器
        
        Args:
            config_manager: 配置管理器实例
            current_version: 当前版本号
            console: Rich控制台实例
        """
        self.config_manager = config_manager
        self.console = console
        
        # 版本信息
        self.current_version = current_version
        self.latest_version = None
        self.update_available = False
        self.version_check_failed = False
        
        # 版本检查结果缓存
        self.last_check_time = 0
        self.check_interval = 86400  # 24小时
        
        # 网络工具将在需要时通过依赖注入获取
        self.network_tools = None
        
    def set_network_tools(self, network_tools):
        """设置网络工具插件实例
        
        Args:
            network_tools: 网络工具插件实例
        """
        self.network_tools = network_tools
    
    def check_for_updates(self, force_check: bool = False) -> Tuple[bool, Optional[str]]:
        """检查版本更新（兼容旧接口）
        
        Args:
            force_check: 是否强制检查，忽略缓存时间
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有更新, 最新版本号)
        """
        return self.check_version_update(force_check)
    
    def check_version_update(self, force_check: bool = False) -> Tuple[bool, Optional[str]]:
        """检查GitHub上的版本更新
        
        Args:
            force_check: 是否强制检查，忽略缓存时间
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有更新, 最新版本号)
        """
        # 检查是否在配置中启用了自动更新检查
        if not force_check and not self.config_manager.get_config("auto_check_updates", True):
            logger.info("自动版本检查已禁用")
            return False, None
        
        # 检查时间间隔，避免频繁检查
        current_time = time.time()
        if not force_check and current_time - self.last_check_time < self.check_interval:
            logger.info("版本检查时间间隔未到")
            return self.update_available, self.latest_version
        
        # 更新检查时间
        self.last_check_time = current_time
        
        logger.info(f"检查版本更新，当前版本: {self.current_version}")
        self.version_check_failed = False
        
        # 检查网络工具是否可用
        if not self.network_tools:
            logger.warning("网络工具不可用，无法检查版本更新")
            self.version_check_failed = True
            return False, None
            
        try:
            # 使用网络工具插件检查版本更新
            result = self.network_tools.check_github_version(
                current_version=self.current_version.lstrip('v'),
                repo="fastxteam/FastX-Tui"
            )
            
            logger.debug(f"版本检查结果: {result}")
            
            if result['success']:
                self.latest_version = result['latest_version']
                self.update_available = result['update_available']
                logger.info(f"版本检查成功，最新版本: {self.latest_version}, 是否有更新: {self.update_available}")
            else:
                self.version_check_failed = True
                logger.error(f"版本检查失败: {result.get('error', '未知错误')}")
                return False, None
                
        except Exception as e:
            # Set flag on any error
            self.version_check_failed = True
            logger.exception("版本检查发生异常")
            return False, None
            
        return self.update_available, self.latest_version
    
    def get_version_info(self) -> Dict[str, Any]:
        """获取版本信息
        
        Returns:
            Dict[str, Any]: 版本信息字典
        """
        return {
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "update_available": self.update_available,
            "version_check_failed": self.version_check_failed
        }
    
    def should_show_update_prompt(self) -> bool:
        """是否应该显示更新提示
        
        Returns:
            bool: 是否显示更新提示
        """
        return self.update_available and self.latest_version
    
    def get_update_message(self) -> str:
        """获取更新提示消息
        
        Returns:
            str: 更新提示消息
        """
        if not self.should_show_update_prompt():
            return ""
            
        current_version = self.current_version.lstrip('v')
        latest_version = self.latest_version
        
        message = f"FastX-Tui 有新版本可用! {current_version} -> {latest_version}\n"
        message += f"查看最新版本: https://github.com/fastxteam/FastX-Tui/releases/latest"
        
        return message
    

