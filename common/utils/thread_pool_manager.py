#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
线程池管理器
统一管理项目中的线程池配置和创建
"""

import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from common.utils.parallel_config import ParallelConfig


class ThreadPoolManager:
    """线程池管理器，统一管理线程池配置"""
    
    @staticmethod
    def get_optimal_workers(task_type: str = "default") -> int:
        """
        根据任务类型获取最优线程数
        
        Args:
            task_type: 任务类型 ("io_intensive", "cpu_intensive", "default")
            
        Returns:
            建议的线程数
        """
        cpu_count = multiprocessing.cpu_count()
        
        # 检查并行配置
        if not ParallelConfig.is_enabled():
            return 1
        
        # 根据任务类型调整线程数
        if task_type == "io_intensive":
            # IO密集型任务，可以使用更多线程
            return min(cpu_count * 2, 20)
        elif task_type == "cpu_intensive":
            # CPU密集型任务，使用CPU核心数
            return cpu_count
        else:
            # 默认配置
            return min(cpu_count + 1, 8)
    
    @staticmethod
    def create_thread_pool(
        task_type: str = "default",
        max_workers: Optional[int] = None
    ) -> ThreadPoolExecutor:
        """
        创建线程池
        
        Args:
            task_type: 任务类型
            max_workers: 自定义最大线程数（覆盖自动计算）
            
        Returns:
            线程池执行器
        """
        if max_workers is None:
            max_workers = ThreadPoolManager.get_optimal_workers(task_type)
        
        return ThreadPoolExecutor(max_workers=max_workers)


# 为向后兼容，提供配置常量
class OptimalThreadConfig:
    """优化的线程配置常量"""
    
    EVENT_EXTRACTION = ThreadPoolManager.get_optimal_workers("io_intensive")  # 事件提取 (LLM API调用)
    CAUSAL_ANALYSIS = ThreadPoolManager.get_optimal_workers("io_intensive")   # 因果分析 (LLM API调用)
    GRAPH_PROCESSING = ThreadPoolManager.get_optimal_workers("cpu_intensive") # 图处理 (CPU密集)
    DEFAULT = ThreadPoolManager.get_optimal_workers("default")                # 默认配置
