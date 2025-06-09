#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
候选事件对生成器
实现不同的候选事件对生成策略：
1. 同章节事件配对
2. 实体共现事件配对
3. 合并策略结果
"""

import math
import itertools
from typing import List, Dict, Tuple, DefaultDict, Set
from collections import defaultdict

from common.models.event import EventItem


class CandidateGenerator:
    """
    候选事件对生成器
    实现多种不同的候选事件对生成策略
    """
    
    def __init__(
        self,
        max_events_per_chapter: int = 20,
        min_entity_support: int = 2,
        max_chapter_span: int = 10,
        max_candidate_pairs: int = 10000,
        use_entity_weights: bool = True
    ):
        """
        初始化事件对生成器
        
        Args:
            max_events_per_chapter: 每章节最多处理的事件数
            min_entity_support: 实体最小支持度，低于此值不考虑实体配对
            max_chapter_span: 跨章节配对的最大章节跨度
            max_candidate_pairs: 最大候选事件对数量
            use_entity_weights: 是否使用实体频率反向权重
        """
        self.max_events_per_chapter = max_events_per_chapter
        self.min_entity_support = min_entity_support
        self.max_chapter_span = max_chapter_span
        self.max_candidate_pairs = max_candidate_pairs
        self.use_entity_weights = use_entity_weights
    
    def generate_candidates(self, events: List[EventItem]) -> List[Tuple[str, str]]:
        """
        生成候选事件对
        
        Args:
            events: 事件列表
            
        Returns:
            事件ID对列表 [(event_id1, event_id2), ...]
        """
        # 1. 同章节事件配对
        print("正在执行策略1: 同章节事件配对...")
        chapter_pairs = self._generate_same_chapter_pairs(events)
        print(f"同章节事件配对完成，共生成 {len(chapter_pairs)} 对候选")
        
        # 2. 实体共现跨章配对
        print("正在执行策略2: 实体共现跨章配对...")
        entity_pairs = self._generate_entity_co_occurrence_pairs(events)
        print(f"实体共现跨章配对完成，共生成 {len(entity_pairs)} 对候选")
        
        # 3. 合并候选事件对，去重
        candidate_pairs = self._merge_candidate_pairs(chapter_pairs, entity_pairs)
        print(f"合并去重后的候选事件对: {len(candidate_pairs)} 对")
        
        return candidate_pairs
    
    def _generate_same_chapter_pairs(self, events: List[EventItem]) -> List[Tuple[str, str]]:
        """
        生成同章节事件配对
        
        Args:
            events: 事件列表
            
        Returns:
            事件ID对列表 [(event_id1, event_id2), ...]
        """
        # 按章节分组事件
        chapter_events: Dict[str, List[EventItem]] = defaultdict(list)
        for event in events:
            if event.chapter_id:
                chapter_events[event.chapter_id].append(event)
        
        # 生成同章节事件对
        pairs = []
        for chapter_id, chapter_event_list in chapter_events.items():
            # 限制每章处理的事件数
            if len(chapter_event_list) > self.max_events_per_chapter:
                print(f"警告: 章节 {chapter_id} 的事件数量 {len(chapter_event_list)} 超过限制 {self.max_events_per_chapter}，将被截断")
                chapter_event_list = chapter_event_list[:self.max_events_per_chapter]
            
            # 生成章节内两两组合，并规范化方向（保持索引顺序）
            chapter_pairs = []
            for event1, event2 in itertools.combinations(chapter_event_list, 2):
                # 确保事件对按ID排序，避免重复
                if event1.event_id < event2.event_id:
                    chapter_pairs.append((event1.event_id, event2.event_id))
                else:
                    chapter_pairs.append((event2.event_id, event1.event_id))
            
            pairs.extend(chapter_pairs)
        
        return list(set(pairs))  # 去重
    
    def _generate_entity_co_occurrence_pairs(self, events: List[EventItem]) -> List[Tuple[str, str]]:
        """
        生成基于实体共现的跨章节事件配对
        
        Args:
            events: 事件列表
            
        Returns:
            事件ID对列表 [(event_id1, event_id2), ...]
        """
        # 创建实体到事件的倒排索引
        character_to_events: DefaultDict[str, List[EventItem]] = defaultdict(list)
        treasure_to_events: DefaultDict[str, List[EventItem]] = defaultdict(list)
        
        # 构建实体-事件倒排索引
        for event in events:
            for character in event.characters:
                character_to_events[character].append(event)
            for treasure in event.treasures:
                treasure_to_events[treasure].append(event)
        
        # 计算实体频率
        entity_freq = {
            entity: len(events_list) 
            for entity, events_list in {**character_to_events, **treasure_to_events}.items()
        }
        
        # 实体支持度过滤
        candidate_entities = {
            entity: events_list 
            for entity, events_list in {**character_to_events, **treasure_to_events}.items() 
            if len(events_list) >= self.min_entity_support
        }
        
        if not self.use_entity_weights:
            # 不使用权重，简单生成配对
            pairs = []
            for entity, entity_events in candidate_entities.items():
                # 根据事件的chapter_id排序以便应用章节跨度限制
                entity_events.sort(key=lambda e: e.chapter_id if e.chapter_id else "")
                
                for event1, event2 in itertools.combinations(entity_events, 2):
                    # 检查章节跨度
                    if self._check_chapter_span(event1, event2):
                        # 确保事件对按ID排序，避免重复
                        if event1.event_id < event2.event_id:
                            pairs.append((event1.event_id, event2.event_id))
                        else:
                            pairs.append((event2.event_id, event1.event_id))
            
            return list(set(pairs))  # 去重后返回
        else:
            # 计算实体的反向权重：频率越高，权重越低
            # 使用 weight = 1 / log(frequency + 1.1) 公式
            entity_weights = {
                entity: 1.0 / math.log(freq + 1.1)  # 避免 log(1) = 0
                for entity, freq in entity_freq.items()
            }
            
            print(f"实体频率示例: {dict(list(entity_freq.items())[:5])}")
            print(f"实体权重示例: {dict(list(entity_weights.items())[:5])}")
            
            # 使用权重，生成带权重的配对并排序
            weighted_pairs = []
            for entity, entity_events in candidate_entities.items():
                # 根据事件的chapter_id排序以便应用章节跨度限制
                entity_events.sort(key=lambda e: e.chapter_id if e.chapter_id else "")
                
                entity_weight = entity_weights[entity]
                
                for event1, event2 in itertools.combinations(entity_events, 2):
                    # 检查章节跨度
                    if self._check_chapter_span(event1, event2):
                        # 确保事件对按ID排序，避免重复
                        if event1.event_id < event2.event_id:
                            weighted_pairs.append((event1.event_id, event2.event_id, entity_weight))
                        else:
                            weighted_pairs.append((event2.event_id, event1.event_id, entity_weight))
            
            # 合并共享多个实体的事件对的权重
            pair_weights = {}
            for id1, id2, weight in weighted_pairs:
                pair_key = (id1, id2)
                if pair_key in pair_weights:
                    pair_weights[pair_key] += weight  # 累加权重
                else:
                    pair_weights[pair_key] = weight
            
            # 按权重排序
            sorted_pairs = sorted(
                [(id1, id2) for (id1, id2) in pair_weights.keys()],
                key=lambda pair: pair_weights[pair],
                reverse=True  # 高权重优先
            )
            
            return sorted_pairs
    
    def _check_chapter_span(self, event1: EventItem, event2: EventItem) -> bool:
        """
        检查两个事件的章节跨度是否在允许范围内
        
        Args:
            event1: 第一个事件
            event2: 第二个事件
            
        Returns:
            如果章节跨度合法则返回True，否则返回False
        """
        if event1.chapter_id and event2.chapter_id:
            try:
                ch1 = int(event1.chapter_id.replace("第", "").replace("章", ""))
                ch2 = int(event2.chapter_id.replace("第", "").replace("章", ""))
                if abs(ch1 - ch2) > self.max_chapter_span:
                    return False
            except (ValueError, AttributeError):
                # 如果章节ID不是数字格式，跳过跨度检查
                pass
        return True
    
    def _merge_candidate_pairs(
        self, 
        chapter_pairs: List[Tuple[str, str]], 
        entity_pairs: List[Tuple[str, str]]
    ) -> List[Tuple[str, str]]:
        """
        合并两种来源的候选事件对，并去重
        
        Args:
            chapter_pairs: 同章节事件配对结果
            entity_pairs: 实体共现配对结果（已按权重排序）
            
        Returns:
            合并去重后的候选事件对列表
        """
        # 首先将所有同章节对放入结果列表
        result_pairs = list(chapter_pairs)
        
        # 然后添加实体共现对，但避免重复
        chapter_pairs_set = set(chapter_pairs)
        
        for pair in entity_pairs:
            if pair not in chapter_pairs_set:
                result_pairs.append(pair)
            
            # 如果候选对数量已经达到上限，停止添加
            if len(result_pairs) >= self.max_candidate_pairs:
                print(f"达到候选对上限 {self.max_candidate_pairs}，停止添加更多候选")
                break
        
        print(f"合并后总共 {len(result_pairs)} 对候选，其中同章节 {len(chapter_pairs)} 对，实体共现 {len(result_pairs) - len(chapter_pairs)} 对")
        return result_pairs
