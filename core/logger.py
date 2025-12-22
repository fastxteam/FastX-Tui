#!/usr/bin/env python3
"""
统一日志管理模块
"""
import sys
import os
from typing import Optional
from loguru import logger

class Logger:
    """统一日志管理器"""
    
    def __init__(self, name: str = "fastx-tui", log_level: str = "INFO"):
        self.name = name
        self.log_level = log_level.upper()
        
        # 清除默认处理器
        logger.remove()
        
        # 添加控制台处理器
        logger.add(
            sys.stdout,
            level=self.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} [{level}] [{name}] {message}",
            enqueue=True  # 异步日志
        )
        
        # 获取应用程序所在目录
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # 创建日志目录
        log_dir = os.path.join(app_dir, "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 添加文件处理器
        logger.add(
            os.path.join(log_dir, "fastx-tui.log"),
            level="DEBUG",  # 文件日志记录所有级别
            format="{time:YYYY-MM-DD HH:mm:ss} [{level}] [{name}] {message}",
            enqueue=True,
            rotation="10 MB",  # 日志文件大小限制
            retention="7 days",  # 保留7天日志
            compression="zip"  # 压缩旧日志
        )
        
        # 配置loguru的上下文
        self.logger = logger.bind(name=self.name)
    
    def set_log_level(self, level: str):
        """设置日志级别"""
        self.log_level = level.upper()
        logger.remove()
        logger.add(
            sys.stdout,
            level=self.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} [{level}] [{name}] {message}",
            enqueue=True
        )
        
        # 获取应用程序所在目录
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # 添加文件处理器
        log_dir = os.path.join(app_dir, "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        logger.add(
            os.path.join(log_dir, "fastx-tui.log"),
            level="DEBUG",  # 文件日志记录所有级别
            format="{time:YYYY-MM-DD HH:mm:ss} [{level}] [{name}] {message}",
            enqueue=True,
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )
        
        self.logger = logger.bind(name=self.name)
    
    def get_logger(self, name: Optional[str] = None):
        """获取日志器实例
        
        Args:
            name: 日志器名称，如果提供则创建子日志器
            
        Returns:
            绑定了名称的loguru logger
        """
        if name:
            return logger.bind(name=f"{self.name}.{name}")
        return self.logger
    
    def debug(self, msg: str, *args, **kwargs):
        """调试日志"""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """信息日志"""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """警告日志"""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """错误日志"""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """严重错误日志"""
        self.logger.critical(msg, *args, **kwargs)
    
    def get_current_level(self) -> str:
        """获取当前日志级别"""
        return self.log_level
    
    def get_available_levels(self) -> list:
        """获取可用的日志级别"""
        return ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# 创建全局日志实例
global_logger = Logger()

# 便捷方法
def get_logger(name: Optional[str] = None):
    """获取日志器"""
    return global_logger.get_logger(name)


def debug(msg: str, *args, **kwargs):
    """调试日志"""
    global_logger.debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """信息日志"""
    global_logger.info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """警告日志"""
    global_logger.warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """错误日志"""
    global_logger.error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """严重错误日志"""
    global_logger.critical(msg, *args, **kwargs)


def set_log_level(level: str):
    """设置全局日志级别"""
    global_logger.set_log_level(level)


def get_current_log_level() -> str:
    """获取当前全局日志级别"""
    return global_logger.get_current_level()


def get_available_log_levels() -> list:
    """获取可用的日志级别"""
    return global_logger.get_available_levels()

