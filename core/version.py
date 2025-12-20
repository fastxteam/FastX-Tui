#!/usr/bin/env python3
"""
版本管理模块，统一管理项目版本号
"""

from typing import Dict, Any
import toml
import os

# 项目根目录
get_root_dir = lambda: os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_version() -> str:
    """从pyproject.toml获取当前版本号"""
    pyproject_path = os.path.join(get_root_dir(), 'pyproject.toml')
    
    try:
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        return data['project']['version']
    except Exception as e:
        print(f"获取版本号失败: {e}")
        return "0.1.0"


def get_version_info() -> Dict[str, Any]:
    """获取完整的版本信息"""
    return {
        "version": get_version(),
        "project_name": "fastx-tui",
        "full_version": f"v{get_version()}"
    }


# 导出版本常量
VERSION = get_version()
FULL_VERSION = f"v{VERSION}"
