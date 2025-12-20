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
    
    def update_app(self) -> bool:
        """自动更新应用程序
        
        Returns:
            bool: 更新是否成功
        """
        if not self.update_available or not self.latest_version:
            logger.info("没有可用更新")
            if self.console:
                self.console.print("[yellow]没有可用更新[/yellow]")
            return False
        
        logger.info(f"开始更新应用，当前版本: {self.current_version}, 最新版本: {self.latest_version}")
        if self.console:
            self.console.print(f"[green]开始更新应用...[/green]")
            self.console.print(f"当前版本: {self.current_version}")
            self.console.print(f"最新版本: {self.latest_version}")
        
        try:
            # 检查网络工具是否可用
            if not self.network_tools:
                logger.error("网络工具不可用，无法下载更新")
                if self.console:
                    self.console.print("[red]网络工具不可用，无法下载更新[/red]")
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
            if self.console:
                self.console.print(f"[red]更新失败: {str(e)}[/red]")
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
            
            if self.console:
                self.console.print(f"[cyan]检测到当前运行的是可执行文件: {current_exe_name}[/cyan]")
            
            # 根据平台获取下载URL
            exe_url = self._get_exe_download_url()
            if not exe_url:
                return False
            
            # 下载新版本到当前目录
            new_exe_path = os.path.join(current_exe_dir, f"fastx_new.exe")
            if self.console:
                self.console.print(f"[cyan]正在下载新版本: {exe_url}[/cyan]")
            
            success = self._download_file(exe_url, new_exe_path)
            if not success:
                return False
            
            # 验证下载的文件
            if not os.path.exists(new_exe_path) or os.path.getsize(new_exe_path) == 0:
                logger.error("下载的文件无效")
                if self.console:
                    self.console.print("[red]下载的文件无效[/red]")
                return False
            
            if self.console:
                self.console.print("[green]新版本下载成功[/green]")
            
            # 创建批处理脚本用于更新
            batch_script_path = os.path.join(current_exe_dir, f"fastx_update.bat")
            
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
            
            if self.console:
                self.console.print("[green]更新脚本创建成功[/green]")
                self.console.print("[yellow]应用将退出并开始更新...[/yellow]")
            
            # 执行批处理脚本并退出当前应用
            subprocess.Popen(batch_script_path, shell=True, cwd=current_exe_dir)
            
            # 退出当前应用
            sys.exit(0)
            
        except Exception as e:
            logger.exception("从exe更新失败")
            if self.console:
                self.console.print(f"[red]从exe更新失败: {str(e)}[/red]")
            return False
    
    def _update_from_script(self) -> bool:
        """从Python脚本启动的应用更新逻辑
        
        Returns:
            bool: 更新是否成功
        """
        try:
            if self.console:
                self.console.print("[cyan]检测到当前运行的是Python脚本[/cyan]")
                self.console.print("[cyan]使用pip更新应用...[/cyan]")
            
            # 使用pip更新
            update_command = [sys.executable, '-m', 'pip', 'install', '--upgrade', 'fastx_tui']
            
            if self.console:
                self.console.print(f"[yellow]执行命令: {' '.join(update_command)}[/yellow]")
            
            result = subprocess.run(
                update_command,
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                logger.info("应用更新成功")
                if self.console:
                    self.console.print("[green]应用更新成功! 请重启应用以应用新功能[/green]")
                return True
            else:
                logger.error(f"应用更新失败: {result.stderr}")
                if self.console:
                    self.console.print(f"[red]应用更新失败: {result.stderr}[/red]")
                return False
                
        except Exception as e:
            logger.exception("从脚本更新失败")
            if self.console:
                self.console.print(f"[red]从脚本更新失败: {str(e)}[/red]")
            return False
    
    def _get_exe_download_url(self) -> Optional[str]:
        """获取可执行文件的下载URL
        
        Returns:
            Optional[str]: 下载URL
        """
        # 根据平台选择下载URL
        current_platform = platform.system()
        
        if current_platform == "Windows":
            asset_name = "fastx.exe"
        elif current_platform == "Linux":
            asset_name = "fastx-linux"
        else:
            logger.error(f"不支持的平台: {current_platform}")
            if self.console:
                self.console.print(f"[red]不支持的平台: {current_platform}[/red]")
            return None
        
        # 构建下载URL
        download_url = f"https://github.com/fastxteam/FastX-Tui/releases/download/v{self.latest_version}/{asset_name}"
        
        logger.info(f"构建下载URL: {download_url}")
        return download_url
    
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
            
            if self.console:
                self.console.print(f"[cyan]开始下载: {url}[/cyan]")
            
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
                    
                    # 显示下载进度
                    if total_size > 0 and self.console:
                        progress = int((downloaded / total_size) * 100)
                        self.console.print(f"[cyan]下载进度: {progress}%[/cyan] [{downloaded}/{total_size} bytes]", end="\r")
            
            if self.console:
                self.console.print()  # 换行
            
            logger.info(f"文件下载成功: {save_path}, 大小: {os.path.getsize(save_path)} bytes")
            return True
            
        except urllib.error.URLError as e:
            logger.error(f"下载失败: {str(e)}")
            if self.console:
                self.console.print(f"[red]下载失败: {str(e)}[/red]")
            return False
        except Exception as e:
            logger.exception("下载文件发生异常")
            if self.console:
                self.console.print(f"[red]下载文件发生异常: {str(e)}[/red]")
            return False
    

