#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化后的PairAnalyzer示例
展示如何应用新的工具类来改进现有代码
"""

import os
import logging
from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor

from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from common.utils.api_client_factory import APIClientFactory
from common.utils.thread_pool_manager import ThreadPoolManager, OptimalThreadConfig
from common.utils.llm_cache_manager import LLMCacheManager
from common.utils.error_handler import handle_exceptions, CausalLinkingException, ErrorReporter
from common.utils.performance_tracker import track_performance, performance_tracker


class OptimizedPairAnalyzer:
    """优化后的事件对因果关系分析器"""
    
    def __init__(
        self,
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: Optional[int] = None,
        provider: str = "openai",
        enable_cache: bool = True
    ):
        """
        初始化优化后的事件对分析器
        
        Args:
            model: LLM模型
            prompt_path: 提示模板路径
            api_key: API密钥
            base_url: 自定义API基础URL
            max_workers: 最大工作线程数（None则自动优化）
            provider: API提供商
            enable_cache: 是否启用缓存
        """
        self.model = model
        self.provider = provider
        self.prompt_path = prompt_path
        
        # 使用优化的线程数配置
        self.max_workers = max_workers or OptimalThreadConfig.CAUSAL_ANALYSIS
        
        # 使用API客户端工厂
        self.llm_client = APIClientFactory.create_llm_client(
            model=model,
            provider=provider,
            api_key=api_key,
            base_url=base_url
        )
        
        # 初始化缓存管理器
        self.cache_manager = LLMCacheManager() if enable_cache else None
        
        # 初始化错误报告器
        self.error_reporter = ErrorReporter(logger_name=__name__)
        
        # 加载提示模板
        self.prompt_template = self._load_prompt_template(prompt_path)
    
    @handle_exceptions(default_return=None, exception_types=(Exception,))
    def _load_prompt_template(self, prompt_path: str) -> Dict[str, str]:
        """加载提示模板"""
        if not prompt_path:
            from common.utils.path_utils import get_config_path
            prompt_path = get_config_path("prompt_causal_linking.json")
        
        from common.utils.json_loader import JsonLoader
        return JsonLoader.load_json(prompt_path)
    
    @track_performance("batch_causal_analysis")
    def analyze_batch(self, event_pairs: List[Tuple[EventItem, EventItem]]) -> List[CausalEdge]:
        """
        批量分析事件对的因果关系
        
        Args:
            event_pairs: 事件对列表
            
        Returns:
            因果边列表
        """
        if not event_pairs:
            return []
        
        edges = []
        cache_hits = 0
        
        # 使用优化的线程池
        with ThreadPoolManager.create_thread_pool("io_intensive", self.max_workers) as executor:
            # 提交所有任务
            future_to_pair = {}
            
            for event1, event2 in event_pairs:
                # 检查缓存
                if self.cache_manager:
                    cached_result = self.cache_manager.get_cached_result(
                        event1.event_id, event2.event_id, self.model
                    )
                    if cached_result:
                        edge = self._parse_cached_result(cached_result, event1.event_id, event2.event_id)
                        if edge:
                            edges.append(edge)
                        cache_hits += 1
                        continue
                
                # 提交到线程池
                future = executor.submit(self._analyze_pair_with_error_handling, event1, event2)
                future_to_pair[future] = (event1, event2)
            
            # 收集结果
            import concurrent.futures
            for future in concurrent.futures.as_completed(future_to_pair):
                edge = future.result()
                if edge:
                    edges.append(edge)
        
        # 记录缓存命中率
        if self.cache_manager and event_pairs:
            cache_hit_rate = cache_hits / len(event_pairs) * 100
            print(f"Cache hit rate: {cache_hit_rate:.1f}% ({cache_hits}/{len(event_pairs)})")
        
        return edges
    
    @handle_exceptions(
        default_return=None, 
        exception_types=(CausalLinkingException, Exception),
        log_level=logging.WARNING
    )
    def _analyze_pair_with_error_handling(
        self, 
        event1: EventItem, 
        event2: EventItem
    ) -> Optional[CausalEdge]:
        """带错误处理的事件对分析"""
        try:
            with performance_tracker.track_operation(
                "single_pair_analysis",
                metadata={"event1_id": event1.event_id, "event2_id": event2.event_id}
            ):
                return self._analyze_pair(event1, event2)
        except Exception as e:
            self.error_reporter.report_processing_error(
                "causal_pair_analysis", 
                f"{event1.event_id}-{event2.event_id}", 
                e
            )
            raise CausalLinkingException(
                f"Failed to analyze pair {event1.event_id}-{event2.event_id}",
                error_code="PAIR_ANALYSIS_FAILED",
                details={"event1_id": event1.event_id, "event2_id": event2.event_id}
            )
    
    def _analyze_pair(self, event1: EventItem, event2: EventItem) -> Optional[CausalEdge]:
        """分析单个事件对"""
        # 格式化提示
        prompt = self.format_prompt(event1, event2)
        
        # 调用LLM
        response = self.llm_client.call_with_json_response(
            prompt['system'], 
            prompt['instruction']
        )
        
        if not response["success"] or "json_content" not in response:
            self.error_reporter.report_api_error(
                "llm_causal_analysis",
                Exception(response.get('error', 'Unknown LLM error')),
                {"event1_id": event1.event_id, "event2_id": event2.event_id}
            )
            return None
        
        # 缓存结果
        if self.cache_manager:
            self.cache_manager.cache_result(
                event1.event_id, 
                event2.event_id, 
                self.model, 
                response["json_content"]
            )
        
        # 解析响应
        return self.parse_response(response["json_content"], event1.event_id, event2.event_id)
    
    def _parse_cached_result(
        self, 
        cached_result: Dict[str, Any], 
        event1_id: str, 
        event2_id: str
    ) -> Optional[CausalEdge]:
        """解析缓存的结果"""
        return self.parse_response(cached_result, event1_id, event2_id)
    
    def format_prompt(self, event1: EventItem, event2: EventItem) -> Dict[str, str]:
        """格式化提示"""
        # 这里保持原有的提示格式化逻辑
        # 暂时返回空字典作为占位符
        return {"system": "", "instruction": ""}
    
    def parse_response(
        self, 
        response: Dict[str, Any], 
        event1_id: str, 
        event2_id: str
    ) -> Optional[CausalEdge]:
        """解析LLM响应"""
        # 这里保持原有的响应解析逻辑
        # 暂时返回None作为占位符
        return None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        stats = performance_tracker.get_summary()
        
        if self.cache_manager:
            cache_stats = self.cache_manager.get_cache_stats()
            stats['cache'] = cache_stats
        
        return stats
