#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thread usage monitoring tool

Used to record and monitor the number of threads used by various modules during system runtime.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from common.utils.parallel_config import ParallelConfig


class ThreadUsageMonitor:
    """
    Thread usage monitoring class
    
    Responsible for recording and monitoring the number of threads used by various modules in the system, as well as overall system thread usage.
    """
    
    _logger: Optional[logging.Logger] = None
    _instance: Optional['ThreadUsageMonitor'] = None
    
    @classmethod
    def get_instance(cls):
        """Get instance using singleton pattern"""
        if cls._instance is None:
            cls._instance = ThreadUsageMonitor()
        return cls._instance
    
    def __init__(self):
        """Initialize monitor"""
        self._setup_logging()
        self.thread_usage = {}
    
    def _setup_logging(self):
        """Setup logging"""
        if ThreadUsageMonitor._logger is None:
            ThreadUsageMonitor._logger = logging.getLogger("thread_monitor")
            # Log level
            ThreadUsageMonitor._logger.setLevel(logging.INFO)
            
            # File handler
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"thread_usage_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            ThreadUsageMonitor._logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            ThreadUsageMonitor._logger.addHandler(console_handler)
    
    def log_module_thread_usage(self, module_name: str, thread_count: int, task_type: str = "default"):
        """
        Record module thread usage
        
        Args:
            module_name: Module name
            thread_count: Number of threads used
            task_type: Task type (io_bound, cpu_bound, default)
        """
        self.thread_usage[module_name] = {
            "thread_count": thread_count,
            "task_type": task_type
        }
        
        # Record to log
        ThreadUsageMonitor._logger.info(
            f"Module '{module_name}' uses {thread_count} threads for {task_type} type tasks"
        )
    
    def log_system_thread_usage(self):
        """Record overall system thread usage"""
        # Get configuration
        enabled = ParallelConfig.is_enabled()
        max_workers = ParallelConfig._config["max_workers"]
        module_config = ParallelConfig._config["default_workers"]
        
        ThreadUsageMonitor._logger.info(
            f"System parallel configuration: enabled={enabled}, global threads={max_workers}"
        )
        
        # Record module configuration
        ThreadUsageMonitor._logger.info("Module thread configuration:")
        for module, workers in module_config.items():
            ThreadUsageMonitor._logger.info(f"  - {module}: {workers}")
        
        # Record actual usage
        ThreadUsageMonitor._logger.info("Actual module thread usage:")
        for module, info in self.thread_usage.items():
            ThreadUsageMonitor._logger.info(
                f"  - {module}: {info['thread_count']} threads ({info['task_type']} tasks)"
            )


# Import datetime to avoid errors when used inside the class
from datetime import datetime


def log_thread_usage(module_name: str, thread_count: int, task_type: str = "default"):
    """
    Convenience function for recording module thread usage
    
    Args:
        module_name: Module name
        thread_count: Number of threads used
        task_type: Task type
    """
    monitor = ThreadUsageMonitor.get_instance()
    monitor.log_module_thread_usage(module_name, thread_count, task_type)
