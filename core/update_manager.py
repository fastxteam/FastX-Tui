#!/usr/bin/env python3
"""
更新管理器模块
"""
import time
import os
import sys
import shutil
import tempfile
import subprocess
import platform
from typing import Dict, Optional, Tuple, Any

from core.logger import get_logger
from core.network_tools import NetworkToolsPlugin
from core.config_manager import ConfigManager

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
        
        # GitHub发布的assets列表
        self.assets = []
        
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
                # 保存assets信息，用于后续下载
                self.assets = result.get('assets', [])
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
    
    def get_available_versions(self, per_page: int = 10) -> Dict:
        """获取所有可用的发布版本
        
        Args:
            per_page: 获取的版本数量
            
        Returns:
            Dict: 包含可用版本列表的字典
        """
        logger.info(f"获取可用的发布版本，数量: {per_page}")
        
        # 检查网络工具是否可用
        if not self.network_tools:
            logger.warning("网络工具不可用，无法获取可用版本")
            return {'success': False, 'error': '网络工具不可用'}
            
        try:
            # 使用网络工具插件获取所有发布版本
            result = self.network_tools.get_all_github_releases(
                repo="fastxteam/FastX-Tui",
                per_page=per_page
            )
            
            logger.debug(f"可用版本获取结果: {result}")
            
            return result
                
        except Exception as e:
            logger.exception("获取可用版本发生异常")
            return {'success': False, 'error': str(e)}
    
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
    
    def update_app(self) -> bool:
        """自动更新应用程序
        
        Returns:
            bool: 更新是否成功
        """
        if not self.update_available or not self.latest_version:
            logger.info("没有可用更新")
            return False
        
        logger.info(f"开始更新应用，当前版本: {self.current_version}, 最新版本: {self.latest_version}")
        
        try:
            # 检查网络工具是否可用
            if not self.network_tools:
                logger.error("网络工具不可用，无法下载更新")
                return False
            
            # 确定当前运行的是exe还是python脚本
            is_exe = getattr(sys, 'frozen', False)
            
            if is_exe:
                # 从exe启动的应用
                return self._update_from_exe()
            else:
                # 从Python脚本启动的应用
                return self._update_from_script()
                
        except Exception as e:
            logger.exception("更新过程发生异常")
            return False
    
    def _update_from_exe(self) -> bool:
        """从exe启动的应用更新逻辑
        
        Returns:
            bool: 更新是否成功
        """
        try:
            # 获取当前exe路径
            current_exe_path = sys.executable
            current_exe_dir = os.path.dirname(current_exe_path)
            current_exe_name = os.path.basename(current_exe_path)
            
            logger.info(f"检测到当前运行的是可执行文件: {current_exe_name}")
            
            # 根据平台获取下载URL
            exe_url = self._get_exe_download_url()
            if not exe_url:
                return False
            
            # 下载新版本到当前目录
            new_exe_path = os.path.join(current_exe_dir, f"fastx-tui_new.exe")
            logger.info(f"正在下载新版本: {exe_url}")
            
            success = self._download_file(exe_url, new_exe_path)
            if not success:
                return False
            
            # 验证下载的文件
            if not os.path.exists(new_exe_path) or os.path.getsize(new_exe_path) == 0:
                logger.error("下载的文件无效")
                return False
            
            logger.info("新版本下载成功")
            
            # 创建批处理脚本用于更新
            batch_script_path = os.path.join(current_exe_dir, f"fastx-tui_update.bat")
            
            # 批处理脚本内容
            batch_content = f'''
@echo off
:: 等待当前进程退出
timeout /t 2 /nobreak >nul

:: 替换旧版本
if exist "{current_exe_path}" del "{current_exe_path}"
rename "{new_exe_path}" "{current_exe_name}"

:: 清理临时文件
if exist "{batch_script_path}" del "{batch_script_path}"

:: 重启应用
start "" "{os.path.join(current_exe_dir, current_exe_name)}"
'''
            
            # 写入批处理脚本
            with open(batch_script_path, 'w') as f:
                f.write(batch_content)
                f.flush()  # 刷新缓冲区到OS
                os.fsync(f.fileno())  # 强制写入磁盘
            
            logger.info("更新脚本创建成功")
            
            # 使用cmd.exe显式执行批处理脚本，确保正确运行
            subprocess.Popen(
                ['cmd.exe', '/c', batch_script_path],
                shell=False,  # 不使用shell，直接执行cmd
                cwd=current_exe_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 退出当前应用
            sys.exit(0)
            
        except Exception as e:
            logger.exception("从exe更新失败")
            return False
    
    def _update_from_script(self) -> bool:
        """从Python脚本启动的应用更新逻辑
        
        Returns:
            bool: 更新是否成功
        """
        try:
            logger.info("检测到当前运行的是Python脚本")
            logger.info("使用pip更新应用...")
            
            # 使用pip更新
            update_command = [sys.executable, '-m', 'pip', 'install', '--upgrade', 'fastx_tui']
            
            logger.info(f"执行命令: {' '.join(update_command)}")
            
            result = subprocess.run(
                update_command,
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                logger.info("应用更新成功")
                return True
            else:
                logger.error(f"应用更新失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.exception("从脚本更新失败")
            return False
    
    def _get_exe_download_url(self) -> Optional[str]:
        """获取可执行文件的下载URL
        
        Returns:
            Optional[str]: 下载URL
        """
        # 获取当前平台
        current_platform = platform.system()
        
        # 定义平台标识
        platform_identifier = "win" if current_platform == "Windows" else "linux" if current_platform == "Linux" else None
        
        if not platform_identifier:
            logger.error(f"不支持的平台: {current_platform}")
            return None
        
        # 如果没有assets信息，尝试直接构建URL作为备选方案
        if not self.assets:
            logger.warning("没有获取到assets信息，使用备选URL构建方案")
            # 构建备选URL
            base_name = f"fastx-tui-{platform_identifier}"
            if platform_identifier == "win":
                base_name += ".exe"
            download_url = f"https://github.com/fastxteam/FastX-Tui/releases/download/v{self.latest_version}/{base_name}"
            logger.info(f"使用备选方案构建下载URL: {download_url}")
            return download_url
        
        # 根据平台动态查找合适的asset
        import re
        
        # 查找匹配的asset
        matched_asset = None
        for asset in self.assets:
            asset_name = asset['name'].lower()
            
            # 匹配规则：
            # 1. 对于Windows平台，匹配以.exe结尾的文件
            # 2. 对于Linux平台，匹配没有扩展名且包含linux或fastx的可执行文件
            # 3. 排除source code和其他非可执行文件
            is_windows_match = current_platform == "Windows" and asset_name.endswith(".exe")
            is_linux_match = current_platform == "Linux" and (not asset_name.endswith(".") and not "." in asset_name.split(".")[-1] or asset_name.endswith("-linux"))
            
            if ((is_windows_match or is_linux_match) and 
                not any(keyword in asset_name for keyword in ['source', 'src', '.zip', '.tar', '.gz', '.7z', '.whl'])):
                matched_asset = asset
                break
        
        if matched_asset:
            logger.info(f"找到匹配的asset: {matched_asset['name']}")
            return matched_asset['browser_download_url']
        else:
            logger.error(f"未找到匹配的可执行文件，assets列表: {[asset['name'] for asset in self.assets]}")
            return None
    
    def _download_file(self, url: str, save_path: str) -> bool:
        """下载文件
        
        Args:
            url: 下载URL
            save_path: 保存路径
            
        Returns:
            bool: 下载是否成功
        """
        try:
            import urllib.request
            
            logger.info(f"开始下载: {url}")
            
            # 下载文件
            response = urllib.request.urlopen(url, timeout=30)
            total_size = int(response.getheader('Content-Length', 0))
            downloaded = 0
            block_size = 8192
            
            with open(save_path, 'wb') as file:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    
                    file.write(buffer)
                    downloaded += len(buffer)
                    
                    # 记录下载进度
                    if total_size > 0:
                        progress = int((downloaded / total_size) * 100)
                        # 每10%记录一次进度，避免日志过于密集
                        if progress % 10 == 0 or downloaded == total_size:
                            logger.info(f"下载进度: {progress}% [{downloaded}/{total_size} bytes]")
            
            logger.info(f"文件下载成功: {save_path}, 大小: {os.path.getsize(save_path)} bytes")
            return True
            
        except urllib.error.URLError as e:
            logger.error(f"下载失败: {str(e)}")
            return False
        except Exception as e:
            logger.exception("下载文件发生异常")
            return False
    

