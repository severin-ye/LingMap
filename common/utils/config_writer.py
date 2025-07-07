#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置写入工具

提供对系统配置文件的写入和更新功能，支持在运行时修改配置。
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigWriter:
    """
    配置写入类
    
    负责将配置写入到配置文件，支持部分更新和全量替换。
    """
    
    @staticmethod
    def update_parallel_config(updates: Dict[str, Any]) -> bool:
        """
        更新并行处理配置
        
        Args:
            updates: 要更新的配置项，支持嵌套字典
                例如: {"max_workers": 8, "default_workers": {"graph_builder": 4}}
                
        Returns:
            更新是否成功
        """
        try:
            # TODO: Translate - 尝试找到Configure文件路径
            try:
                from common.utils.path_utils import get_config_path
                config_file = get_config_path("parallel_config.json")
            except ImportError:
                # TODO: Translate - 如果找不到path_utils，尝试直接查找Configure文件
                current_dir = Path(__file__).parent.absolute()
                project_root = current_dir.parent.parent
                config_file = project_root / "common" / "config" / "parallel_config.json"
                
            if not os.path.exists(config_file):
                logging.error(f"找不到并行配置文件: {config_file}")
                return False
            
            # TODO: Translate - Read现有Configure
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # TODO: Translate - 递归更新Configure
            ConfigWriter._update_nested_dict(config["parallel"], updates)
            
            # TODO: Translate - 写回Configure文件
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # TODO: Translate - 重新InitializeParallelConfig
            from common.utils.parallel_config import ParallelConfig
            ParallelConfig.initialize()
            
            logging.info(f"已更新并行配置: {updates}")
            return True
            
        except Exception as e:
            logging.error(f"更新并行配置失败: {e}")
            return False
    
    @staticmethod
    def _update_nested_dict(target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        递归更新嵌套字典
        
        Args:
            target: 目标字典
            source: 源字典
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # TODO: Translate - 对嵌套字典递归更新
                ConfigWriter._update_nested_dict(target[key], value)
            else:
                # TODO: Translate - 直接更新值
                target[key] = value
