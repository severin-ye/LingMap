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
        max_events_per_chapter: int = 50,  # TODO: Translate - 大幅提高单章event数量限制
        min_entity_support: int = 3,
        max_chapter_span: int = 10,
        max_candidate_pairs: int = 150,  # TODO: Translate - 适当增加最大候选对上限
        use_entity_weights: bool = True,
        max_pairs_per_entity: int = 15,  # TODO: Translate - 增加每个实体最多Generate的event对数量
        connection_density: float = 0.2  # TODO: Translate - 新参数：控制连接密度的系数(0-1之间)
    ):
        """
        初始化事件对生成器
        
        Args:
            max_events_per_chapter: 每章节最多处理的事件数
            min_entity_support: 实体最小支持度，低于此值不考虑实体配对
            max_chapter_span: 跨章节配对的最大章节跨度
            max_candidate_pairs: 最大候选事件对数量
            use_entity_weights: 是否使用实体频率反向权重
            max_pairs_per_entity: 每个实体最多生成的事件对数量
            connection_density: 连接密度系数，控制生成事件对的稠密度
        """
        self.max_events_per_chapter = max_events_per_chapter
        self.min_entity_support = min_entity_support
        self.max_chapter_span = max_chapter_span
        self.max_candidate_pairs = max_candidate_pairs
        self.use_entity_weights = use_entity_weights
        self.max_pairs_per_entity = max_pairs_per_entity
        self.connection_density = min(1.0, max(0.1, connection_density))  # TODO: Translate - 确保在0.1-1之间
    
    def generate_candidates(self, events: List[EventItem]) -> List[Tuple[str, str]]:
        """
        生成候选事件对
        
        Args:
            events: 事件列表
            
        Returns:
            事件ID对列表 [(event_id1, event_id2), ...]
        """
        # TODO: Translate - 显示当前Configure参数
        print(f"候选生成器配置: 单章最大事件数={self.max_events_per_chapter}, 最小实体支持度={self.min_entity_support}, "
              f"最大章节跨度={self.max_chapter_span}, 最大候选对数={self.max_candidate_pairs}, "
              f"每实体最大对数={self.max_pairs_per_entity}")
        
        # TODO: Translate - 1. 同chapterevent配对
        print("正在执行策略1: 同章节事件配对...")
        chapter_pairs = self._generate_same_chapter_pairs(events)
        print(f"同章节事件配对完成，共生成 {len(chapter_pairs)} 对候选")
        
        # TODO: Translate - 2. 实体共现跨章配对
        print("正在执行策略2: 实体共现跨章配对...")
        entity_pairs = self._generate_entity_co_occurrence_pairs(events)
        print(f"实体共现跨章配对完成，共生成 {len(entity_pairs)} 对候选")
        
        # TODO: Translate - 3. 合并候选event对，去重
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
        # TODO: Translate - 按chapter分组event
        chapter_events: Dict[str, List[EventItem]] = defaultdict(list)
        for event in events:
            if event.chapter_id:
                chapter_events[event.chapter_id].append(event)
        
        # TODO: Translate - Generate同chapterevent对
        pairs = []
        for chapter_id, chapter_event_list in chapter_events.items():
            chapter_size = len(chapter_event_list)
            
            # TODO: Translate - 限制每章Process的event数，但保持较高的阈值
            if chapter_size > self.max_events_per_chapter:
                print(f"警告: 章节 {chapter_id} 的事件数量 {chapter_size} 超过限制 {self.max_events_per_chapter}，将被截断")
                chapter_event_list = chapter_event_list[:self.max_events_per_chapter]
                chapter_size = len(chapter_event_list)
            
            # TODO: Translate - 根据chapter大小动态调整连接密度
            # TODO: Translate - 小chapter(少于10个event)：保持全连接
            # TODO: Translate - 中等chapter(10-30个event)：根据密度系数减少连接
            # TODO: Translate - 大chapter(30个以上)：进一步降低密度
            if chapter_size <= 10:
                density_factor = 1.0  # TODO: Translate - 保持全连接
            elif chapter_size <= 30:
                density_factor = self.connection_density * 1.5  # TODO: Translate - 适当提高小chapter的连接密度
            else:
                density_factor = self.connection_density  # TODO: Translate - 大chapterUse标准密度
            
            # TODO: Translate - 计算目标连接数量
            all_possible_pairs = (chapter_size * (chapter_size - 1)) // 2
            target_pairs_count = max(10, int(all_possible_pairs * density_factor))
            
            # TODO: Translate - Generatechapter内两两组合，并规范化方向（保持索引顺序）
            chapter_pairs = []
            # TODO: Translate - 优先连接相邻event（时序相近更可能有causal关系）
            for i in range(len(chapter_event_list) - 1):
                event1 = chapter_event_list[i]
                for j in range(i + 1, min(i + 4, len(chapter_event_list))):
                    event2 = chapter_event_list[j]
                    if event1.event_id < event2.event_id:
                        chapter_pairs.append((event1.event_id, event2.event_id))
                    else:
                        chapter_pairs.append((event2.event_id, event1.event_id))
            
            # TODO: Translate - 如果仍未达到目标数量，添加随机event对
            if len(chapter_pairs) < target_pairs_count:
                # TODO: Translate - 组合所有可能的event对
                all_pairs = []
                for event1, event2 in itertools.combinations(chapter_event_list, 2):
                    pair = (event1.event_id, event2.event_id) if event1.event_id < event2.event_id else (event2.event_id, event1.event_id)
                    if pair not in chapter_pairs:  # TODO: Translate - 避免重复已添加的相邻event对
                        all_pairs.append(pair)
                
                # TODO: Translate - 随机选择剩余的event对
                import random
                remaining_needed = min(target_pairs_count - len(chapter_pairs), len(all_pairs))
                if remaining_needed > 0 and all_pairs:
                    random_pairs = random.sample(all_pairs, remaining_needed)
                    chapter_pairs.extend(random_pairs)
            
            pairs.extend(chapter_pairs)
            print(f"章节 {chapter_id}: {chapter_size} 个事件，生成 {len(chapter_pairs)} 对连接 (目标: {target_pairs_count}, 最大可能: {all_possible_pairs})")
        
        return list(set(pairs))  # TODO: Translate - 去重
    
    def _get_chapter_num(self, event: EventItem) -> int:
        """
        提取事件的章节编号
        
        Args:
            event: 事件对象
            
        Returns:
            章节编号，如果无法解析则返回0
        """
        if not event.chapter_id:
            return 0
            
        try:
            # TODO: Translate - Process不同格式的chapterID
            chapter_id = event.chapter_id
            # TODO: Translate - Process"第X章"格式
            if "第" in chapter_id and "章" in chapter_id:
                chapter_id = chapter_id.replace("第", "").replace("章", "")
            # TODO: Translate - Process"EXX-Y"格式（如E01-2）
            elif chapter_id.startswith("E") and "-" in chapter_id:
                chapter_id = chapter_id.split("-")[0][1:]
            
            # TODO: Translate - 尝试转换为整数
            return int(chapter_id)
        except (ValueError, TypeError):
            return 0
    
    def _generate_entity_co_occurrence_pairs(self, events: List[EventItem]) -> List[Tuple[str, str]]:
        """
        生成基于实体共现的跨章节事件配对
        
        Args:
            events: 事件列表
            
        Returns:
            事件ID对列表 [(event_id1, event_id2), ...]
        """
        # TODO: Translate - Create实体到event的倒排索引
        character_to_events: DefaultDict[str, List[EventItem]] = defaultdict(list)
        treasure_to_events: DefaultDict[str, List[EventItem]] = defaultdict(list)
        
        # TODO: Translate - Build实体-event倒排索引
        for event in events:
            for character in event.characters:
                character_to_events[character].append(event)
            for treasure in event.treasures:
                treasure_to_events[treasure].append(event)
        
        # TODO: Translate - 计算实体频率
        entity_freq = {
            entity: len(events_list) 
            for entity, events_list in {**character_to_events, **treasure_to_events}.items()
        }
        
        # TODO: Translate - 实体支持度过滤
        candidate_entities = {
            entity: events_list 
            for entity, events_list in {**character_to_events, **treasure_to_events}.items() 
            if len(events_list) >= self.min_entity_support
        }
        
        if not self.use_entity_weights:
            # TODO: Translate - 不Use权重，简单Generate配对
            pairs = []
            for entity, entity_events in candidate_entities.items():
                # TODO: Translate - 根据event的chapter_id排序以便应用chapter跨度限制
                entity_events.sort(key=lambda e: e.chapter_id if e.chapter_id else "")
                
                for event1, event2 in itertools.combinations(entity_events, 2):
                    # TODO: Translate - Checkchapter跨度
                    if self._check_chapter_span(event1, event2):
                        # TODO: Translate - 确保event对按ID排序，避免重复
                        if event1.event_id < event2.event_id:
                            pairs.append((event1.event_id, event2.event_id))
                        else:
                            pairs.append((event2.event_id, event1.event_id))
            
            return list(set(pairs))  # TODO: Translate - 去重后Return
        else:
            # TODO: Translate - 计算实体的反向权重：频率越高，权重越低
            # TODO: Translate - Use weight = 1 / log(frequency + 1.1) 公式
            entity_weights = {
                entity: 1.0 / math.log(freq + 1.1)  # TODO: Translate - 避免 log(1) = 0
                for entity, freq in entity_freq.items()
            }
            
            print(f"实体频率示例: {dict(list(entity_freq.items())[:5])}")
            print(f"实体权重示例: {dict(list(entity_weights.items())[:5])}")
            
            # TODO: Translate - Use权重，Generate带权重的配对并排序
            weighted_pairs = []
            # TODO: Translate - 按实体频率排序，先Process低频实体（频率越低，越可能包含关键信息）
            sorted_entities = sorted(
                candidate_entities.items(),
                key=lambda x: entity_freq[x[0]]  # TODO: Translate - 按频率排序
            )
            
            # TODO: Translate - 计算总共可Generate的实体对配额
            total_quota = min(self.max_candidate_pairs * 2, sum(1 for e in candidate_entities.values() for _ in itertools.combinations(e, 2)))
            remaining_quota = total_quota
            
            for entity, entity_events in sorted_entities:
                # TODO: Translate - 根据event的chapter_id排序以便应用chapter跨度限制
                entity_events.sort(key=lambda e: e.chapter_id if e.chapter_id else "")
                
                entity_weight = entity_weights[entity]
                entity_freq_count = entity_freq[entity]
                
                # TODO: Translate - 动态调整每个实体的配额，保证稀有实体有更高的配额
                # TODO: Translate - 但反转高频实体的逻辑：主角级实体虽然出现频率高，但往往是故事的关键驱动者
                if entity_freq_count > 30:  # TODO: Translate - 非常高频的主角实体
                    # TODO: Translate - 适度增加主角的配额，但仍保持相对限制
                    entity_quota = min(int(self.max_pairs_per_entity * 0.7), 12)
                    # TODO: Translate - 对其进行分chapterProcess，每个chapter选择几个关键event
                    chapter_groups = {}
                    for event in entity_events:
                        if event.chapter_id:
                            if event.chapter_id not in chapter_groups:
                                chapter_groups[event.chapter_id] = []
                            chapter_groups[event.chapter_id].append(event)
                    
                    # TODO: Translate - 每个chapter选择几个关键event点
                    chapter_events = []
                    for chapter_id, events_list in chapter_groups.items():
                        if len(events_list) > 3:
                            # TODO: Translate - 选择chapterStart、中间和结尾的event
                            chapter_events.append(events_list[0])  # TODO: Translate - 第一个
                            chapter_events.append(events_list[len(events_list)//2])  # TODO: Translate - 中间
                            chapter_events.append(events_list[-1])  # TODO: Translate - 最后一个
                        else:
                            chapter_events.extend(events_list)
                    
                    # TODO: Translate - 用筛选后的关键event替代原来的全部event
                    entity_events = chapter_events
                    print(f"实体 '{entity}' 频率很高 ({entity_freq_count})，已筛选为 {len(entity_events)} 个关键事件点")
                    
                elif entity_freq_count > 15:  # TODO: Translate - 重要配角
                    entity_quota = min(int(self.max_pairs_per_entity * 0.8), 10)
                else:  # TODO: Translate - 普通或稀有实体（往往更有信息价值）
                    entity_quota = self.max_pairs_per_entity
                
                # TODO: Translate - 计算该实体可能的总对数
                possible_entity_pairs = len(entity_events) * (len(entity_events) - 1) // 2
                
                # TODO: Translate - 限制每个实体Generate的event对数量，但要确保有足够的样本
                entity_pairs_count = 0
                valid_combinations = []
                
                # TODO: Translate - 预先收集所有有效的event对
                for event1, event2 in itertools.combinations(entity_events, 2):
                    if self._check_chapter_span(event1, event2):
                        # TODO: Translate - 确定event对顺序
                        pair = (event1, event2) if event1.event_id < event2.event_id else (event2, event1)
                        valid_combinations.append(pair)
                
                # TODO: Translate - 优先考虑chapter接近的event对（可能性更高）
                valid_combinations.sort(key=lambda pair: abs(self._get_chapter_num(pair[0]) - self._get_chapter_num(pair[1])))
                
                # TODO: Translate - 根据配额选择event对
                quota_to_use = min(entity_quota, len(valid_combinations))
                for event1, event2 in valid_combinations[:quota_to_use]:
                    # TODO: Translate - 确保event对按ID排序
                    if event1.event_id < event2.event_id:
                        weighted_pairs.append((event1.event_id, event2.event_id, entity_weight))
                    else:
                        weighted_pairs.append((event2.event_id, event1.event_id, entity_weight))
                    
                    entity_pairs_count += 1
                    remaining_quota -= 1
                
                print(f"实体 '{entity}' (频率:{entity_freq_count}): 添加了 {entity_pairs_count}/{possible_entity_pairs} 对事件 (配额:{quota_to_use})")
                
                # TODO: Translate - 如果总配额已用完，停止Process更多实体
                if remaining_quota <= 0:
                    print(f"实体事件对生成配额已用完，停止处理更多实体")
                    break
            
            # TODO: Translate - 合并共享多个实体的event对的权重
            pair_weights = {}
            for id1, id2, weight in weighted_pairs:
                pair_key = (id1, id2)
                if pair_key in pair_weights:
                    pair_weights[pair_key] += weight  # TODO: Translate - 累加权重
                else:
                    pair_weights[pair_key] = weight
            
            # TODO: Translate - 按权重排序
            sorted_pairs = sorted(
                [(id1, id2) for (id1, id2) in pair_weights.keys()],
                key=lambda pair: pair_weights[pair],
                reverse=True  # TODO: Translate - 高权重优先
            )
            
            return sorted_pairs
    
    def _check_chapter_span(self, event1: EventItem, event2: EventItem) -> bool:
        """
        检查两个事件的章节跨度是否在允许范围内
        
        Args:
            event1: First event
            event2: Second event
            
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
                # TODO: Translate - 如果chapterID不是数字格式，跳过跨度Check
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
        # TODO: Translate - 先Check同chapter对数量是否已经超过最大限制
        if len(chapter_pairs) >= self.max_candidate_pairs:
            print(f"同章节对数量 {len(chapter_pairs)} 已超过上限 {self.max_candidate_pairs}，截断")
            result_pairs = list(chapter_pairs[:self.max_candidate_pairs])
            print(f"最终候选对: {len(result_pairs)} 对，全部来自同章节配对")
            return result_pairs
        
        # TODO: Translate - 首先将同chapter对放入结果列表
        result_pairs = list(chapter_pairs)
        remaining_slots = self.max_candidate_pairs - len(result_pairs)
        
        # TODO: Translate - 如果还有剩余配额，添加实体共现对（避免重复）
        if remaining_slots > 0:
            chapter_pairs_set = set(chapter_pairs)
            added_entity_pairs = 0
            
            for pair in entity_pairs:
                if pair not in chapter_pairs_set:
                    result_pairs.append(pair)
                    added_entity_pairs += 1
                
                # TODO: Translate - 如果候选对数量已经达到上限，停止添加
                if added_entity_pairs >= remaining_slots:
                    print(f"达到候选对上限 {self.max_candidate_pairs}，停止添加更多候选")
                    break
            
            print(f"合并后总共 {len(result_pairs)} 对候选，其中同章节 {len(chapter_pairs)} 对，实体共现 {added_entity_pairs} 对（原始实体共现对 {len(entity_pairs)} 对）")
        else:
            print(f"同章节对数量 {len(chapter_pairs)} 已占用所有配额，未添加实体共现对")
        return result_pairs
