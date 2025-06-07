"""项目路径管理模块

用于提供项目的根路径，确保所有模块能够正确引用文件
"""

import os
from pathlib import Path

# 项目根目录的绝对路径 - 从common/utils向上两级
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))).absolute()

def get_project_root() -> Path:
    """
    获取项目根目录的绝对路径
    
    Returns:
        Path: 项目根目录的绝对路径
    """
    return PROJECT_ROOT

def get_config_path(config_name: str) -> str:
    """
    获取配置文件的绝对路径
    
    Args:
        config_name: 配置文件名
        
    Returns:
        str: 配置文件的绝对路径
    """
    return str(PROJECT_ROOT / "common" / "config" / config_name)

def get_novel_path(filename: str = "") -> str:
    """
    获取小说文件的绝对路径
    
    Args:
        filename: 小说文件名，如果为空则返回小说目录
        
    Returns:
        str: 小说文件或目录的绝对路径
    """
    if filename:
        return str(PROJECT_ROOT / "novel" / filename)
    return str(PROJECT_ROOT / "novel")

def get_output_path(dirname: str = "") -> str:
    """
    获取输出目录的绝对路径
    
    Args:
        dirname: 子目录名，如果为空则返回输出根目录
        
    Returns:
        str: 输出目录的绝对路径
    """
    if dirname:
        return str(PROJECT_ROOT / "output" / dirname)
    return str(PROJECT_ROOT / "output")
