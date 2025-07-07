#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
线程使用情况监控工具

用于在系统运行时记录和监控各个模块使用的线程数。
"""

import os
import sys
import logging
from typing import Dict, Any
from pathlib import Path

from common.utils.parallel_config import ParallelConfig


class ThreadUsageMonitor:
    """
    线程使用情况监控类
    
    负责记录和监控系统中各模块使用的线程数，以及系统整体线程使用情况。
    """
    
    _logger = None
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """单例模式获取实例"""
        if cls._instance is None:
            cls._instance = ThreadUsageMonitor()
        return cls._instance
    
    def __init__(self):
        """初始化监控器"""
        self._setup_logging()
        self.thread_usage = {}
    
    def _setup_logging(self):
        """设置日志记录"""
        if ThreadUsageMonitor._logger is None:
            ThreadUsageMonitor._logger = logging.getLogger("thread_monitor")
            # TODO: Translate - 日志级别
            ThreadUsageMonitor._logger.setLevel(logging.INFO)
            
            # TODO: Translate - 文件Process器
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"thread_usage_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            ThreadUsageMonitor._logger.addHandler(file_handler)
            
            # TODO: Translate - 控制台Process器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            ThreadUsageMonitor._logger.addHandler(console_handler)
    
    def log_module_thread_usage(self, module_name: str, thread_count: int, task_type: str = "default"):
        """
        记录模块线程使用情况
        
        Args:
            module_name: 模块名称
            thread_count: 使用的线程数
            task_type: 任务类型 (io_bound, cpu_bound, default)
        """
        self.thread_usage[module_name] = {
            "thread_count": thread_count,
            "task_type": task_type
        }
        
        # TODO: Translate - 记录到日志
        ThreadUsageMonitor._logger.info(
            f"模块 '{module_name}' 使用 {thread_count} 个线程执行 {task_type} 类型任务"
        )
    
    def log_system_thread_usage(self):
        """记录系统整体线程使用情况"""
        # GetConfigure
        enabled = ParallelConfig.is_enabled()
        max_workers = ParallelConfig._config["max_workers"]
        module_config = ParallelConfig._config["default_workers"]
        
        ThreadUsageMonitor._logger.info(
            f"系统并行配置: 启用状态={enabled}, 全局线程数={max_workers}"
        )
        
        # TODO: Translate - 记录各模块Configure
        ThreadUsageMonitor._logger.info("模块线程配置:")
        for module, workers in module_config.items():
            ThreadUsageMonitor._logger.info(f"  - {module}: {workers}")
        
        # TODO: Translate - 记录实际Use情况
        ThreadUsageMonitor._logger.info("模块实际线程使用情况:")
        for module, info in self.thread_usage.items():
            ThreadUsageMonitor._logger.info(
                f"  - {module}: {info['thread_count']} 线程 ({info['task_type']} 任务)"
            )


# TODO: Translate - Importdatetime，避免在类内部Use时报错
from datetime import datetime


def log_thread_usage(module_name: str, thread_count: int, task_type: str = "default"):
    """
    记录模块线程使用情况的便捷函数
    
    Args:
        module_name: 模块名称
        thread_count: 使用的线程数
        task_type: 任务类型
    """
    monitor = ThreadUsageMonitor.get_instance()
    monitor.log_module_thread_usage(module_name, thread_count, task_type)
