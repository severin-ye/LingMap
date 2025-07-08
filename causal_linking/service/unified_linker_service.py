#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# [CN] 统一因果链接器实现
# [EN] Unified causal linker implementation
# [CN] 融合基础版和优化版因果链接器功能：
# [EN] Integrates basic and optimized causal linker functionality:
# [CN] 1. 使用CandidateGenerator生成候选事件对
# [EN] 1. Use CandidateGenerator to generate candidate event pairs
# [CN] 2. 使用PairAnalyzer分析事件对因果关系
# [EN] 2. Use PairAnalyzer to analyze causal relationships between event pairs
# [CN] 3. 实现BaseLinker接口提供链接器功能
# [EN] 3. Implement BaseLinker interface to provide linker functionality
# [CN] 4. 构建有向无环图（DAG）
# [EN] 4. Build directed acyclic graph (DAG)

# [CN] 降低整体时间复杂度，从O(N²)降低到O(N·avg_m²) + O(E × k²)
# [EN] Reduce overall time complexity from O(N²) to O(N·avg_m²) + O(E × k²)
"""

import os
import sys
import time
import itertools
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Tuple, Set

# [CN] 添加项目根目录到Python路径
# [EN] Add project root directory to Python path
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
    # [CN] 统一版因果链接器，结合原始版和优化版的功能
    # [EN] Unified causal linker, combining original and optimized functionality
    # [CN] 支持完整的旧版功能，同时提供优化策略选项
    # [EN] Supports complete legacy functionality while providing optimization strategy options
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
        # [CN] 优化参数，默认启用优化
        # [EN] Optimization parameters, optimization enabled by default
        use_optimization: bool = True,
        max_events_per_chapter: int = 50,  # 大幅提高单章事件数量限制
        min_entity_support: int = 3,  # 保持中等实体支持度要求
        max_chapter_span: int = 10, 
        max_candidate_pairs: int = 150,  # 适当增加候选对数量上限
        use_entity_weights: bool = True
    ):
        """
        # [CN] 初始化统一因果链接器
        # [EN] Initialize unified causal linker
        
        Args:
            # [CN] model: 使用的LLM模型
            # [EN] model: LLM model to use
            # [CN] prompt_path: 提示词模板路径
            # [EN] prompt_path: Path to prompt template
            # [CN] api_key: API密钥
            # [EN] api_key: API key
            # [CN] base_url: 自定义API基础URL
            # [EN] base_url: Custom API base URL
            # [CN] max_workers: 并行处理的最大工作线程数
            # [EN] max_workers: Maximum number of worker threads for parallel processing
            # [CN] strength_mapping: 因果强度映射，用于权重比较
            # [EN] strength_mapping: Causal strength mapping for weight comparison
            # [CN] provider: API提供商，如"openai"或"deepseek"
            # [EN] provider: API provider, such as "openai" or "deepseek"
            # [CN] use_optimization: 是否使用优化策略，禁用则回退到原始全配对方法
            # [EN] use_optimization: Whether to use optimization strategy, fallback to original full pairing if disabled
            # [CN] max_events_per_chapter: 每章节最多处理的事件数
            # [EN] max_events_per_chapter: Maximum number of events to process per chapter
            # [CN] min_entity_support: 实体最小支持度，低于此值不考虑实体配对
            # [EN] min_entity_support: Minimum entity support level, entities below this threshold are not considered for pairing
            # [CN] max_chapter_span: 跨章节配对的最大章节跨度
            # [EN] max_chapter_span: Maximum chapter span for cross-chapter pairing
            # [CN] max_candidate_pairs: 最大候选事件对数量
            # [EN] max_candidate_pairs: Maximum number of candidate event pairs
            # [CN] use_entity_weights: 是否使用实体频率反向权重（频率越高权重越低）
            # [EN] use_entity_weights: Whether to use inverse entity frequency weights (higher frequency gets lower weight)
        """
        if not prompt_path:
            # [CN] 导入path_utils获取配置文件路径
            # [EN] Import path_utils to get configuration file path
            from common.utils.path_utils import get_config_path
            prompt_path = get_config_path("prompt_causal_linking.json")
            
        super().__init__(prompt_path)
        
        # [CN] 如果未提供API密钥，尝试从环境变量获取
        # [EN] If no API key is provided, try to get it from environment variables
        if not api_key:
            if provider == "openai":
                api_key_env = os.environ.get("OPENAI_API_KEY")
                if not api_key_env:
                    # [CN] 请提供 OpenAI API 密钥
                    # [EN] Please provide OpenAI API key
                    raise ValueError("请提供 OpenAI API 密钥")
                api_key = api_key_env
            elif provider == "deepseek":
                api_key_env = os.environ.get("DEEPSEEK_API_KEY")
                if not api_key_env:
                    # [CN] 请提供 DeepSeek API 密钥
                    # [EN] Please provide DeepSeek API key
                    raise ValueError("请提供 DeepSeek API 密钥")
                api_key = api_key_env
            else:
                # [CN] 不支持的 API 提供商
                # [EN] Unsupported API provider
                raise ValueError(f"不支持的 API 提供商: {provider}")
        
        self.model = model
        self.max_workers = max_workers
        self.provider = provider
        self.use_optimization = use_optimization
        
        # [CN] 设置强度映射
        # [EN] Set strength mapping
        self.strength_mapping = strength_mapping or {
            "高": 3,
            "中": 2,
            "低": 1
        }
        
        # [CN] 初始化候选生成器
        # [EN] Initialize candidate generator
        self.candidate_generator = CandidateGenerator(
            max_events_per_chapter=max_events_per_chapter,
            min_entity_support=min_entity_support,
            max_chapter_span=max_chapter_span,
            max_candidate_pairs=max_candidate_pairs,
            use_entity_weights=use_entity_weights,
            max_pairs_per_entity=15,  # [CN] 每个实体最多生成15对事件  # [EN] Maximum 15 event pairs per entity
            connection_density=0.2    # [CN] 控制连接密度的系数  # [EN] Coefficient to control connection density
        )
        
        # [CN] 初始化对分析器
        # [EN] Initialize pair analyzer
        self.pair_analyzer = PairAnalyzer(
            model=model,
            prompt_path=prompt_path,
            api_key=api_key,
            base_url=base_url,
            max_workers=max_workers,
            provider=provider
        )
        
        # [CN] 初始化图过滤器
        # [EN] Initialize graph filter
        self.graph_filter = GraphFilter(strength_mapping=self.strength_mapping)
        
        # [CN] 初始化LLM客户端 (仍然需要保留，用于analyze_causal_relation方法)
        # [EN] Initialize LLM client (still needed for analyze_causal_relation method)
        self.llm_client = LLMClient(
            api_key=api_key,
            model=self.model,
            base_url=base_url,
            provider=self.provider
        )
    
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        """
        # [CN] 识别事件之间的因果关系
        # [EN] Identify causal relationships between events
        
        Args:
            # [CN] events: 事件列表
            # [EN] events: List of events
            
        Returns:
            # [CN] 事件因果边列表
            # [EN] List of causal edges between events
        """
        start_time = time.time()
        
        if self.use_optimization:
            # [CN] 使用优化版策略
            # [EN] Use optimization strategy
            print("# [CN] 使用优化策略生成候选事件对...")
            print("# [EN] Using optimization strategy to generate candidate event pairs...")
            # [CN] 通过CandidateGenerator生成候选事件对
            # [EN] Generate candidate event pairs through CandidateGenerator
            candidate_pairs = self.candidate_generator.generate_candidates(events)
            
            # [CN] 准备事件ID到事件对象的映射，便于后续查询
            # [EN] Prepare mapping from event IDs to event objects for subsequent queries
            event_map = {event.event_id: event for event in events}
            
            # [CN] 将候选事件对(ID对)转换为事件对象对
            # [EN] Convert candidate event pairs (ID pairs) to event object pairs
            event_pairs = []
            for id1, id2 in candidate_pairs:
                if id1 in event_map and id2 in event_map:
                    event_pairs.append((event_map[id1], event_map[id2]))
                else:
                    # [CN] 警告: 事件ID {id1} 或 {id2} 在事件列表中不存在
                    # [EN] Warning: Event ID {id1} or {id2} does not exist in event list
                    print(f"# [CN] 警告: 事件ID {id1} 或 {id2} 在事件列表中不存在")
                    print(f"# [EN] Warning: Event ID {id1} or {id2} does not exist in event list")
            
            # [CN] 开始分析 {len(event_pairs)} 对事件的因果关系...
            # [EN] Starting to analyze causal relationships for {len(event_pairs)} event pairs...
            print(f"# [CN] 开始分析 {len(event_pairs)} 对事件的因果关系...")
            print(f"# [EN] Starting to analyze causal relationships for {len(event_pairs)} event pairs...")
            # [CN] 使用PairAnalyzer批量分析事件对
            # [EN] Use PairAnalyzer to analyze event pairs in batch
            edges = self.pair_analyzer.analyze_batch(event_pairs)
            
            # [CN] 计算优化效果
            # [EN] Calculate optimization effect
            original_pairs = len(events) * (len(events) - 1) // 2
            print(f"# [CN] 优化前可能的事件对数量：{original_pairs}")
            print(f"# [EN] Number of possible event pairs before optimization: {original_pairs}")
            # [CN] 优化后实际分析的事件对数量：{len(event_pairs)}，节省了 {original_pairs - len(event_pairs)} 对（{...}%）
            # [EN] Number of event pairs actually analyzed after optimization: {len(event_pairs)}, saved {original_pairs - len(event_pairs)} pairs ({...}%)
            print(f"# [CN] 优化后实际分析的事件对数量：{len(event_pairs)}，节省了 {original_pairs - len(event_pairs)} 对（{(original_pairs - len(event_pairs)) / original_pairs * 100:.2f}%）")
            print(f"# [EN] Number of event pairs actually analyzed after optimization: {len(event_pairs)}, saved {original_pairs - len(event_pairs)} pairs ({(original_pairs - len(event_pairs)) / original_pairs * 100:.2f}%)")
        else:
            # [CN] 使用原始版全配对策略
            # [EN] Use original full pairing strategy
            # [CN] 创建所有可能的事件对组合
            # [EN] Create all possible event pair combinations
            all_event_pairs = list(itertools.combinations(events, 2))
            # [CN] 分析 {len(all_event_pairs)} 对事件的因果关系...
            # [EN] Analyzing causal relationships for {len(all_event_pairs)} event pairs...
            print(f"# [CN] 分析 {len(all_event_pairs)} 对事件的因果关系...")
            print(f"# [EN] Analyzing causal relationships for {len(all_event_pairs)} event pairs...")
            
            # [CN] 使用PairAnalyzer批量分析事件对
            # [EN] Use PairAnalyzer to analyze event pairs in batch
            edges = self.pair_analyzer.analyze_batch(all_event_pairs)
        
        elapsed = time.time() - start_time
        # [CN] 发现 {len(edges)} 个因果关系
        # [EN] Discovered {len(edges)} causal relationships
        print(f"# [CN] 发现 {len(edges)} 个因果关系")
        print(f"# [EN] Discovered {len(edges)} causal relationships")
        # [CN] 总耗时: {elapsed:.2f} 秒
        # [EN] Total time elapsed: {elapsed:.2f} seconds
        print(f"# [CN] 总耗时: {elapsed:.2f} 秒")
        print(f"# [EN] Total time elapsed: {elapsed:.2f} seconds")
        
        return edges
    
    def analyze_causal_relation(self, event1: EventItem, event2: EventItem) -> Optional[CausalEdge]:
        """
        # [CN] 分析两个事件之间的因果关系
        # [EN] Analyze causal relationship between two events
        
        Args:
            # [CN] event1: 第一个事件
            # [EN] event1: First event
            # [CN] event2: 第二个事件
            # [EN] event2: Second event
            
        Returns:
            # [CN] 因果边对象，如果不存在因果关系则返回None
            # [EN] CausalEdge object, returns None if no causal relationship exists
        """
        # [CN] 格式化提示
        # [EN] Format prompt
        prompt = self.format_prompt(event1, event2)
        
        # [CN] 调用LLM
        # [EN] Call LLM
        response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
        
        if not response["success"] or "json_content" not in response:
            # [CN] 事件 {event1.event_id} 和 {event2.event_id} 的因果分析失败
            # [EN] Causal analysis failed for events {event1.event_id} and {event2.event_id}
            print(f"# [CN] 事件 {event1.event_id} 和 {event2.event_id} 的因果分析失败: {response.get('error', '未知错误')}")
            print(f"# [EN] Causal analysis failed for events {event1.event_id} and {event2.event_id}: {response.get('error', 'unknown error')}")
            return None
            
        # [CN] 解析响应
        # [EN] Parse response
        edge = self.parse_response(response["json_content"], event1.event_id, event2.event_id)
        
        if edge:
            # [CN] 发现因果关系: {edge.from_id} -> {edge.to_id}, 强度: {edge.strength}
            # [EN] Discovered causal relationship: {edge.from_id} -> {edge.to_id}, strength: {edge.strength}
            print(f"# [CN] 发现因果关系: {edge.from_id} -> {edge.to_id}, 强度: {edge.strength}")
            print(f"# [EN] Discovered causal relationship: {edge.from_id} -> {edge.to_id}, strength: {edge.strength}")
            
        return edge
    
    def parse_response(self, response: Dict[str, Any], event1_id: str, event2_id: str) -> Optional[CausalEdge]:
        """
        # [CN] 解析LLM响应，提取因果关系
        # [EN] Parse LLM response and extract causal relationships
        
        Args:
            # [CN] response: LLM响应
            # [EN] response: LLM response
            # [CN] event1_id: 第一个事件ID
            # [EN] event1_id: First event ID
            # [CN] event2_id: 第二个事件ID
            # [EN] event2_id: Second event ID
            
        Returns:
            # [CN] 因果边对象，如果不存在因果关系则返回None
            # [EN] CausalEdge object, returns None if no causal relationship exists
        """
        # [CN] 检查是否存在因果关系
        # [EN] Check if causal relationship exists
        has_causal = response.get("has_causal_relation", False)
        if not has_causal:
            return None
        
        # [CN] 获取因果方向
        # [EN] Get causal direction
        direction = response.get("direction", "")
        
        if "event1->event2" in direction:
            from_id = event1_id
            to_id = event2_id
        elif "event2->event1" in direction:
            from_id = event2_id
            to_id = event1_id
        else:
            # [CN] 无法解析因果方向
            # [EN] Unable to parse causal direction
            print(f"# [CN] 无法解析因果方向: {direction}")
            print(f"# [EN] Unable to parse causal direction: {direction}")
            return None
        
        # [CN] 获取因果强度和理由
        # [EN] Get causal strength and reason
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
        # [CN] 构建有向无环图（DAG）
        # [EN] Build Directed Acyclic Graph (DAG)
        
        Args:
            # [CN] events: 事件列表
            # [EN] events: List of events
            # [CN] edges: 因果边列表
            # [EN] edges: List of causal edges
            
        Returns:
            # [CN] 处理后的事件列表和因果边列表
            # [EN] Processed event list and causal edge list
        """
        # [CN] 首先，处理重复的节点ID
        # [EN] First, handle duplicate node IDs
        unique_events, updated_edges = self._ensure_unique_node_ids(events, edges)
        
        # [CN] 使用图过滤器处理环和冲突
        # [EN] Use graph filter to handle cycles and conflicts
        filtered_edges = self.graph_filter.filter_edges_to_dag(unique_events, updated_edges)
        
        if len(filtered_edges) != len(updated_edges):
            # [CN] 图中检测到环，已移除 {len(updated_edges) - len(filtered_edges)} 条边以构建DAG
            # [EN] Cycles detected in graph, removed {len(updated_edges) - len(filtered_edges)} edges to build DAG
            print(f"# [CN] 图中检测到环，已移除 {len(updated_edges) - len(filtered_edges)} 条边以构建DAG")
            print(f"# [EN] Cycles detected in graph, removed {len(updated_edges) - len(filtered_edges)} edges to build DAG")
            
        return unique_events, filtered_edges
        
    def _ensure_unique_node_ids(self, events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        # [CN] 确保事件节点ID的唯一性，并更新边的引用
        # [EN] Ensure uniqueness of event node IDs and update edge references
        
        Args:
            # [CN] events: 事件列表
            # [EN] events: List of events
            # [CN] edges: 因果边列表
            # [EN] edges: List of causal edges
            
        Returns:
            # [CN] 处理后的事件列表和边列表
            # [EN] Processed event list and edge list
        """
        # [CN] 优化: 先进行事件ID重复性检查，如果没有重复ID，可以直接返回原始数据
        # [CN] 这是一个常见优化技术，避免在不需要处理时进行复杂操作
        # [EN] Optimization: First check for duplicate event IDs, if no duplicates exist, return original data directly
        # [EN] This is a common optimization technique to avoid complex operations when not needed
        event_ids = [event.event_id for event in events]
        if len(event_ids) == len(set(event_ids)):
            # [CN] 没有重复ID，可以直接返回
            # [EN] No duplicate IDs, can return directly
            print("# [CN] 没有检测到重复的事件ID，跳过ID处理")
            print("# [EN] No duplicate event IDs detected, skipping ID processing")
            return events, edges
            
        # [CN] 检测到重复的事件ID，正在处理 {len(events)} 个事件...
        # [EN] Detected duplicate event IDs, processing {len(events)} events...
        print(f"# [CN] 检测到重复的事件ID，正在处理 {len(events)} 个事件...")
        print(f"# [EN] Detected duplicate event IDs, processing {len(events)} events...")
            
        # [CN] 创建事件ID到事件的映射
        # [EN] Create mapping from event IDs to events
        event_map = {}
        unique_events = []
        id_counter = {}  # [CN] 计数器，用于跟踪每个基本ID出现的次数  # [EN] Counter to track occurrences of each base ID
        id_mapping = {}  # [CN] 原始ID到唯一ID的映射  # [EN] Mapping from original IDs to unique IDs
        
        # [CN] 处理重复ID，为每个节点分配唯一ID
        # [EN] Handle duplicate IDs, assign unique ID for each node
        for event in events:
            original_id = event.event_id
            
            if original_id in event_map:
                # [CN] 如果ID已经存在，为其创建唯一ID
                # [EN] If ID already exists, create unique ID for it
                if original_id not in id_counter:
                    id_counter[original_id] = 1
                    # [CN] 为第一个出现的ID也创建映射
                    # [EN] Create mapping for the first occurrence of ID as well
                    first_unique_id = f"{original_id}_1"
                    id_mapping[original_id] = first_unique_id
                    
                    # [CN] 更新之前存储的事件
                    # [EN] Update previously stored event
                    old_event = event_map[original_id]
                    unique_event = EventItem(
                        event_id=first_unique_id,
                        description=old_event.description,
                        characters=old_event.characters,
                        treasures=old_event.treasures,
                        result=old_event.result,
                        location=old_event.location,
                        time=old_event.time,
                        chapter_id=old_event.chapter_id
                    )
                    
                    # [CN] 替换存储的事件
                    # [EN] Replace stored event
                    event_map[first_unique_id] = unique_event
                    
                    # [CN] 移除原始ID的映射
                    # [EN] Remove mapping of original ID
                    del event_map[original_id]
                    
                    # [CN] 在unique_events中找到并替换
                    # [EN] Find and replace in unique_events
                    for i, node in enumerate(unique_events):
                        if node.event_id == original_id:
                            unique_events[i] = unique_event
                            break
                
                # [CN] 为当前事件创建唯一ID
                # [EN] Create unique ID for current event
                id_counter[original_id] += 1
                unique_id = f"{original_id}_{id_counter[original_id]}"
                
                # [CN] 创建带有唯一ID的新事件
                # [EN] Create new event with unique ID
                unique_event = EventItem(
                    event_id=unique_id,
                    description=event.description,
                    characters=event.characters,
                    treasures=event.treasures,
                    result=event.result,
                    location=event.location,
                    time=event.time,
                    chapter_id=event.chapter_id
                )
                
                # [CN] 存储映射关系
                # [EN] Store mapping relationship
                id_mapping[unique_id] = unique_id  # [CN] 自映射，简化后续查找  # [EN] Self-mapping to simplify subsequent lookup
                event_map[unique_id] = unique_event
                unique_events.append(unique_event)
            else:
                # [CN] 第一次出现的ID
                # [EN] First occurrence of ID
                event_map[original_id] = event
                id_mapping[original_id] = original_id  # [CN] 自映射，简化后续查找  # [EN] Self-mapping to simplify subsequent lookup
                unique_events.append(event)
        
        # [CN] 并行更新边的引用，使用唯一ID
        # [EN] Update edge references in parallel using unique IDs
        updated_edges = []
        
        # [CN] 如果边的数量超过一定阈值，使用并行处理
        # [EN] Use parallel processing if number of edges exceeds certain threshold
        if len(edges) > 20:  # [CN] 设置一个合理的阈值，小于此值时顺序处理更快  # [EN] Set reasonable threshold, sequential processing is faster below this value
            def process_edge(edge):
                from_id = edge.from_id
                to_id = edge.to_id
                
                # [CN] 获取映射后的ID，如果没有映射则使用原始ID
                # [EN] Get mapped ID, use original ID if no mapping exists
                from_id_mapped = id_mapping.get(from_id, from_id)
                to_id_mapped = id_mapping.get(to_id, to_id)
                
                # [CN] 如果源节点或目标节点在映射中不存在，返回None
                # [EN] Return None if source or target node doesn't exist in mapping
                if from_id_mapped not in event_map or to_id_mapped not in event_map:
                    return None
                
                # [CN] 创建新的边
                # [EN] Create new edge
                return CausalEdge(
                    from_id=from_id_mapped,
                    to_id=to_id_mapped,
                    strength=edge.strength,
                    reason=edge.reason
                )
            
            # [CN] 使用并行处理更新 {len(edges)} 条边的引用...
            # [EN] Using parallel processing to update references for {len(edges)} edges...
            print(f"# [CN] 使用并行处理更新 {len(edges)} 条边的引用...")
            print(f"# [EN] Using parallel processing to update references for {len(edges)} edges...")
            # [CN] 使用线程池并行处理边
            # [EN] Use thread pool to process edges in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # [CN] 提交所有边处理任务
                # [EN] Submit all edge processing tasks
                results = list(executor.map(process_edge, edges))
                
            # [CN] 过滤掉无效的边
            # [EN] Filter out invalid edges
            updated_edges = [edge for edge in results if edge is not None]
            
            # [CN] 统计跳过的边数量
            # [EN] Count number of skipped edges
            skipped_count = len(edges) - len(updated_edges)
            if skipped_count > 0:
                # [CN] 警告：有 {skipped_count} 条边引用了不存在的节点，已被跳过
                # [EN] Warning: {skipped_count} edges referenced non-existent nodes and were skipped
                print(f"# [CN] 警告：有 {skipped_count} 条边引用了不存在的节点，已被跳过")
                print(f"# [EN] Warning: {skipped_count} edges referenced non-existent nodes and were skipped")
                
        else:
            # [CN] 对于边数量较少的情况，使用顺序处理
            # [EN] Use sequential processing for cases with fewer edges
            for edge in edges:
                from_id = edge.from_id
                to_id = edge.to_id
                
                # [CN] 获取映射后的ID，如果没有映射则使用原始ID
                # [EN] Get mapped ID, use original ID if no mapping exists
                from_id_mapped = id_mapping.get(from_id, from_id)
                to_id_mapped = id_mapping.get(to_id, to_id)
                
                # [CN] 如果源节点或目标节点在映射中不存在，直接跳过
                # [EN] Skip directly if source or target node doesn't exist in mapping
                if from_id_mapped not in event_map or to_id_mapped not in event_map:
                    # [CN] 警告：边 {from_id} -> {to_id} 引用了不存在的节点，将被跳过
                    # [EN] Warning: Edge {from_id} -> {to_id} references non-existent node and will be skipped
                    print(f"# [CN] 警告：边 {from_id} -> {to_id} 引用了不存在的节点，将被跳过")
                    print(f"# [EN] Warning: Edge {from_id} -> {to_id} references non-existent node and will be skipped")
                    continue
                
                # [CN] 创建新的边
                # [EN] Create new edge
                updated_edge = CausalEdge(
                    from_id=from_id_mapped,
                    to_id=to_id_mapped,
                    strength=edge.strength,
                    reason=edge.reason
                )
                updated_edges.append(updated_edge)
        
        # [CN] 处理了节点ID唯一性：原始事件数 {len(events)}，处理后事件数 {len(unique_events)}，处理后边数 {len(updated_edges)}
        # [EN] Processed node ID uniqueness: original events {len(events)}, processed events {len(unique_events)}, processed edges {len(updated_edges)}
        print(f"# [CN] 处理了节点ID唯一性：原始事件数 {len(events)}，处理后事件数 {len(unique_events)}，处理后边数 {len(updated_edges)}")
        print(f"# [EN] Processed node ID uniqueness: original events {len(events)}, processed events {len(unique_events)}, processed edges {len(updated_edges)}")
        return unique_events, updated_edges
    
    # [CN] 以下方法是为了保持与测试兼容
    # [EN] The following methods are for maintaining test compatibility
    def _will_form_cycle(self, graph: List[List[int]], from_idx: int, to_idx: int) -> bool:
        """
        # [CN] 检查添加边是否会在图中形成环
        # [EN] Check if adding an edge will form a cycle in the graph
        
        Args:
            # [CN] graph: 当前图的邻接表
            # [EN] graph: Adjacency list of current graph
            # [CN] from_idx: 边的起始节点索引
            # [EN] from_idx: Starting node index of the edge
            # [CN] to_idx: 边的终止节点索引
            # [EN] to_idx: Ending node index of the edge
            
        Returns:
            # [CN] 如果会形成环则返回True，否则返回False
            # [EN] Returns True if it will form a cycle, False otherwise
        """
        # [CN] 如果to_idx已经可以到达from_idx，添加边会形成环
        # [EN] If to_idx can already reach from_idx, adding edge will form a cycle
        return self._is_reachable(graph, to_idx, from_idx, set())
    
    def _is_reachable(self, graph: List[List[int]], start: int, end: int, visited: Set[int]) -> bool:
        """
        # [CN] 检查在图中是否存在从start到end的路径
        # [EN] Check if there exists a path from start to end in the graph
        
        Args:
            # [CN] graph: 图的邻接表
            # [EN] graph: Adjacency list of the graph
            # [CN] start: 起始节点索引
            # [EN] start: Starting node index
            # [CN] end: 目标节点索引
            # [EN] end: Target node index
            # [CN] visited: 已访问节点集合
            # [EN] visited: Set of visited nodes
            
        Returns:
            # [CN] 如果存在路径则返回True，否则返回False
            # [EN] Returns True if path exists, False otherwise
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
        # [CN] 处理事件列表，完成从链接到DAG构建的完整流程
        # [EN] Process event list, complete the full workflow from linking to DAG construction
        
        Args:
            # [CN] events: 事件列表
            # [EN] events: List of events
            
        Returns:
            # [CN] 处理后的事件列表和因果边列表(DAG)
            # [EN] Processed event list and causal edge list (DAG)
        """
        # [CN] 1. 找出事件间的因果关系
        # [EN] 1. Find causal relationships between events
        edges = self.link_events(events)
        
        # [CN] 2. 构建有向无环图
        # [EN] 2. Build directed acyclic graph
        return self.build_dag(events, edges)


# [CN] 为向后兼容性提供原始版和优化版链接器的别名类
# [EN] Provide alias classes for original and optimized linkers for backward compatibility
class CausalLinker(UnifiedCausalLinker):
    """
    # [CN] 原始版因果链接器的兼容类
    # [CN] 实际使用统一版但禁用优化
    # [EN] Compatibility class for original causal linker
    # [EN] Actually uses unified version but disables optimization
    """
    def __init__(self, *args, **kwargs):
        # [CN] 移除可能传入的优化参数
        # [EN] Remove optimization parameters that might be passed in
        for param in ['use_optimization', 'max_events_per_chapter', 'min_entity_support', 
                     'max_chapter_span', 'max_candidate_pairs', 'use_entity_weights']:
            if param in kwargs:
                kwargs.pop(param)
        
        # [CN] 固定使用不优化模式
        # [EN] Fixed to use non-optimization mode
        super().__init__(*args, use_optimization=False, **kwargs)
    
    def _will_form_cycle(self, graph, from_idx, to_idx):
        """
        # [CN] 检查添加边是否会形成环
        # [EN] Check if adding an edge will form a cycle
        
        Args:
            # [CN] graph: 当前图的邻接表
            # [EN] graph: Adjacency list of current graph
            # [CN] from_idx: 边的起始节点索引
            # [EN] from_idx: Starting node index of the edge
            # [CN] to_idx: 边的终止节点索引
            # [EN] to_idx: Ending node index of the edge
            
        Returns:
            # [CN] 如果会形成环则返回True，否则返回False
            # [EN] Returns True if it will form a cycle, False otherwise
        """
        # [CN] 如果to_idx已经可以到达from_idx，添加边会形成环
        # [EN] If to_idx can already reach from_idx, adding edge will form a cycle
        return self._is_reachable(graph, to_idx, from_idx, set())
    
    def _is_reachable(self, graph, start, end, visited):
        """
        # [CN] 检查在图中是否存在从start到end的路径
        # [EN] Check if there exists a path from start to end in the graph
        
        Args:
            # [CN] graph: 图的邻接表
            # [EN] graph: Adjacency list of the graph
            # [CN] start: 起始节点索引
            # [EN] start: Starting node index
            # [CN] end: 目标节点索引
            # [EN] end: Target node index
            # [CN] visited: 已访问节点集合
            # [EN] visited: Set of visited nodes
            
        Returns:
            # [CN] 如果存在路径则返回True，否则返回False
            # [EN] Returns True if path exists, False otherwise
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
    # [CN] 优化版因果链接器的兼容类
    # [CN] 实际使用统一版且启用优化
    # [EN] Compatibility class for optimized causal linker
    # [EN] Actually uses unified version with optimization enabled
    """
    def __init__(self, *args, **kwargs):
        # [CN] 确保优化被启用
        # [EN] Ensure optimization is enabled
        kwargs['use_optimization'] = True
        super().__init__(*args, **kwargs)


# [CN] 当直接运行此文件时执行的测试代码
# [EN] Test code executed when running this file directly
if __name__ == "__main__":
    # [CN] 运行统一因果链接器模块测试...
    # [EN] Running unified causal linker module test...
    print("# [CN] 运行统一因果链接器模块测试...")
    print("# [EN] Running unified causal linker module test...")
    
    # [CN] 简单初始化测试 - 验证模块可以正确加载和初始化
    # [EN] Simple initialization test - verify module can be loaded and initialized correctly
    try:
        # [CN] 创建没有API密钥的实例（仅用于验证导入成功）
        # [CN] 实际使用时应该提供正确的API密钥
        # [EN] Create instance without API key (only for verifying successful import)
        # [EN] Should provide correct API key when actually using
        linker = UnifiedCausalLinker(prompt_path="", api_key="test_key")
        # [CN] ✓ 统一因果链接器初始化成功
        # [EN] ✓ Unified causal linker initialization successful
        print("# [CN] ✓ 统一因果链接器初始化成功")
        print("# [EN] ✓ Unified causal linker initialization successful")
        
        # [CN] 验证导入的其他模块
        # [EN] Verify other imported modules
        # [CN] ✓ 成功导入 PairAnalyzer
        # [EN] ✓ Successfully imported PairAnalyzer
        print("# [CN] ✓ 成功导入 PairAnalyzer")
        print("# [EN] ✓ Successfully imported PairAnalyzer")
        # [CN] ✓ 成功导入 CandidateGenerator
        # [EN] ✓ Successfully imported CandidateGenerator
        print("# [CN] ✓ 成功导入 CandidateGenerator")
        print("# [EN] ✓ Successfully imported CandidateGenerator")
        # [CN] ✓ 成功导入 GraphFilter
        # [EN] ✓ Successfully imported GraphFilter
        print("# [CN] ✓ 成功导入 GraphFilter")
        print("# [EN] ✓ Successfully imported GraphFilter")
        
        # [CN] 所有模块加载成功！模块重构完成。
        # [EN] All modules loaded successfully! Module refactoring completed.
        print("# [CN] 所有模块加载成功！模块重构完成。")
        print("# [EN] All modules loaded successfully! Module refactoring completed.")
    except Exception as e:
        # [CN] 测试失败
        # [EN] Test failed
        print(f"# [CN] 测试失败: {str(e)}")
        print(f"# [EN] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
