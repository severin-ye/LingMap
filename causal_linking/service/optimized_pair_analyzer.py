#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版事件对因果关系分析器
集成了缓存、批处理和性能监控等优化功能
"""

import os
import time
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from event_extraction.repository.llm_client import LLMClient

# 导入优化工具
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from common.utils.practical_optimizer import SimpleCache, OptimizedBatchProcessor
from common.utils.performance_tracker import PerformanceTracker
from common.utils.unified_config_manager_fixed import get_project_config

class OptimizedPairAnalyzer:
    """
    优化版事件对因果关系分析器
    集成了缓存、批处理和性能监控功能
    """
    
    def __init__(
        self,
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: int = 3,
        provider: str = "openai",
        enable_cache: bool = True,
        enable_performance_tracking: bool = True
    ):
        """
        初始化优化版事件对分析器
        """
        # 获取项目配置
        self.config = get_project_config()
        
        # API配置
        if not api_key:
            if provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
            elif provider == "deepseek":
                self.api_key = os.environ.get("DEEPSEEK_API_KEY")
            else:
                self.api_key = os.environ.get("LLM_API_KEY")
        else:
            self.api_key = api_key
        
        self.model = model
        self.base_url = base_url
        self.provider = provider
        self.max_workers = max_workers or self.config.max_workers
        
        # 初始化LLM客户端
        self.llm_client = LLMClient(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            provider=self.provider
        )
        
        # 加载提示模板
        self.prompt_template = self._load_prompt_template(prompt_path)
        
        # 优化组件
        self.enable_cache = enable_cache
        self.cache = SimpleCache(max_size=self.config.cache_size) if enable_cache else None
        self.batch_processor = OptimizedBatchProcessor(batch_size=self.config.batch_size)
        
        # 性能监控
        self.enable_performance_tracking = enable_performance_tracking
        self.performance_tracker = PerformanceTracker() if enable_performance_tracking else None
        
        # 统计信息
        self.stats = {
            "total_pairs_analyzed": 0,
            "cache_hits": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "total_time": 0.0
        }
        
        print(f"优化版PairAnalyzer初始化完成 - 缓存: {enable_cache}, 监控: {enable_performance_tracking}")
    
    def _load_prompt_template(self, prompt_path: str) -> Dict[str, str]:
        """加载提示模板"""
        if prompt_path and os.path.exists(prompt_path):
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载提示模板失败: {e}")
        
        # 返回默认模板
        return {
            "system": "你是一个因果关系分析助手，你需要分析两个事件之间是否存在因果关系。",
            "instruction": "请分析以下两个事件之间是否存在因果关系:\n\n事件1: {event1}\n\n事件2: {event2}\n\n请以JSON格式回答，包含以下字段:\n- has_causal_relation: 布尔值，表示是否存在因果关系\n- direction: 如果存在因果关系，请指明方向(事件1→事件2 或 事件2→事件1)\n- strength: 因果关系强度(高/中/低)\n- reason: 关系存在的理由或不存在的解释"
        }
    
    def _generate_cache_key(self, event1: EventItem, event2: EventItem) -> str:
        """生成缓存键"""
        # 使用事件内容的哈希值作为缓存键
        content1 = f"{event1.event_id}:{event1.description}"
        content2 = f"{event2.event_id}:{event2.description}"
        combined = f"{content1}|{content2}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def analyze_batch_optimized(self, event_pairs: List[Tuple[EventItem, EventItem]]) -> List[CausalEdge]:
        """
        优化版批量分析事件对因果关系
        集成了缓存、性能监控和错误处理
        """
        start_time = time.time()
        
        with self.performance_tracker.track_operation(
            "optimized_batch_analysis",
            input_size=len(event_pairs)
        ) if self.performance_tracker else self._dummy_context():
            
            edges = []
            cache_hits = 0
            
            # 检查缓存
            pairs_to_analyze = []
            cached_results = []
            
            for event1, event2 in event_pairs:
                if self.cache:
                    cache_key = self._generate_cache_key(event1, event2)
                    cached_edge = self.cache.get(cache_key)
                    if cached_edge:
                        cached_results.append(cached_edge)
                        cache_hits += 1
                        continue
                
                pairs_to_analyze.append((event1, event2))
            
            # 分析未缓存的事件对
            if pairs_to_analyze:
                new_edges = self._analyze_pairs_parallel(pairs_to_analyze)
                edges.extend(new_edges)
                
                # 缓存新结果
                if self.cache:
                    for i, (event1, event2) in enumerate(pairs_to_analyze):
                        if i < len(new_edges) and new_edges[i]:
                            cache_key = self._generate_cache_key(event1, event2)
                            self.cache.set(cache_key, new_edges[i])
            
            # 添加缓存结果
            edges.extend(cached_results)
            
            # 更新统计
            self.stats["total_pairs_analyzed"] += len(event_pairs)
            self.stats["cache_hits"] += cache_hits
            self.stats["successful_analyses"] += len(edges)
            self.stats["failed_analyses"] += len(event_pairs) - len(edges)
            self.stats["total_time"] += time.time() - start_time
            
            print(f"批量分析完成: {len(event_pairs)}对 -> {len(edges)}条边, 缓存命中: {cache_hits}")
            
            return edges
    
    def _analyze_pairs_parallel(self, event_pairs: List[Tuple[EventItem, EventItem]]) -> List[CausalEdge]:
        """并行分析事件对"""
        edges = []
        
        # 使用优化的批处理
        def analyze_single_pair(pair_data):
            event1, event2 = pair_data
            return self.analyze_pair_core(event1, event2)
        
        results = self.batch_processor.process_batch(
            event_pairs,
            analyze_single_pair,
            use_cache=False  # 这里不使用batch_processor的缓存，因为我们有专门的缓存
        )
        
        # 过滤掉None结果
        edges = [edge for edge in results if edge is not None]
        
        return edges
    
    def analyze_pair_core(self, event1: EventItem, event2: EventItem) -> Optional[CausalEdge]:
        """
        核心的单对事件分析逻辑
        """
        try:
            # 格式化提示
            prompt = self.format_prompt(event1, event2)
            
            # 调用LLM
            response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
            
            if not response["success"] or "json_content" not in response:
                print(f"事件 {event1.event_id} 和 {event2.event_id} 的因果分析失败: {response.get('error', '未知错误')}")
                return None
                
            # 解析响应
            edge = self.parse_response(response["json_content"], event1.event_id, event2.event_id)
            return edge
            
        except Exception as e:
            print(f"分析事件对时出错: {e}")
            return None
    
    def format_prompt(self, event1: EventItem, event2: EventItem) -> Dict[str, str]:
        """格式化提示"""
        instruction = self.prompt_template["instruction"].format(
            event1=f"ID: {event1.event_id}, 内容: {event1.description}",
            event2=f"ID: {event2.event_id}, 内容: {event2.description}"
        )
        
        return {
            "system": self.prompt_template["system"],
            "instruction": instruction
        }
    
    def parse_response(self, json_content: Dict[str, Any], event1_id: str, event2_id: str) -> Optional[CausalEdge]:
        """解析LLM响应"""
        try:
            has_relation = json_content.get("has_causal_relation", False)
            if not has_relation:
                return None
            
            # 确定源事件和目标事件
            direction = json_content.get("direction", "")
            if "事件1→事件2" in direction or "event1" in direction.lower():
                source_id, target_id = event1_id, event2_id
            elif "事件2→事件1" in direction or "event2" in direction.lower():
                source_id, target_id = event2_id, event1_id
            else:
                source_id, target_id = event1_id, event2_id  # 默认方向
            
            # 创建因果边
            edge = CausalEdge(
                from_id=source_id,
                to_id=target_id,
                strength=json_content.get("strength", "中"),
                reason=json_content.get("reason", "")
            )
            
            return edge
            
        except Exception as e:
            print(f"解析响应时出错: {e}")
            return None
    
    def _map_strength_to_confidence(self, strength: str) -> float:
        """将强度映射为置信度"""
        mapping = {"高": 0.9, "中": 0.7, "低": 0.5}
        return mapping.get(strength, 0.7)
    
    def _dummy_context(self):
        """当性能跟踪器不可用时的虚拟上下文管理器"""
        from contextlib import nullcontext
        return nullcontext()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        cache_hit_rate = 0
        if self.stats["total_pairs_analyzed"] > 0:
            cache_hit_rate = (self.stats["cache_hits"] / self.stats["total_pairs_analyzed"]) * 100
        
        return {
            **self.stats,
            "cache_hit_rate_percent": cache_hit_rate,
            "average_time_per_pair": self.stats["total_time"] / max(1, self.stats["total_pairs_analyzed"]),
            "success_rate_percent": (self.stats["successful_analyses"] / max(1, self.stats["total_pairs_analyzed"])) * 100,
            "cache_size": len(self.cache.cache) if self.cache else 0
        }
    
    def save_performance_report(self, filepath: Optional[str] = None) -> str:
        """保存性能报告"""
        if not filepath:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filepath = f"pair_analyzer_performance_{timestamp}.json"
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": {
                "model": self.model,
                "provider": self.provider,
                "max_workers": self.max_workers,
                "enable_cache": self.enable_cache,
                "cache_size": self.config.cache_size,
                "batch_size": self.config.batch_size
            },
            "performance_stats": self.get_performance_stats(),
            "performance_metrics": [asdict(m) for m in self.performance_tracker.metrics] if self.performance_tracker else []
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"性能报告已保存到: {filepath}")
        return filepath
    
    def clear_cache(self):
        """清空缓存"""
        if self.cache:
            self.cache.clear()
            print("缓存已清空")

    # 兼容性方法 - 保持与原始接口的兼容性
    def analyze_batch(self, event_pairs: List[Tuple[EventItem, EventItem]]) -> List[CausalEdge]:
        """兼容性方法 - 调用优化版本"""
        return self.analyze_batch_optimized(event_pairs)
    
    def analyze_pair(self, event1: EventItem, event2: EventItem) -> Optional[CausalEdge]:
        """兼容性方法 - 单个事件对分析"""
        return self.analyze_pair_core(event1, event2)

if __name__ == "__main__":
    # 测试代码
    from common.models.event import EventItem
    
    # 创建测试事件
    event1 = EventItem(
        event_id="test1",
        description="张三修炼了新的功法",
        chapter_id="ch1"
    )
    
    event2 = EventItem(
        event_id="test2", 
        description="张三的实力大幅提升",
        chapter_id="ch1"
    )
    
    # 测试优化版分析器
    analyzer = OptimizedPairAnalyzer(enable_cache=True, enable_performance_tracking=True)
    
    # 测试单对分析
    edge = analyzer.analyze_pair_core(event1, event2)
    if edge:
        print(f"发现因果关系: {edge.from_id} -> {edge.to_id}")
    
    # 测试批量分析
    pairs = [(event1, event2)] * 3  # 重复测试缓存效果
    edges = analyzer.analyze_batch_optimized(pairs)
    
    print(f"批量分析结果: {len(edges)} 条边")
    print("性能统计:", analyzer.get_performance_stats())
    
    # 保存性能报告
    analyzer.save_performance_report()
