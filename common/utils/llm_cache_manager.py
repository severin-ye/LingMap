#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM响应缓存管理器
缓存LLM API调用结果，避免重复计算相同的事件对
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta


class LLMCacheManager:
    """LLM响应缓存管理器"""
    
    def __init__(self, cache_dir: str = "cache", cache_ttl_hours: int = 24):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            cache_ttl_hours: 缓存生存时间（小时）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
    
    def _generate_cache_key(self, event1_id: str, event2_id: str, model: str) -> str:
        """
        生成缓存键
        
        Args:
            event1_id: 第一个事件ID
            event2_id: 第二个事件ID  
            model: 模型名称
            
        Returns:
            缓存键的哈希值
        """
        # 确保事件对的顺序一致
        sorted_events = tuple(sorted([event1_id, event2_id]))
        cache_input = f"{sorted_events[0]}_{sorted_events[1]}_{model}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def get_cached_result(
        self, 
        event1_id: str, 
        event2_id: str, 
        model: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取缓存的结果
        
        Args:
            event1_id: 第一个事件ID
            event2_id: 第二个事件ID
            model: 模型名称
            
        Returns:
            缓存的结果，如果不存在或过期则返回None
        """
        cache_key = self._generate_cache_key(event1_id, event2_id, model)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查缓存是否过期
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.cache_ttl:
                # 删除过期缓存
                cache_file.unlink()
                return None
            
            return cache_data['result']
            
        except (json.JSONDecodeError, KeyError, ValueError):
            # 缓存文件损坏，删除它
            cache_file.unlink()
            return None
    
    def cache_result(
        self, 
        event1_id: str, 
        event2_id: str, 
        model: str, 
        result: Dict[str, Any]
    ) -> None:
        """
        缓存结果
        
        Args:
            event1_id: 第一个事件ID
            event2_id: 第二个事件ID
            model: 模型名称
            result: 要缓存的结果
        """
        cache_key = self._generate_cache_key(event1_id, event2_id, model)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'event1_id': event1_id,
            'event2_id': event2_id,
            'model': model,
            'result': result
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to cache result: {e}")
    
    def clear_cache(self) -> int:
        """
        清空所有缓存
        
        Returns:
            删除的缓存文件数量
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except Exception:
                pass
        return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_files': len(cache_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }
