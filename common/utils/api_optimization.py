#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连接池和批处理优化
提供高效的API调用管理，包括连接池复用、批量请求、智能重试
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIConnectionPool:
    """API连接池管理器"""
    
    def __init__(self, base_url: str = "", pool_connections: int = 10, pool_maxsize: int = 20):
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # 配置连接池
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        if base_url:
            self.base_url = base_url.rstrip('/')
        else:
            self.base_url = ""
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """发送POST请求"""
        full_url = f"{self.base_url}/{url.lstrip('/')}" if self.base_url else url
        return self.session.post(full_url, **kwargs)
    
    def close(self):
        """关闭连接池"""
        self.session.close()


class BatchAPIProcessor:
    """批量API处理器"""
    
    def __init__(self, connection_pool: APIConnectionPool, batch_size: int = 10):
        self.connection_pool = connection_pool
        self.batch_size = batch_size
    
    def process_batch(
        self, 
        requests_data: List[Dict[str, Any]],
        endpoint: str,
        processor_func: Callable[[Dict], Any]
    ) -> List[Any]:
        """
        批量处理API请求
        
        Args:
            requests_data: 请求数据列表
            endpoint: API端点
            processor_func: 结果处理函数
            
        Returns:
            处理结果列表
        """
        results = []
        
        # 分批处理
        for i in range(0, len(requests_data), self.batch_size):
            batch = requests_data[i:i + self.batch_size]
            batch_results = self._process_single_batch(batch, endpoint, processor_func)
            results.extend(batch_results)
            
            # 添加延迟避免API限流
            if i + self.batch_size < len(requests_data):
                time.sleep(0.1)
        
        return results
    
    def _process_single_batch(
        self, 
        batch: List[Dict[str, Any]], 
        endpoint: str,
        processor_func: Callable[[Dict], Any]
    ) -> List[Any]:
        """处理单个批次"""
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(batch), 5)) as executor:
            futures = []
            
            for request_data in batch:
                future = executor.submit(self._single_request, endpoint, request_data, processor_func)
                futures.append(future)
            
            for future in futures:
                try:
                    result = future.result(timeout=30)
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    print(f"Batch request failed: {e}")
        
        return results
    
    def _single_request(self, endpoint: str, data: Dict[str, Any], processor_func: Callable) -> Any:
        """单个请求处理"""
        try:
            response = self.connection_pool.post(endpoint, json=data)
            response.raise_for_status()
            return processor_func(response.json())
        except Exception as e:
            print(f"Single request failed: {e}")
            return None


class CircuitBreaker:
    """熔断器模式实现"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """执行函数调用with熔断保护"""
        if self.state == "OPEN":
            if self.last_failure_time and time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """成功时的处理"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


# 全局连接池实例
_connection_pools = {}

def get_connection_pool(provider: str = "default", base_url: str = "") -> APIConnectionPool:
    """获取或创建连接池"""
    if provider not in _connection_pools:
        _connection_pools[provider] = APIConnectionPool(base_url)
    return _connection_pools[provider]


def cleanup_connection_pools():
    """清理所有连接池"""
    for pool in _connection_pools.values():
        pool.close()
    _connection_pools.clear()
