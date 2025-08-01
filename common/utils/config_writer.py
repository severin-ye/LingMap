#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration writer utility

Provides write and update functionality for system configuration files, supports runtime configuration modification.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigWriter:
    """
    Configuration writer class
    
    Responsible for writing configurations to config files, supports partial updates and full replacement.
    """
    
    @staticmethod
    def update_parallel_config(updates: Dict[str, Any]) -> bool:
        """
        Update parallel processing configuration
        
        Args:
            updates: Configuration items to update, supports nested dictionaries
                Example: {"max_workers": 8, "default_workers": {"graph_builder": 4}}
                
        Returns:
            Whether the update was successful
        """
        try:
            # Try to find config file path
            try:
                from common.utils.path_utils import get_config_path
                config_file = get_config_path("parallel_config.json")
            except ImportError:
                # If path_utils not found, try to find config file directly
                current_dir = Path(__file__).parent.absolute()
                project_root = current_dir.parent.parent
                config_file = project_root / "common" / "config" / "parallel_config.json"
                
            if not os.path.exists(config_file):
                logging.error(f"Parallel configuration file not found: {config_file}")
                return False
            
            # Read existing configuration
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Recursively update configuration
            ConfigWriter._update_nested_dict(config["parallel"], updates)
            
            # Write back to configuration file
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # Reinitialize parallel config
            from common.utils.parallel_config import ParallelConfig
            ParallelConfig.initialize()
            
            logging.info(f"Updated parallel configuration: {updates}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to update parallel configuration: {e}")
            return False
    
    @staticmethod
    def _update_nested_dict(target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively update nested dictionary
        
        Args:
            target: Target dictionary
            source: Source dictionary
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively update nested dictionaries
                ConfigWriter._update_nested_dict(target[key], value)
            else:
                # Directly update value
                target[key] = value
