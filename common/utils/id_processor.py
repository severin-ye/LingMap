#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ID处理工具模块

处理事件ID的唯一性，确保在最上游的事件提取阶段生成唯一ID。
"""

from typing import Dict, List, Tuple, Set
import re
from common.models.event import EventItem


class IdProcessor:
    """ID处理器，确保事件ID的唯一性"""

    @staticmethod
    def ensure_unique_event_ids(events: List[EventItem]) -> List[EventItem]:
        """
        确保事件ID的唯一性

        Args:
            events: 事件列表

        Returns:
            处理后具有唯一ID的事件列表
        """
        # 创建ID计数器，用于跟踪每个基本ID的出现次数
        id_counter: Dict[str, int] = {}
        # 记录已存在的ID
        existing_ids: Set[str] = set()
        # 返回的唯一ID事件列表
        unique_events: List[EventItem] = []

        for event in events:
            original_id = event.event_id
            
            # 如果ID已存在，为其创建唯一变体
            if original_id in existing_ids:
                if original_id not in id_counter:
                    # 第一次遇到重复，初始化计数为1
                    id_counter[original_id] = 1
                
                # 增加计数
                id_counter[original_id] += 1
                
                # 创建带有序号的唯一ID
                unique_id = f"{original_id}_{id_counter[original_id]}"
                
                # 创建带有唯一ID的新事件对象
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
                # ID不重复，直接使用
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
        # 如果没有事件ID，则基于章节ID和索引生成
        if not event_id:
            normalized_chapter_id = re.sub(r'[章节]', '', chapter_id)
            return f"E{normalized_chapter_id:02d}-{index}"
        
        # 如果已有事件ID，检查格式
        if re.match(r'E\d+-\d+', event_id):
            return event_id
        
        # 尝试从现有ID中提取章节和索引信息
        match = re.search(r'第([一二三四五六七八九十百千万零]+|\d+)章-(\d+)', event_id)
        if match:
            chapter_number = match.group(1)
            event_number = match.group(2)
            
            # 处理中文数字
            chinese_numbers = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
                              '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
            try:
                if chapter_number in chinese_numbers:
                    chapter_number = chinese_numbers[chapter_number]
                else:
                    chapter_number = int(chapter_number)
            except ValueError:
                # 处理复合中文数字，此处简化处理
                chapter_number = 1  # 默认值
                
            return f"E{chapter_number:02d}-{event_number}"
        
        # 默认情况，使用原始ID
        return event_id
