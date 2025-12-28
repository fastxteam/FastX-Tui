#!/usr/bin/env python3
"""
版本管理模块，统一管理项目版本号
"""

import importlib.metadata
import os
from typing import Any

import toml

# 项目根目录
get_root_dir = lambda: os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_version() -> str:
    """获取当前版本号
    优先从pyproject.toml获取，如果失败则尝试从已安装的包元数据获取
    """
    # 尝试从pyproject.toml获取
    pyproject_path = os.path.join(get_root_dir(), 'pyproject.toml')

    try:
        with open(pyproject_path, encoding='utf-8') as f:
            data = toml.load(f)
        return data['project']['version']
    except Exception:
        # pyproject.toml不存在或读取失败，尝试从包元数据获取
        try:
            # 从已安装的包元数据获取版本
            return importlib.metadata.version('fastx-tui')
        except Exception:
            # 所有方式都失败，返回默认值（这个值会被bump工作流自动更新）
            return "0.1.0"


def get_version_info() -> dict[str, Any]:
    """获取完整的版本信息"""
    return {
        "version": get_version(),
        "project_name": "fastx-tui",
        "full_version": f"v{get_version()}"
    }


# 导出版本常量
VERSION = get_version()
FULL_VERSION = f"v{VERSION}"
