"""Project path management module

Used to provide project root path, ensuring all modules can correctly reference files
"""

import os
from pathlib import Path

# Project root directory absolute path - two levels up from common/utils
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))).absolute()

def get_project_root() -> Path:
    """
    Get absolute path of project root directory
    
    Returns:
        Path: Absolute path of project root directory
    """
    return PROJECT_ROOT

def get_config_path(config_name: str) -> str:
    """
    Get absolute path of configuration file
    
    Args:
        config_name: Configuration file name
        
    Returns:
        str: Absolute path of configuration file
    """
    return str(PROJECT_ROOT / "common" / "config" / config_name)

def get_novel_path(filename: str = "") -> str:
    """
    Get absolute path of novel file
    
    Args:
        filename: Novel file name, returns novel directory if empty
        
    Returns:
        str: Absolute path of novel file or directory
    """
    if filename:
        return str(PROJECT_ROOT / "novel" / filename)
    return str(PROJECT_ROOT / "novel")

def get_output_path(dirname: str = "") -> str:
    """
    Get absolute path of output directory
    
    Args:
        dirname: Subdirectory name, returns output root directory if empty
        
    Returns:
        str: Absolute path of output directory
    """
    if dirname:
        return str(PROJECT_ROOT / "output" / dirname)
    return str(PROJECT_ROOT / "output")
