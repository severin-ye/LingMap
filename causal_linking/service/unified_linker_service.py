#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一因果链接器实现
融合基础版和优化版因果链接器功能：
1. 使用CandidateGenerator生成候选事件对
2. 使用PairAnalyzer分析事件对因果关系
3. 实现BaseLinker接口提供链接器功能
4. 构建有向无环图（DAG）

降低整体时间复杂度，从O(N²)降低到O(N·avg_m²) + O(E × k²)
"""

import os
import sys
import time
import itertools
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Tuple, Set

# 添加项目根目录到Python路径
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)

from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from causal_linking.service.base_causal_linker import BaseLinker
from causal_linking.service.candidate_generator import CandidateGenerator
from causal_linking.service.pair_analyzer import PairAnalyzer
from causal_linking.service.graph_filter import GraphFilter
from event_extraction.repository.llm_client import LLMClient


class UnifiedCausalLinker(BaseLinker):
    """
    统一版因果链接器，结合原始版和优化版的功能
    支持完整的旧版功能，同时提供优化策略选项
    """
    
    def __init__(
        self,
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: int = 3,
        strength_mapping: Dict[str, int] = {},
        provider: str = "openai",
        # 优化参数，默认启用优化
        use_optimization: bool = True,
        max_events_per_chapter: int = 20,
        min_entity_support: int = 2,
        max_chapter_span: int = 10,
        max_candidate_pairs: int = 10000,
        use_entity_weights: bool = True
    ):
        """
        初始化统一因果链接器
        
        Args:
            model: 使用的LLM模型
            prompt_path: 提示词模板路径
            api_key: API密钥
            base_url: 自定义API基础URL
            max_workers: 并行处理的最大工作线程数
            strength_mapping: 因果强度映射，用于权重比较
            provider: API提供商，如"openai"或"deepseek"
            use_optimization: 是否使用优化策略，禁用则回退到原始全配对方法
            max_events_per_chapter: 每章节最多处理的事件数
            min_entity_support: 实体最小支持度，低于此值不考虑实体配对
            max_chapter_span: 跨章节配对的最大章节跨度
            max_candidate_pairs: 最大候选事件对数量
            use_entity_weights: 是否使用实体频率反向权重（频率越高权重越低）
        """
        if not prompt_path:
            # 导入path_utils获取配置文件路径
            from common.utils.path_utils import get_config_path
            prompt_path = get_config_path("prompt_causal_linking.json")
            
        super().__init__(prompt_path)
        
        # 如果未提供API密钥，尝试从环境变量获取
        if not api_key:
            if provider == "openai":
                api_key_env = os.environ.get("OPENAI_API_KEY")
                if not api_key_env:
                    raise ValueError("请提供 OpenAI API 密钥")
                api_key = api_key_env
            elif provider == "deepseek":
                api_key_env = os.environ.get("DEEPSEEK_API_KEY")
                if not api_key_env:
                    raise ValueError("请提供 DeepSeek API 密钥")
                api_key = api_key_env
            else:
                raise ValueError(f"不支持的 API 提供商: {provider}")
        
        self.model = model
        self.max_workers = max_workers
        self.provider = provider
        self.use_optimization = use_optimization
        
        # 设置强度映射
        self.strength_mapping = strength_mapping or {
            "高": 3,
            "中": 2,
            "低": 1
        }
        
        # 初始化候选生成器
        self.candidate_generator = CandidateGenerator(
            max_events_per_chapter=max_events_per_chapter,
            min_entity_support=min_entity_support,
            max_chapter_span=max_chapter_span,
            max_candidate_pairs=max_candidate_pairs,
            use_entity_weights=use_entity_weights
        )
        
        # 初始化对分析器
        self.pair_analyzer = PairAnalyzer(
            model=model,
            prompt_path=prompt_path,
            api_key=api_key,
            base_url=base_url,
            max_workers=max_workers,
            provider=provider
        )
        
        # 初始化图过滤器
        self.graph_filter = GraphFilter(strength_mapping=self.strength_mapping)
        
        # 初始化LLM客户端 (仍然需要保留，用于analyze_causal_relation方法)
        self.llm_client = LLMClient(
            api_key=api_key,
            model=self.model,
            base_url=base_url,
            provider=self.provider
        )
    
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        """
        识别事件之间的因果关系
        
        Args:
            events: 事件列表
            
        Returns:
            事件因果边列表
        """
        start_time = time.time()
        
        if self.use_optimization:
            # 使用优化版策略
            print("使用优化策略生成候选事件对...")
            # 通过CandidateGenerator生成候选事件对
            candidate_pairs = self.candidate_generator.generate_candidates(events)
            
            # 准备事件ID到事件对象的映射，便于后续查询
            event_map = {event.event_id: event for event in events}
            
            # 将候选事件对(ID对)转换为事件对象对
            event_pairs = []
            for id1, id2 in candidate_pairs:
                if id1 in event_map and id2 in event_map:
                    event_pairs.append((event_map[id1], event_map[id2]))
                else:
                    print(f"警告: 事件ID {id1} 或 {id2} 在事件列表中不存在")
            
            print(f"开始分析 {len(event_pairs)} 对事件的因果关系...")
            # 使用PairAnalyzer批量分析事件对
            edges = self.pair_analyzer.analyze_batch(event_pairs)
            
            # 计算优化效果
            original_pairs = len(events) * (len(events) - 1) // 2
            print(f"优化前可能的事件对数量：{original_pairs}")
            print(f"优化后实际分析的事件对数量：{len(event_pairs)}，节省了 {original_pairs - len(event_pairs)} 对（{(original_pairs - len(event_pairs)) / original_pairs * 100:.2f}%）")
        else:
            # 使用原始版全配对策略
            # 创建所有可能的事件对组合
            all_event_pairs = list(itertools.combinations(events, 2))
            print(f"分析 {len(all_event_pairs)} 对事件的因果关系...")
            
            # 使用PairAnalyzer批量分析事件对
            edges = self.pair_analyzer.analyze_batch(all_event_pairs)
        
        elapsed = time.time() - start_time
        print(f"发现 {len(edges)} 个因果关系")
        print(f"总耗时: {elapsed:.2f} 秒")
        
        return edges
    
    def analyze_causal_relation(self, event1: EventItem, event2: EventItem) -> Optional[CausalEdge]:
        """
        分析两个事件之间的因果关系
        
        Args:
            event1: 第一个事件
            event2: 第二个事件
            
        Returns:
            因果边对象，如果不存在因果关系则返回None
        """
        # 格式化提示
        prompt = self.format_prompt(event1, event2)
        
        # 调用LLM
        response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
        
        if not response["success"] or "json_content" not in response:
            print(f"事件 {event1.event_id} 和 {event2.event_id} 的因果分析失败: {response.get('error', '未知错误')}")
            return None
            
        # 解析响应
        edge = self.parse_response(response["json_content"], event1.event_id, event2.event_id)
        
        if edge:
            print(f"发现因果关系: {edge.from_id} -> {edge.to_id}, 强度: {edge.strength}")
            
        return edge
    
    def parse_response(self, response: Dict[str, Any], event1_id: str, event2_id: str) -> Optional[CausalEdge]:
        """
        解析LLM响应，提取因果关系
        
        Args:
            response: LLM响应
            event1_id: 第一个事件ID
            event2_id: 第二个事件ID
            
        Returns:
            因果边对象，如果不存在因果关系则返回None
        """
        # 检查是否存在因果关系
        has_causal = response.get("has_causal_relation", False)
        if not has_causal:
            return None
        
        # 获取因果方向
        direction = response.get("direction", "")
        
        if "event1->event2" in direction:
            from_id = event1_id
            to_id = event2_id
        elif "event2->event1" in direction:
            from_id = event2_id
            to_id = event1_id
        else:
            print(f"无法解析因果方向: {direction}")
            return None
        
        # 获取因果强度和理由
        strength = response.get("strength", "中")
        reason = response.get("reason", "")
        
        return CausalEdge(
            from_id=from_id,
            to_id=to_id,
            strength=strength,
            reason=reason
        )
    
    def build_dag(self, events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        构建有向无环图（DAG）
        
        Args:
            events: 事件列表
            edges: 因果边列表
            
        Returns:
            处理后的事件列表和因果边列表
        """
        # 使用图过滤器处理环和冲突
        filtered_edges = self.graph_filter.filter_edges_to_dag(events, edges)
        
        if len(filtered_edges) != len(edges):
            print(f"图中检测到环，已移除 {len(edges) - len(filtered_edges)} 条边以构建DAG")
            
        return events, filtered_edges
    
    # 以下方法是为了保持与测试兼容
    def _will_form_cycle(self, graph: List[List[int]], from_idx: int, to_idx: int) -> bool:
        """
        检查添加边是否会在图中形成环
        
        Args:
            graph: 当前图的邻接表
            from_idx: 边的起始节点索引
            to_idx: 边的终止节点索引
            
        Returns:
            如果会形成环则返回True，否则返回False
        """
        # 如果to_idx已经可以到达from_idx，添加边会形成环
        return self._is_reachable(graph, to_idx, from_idx, set())
    
    def _is_reachable(self, graph: List[List[int]], start: int, end: int, visited: Set[int]) -> bool:
        """
        检查在图中是否存在从start到end的路径
        
        Args:
            graph: 图的邻接表
            start: 起始节点索引
            end: 目标节点索引
            visited: 已访问节点集合
            
        Returns:
            如果存在路径则返回True，否则返回False
        """
        if start == end:
            return True
            
        visited.add(start)
        
        for neighbor in graph[start]:
            if neighbor not in visited and self._is_reachable(graph, neighbor, end, visited):
                return True
                
        return False
    
    def process_events(self, events: List[EventItem]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        处理事件列表，完成从链接到DAG构建的完整流程
        
        Args:
            events: 事件列表
            
        Returns:
            处理后的事件列表和因果边列表(DAG)
        """
        # 1. 找出事件间的因果关系
        edges = self.link_events(events)
        
        # 2. 构建有向无环图
        return self.build_dag(events, edges)


# 为向后兼容性提供原始版和优化版链接器的别名类
class CausalLinker(UnifiedCausalLinker):
    """
    原始版因果链接器的兼容类
    实际使用统一版但禁用优化
    """
    def __init__(self, *args, **kwargs):
        # 移除可能传入的优化参数
        for param in ['use_optimization', 'max_events_per_chapter', 'min_entity_support', 
                     'max_chapter_span', 'max_candidate_pairs', 'use_entity_weights']:
            if param in kwargs:
                kwargs.pop(param)
        
        # 固定使用不优化模式
        super().__init__(*args, use_optimization=False, **kwargs)
    
    def _will_form_cycle(self, graph, from_idx, to_idx):
        """
        检查添加边是否会形成环
        
        Args:
            graph: 当前图的邻接表
            from_idx: 边的起始节点索引
            to_idx: 边的终止节点索引
            
        Returns:
            如果会形成环则返回True，否则返回False
        """
        # 如果to_idx已经可以到达from_idx，添加边会形成环
        return self._is_reachable(graph, to_idx, from_idx, set())
    
    def _is_reachable(self, graph, start, end, visited):
        """
        检查在图中是否存在从start到end的路径
        
        Args:
            graph: 图的邻接表
            start: 起始节点索引
            end: 目标节点索引
            visited: 已访问节点集合
            
        Returns:
            如果存在路径则返回True，否则返回False
        """
        if start == end:
            return True
            
        visited.add(start)
        
        for neighbor in graph[start]:
            if neighbor not in visited and self._is_reachable(graph, neighbor, end, visited):
                return True
                
        return False


class OptimizedCausalLinker(UnifiedCausalLinker):
    """
    优化版因果链接器的兼容类
    实际使用统一版且启用优化
    """
    def __init__(self, *args, **kwargs):
        # 确保优化被启用
        kwargs['use_optimization'] = True
        super().__init__(*args, **kwargs)


# 当直接运行此文件时执行的测试代码
if __name__ == "__main__":
    print("运行统一因果链接器模块测试...")
    
    # 简单初始化测试 - 验证模块可以正确加载和初始化
    try:
        # 创建没有API密钥的实例（仅用于验证导入成功）
        # 实际使用时应该提供正确的API密钥
        linker = UnifiedCausalLinker(prompt_path="", api_key="test_key")
        print("✓ 统一因果链接器初始化成功")
        
        # 验证导入的其他模块
        print("✓ 成功导入 PairAnalyzer")
        print("✓ 成功导入 CandidateGenerator")
        print("✓ 成功导入 GraphFilter")
        
        print("\n所有模块加载成功！模块重构完成。")
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
