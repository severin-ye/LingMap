#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能监控和指标收集工具
"""

import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from contextlib import contextmanager


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    
    operation: str
    start_time: float
    end_time: float
    duration: float
    memory_before: Optional[float] = None
    memory_after: Optional[float] = None
    memory_peak: Optional[float] = None
    input_size: Optional[int] = None
    output_size: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PerformanceTracker:
    """性能跟踪器"""
    
    def __init__(self, output_dir: str = "performance_logs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.metrics: List[PerformanceMetrics] = []
    
    @contextmanager
    def track_operation(
        self, 
        operation_name: str, 
        input_size: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        跟踪操作性能的上下文管理器
        
        Args:
            operation_name: 操作名称
            input_size: 输入数据大小
            metadata: 额外的元数据
        """
        start_time = time.time()
        memory_before = None
        error = None
        
        # 尝试获取内存使用情况
        try:
            from common.utils.memory_optimizer import MemoryMonitor
            memory_before = MemoryMonitor.get_memory_usage()['rss_mb']
        except ImportError:
            pass
        
        try:
            yield
        except Exception as e:
            error = str(e)
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            memory_after = None
            if memory_before is not None:
                try:
                    memory_after = MemoryMonitor.get_memory_usage()['rss_mb']
                except:
                    pass
            
            metrics = PerformanceMetrics(
                operation=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                memory_before=memory_before,
                memory_after=memory_after,
                input_size=input_size,
                error=error,
                metadata=metadata
            )
            
            self.metrics.append(metrics)
    
    def save_metrics(self, filename: Optional[str] = None) -> Path:
        """
        保存性能指标到文件
        
        Args:
            filename: 文件名，默认使用时间戳
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # 将dataclass转换为dict
        metrics_data = [asdict(metric) for metric in self.metrics]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取性能摘要
        
        Returns:
            性能摘要统计
        """
        if not self.metrics:
            return {"total_operations": 0}
        
        operations = {}
        total_duration = 0
        total_errors = 0
        
        for metric in self.metrics:
            op_name = metric.operation
            if op_name not in operations:
                operations[op_name] = {
                    "count": 0,
                    "total_duration": 0,
                    "max_duration": 0,
                    "min_duration": float('inf'),
                    "errors": 0
                }
            
            op_stats = operations[op_name]
            op_stats["count"] += 1
            op_stats["total_duration"] += metric.duration
            op_stats["max_duration"] = max(op_stats["max_duration"], metric.duration)
            op_stats["min_duration"] = min(op_stats["min_duration"], metric.duration)
            
            total_duration += metric.duration
            
            if metric.error:
                op_stats["errors"] += 1
                total_errors += 1
        
        # 计算平均值
        for op_stats in operations.values():
            op_stats["avg_duration"] = op_stats["total_duration"] / op_stats["count"]
            if op_stats["min_duration"] == float('inf'):
                op_stats["min_duration"] = 0
        
        return {
            "total_operations": len(self.metrics),
            "total_duration": total_duration,
            "total_errors": total_errors,
            "operations": operations,
            "avg_duration_per_operation": total_duration / len(self.metrics) if self.metrics else 0
        }
    
    def clear_metrics(self):
        """清空指标"""
        self.metrics.clear()


# 全局性能跟踪器实例
performance_tracker = PerformanceTracker()


def track_performance(operation_name: str, input_size: Optional[int] = None):
    """性能跟踪装饰器"""
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with performance_tracker.track_operation(operation_name, input_size):
                return func(*args, **kwargs)
        return wrapper
    return decorator
