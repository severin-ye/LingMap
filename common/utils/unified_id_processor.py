#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一ID处理工具模块

提供集成的ID处理功能，包括：
1. 事件ID的唯一性保证
2. 图谱节点ID的处理
3. ID格式标准化
"""

import re
from typing import Dict, List, Tuple, Any, Set
from common.models.event import EventItem
from common.models.causal_edge import CausalEdge


class UnifiedIdProcessor:
    """统一ID处理器，管理系统中所有ID的唯一性和标准化"""
    
    @staticmethod
    def check_id_uniqueness(events: List[EventItem]) -> Dict[str, Any]:
        """
        检查事件列表中的ID唯一性
        
        Args:
            events: 事件列表
            
        Returns:
            包含唯一性检查结果的字典，包括:
            - unique: 是否所有ID都唯一
            - total_count: 总事件数
            - unique_count: 唯一ID数量
            - duplicate_ids: 重复ID列表
            - duplicate_counts: 每个重复ID的出现次数
        """
        if not events:
            return {
                "unique": True,
                "total_count": 0,
                "unique_count": 0,
                "duplicate_ids": [],
                "duplicate_counts": {}
            }
        
        event_ids = [event.event_id for event in events]
        id_counts = {}
        
        # TODO: Translate - 计算每个ID的出现次数
        for event_id in event_ids:
            id_counts[event_id] = id_counts.get(event_id, 0) + 1
        
        # TODO: Translate - 找出重复ID
        duplicate_ids = [id for id, count in id_counts.items() if count > 1]
        duplicate_counts = {id: count for id, count in id_counts.items() if count > 1}
        
        return {
            "unique": len(duplicate_ids) == 0,
            "total_count": len(events),
            "unique_count": len(set(event_ids)),
            "duplicate_ids": duplicate_ids,
            "duplicate_counts": duplicate_counts
        }

    @staticmethod
    def ensure_unique_event_ids(events: List[EventItem]) -> List[EventItem]:
        """
        确保事件ID的唯一性

        Args:
            events: 事件列表

        Returns:
            处理后具有唯一ID的事件列表
        """
        # TODO: Translate - CreateID计数器，用于跟踪每个基本ID的出现次数
        id_counter: Dict[str, int] = {}
        # TODO: Translate - 记录已存在的ID
        existing_ids: Set[str] = set()
        # TODO: Translate - Return的唯一IDevent列表
        unique_events: List[EventItem] = []

        for event in events:
            original_id = event.event_id
            
            # TODO: Translate - 如果ID已存在，为其Create唯一变体
            if original_id in existing_ids:
                if original_id not in id_counter:
                    # TODO: Translate - 第一次遇到重复，Initialize计数为1
                    id_counter[original_id] = 1
                
                # TODO: Translate - 增加计数
                id_counter[original_id] += 1
                
                # TODO: Translate - Create带有序号的唯一ID
                unique_id = f"{original_id}_{id_counter[original_id]}"
                
                # TODO: Translate - Create带有唯一ID的新event对象
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
                
                unique_events.append(unique_event)
                existing_ids.add(unique_id)
            else:
                # TODO: Translate - ID不重复，直接Use
                existing_ids.add(original_id)
                unique_events.append(event)
        
        return unique_events

    @staticmethod
    def normalize_event_id(event_id: str, chapter_id: str, index: int) -> str:
        """
        标准化事件ID，确保格式一致

        Args:
            event_id: 原始事件ID
            chapter_id: 章节ID
            index: 事件索引

        Returns:
            标准化的事件ID
        """
        # TODO: Translate - 如果没有eventID，则基于chapterID和索引Generate
        if not event_id:
            normalized_chapter_id = re.sub(r'[章节]', '', chapter_id)
            try:
                chapter_num = int(normalized_chapter_id)
                return f"E{chapter_num:02d}-{index}"
            except ValueError:
                # TODO: Translate - 如果无法转换为整数，直接Use原值
                return f"E{normalized_chapter_id}-{index}"
        
        # TODO: Translate - 如果已有eventID，Check格式
        if re.match(r'E\d+-\d+', event_id):
            return event_id
        
        # TODO: Translate - 尝试从现有ID中Extractchapter和索引信息
        match = re.search(r'第([一二三四五六七八九十百千万零]+|\d+)章-(\d+)', event_id)
        if match:
            chapter_number = match.group(1)
            event_number = match.group(2)
            
            # TODO: Translate - Process中文数字
            chinese_numbers = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
                              '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
            try:
                if chapter_number in chinese_numbers:
                    chapter_number = chinese_numbers[chapter_number]
                else:
                    chapter_number = int(chapter_number)
            except ValueError:
                # TODO: Translate - Process复合中文数字，此处简化Process
                chapter_number = 1  # TODO: Translate - 默认值
                
            return f"E{chapter_number:02d}-{event_number}"
        
        # TODO: Translate - 默认情况，Use原始ID
        return event_id

    @staticmethod
    def ensure_unique_node_ids(events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        确保图谱节点ID的唯一性，并更新边的引用
        
        Args:
            events: 事件列表
            edges: 因果边列表
            
        Returns:
            处理后的事件列表和边列表
        """
        # TODO: Translate - CreateeventID到event的映射
        event_map = {}
        unique_events = []
        duplicate_ids = set()  # TODO: Translate - 用于存储重复的ID
        id_counter = {}  # TODO: Translate - 计数器，用于跟踪每个基本ID出现的次数
        
        # TODO: Translate - 第一遍：检测重复ID
        for event in events:
            if event.event_id in event_map:
                duplicate_ids.add(event.event_id)
            else:
                event_map[event.event_id] = event
        
        # TODO: Translate - 清空event映射表，重新Build
        event_map.clear()
        
        # TODO: Translate - 第二遍：Process所有节点，为重复ID的节点分配唯一ID
        for event in events:
            original_id = event.event_id
            
            if original_id in duplicate_ids:
                # TODO: Translate - 这是一个重复ID
                if original_id not in id_counter:
                    id_counter[original_id] = 0
                
                # TODO: Translate - 增加计数
                id_counter[original_id] += 1
                
                # TODO: Translate - Create唯一ID
                unique_id = f"{original_id}_{id_counter[original_id]}"
                
                # TODO: Translate - Create新的event对象
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
                
                # TODO: Translate - 添加到映射
                event_map[unique_id] = unique_event
                unique_events.append(unique_event)
            else:
                # TODO: Translate - 非重复ID，直接Use
                event_map[original_id] = event
                unique_events.append(event)
        
        # TODO: Translate - Create用于更新边的映射，将原始ID映射到唯一ID列表
        original_to_unique_ids = {}
        for unique_event in unique_events:
            event_id = unique_event.event_id
            if "_" in event_id:
                # TODO: Translate - 这是一个带后缀的唯一ID
                original_id = event_id.rsplit("_", 1)[0]
                if original_id not in original_to_unique_ids:
                    original_to_unique_ids[original_id] = []
                original_to_unique_ids[original_id].append(event_id)
            else:
                # TODO: Translate - 非重复ID，自映射
                if event_id not in original_to_unique_ids:
                    original_to_unique_ids[event_id] = [event_id]
        
        # TODO: Translate - 更新边的引用
        updated_edges = []
        for edge in edges:
            from_id = edge.from_id
            to_id = edge.to_id
            
            # TODO: Translate - Get所有可能的唯一ID
            from_unique_ids = original_to_unique_ids.get(from_id, [from_id])
            to_unique_ids = original_to_unique_ids.get(to_id, [to_id])
            
            # TODO: Translate - 为每对唯一IDCreate边
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

    @staticmethod
    def fix_duplicate_event_ids(input_path: str, output_path: str = None) -> None:
        """
        修复文件中的重复事件ID
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径，如果为None则覆盖输入文件
        """
        import json
        
        # TODO: Translate - 如果未指定Output路径，则覆盖输入文件
        if output_path is None:
            output_path = input_path
            
        try:
            # TODO: Translate - Read文件
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                # TODO: Translate - 假设文件包含event列表
                try:
                    from common.models.event import EventItem
                    events = [EventItem(**item) if isinstance(item, dict) else item for item in data]
                    unique_events = UnifiedIdProcessor.ensure_unique_event_ids(events)
                    # TODO: Translate - 转换回原始格式
                    result = [event.__dict__ for event in unique_events]
                except Exception as e:
                    print(f"解析事件数据失败: {e}，尝试其他格式")
                    result = data
            elif isinstance(data, dict) and "events" in data:
                # TODO: Translate - 假设文件包含带有events键的字典
                try:
                    from common.models.event import EventItem
                    events = [EventItem(**item) if isinstance(item, dict) else item for item in data["events"]]
                    unique_events = UnifiedIdProcessor.ensure_unique_event_ids(events)
                    # TODO: Translate - 更新events键
                    data["events"] = [event.__dict__ for event in unique_events]
                    result = data
                except Exception as e:
                    print(f"解析嵌套事件数据失败: {e}，保留原有数据")
                    result = data
            else:
                print("未识别的数据格式，保持不变")
                result = data
                
            # TODO: Translate - 写回文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
            print(f"已处理文件并保存到 {output_path}")
            
        except Exception as e:
            import traceback
            print(f"处理文件时出错: {e}")
            traceback.print_exc()
