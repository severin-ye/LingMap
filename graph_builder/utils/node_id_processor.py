#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点ID处理工具模块

专门处理重复节点ID，为Mermaid图谱生成提供唯一ID支持。
"""

from typing import List, Dict, Tuple, Any, Set
from common.models.event import EventItem
from common.models.causal_edge import CausalEdge


class NodeIdProcessor:
    """节点ID处理器，确保节点ID的唯一性"""
    
    @staticmethod
    def ensure_unique_node_ids(events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        确保事件节点ID的唯一性，并更新边的引用
        
        Args:
            events: 事件列表
            edges: 因果边列表
            
        Returns:
            处理后的事件列表和边列表
        """
        # 创建事件ID到事件的映射
        event_map = {}
        unique_events = []
        duplicate_ids = set()  # 用于存储重复的ID
        id_counter = {}  # 计数器，用于跟踪每个基本ID出现的次数
        
        # 第一遍：检测重复ID
        for event in events:
            if event.event_id in event_map:
                duplicate_ids.add(event.event_id)
            else:
                event_map[event.event_id] = event
        
        # 清空事件映射表，重新构建
        event_map.clear()
        
        # 第二遍：处理所有节点，为重复ID的节点分配唯一ID
        for event in events:
            original_id = event.event_id
            
            if original_id in duplicate_ids:
                # 这是一个重复ID
                if original_id not in id_counter:
                    id_counter[original_id] = 0
                
                # 增加计数
                id_counter[original_id] += 1
                
                # 创建唯一ID
                unique_id = f"{original_id}_{id_counter[original_id]}"
                
                # 创建新的事件对象
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
                
                # 添加到映射
                event_map[unique_id] = unique_event
                unique_events.append(unique_event)
            else:
                # 非重复ID，直接使用
                event_map[original_id] = event
                unique_events.append(event)
        
        # 创建用于更新边的映射，将原始ID映射到唯一ID列表
        original_to_unique_ids = {}
        for unique_event in unique_events:
            event_id = unique_event.event_id
            if "_" in event_id:
                # 这是一个带后缀的唯一ID
                original_id = event_id.rsplit("_", 1)[0]
                if original_id not in original_to_unique_ids:
                    original_to_unique_ids[original_id] = []
                original_to_unique_ids[original_id].append(event_id)
            else:
                # 非重复ID，自映射
                if event_id not in original_to_unique_ids:
                    original_to_unique_ids[event_id] = [event_id]
        
        # 更新边的引用
        updated_edges = []
        for edge in edges:
            from_id = edge.from_id
            to_id = edge.to_id
            
            # 获取所有可能的唯一ID
            from_unique_ids = original_to_unique_ids.get(from_id, [from_id])
            to_unique_ids = original_to_unique_ids.get(to_id, [to_id])
            
            # 为每对唯一ID创建边
            for from_unique_id in from_unique_ids:
                for to_unique_id in to_unique_ids:
                    if from_unique_id in event_map and to_unique_id in event_map:
                        updated_edge = CausalEdge(
                            from_id=from_unique_id,
                            to_id=to_unique_id,
                            strength=edge.strength,
                            reason=edge.reason
                        )
                        updated_edges.append(updated_edge)
        
        print(f"处理了节点ID唯一性：原始事件数 {len(events)}，处理后事件数 {len(unique_events)}，重复ID数量 {len(duplicate_ids)}")
        return unique_events, updated_edges
