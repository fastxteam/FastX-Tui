#!/usr/bin/env python3
"""
虚拟环境管理器模块
用于管理插件的虚拟环境，解决不同插件之间的环境隔离问题
"""
import os
import subprocess
import sys
import tempfile
from typing import Dict, Optional, List
from .logger import get_logger

class VenvManager:
    """虚拟环境管理器
    
    用于为每个插件创建和管理独立的虚拟环境，确保不同插件之间的依赖隔离
    优先使用uv进行虚拟环境管理，以提高速度和效率
    """
    
    def __init__(self, venv_base_dir: str = ".venv_plugins"):
        """初始化虚拟环境管理器
        
        Args:
            venv_base_dir: 虚拟环境的基础目录
        """
        self.venv_base_dir = venv_base_dir
        self.logger = get_logger("VenvManager")
        
        # 创建虚拟环境基础目录
        os.makedirs(venv_base_dir, exist_ok=True)
        
        # 记录已创建的虚拟环境
        self.created_venvs: Dict[str, str] = {}  # plugin_name -> venv_path
        
        # 记录当前激活的虚拟环境
        self.active_venv: Optional[str] = None
        
        # 检查系统中是否有uv可用
        self.uv_available = self._check_uv_availability()
        if not self.uv_available:
            self.logger.warning("uv不可用，将使用venv/pip作为备选方案")
        else:
            self.logger.info("uv可用，将优先使用uv进行虚拟环境管理")
    
    def _check_uv_availability(self) -> bool:
        """检查系统中是否有uv可用
        
        Returns:
            bool: uv是否可用
        """
        try:
            # 检查uv模块是否可用
            import uv
            return True
        except ImportError:
            pass
        
        try:
            # 检查uv命令是否可用
            result = subprocess.run(
                ["uv", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def get_venv_path(self, plugin_name: str) -> str:
        """获取插件的虚拟环境路径
        
        Args:
            plugin_name: 插件名称
        
        Returns:
            str: 虚拟环境路径
        """
        return os.path.join(self.venv_base_dir, plugin_name)
    
    def get_venv_python_path(self, plugin_name: str) -> str:
        """获取插件虚拟环境中的Python可执行文件路径
        
        Args:
            plugin_name: 插件名称
        
        Returns:
            str: Python可执行文件路径
        """
        venv_path = self.get_venv_path(plugin_name)
        if sys.platform == "win32":
            return os.path.join(venv_path, "Scripts", "python.exe")
        else:
            return os.path.join(venv_path, "bin", "python")
    
    def get_venv_uv_path(self, plugin_name: str) -> str:
        """获取插件虚拟环境中的uv可执行文件路径
        
        Args:
            plugin_name: 插件名称
        
        Returns:
            str: uv可执行文件路径
        """
        venv_path = self.get_venv_path(plugin_name)
        if sys.platform == "win32":
            return os.path.join(venv_path, "Scripts", "uv.exe")
        else:
            return os.path.join(venv_path, "bin", "uv")
    
    def venv_exists(self, plugin_name: str) -> bool:
        """检查插件的虚拟环境是否已存在
        
        Args:
            plugin_name: 插件名称
        
        Returns:
            bool: 虚拟环境是否存在
        """
        venv_path = self.get_venv_path(plugin_name)
        python_path = self.get_venv_python_path(plugin_name)
        return os.path.exists(venv_path) and os.path.exists(python_path)
    
    def _check_venv_up_to_date(self, plugin_name: str, plugin_path: str) -> bool:
        """检查虚拟环境是否是最新的
        
        Args:
            plugin_name: 插件名称
            plugin_path: 插件目录路径
        
        Returns:
            bool: 虚拟环境是否是最新的
        """
        # 检查虚拟环境是否存在
        if not self.venv_exists(plugin_name):
            return False
        
        # 检查pyproject.toml或uv.lock文件的修改时间是否比虚拟环境创建时间晚
        venv_path = self.get_venv_path(plugin_name)
        venv_mtime = os.path.getmtime(venv_path)
        
        # 检查pyproject.toml
        pyproject_path = os.path.join(plugin_path, "pyproject.toml")
        if os.path.exists(pyproject_path):
            pyproject_mtime = os.path.getmtime(pyproject_path)
            if pyproject_mtime > venv_mtime:
                self.logger.debug(f"插件 {plugin_name} 的pyproject.toml已更新，需要更新虚拟环境")
                return False
        
        # 检查uv.lock
        uv_lock_path = os.path.join(plugin_path, "uv.lock")
        if os.path.exists(uv_lock_path):
            uv_lock_mtime = os.path.getmtime(uv_lock_path)
            if uv_lock_mtime > venv_mtime:
                self.logger.debug(f"插件 {plugin_name} 的uv.lock已更新，需要更新虚拟环境")
                return False
        
        # 检查requirements.txt
        requirements_path = os.path.join(plugin_path, "requirements.txt")
        if os.path.exists(requirements_path):
            requirements_mtime = os.path.getmtime(requirements_path)
            if requirements_mtime > venv_mtime:
                self.logger.debug(f"插件 {plugin_name} 的requirements.txt已更新，需要更新虚拟环境")
                return False
        
        return True
    
    def create_venv(self, plugin_name: str, plugin_path: str) -> bool:
        """为插件创建虚拟环境
        
        Args:
            plugin_name: 插件名称
            plugin_path: 插件目录路径
        
        Returns:
            bool: 是否成功创建虚拟环境
        """
        try:
            # 检查虚拟环境是否已经是最新的
            if self._check_venv_up_to_date(plugin_name, plugin_path):
                self.logger.info(f"插件 {plugin_name} 的虚拟环境已经是最新的，跳过创建")
                return True
            
            self.logger.info(f"为插件 {plugin_name} 创建虚拟环境")
            
            # 检查插件目录下是否有pyproject.toml文件
            pyproject_path = os.path.join(plugin_path, "pyproject.toml")
            if not os.path.exists(pyproject_path):
                self.logger.error(f"插件 {plugin_name} 缺少pyproject.toml文件")
                return False
            
            # 检查插件目录下是否有uv.lock文件
            uv_lock_path = os.path.join(plugin_path, "uv.lock")
            if not os.path.exists(uv_lock_path):
                self.logger.warning(f"插件 {plugin_name} 缺少uv.lock文件")
            
            # 创建虚拟环境
            venv_path = self.get_venv_path(plugin_name)
            
            # 确保虚拟环境目录不存在
            if os.path.exists(venv_path):
                import shutil
                shutil.rmtree(venv_path)
            
            # 使用uv创建虚拟环境（优先）
            if self.uv_available:
                try:
                    # 使用系统uv创建虚拟环境
                    result = subprocess.run(
                        ["uv", "venv", venv_path],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        raise Exception(f"uv创建虚拟环境失败: {result.stderr}")
                    
                    self.logger.info("使用uv创建虚拟环境成功")
                except Exception as e:
                    self.logger.warning(f"使用uv创建虚拟环境失败，尝试使用venv模块: {str(e)}")
                    
                    # 使用标准库venv模块创建虚拟环境
                    import venv
                    try:
                        venv.create(venv_path, with_pip=True)
                        self.logger.info("使用venv模块创建虚拟环境成功")
                    except Exception as venv_e:
                        self.logger.error(f"使用venv模块创建虚拟环境失败: {str(venv_e)}")
                        return False
            else:
                # uv不可用，直接使用venv模块
                import venv
                try:
                    venv.create(venv_path, with_pip=True)
                    self.logger.info("使用venv模块创建虚拟环境成功")
                except Exception as venv_e:
                    self.logger.error(f"使用venv模块创建虚拟环境失败: {str(venv_e)}")
                    return False
            
            # 安装依赖
            if not self._install_dependencies(plugin_name, plugin_path):
                return False
            
            self.created_venvs[plugin_name] = venv_path
            self.logger.info(f"插件 {plugin_name} 的虚拟环境创建成功")
            return True
            
        except Exception as e:
            self.logger.error(f"为插件 {plugin_name} 创建虚拟环境时发生错误: {str(e)}")
            return False
    
    def _install_dependencies(self, plugin_name: str, plugin_path: str) -> bool:
        """安装插件依赖
        
        Args:
            plugin_name: 插件名称
            plugin_path: 插件目录路径
        
        Returns:
            bool: 是否成功安装依赖
        """
        # 使用虚拟环境中的包管理器安装依赖
        venv_python_path = self.get_venv_python_path(plugin_name)
        
        # 检查虚拟环境中是否有uv
        venv_uv_path = self.get_venv_uv_path(plugin_name)
        uv_available = os.path.exists(venv_uv_path)
        
        try:
            if uv_available or self.uv_available:
                # 使用uv安装依赖
                self.logger.info("使用uv安装依赖")
                
                # 使用系统uv或虚拟环境中的uv
                uv_path = venv_uv_path if uv_available else "uv"
                
                # 切换到插件目录并执行uv sync
                result = subprocess.run(
                    [uv_path, "sync"],
                    cwd=plugin_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    raise Exception(f"uv安装依赖失败: {result.stderr}")
            else:
                # 使用pip安装依赖
                self.logger.info("使用pip安装依赖")
                
                # 升级pip
                result = subprocess.run(
                    [venv_python_path, "-m", "pip", "install", "--upgrade", "pip"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    raise Exception(f"升级pip失败: {result.stderr}")
                
                # 检查requirements.txt
                requirements_path = os.path.join(plugin_path, "requirements.txt")
                if os.path.exists(requirements_path):
                    # 使用requirements.txt安装依赖
                    result = subprocess.run(
                        [venv_python_path, "-m", "pip", "install", "-r", requirements_path],
                        cwd=plugin_path,
                        capture_output=True,
                        text=True
                    )
                else:
                    # 使用pyproject.toml安装依赖
                    result = subprocess.run(
                        [venv_python_path, "-m", "pip", "install", "."],
                        cwd=plugin_path,
                        capture_output=True,
                        text=True
                    )
                
                if result.returncode != 0:
                    raise Exception(f"pip安装依赖失败: {result.stderr}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"为插件 {plugin_name} 安装依赖失败: {str(e)}")
            return False
    
    def delete_venv(self, plugin_name: str) -> bool:
        """删除插件的虚拟环境
        
        Args:
            plugin_name: 插件名称
        
        Returns:
            bool: 是否成功删除虚拟环境
        """
        try:
            venv_path = self.get_venv_path(plugin_name)
            
            if not os.path.exists(venv_path):
                self.logger.info(f"插件 {plugin_name} 的虚拟环境不存在")
                return True
            
            # 使用uv删除虚拟环境（优先）
            if self.uv_available:
                try:
                    result = subprocess.run(
                        ["uv", "venv", "remove", venv_path],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        raise Exception(f"uv删除虚拟环境失败: {result.stderr}")
                    
                    self.logger.info("使用uv删除虚拟环境成功")
                except Exception as e:
                    self.logger.warning(f"使用uv删除虚拟环境失败，尝试使用shutil: {str(e)}")
                    
                    # 使用shutil删除虚拟环境
                    import shutil
                    shutil.rmtree(venv_path)
            else:
                # uv不可用，直接使用shutil
                import shutil
                shutil.rmtree(venv_path)
            
            if plugin_name in self.created_venvs:
                del self.created_venvs[plugin_name]
            
            if self.active_venv == plugin_name:
                self.active_venv = None
            
            self.logger.info(f"插件 {plugin_name} 的虚拟环境已删除")
            return True
            
        except Exception as e:
            self.logger.error(f"删除插件 {plugin_name} 的虚拟环境时发生错误: {str(e)}")
            return False
    
    def run_in_venv(self, plugin_name: str, command: List[str], plugin_path: str = None) -> Optional[Dict[str, any]]:
        """在插件的虚拟环境中执行命令
        
        Args:
            plugin_name: 插件名称
            command: 要执行的命令列表
            plugin_path: 插件目录路径
        
        Returns:
            Optional[Dict[str, any]]: 命令执行结果，包含returncode、stdout和stderr
        """
        try:
            # 检查虚拟环境是否存在
            if not self.venv_exists(plugin_name):
                self.logger.error(f"插件 {plugin_name} 的虚拟环境不存在")
                return None
            
            # 获取虚拟环境中的Python可执行文件路径
            python_path = self.get_venv_python_path(plugin_name)
            
            # 构建完整的命令
            full_command = [python_path, "-c"] + command
            
            # 执行命令
            result = subprocess.run(
                full_command,
                cwd=plugin_path,
                capture_output=True,
                text=True
            )
            
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            self.logger.error(f"在插件 {plugin_name} 的虚拟环境中执行命令时发生错误: {str(e)}")
            return None
    
    def get_venv_info(self, plugin_name: str) -> Optional[Dict[str, str]]:
        """获取插件虚拟环境的信息
        
        Args:
            plugin_name: 插件名称
        
        Returns:
            Optional[Dict[str, str]]: 虚拟环境信息
        """
        try:
            if not self.venv_exists(plugin_name):
                return None
            
            python_path = self.get_venv_python_path(plugin_name)
            
            # 获取Python版本
            result = subprocess.run(
                [python_path, "--version"],
                capture_output=True,
                text=True
            )
            python_version = result.stdout.strip()
            
            # 获取已安装的包
            result = subprocess.run(
                [python_path, "-m", "pip", "list"],
                capture_output=True,
                text=True
            )
            installed_packages = result.stdout
            
            return {
                "python_version": python_version,
                "installed_packages": installed_packages
            }
            
        except Exception as e:
            self.logger.error(f"获取插件 {plugin_name} 虚拟环境信息时发生错误: {str(e)}")
            return None
    
    def cleanup(self):
        """清理虚拟环境管理器"""
        self.logger.info("清理虚拟环境管理器")
        # 这里可以添加一些清理逻辑，比如删除临时文件等
    
    def update_venv(self, plugin_name: str, plugin_path: str) -> bool:
        """更新插件的虚拟环境
        
        Args:
            plugin_name: 插件名称
            plugin_path: 插件目录路径
        
        Returns:
            bool: 是否成功更新虚拟环境
        """
        try:
            self.logger.info(f"更新插件 {plugin_name} 的虚拟环境")
            
            # 检查虚拟环境是否已经是最新的
            if self._check_venv_up_to_date(plugin_name, plugin_path):
                self.logger.info(f"插件 {plugin_name} 的虚拟环境已经是最新的，跳过更新")
                return True
            
            # 检查虚拟环境是否存在
            if not self.venv_exists(plugin_name):
                # 如果虚拟环境不存在，创建新的虚拟环境
                return self.create_venv(plugin_name, plugin_path)
            
            # 使用uv更新依赖（优先）
            venv_python_path = self.get_venv_python_path(plugin_name)
            venv_uv_path = self.get_venv_uv_path(plugin_name)
            uv_available = os.path.exists(venv_uv_path) or self.uv_available
            
            try:
                if uv_available:
                    # 使用uv更新依赖
                    self.logger.info("使用uv更新依赖")
                    
                    # 使用系统uv或虚拟环境中的uv
                    uv_path = venv_uv_path if os.path.exists(venv_uv_path) else "uv"
                    
                    result = subprocess.run(
                        [uv_path, "sync"],
                        cwd=plugin_path,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        raise Exception(f"uv更新依赖失败: {result.stderr}")
                else:
                    # 使用pip更新依赖
                    self.logger.info("使用pip更新依赖")
                    
                    # 检查requirements.txt
                    requirements_path = os.path.join(plugin_path, "requirements.txt")
                    if os.path.exists(requirements_path):
                        # 使用requirements.txt更新依赖
                        result = subprocess.run(
                            [venv_python_path, "-m", "pip", "install", "-r", requirements_path],
                            cwd=plugin_path,
                            capture_output=True,
                            text=True
                        )
                    else:
                        # 使用pyproject.toml更新依赖
                        result = subprocess.run(
                            [venv_python_path, "-m", "pip", "install", "."],
                            cwd=plugin_path,
                            capture_output=True,
                            text=True
                        )
                    
                    if result.returncode != 0:
                        raise Exception(f"pip更新依赖失败: {result.stderr}")
            except Exception as e:
                self.logger.error(f"更新插件 {plugin_name} 依赖失败: {str(e)}")
                return False
            
            self.logger.info(f"插件 {plugin_name} 的虚拟环境更新成功")
            return True
            
        except Exception as e:
            self.logger.error(f"更新插件 {plugin_name} 的虚拟环境时发生错误: {str(e)}")
            return False
    
    def list_venvs(self) -> List[str]:
        """列出所有已创建的虚拟环境
        
        Returns:
            List[str]: 已创建的虚拟环境名称列表
        """
        venvs = []
        for item in os.listdir(self.venv_base_dir):
            venv_path = os.path.join(self.venv_base_dir, item)
            if os.path.isdir(venv_path):
                python_path = os.path.join(venv_path, "Scripts", "python.exe") if sys.platform == "win32" else os.path.join(venv_path, "bin", "python")
                if os.path.exists(python_path):
                    venvs.append(item)
        return venvs
