#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内存优化工具
提供生成器模式和批处理功能，优化大数据量处理时的内存使用
"""

from typing import List, Iterator, Tuple, TypeVar, Generic, Callable, Any, Dict
from itertools import islice
import gc

T = TypeVar('T')


class BatchProcessor(Generic[T]):
    """批处理器，将大列表分批处理以节省内存"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    def process_in_batches(
        self, 
        items: List[T], 
        processor: Callable[[List[T]], Any]
    ) -> Iterator[Any]:
        """
        分批处理列表
        
        Args:
            items: 要处理的项目列表
            processor: 批处理函数
            
        Yields:
            每批的处理结果
        """
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            try:
                result = processor(batch)
                yield result
            finally:
                # 强制垃圾回收，释放内存
                gc.collect()


class MemoryEfficientPairGenerator:
    """内存高效的事件对生成器"""
    
    @staticmethod
    def generate_pairs_lazy(events: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """
        惰性生成事件对，避免一次性创建所有组合
        
        Args:
            events: 事件列表
            
        Yields:
            事件对
        """
        for i in range(len(events)):
            for j in range(i + 1, len(events)):
                yield (events[i], events[j])
    
    @staticmethod
    def generate_filtered_pairs(
        events: List[Any], 
        filter_func: Callable[[Any, Any], bool]
    ) -> Iterator[Tuple[Any, Any]]:
        """
        生成过滤后的事件对
        
        Args:
            events: 事件列表
            filter_func: 过滤函数，返回True表示保留该对
            
        Yields:
            通过过滤的事件对
        """
        for event1, event2 in MemoryEfficientPairGenerator.generate_pairs_lazy(events):
            if filter_func(event1, event2):
                yield (event1, event2)


class MemoryMonitor:
    """内存监控器"""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """
        获取当前内存使用情况
        
        Returns:
            内存使用统计
        """
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # 物理内存
            'vms_mb': memory_info.vms / 1024 / 1024,  # 虚拟内存
            'percent': process.memory_percent()        # 内存使用百分比
        }
    
    @staticmethod
    def memory_usage_decorator(func):
        """内存使用监控装饰器"""
        from functools import wraps
        import logging
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            
            before = MemoryMonitor.get_memory_usage()
            logger.debug(f"Memory before {func.__name__}: {before['rss_mb']:.2f} MB")
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                after = MemoryMonitor.get_memory_usage()
                diff = after['rss_mb'] - before['rss_mb']
                logger.debug(f"Memory after {func.__name__}: {after['rss_mb']:.2f} MB (diff: {diff:+.2f} MB)")
                
        return wrapper


# 使用示例的工具函数
def chunked_iterable(iterable, chunk_size: int):
    """将可迭代对象分块"""
    it = iter(iterable)
    while True:
        chunk = list(islice(it, chunk_size))
        if not chunk:
            break
        yield chunk
