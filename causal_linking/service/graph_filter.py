#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图过滤器模块
实现去环和贪心算法保留强边的功能

本模块是第四阶段因果链构建模块（CPC）的核心组件，
专门负责DAG构建中的环检测和移除算法。
"""

from typing import List, Dict, Set, Tuple, Optional
from common.models.event import EventItem
from common.models.causal_edge import CausalEdge


class GraphFilter:
    """
    图过滤器类
    
    实现基于贪心算法的循环打破和强边保留功能，
    按照理论支持文档中描述的算法进行DAG构建。
    """
    
    def __init__(self, strength_mapping: Dict[str, int] = None):
        """
        初始化图过滤器
        
        Args:
            strength_mapping: 强度映射字典，用于权重比较
        """
        self.strength_mapping = strength_mapping or {
            "高": 3,
            "中": 2,
            "低": 1
        }
    
    def filter_edges_to_dag(self, events: List[EventItem], edges: List[CausalEdge]) -> List[CausalEdge]:
        """
        使用贪心循环打破算法过滤边集，构建DAG
        
        这是第四阶段CPC模块的核心算法，实现了理论支持文档中描述的
        "贪婪循环打破算法（The Greedy Cycle-breaking Algorithm）"
        
        Args:
            events: 事件列表
            edges: 因果边列表
            
        Returns:
            过滤后的因果边列表（DAG）
            
        算法步骤：
        1. 按强度从高到低排序边
        2. 对于相同强度的边，按连接节点度数之和排序
        3. 逐个添加边，跳过会形成环的边
        4. 返回最终的无环边集
        """
        if not events or not edges:
            return []
        
        # 创建事件ID到索引的映射
        event_map = {event.event_id: i for i, event in enumerate(events)}
        
        # 按强度降序排序边（贪心算法第一步）
        sorted_edges = self._sort_edges_by_priority(edges, event_map)
        
        # 创建邻接表表示的图
        graph = [[] for _ in range(len(events))]
        
        # 保留的边列表
        dag_edges = []
        added_edges = set()
        
        # 贪心构建DAG（算法核心步骤）
        for edge in sorted_edges:
            # 检查事件是否在映射中
            if edge.from_id not in event_map or edge.to_id not in event_map:
                continue
                
            from_idx = event_map[edge.from_id]
            to_idx = event_map[edge.to_id]
            
            # 检查是否已添加相同的边
            edge_key = (from_idx, to_idx)
            if edge_key in added_edges:
                continue
                
            # 环检测：如果添加这条边会形成环，则跳过
            if not self._will_form_cycle(graph, from_idx, to_idx):
                # 添加边到图中
                graph[from_idx].append(to_idx)
                added_edges.add(edge_key)
                dag_edges.append(edge)
        
        return dag_edges
    
    def _sort_edges_by_priority(self, edges: List[CausalEdge], event_map: Dict[str, int]) -> List[CausalEdge]:
        """
        按优先级排序边
        
        实现贪心算法的排序策略：
        1. 首先按强度从高到低排序
        2. 对于相同强度，按连接节点度数之和排序
        
        Args:
            edges: 边列表
            event_map: 事件ID到索引的映射
            
        Returns:
            排序后的边列表
        """
        def get_edge_priority(edge: CausalEdge) -> Tuple[int, int]:
            """
            获取边的优先级
            
            Returns:
                (强度权重的负值, 度数之和的负值) - 用于降序排序
            """
            strength_weight = self.strength_mapping.get(edge.strength, 0)
            
            # 计算连接节点的度数之和（这里简化为固定权重）
            # 在实际应用中，可以根据节点的实际度数进行计算
            node_degree_sum = 0  # 简化实现
            
            return (-strength_weight, -node_degree_sum)
        
        return sorted(edges, key=get_edge_priority)
    
    def _will_form_cycle(self, graph: List[List[int]], from_idx: int, to_idx: int) -> bool:
        """
        检查添加边是否会形成环
        
        使用深度优先搜索检测环的存在。
        如果to_idx已经可以到达from_idx，那么添加from_idx->to_idx边会形成环。
        
        Args:
            graph: 当前图的邻接表
            from_idx: 边的起始节点索引
            to_idx: 边的终止节点索引
            
        Returns:
            如果会形成环则返回True，否则返回False
        """
        return self._is_reachable(graph, to_idx, from_idx, set())
    
    def _is_reachable(self, graph: List[List[int]], start: int, end: int, visited: Set[int]) -> bool:
        """
        使用深度优先搜索检查节点可达性
        
        Args:
            graph: 图的邻接表表示
            start: 起始节点
            end: 目标节点
            visited: 已访问节点集合
            
        Returns:
            如果从start可以到达end则返回True，否则返回False
        """
        if start == end:
            return True
        
        if start in visited:
            return False
        
        visited.add(start)
        
        for neighbor in graph[start]:
            if self._is_reachable(graph, neighbor, end, visited):
                return True
        
        return False
    
    def detect_cycles(self, events: List[EventItem], edges: List[CausalEdge]) -> List[List[str]]:
        """
        检测图中的所有环
        
        Args:
            events: 事件列表
            edges: 因果边列表
            
        Returns:
            环的列表，每个环由事件ID组成
        """
        if not events or not edges:
            return []
        
        # 创建事件ID到索引的映射
        event_map = {event.event_id: i for i, event in enumerate(events)}
        id_map = {i: event.event_id for i, event in enumerate(events)}
        
        # 构建邻接表
        graph = [[] for _ in range(len(events))]
        for edge in edges:
            if edge.from_id in event_map and edge.to_id in event_map:
                from_idx = event_map[edge.from_id]
                to_idx = event_map[edge.to_id]
                graph[from_idx].append(to_idx)
        
        # 使用DFS检测环
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: int, path: List[int]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph[node]:
                if neighbor in rec_stack:
                    # 找到环
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycle_ids = [id_map[i] for i in cycle]
                    cycles.append(cycle_ids)
                elif neighbor not in visited:
                    dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for i in range(len(events)):
            if i not in visited:
                dfs(i, [])
        
        return cycles
    
    def get_filter_statistics(self, original_edges: List[CausalEdge], filtered_edges: List[CausalEdge]) -> Dict[str, any]:
        """
        获取过滤统计信息
        
        Args:
            original_edges: 原始边集
            filtered_edges: 过滤后边集
            
        Returns:
            统计信息字典
        """
        return {
            "original_edge_count": len(original_edges),
            "filtered_edge_count": len(filtered_edges),
            "removed_edge_count": len(original_edges) - len(filtered_edges),
            "retention_rate": len(filtered_edges) / len(original_edges) if original_edges else 0,
            "strength_distribution": {
                "original": self._get_strength_distribution(original_edges),
                "filtered": self._get_strength_distribution(filtered_edges)
            }
        }
    
    def _get_strength_distribution(self, edges: List[CausalEdge]) -> Dict[str, int]:
        """
        获取边强度分布
        
        Args:
            edges: 边列表
            
        Returns:
            强度分布字典
        """
        distribution = {"高": 0, "中": 0, "低": 0}
        for edge in edges:
            if edge.strength in distribution:
                distribution[edge.strength] += 1
        return distribution
