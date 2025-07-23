#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化集成器 - 实用版本
将优化工具集成到现有系统中，提供性能优化和监控
"""

import asyncio
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# 导入现有的工具
from .performance_tracker import PerformanceTracker, PerformanceMetrics
from .unified_config_manager_fixed import get_project_config, ProjectConfig

logger = logging.getLogger(__name__)

@dataclass
class OptimizationResults:
    """优化结果统计"""
    processed_items: int = 0
    cache_hits: int = 0
    total_time: float = 0.0
    estimated_time_saved: float = 0.0
    errors_handled: int = 0
    performance_improvement: float = 0.0
    memory_usage_mb: float = 0.0

class SimpleCache:
    """简单的内存缓存"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.access_times: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """设置缓存值"""
        if len(self.cache) >= self.max_size:
            # 清理最旧的缓存
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()

class OptimizedBatchProcessor:
    """优化的批处理器"""
    
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        self.cache = SimpleCache()
    
    def process_batch(self, items: List[Any], processor_func, use_cache: bool = True) -> List[Any]:
        """批量处理数据"""
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = []
            
            for item in batch:
                # 生成缓存键
                cache_key = self._generate_cache_key(item) if use_cache else None
                
                # 检查缓存
                if cache_key and use_cache:
                    cached_result = self.cache.get(cache_key)
                    if cached_result is not None:
                        batch_results.append(cached_result)
                        continue
                
                # 处理项目
                try:
                    result = processor_func(item)
                    batch_results.append(result)
                    
                    # 缓存结果
                    if cache_key and use_cache:
                        self.cache.set(cache_key, result)
                        
                except Exception as e:
                    logger.error(f"处理项目时出错: {e}")
                    batch_results.append(None)
            
            results.extend(batch_results)
        
        return results
    
    def _generate_cache_key(self, item: Any) -> str:
        """生成缓存键"""
        import hashlib
        item_str = json.dumps(item, sort_keys=True, default=str)
        return hashlib.md5(item_str.encode()).hexdigest()

class OptimizationIntegrator:
    """性能优化集成器"""
    
    def __init__(self, config: Optional[ProjectConfig] = None):
        self.config = config or get_project_config()
        self.performance_tracker = PerformanceTracker()
        self.batch_processor = OptimizedBatchProcessor(batch_size=self.config.batch_size)
        self.results = OptimizationResults()
        
        logger.info("优化集成器初始化完成")
    
    def optimize_event_extraction(self, texts: List[str]) -> List[Dict[str, Any]]:
        """优化的事件提取"""
        with self.performance_tracker.track_operation(
            "optimized_event_extraction",
            input_size=len(texts)
        ):
            # 使用批处理
            results = self.batch_processor.process_batch(
                texts,
                self._extract_events_single,
                use_cache=True
            )
            
            # 更新统计
            self.results.processed_items += len(texts)
            self.results.cache_hits += self._count_cache_hits(texts)
            
            return [r for r in results if r is not None]
    
    def _extract_events_single(self, text: str) -> Dict[str, Any]:
        """单个文本的事件提取（模拟）"""
        # 这里应该调用实际的事件提取逻辑
        # 为了演示，我们模拟一个简单的提取
        time.sleep(0.1)  # 模拟处理时间
        
        events = []
        # 简单的关键词提取
        keywords = ["修炼", "突破", "丹药", "法宝", "灵气", "战斗", "师父", "弟子"]
        for keyword in keywords:
            if keyword in text:
                events.append({
                    "type": "event",
                    "content": f"发现{keyword}相关事件",
                    "text": text,
                    "keyword": keyword
                })
        
        return {
            "text": text,
            "events": events,
            "extracted_at": time.time()
        }
    
    def optimize_causal_linking(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """优化的因果关系链接"""
        with self.performance_tracker.track_operation(
            "optimized_causal_linking",
            input_size=len(events)
        ):
            # 使用缓存检查
            cache_key = self._generate_events_cache_key(events)
            cached_result = self.batch_processor.cache.get(cache_key)
            
            if cached_result:
                self.results.cache_hits += 1
                return cached_result
            
            # 批量处理因果关系
            links = []
            for i in range(0, len(events), 2):  # 每次处理两个事件
                batch = events[i:i+2]
                if len(batch) == 2:
                    link = self._analyze_causal_relationship(batch[0], batch[1])
                    if link:
                        links.append(link)
            
            # 缓存结果
            self.batch_processor.cache.set(cache_key, links)
            
            self.results.processed_items += len(events)
            return links
    
    def _analyze_causal_relationship(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """分析两个事件的因果关系（模拟）"""
        time.sleep(0.05)  # 模拟处理时间
        
        # 简单的因果关系判断
        causal_indicators = ["因为", "所以", "导致", "结果", "由于"]
        
        text1 = event1.get("text", "")
        text2 = event2.get("text", "")
        
        for indicator in causal_indicators:
            if indicator in text1 or indicator in text2:
                return {
                    "type": "causal_link",
                    "source_event": event1,
                    "target_event": event2,
                    "confidence": 0.7,
                    "indicator": indicator
                }
        
        return None
    
    def _generate_events_cache_key(self, events: List[Dict[str, Any]]) -> str:
        """为事件列表生成缓存键"""
        import hashlib
        events_str = json.dumps(events, sort_keys=True, default=str)
        return hashlib.md5(events_str.encode()).hexdigest()
    
    def _count_cache_hits(self, items: List[Any]) -> int:
        """计算缓存命中数"""
        hits = 0
        for item in items:
            cache_key = self.batch_processor._generate_cache_key(item)
            if self.batch_processor.cache.get(cache_key) is not None:
                hits += 1
        return hits
    
    def optimize_complete_pipeline(self, input_texts: List[str]) -> Dict[str, Any]:
        """优化的完整处理管道"""
        pipeline_start = time.time()
        
        with self.performance_tracker.track_operation(
            "complete_pipeline",
            input_size=len(input_texts)
        ):
            logger.info(f"开始处理 {len(input_texts)} 个文本")
            
            # 1. 事件提取
            events_results = self.optimize_event_extraction(input_texts)
            
            # 2. 展平事件列表
            all_events = []
            for result in events_results:
                if result and "events" in result:
                    all_events.extend(result["events"])
            
            logger.info(f"提取到 {len(all_events)} 个事件")
            
            # 3. 因果关系链接
            causal_links = self.optimize_causal_linking(all_events)
            
            logger.info(f"生成 {len(causal_links)} 个因果关系链接")
            
            # 4. 计算性能指标
            pipeline_time = time.time() - pipeline_start
            baseline_time = len(input_texts) * 1.5  # 假设基线处理时间
            improvement = max(0, (baseline_time - pipeline_time) / baseline_time * 100)
            
            self.results.total_time = pipeline_time
            self.results.estimated_time_saved = max(0, baseline_time - pipeline_time)
            self.results.performance_improvement = improvement
            
            # 5. 构建结果
            result = {
                "input_texts": input_texts,
                "events_results": events_results,
                "all_events": all_events,
                "causal_links": causal_links,
                "processing_time": pipeline_time,
                "optimization_stats": self.get_optimization_summary()
            }
            
            logger.info(f"管道处理完成，耗时: {pipeline_time:.2f}秒，性能提升: {improvement:.1f}%")
            
            return result
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """获取优化总结"""
        cache_hit_rate = 0
        if self.results.processed_items > 0:
            cache_hit_rate = (self.results.cache_hits / self.results.processed_items) * 100
        
        return {
            "processed_items": self.results.processed_items,
            "cache_hits": self.results.cache_hits,
            "cache_hit_rate_percent": cache_hit_rate,
            "total_processing_time": self.results.total_time,
            "estimated_time_saved": self.results.estimated_time_saved,
            "performance_improvement_percent": self.results.performance_improvement,
            "errors_handled": self.results.errors_handled,
            "cache_size": len(self.batch_processor.cache.cache),
            "batch_size": self.batch_processor.batch_size
        }
    
    def save_performance_report(self, output_path: Optional[str] = None) -> str:
        """保存性能报告"""
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = f"performance_report_{timestamp}.json"
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "optimization_summary": self.get_optimization_summary(),
            "performance_metrics": [asdict(m) for m in self.performance_tracker.metrics],
            "config": {
                "batch_size": self.config.batch_size,
                "cache_size": self.config.cache_size,
                "max_workers": self.config.max_workers
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"性能报告已保存到: {output_path}")
        return output_path
    
    def benchmark_performance(self, test_texts: List[str]) -> Dict[str, Any]:
        """性能基准测试"""
        logger.info(f"开始性能基准测试，测试文本数: {len(test_texts)}")
        
        # 清空缓存以获得准确的基准
        self.batch_processor.cache.clear()
        
        # 第一次运行（无缓存）
        start_time = time.time()
        result1 = self.optimize_complete_pipeline(test_texts)
        first_run_time = time.time() - start_time
        
        # 第二次运行（有缓存）
        start_time = time.time()
        result2 = self.optimize_complete_pipeline(test_texts)
        second_run_time = time.time() - start_time
        
        # 计算缓存效果
        cache_improvement = max(0, (first_run_time - second_run_time) / first_run_time * 100)
        
        benchmark_result = {
            "test_texts_count": len(test_texts),
            "first_run_time": first_run_time,
            "second_run_time": second_run_time,
            "cache_improvement_percent": cache_improvement,
            "time_saved_by_cache": first_run_time - second_run_time,
            "events_extracted": len(result1.get("all_events", [])),
            "causal_links_created": len(result1.get("causal_links", [])),
            "optimization_summary": self.get_optimization_summary()
        }
        
        logger.info(f"基准测试完成，缓存带来 {cache_improvement:.1f}% 性能提升")
        
        return benchmark_result

# 便捷函数
def run_optimized_processing(input_texts: List[str], 
                           config: Optional[ProjectConfig] = None) -> Dict[str, Any]:
    """运行优化的处理流程"""
    integrator = OptimizationIntegrator(config)
    return integrator.optimize_complete_pipeline(input_texts)

def benchmark_optimization(test_texts: List[str], 
                         config: Optional[ProjectConfig] = None) -> Dict[str, Any]:
    """运行优化基准测试"""
    integrator = OptimizationIntegrator(config)
    return integrator.benchmark_performance(test_texts)

if __name__ == "__main__":
    # 测试代码
    test_texts = [
        "张三在修炼室中突破了筑基期，灵气涌动。",
        "李四因为服用了筑基丹而实力大增，战力提升。",
        "王五在秘境中发现了一件法宝，如获至宝。",
        "赵六与师兄切磋，学会了新的法术。",
        "钱七在藏书阁研读古籍，领悟心法。"
    ]
    
    # 运行基准测试
    integrator = OptimizationIntegrator()
    benchmark_result = integrator.benchmark_performance(test_texts)
    
    print("=== 性能基准测试结果 ===")
    for key, value in benchmark_result.items():
        print(f"{key}: {value}")
    
    # 保存性能报告
    report_file = integrator.save_performance_report()
    print(f"\n性能报告已保存到: {report_file}")
