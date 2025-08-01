#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parallel processing configuration module

Provides global parallel processing configuration to control multi-threaded parallel processing behavior in the system.
Supports loading configuration from config files to ensure unified thread count usage across the system.
"""

import os
import json
import multiprocessing
from typing import Dict, Any, Optional
from pathlib import Path


class ParallelConfig:
    """
    Parallel processing configuration class
    
    Responsible for managing parallel processing configuration in the system, including whether to enable parallel processing, thread count, etc.
    All modules use the same configuration to ensure thread count consistency.
    """
    
    # Default configuration
    _config = {
        "enabled": True,  # Enable parallel processing by default
        "description": "Whether to enable parallel processing, when set to false all modules will use single thread",
        "max_workers": None,  # Automatically set worker thread count
        "max_workers_description": "Global default maximum worker thread count, usually set to CPU core count or slightly higher than core count",
        "adaptive": {
            "enabled": True,  # Whether to enable adaptive adjustment
            "enabled_description": "Whether to enable adaptive thread allocation, dynamically adjust thread count based on task type",
            "io_bound_factor": 1.5,  # Thread count factor for IO-intensive tasks
            "io_bound_factor_description": "Thread coefficient for IO-intensive tasks (such as API calls), usually set >1",
            "cpu_bound_factor": 0.8,  # Thread count factor for CPU-intensive tasks
            "cpu_bound_factor_description": "Thread coefficient for CPU-intensive tasks (such as graphics rendering), usually set <1"
        },
        "default_workers": {  # Default thread count for each module
            "event_extraction": None,
            "event_extraction_description": "Event extraction: IO-intensive task, many API calls, suitable for more threads",
            "hallucination_refine": None,
            "hallucination_refine_description": "Hallucination refinement: IO-intensive task, many API calls, suitable for more threads",
            "causal_linking": None,
            "causal_linking_description": "Causal linking: Mixed task, both computation and API calls, use standard thread count",
            "graph_builder": None,
            "graph_builder_description": "Graph building: CPU-intensive task, mainly computation and rendering, suitable for fewer threads"
        },
        "default_workers_description": "Default thread count for each module, can override global settings"
    }
    
    @classmethod
    def initialize(cls, options: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize parallel processing configuration
        
        Args:
            options: Configuration options, including:
                - enabled: Whether to enable parallel processing
                - max_workers: Maximum worker thread count
                - adaptive: Adaptive adjustment configuration
                - default_workers: Default thread count for each module
        """
        if options is None:
            options = {}
            
        # First try to load from configuration file
        config_loaded = cls._load_from_config_file()
        
        # Check environment variables
        env_enabled = os.environ.get("PARALLEL_ENABLED", "").lower()
        if env_enabled in ["false", "0", "no"]:
            cls._config["enabled"] = False
        elif env_enabled in ["true", "1", "yes"]:
            cls._config["enabled"] = True
            
        # Thread configuration from environment variables (overrides config file)
        env_workers = os.environ.get("MAX_WORKERS")
        if env_workers and env_workers.isdigit():
            cls._config["max_workers"] = int(env_workers)
            
        # Parameters override environment variables and config file
        if "enabled" in options:
            cls._config["enabled"] = bool(options["enabled"])
        if "max_workers" in options:
            cls._config["max_workers"] = options["max_workers"]
        if "adaptive" in options:
            if isinstance(options["adaptive"], dict):
                for key, value in options["adaptive"].items():
                    if key in cls._config["adaptive"]:
                        cls._config["adaptive"][key] = value
            elif isinstance(options["adaptive"], bool):
                cls._config["adaptive"]["enabled"] = options["adaptive"]
                
        # If thread count not specified, set based on CPU core count
        if cls._config["max_workers"] is None and cls._config["enabled"]:
            cpu_count = multiprocessing.cpu_count()
            # Default to use CPU core count, but set upper and lower limits
            cls._config["max_workers"] = max(2, min(16, cpu_count))
            
        # Set worker thread count for each module to unified configuration
        for module in cls._config["default_workers"]:
            if cls._config["default_workers"][module] is None:
                cls._config["default_workers"][module] = cls._config["max_workers"]
            
        # If parallel processing disabled, force set thread count to 1
        if not cls._config["enabled"]:
            cls._config["max_workers"] = 1
            for module in cls._config["default_workers"]:
                cls._config["default_workers"][module] = 1
    
    @classmethod
    def _load_from_config_file(cls) -> bool:
        """
        Load parallel configuration from config file
        
        Returns:
            Whether configuration was loaded successfully
        """
        # Try to find config file path
        try:
            from common.utils.path_utils import get_config_path
            config_file = get_config_path("parallel_config.json")
        except ImportError:
            # If path_utils not found, try to find config file directly
            current_dir = Path(__file__).parent.absolute()
            project_root = current_dir.parent.parent.parent
            config_file = project_root / "common" / "config" / "parallel_config.json"
            
        if not os.path.exists(config_file):
            return False
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # Parse configuration data
            if "parallel" in config_data:
                parallel_config = config_data["parallel"]
                
                # Basic configuration
                if "enabled" in parallel_config:
                    cls._config["enabled"] = bool(parallel_config["enabled"])
                if "max_workers" in parallel_config:
                    cls._config["max_workers"] = int(parallel_config["max_workers"])
                    
                # Adaptive configuration
                if "adaptive" in parallel_config and isinstance(parallel_config["adaptive"], dict):
                    for key, value in parallel_config["adaptive"].items():
                        if key in cls._config["adaptive"] or key == "enabled":
                            cls._config["adaptive"][key] = value
                            
                # Default thread count for each module
                if "default_workers" in parallel_config and isinstance(parallel_config["default_workers"], dict):
                    for module, workers in parallel_config["default_workers"].items():
                        if module in cls._config["default_workers"]:
                            cls._config["default_workers"][module] = workers
                
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to load parallel configuration file: {e}")
            return False
    
    @classmethod
    def is_enabled(cls) -> bool:
        """
        Check if parallel processing is enabled
        
        Returns:
            Whether parallel processing is enabled
        """
        return cls._config["enabled"]
    
    @classmethod
    def get_max_workers(cls, task_type: str = "default") -> int:
        """
        Get maximum worker thread count
        
        Args:
            task_type: Task type, can be used to adjust thread count for different tasks
            
        Returns:
            Maximum worker thread count
        """
        if not cls._config["enabled"]:
            return 1
            
        max_workers = cls._config["max_workers"]
        
        # Adjustments for specific task types
        if cls._config["adaptive"]:
            if task_type == "io_bound":
                # IO-intensive tasks can use more threads
                return max(4, max_workers)
            elif task_type == "cpu_bound":
                # CPU-intensive tasks limit thread count
                return min(max_workers, max(2, multiprocessing.cpu_count() - 1))
        
        return max_workers
    
    @classmethod
    def set_enabled(cls, enabled: bool) -> None:
        """
        Set whether to enable parallel processing
        
        Args:
            enabled: Whether to enable
        """
        cls._config["enabled"] = enabled
        if not enabled:
            cls._config["max_workers"] = 1
    
    @classmethod
    def set_max_workers(cls, max_workers: int) -> None:
        """
        Set maximum worker thread count
        
        Args:
            max_workers: Maximum thread count
        """
        cls._config["max_workers"] = max(1, max_workers)
    
    @classmethod
    def get_optimal_batch_size(cls, total_items: int, task_type: str = "default") -> int:
        """
        Calculate optimal batch processing size
        
        Args:
            total_items: Total number of items
            task_type: Task type
            
        Returns:
            Optimal batch processing size
        """
        max_workers = cls.get_max_workers(task_type)
        
        if max_workers <= 1 or total_items <= max_workers:
            return total_items
            
        # Calculate number of items per worker thread
        items_per_worker = max(1, (total_items + max_workers - 1) // max_workers)
        
        # Return reasonable batch processing size
        return items_per_worker
    
    @classmethod
    def get_description(cls, key: str) -> Optional[str]:
        """
        Get description information for configuration item
        
        Args:
            key: Key of the configuration item
            
        Returns:
            Description information of the configuration item
        """
        keys = key.split(".")
        config = cls._config
        
        for k in keys:
            if k in config and isinstance(config[k], dict):
                config = config[k]
            else:
                return None
            
        return config.get("description")
