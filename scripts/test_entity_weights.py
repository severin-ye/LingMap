#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试实体频率权重反向调整功能

验证实体频率越高，权重越低的功能
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from common.models.event import EventItem
from causal_linking.service.optimized_linker_service import OptimizedCausalLinker

# 创建测试事件，特意添加一些高频实体和低频实体
def create_test_events(num_events=50, num_chapters=5):
    """创建测试事件，含高频和低频实体"""
    import random
    
    events = []
    
    # 常用角色和宝物，前两个是高频实体，会在所有事件中出现
    characters = ["韩立", "南宫婉", "墨大夫", "银月", "青元子", "七玄门掌门"]
    treasures = ["洗灵池", "青元剑诀", "火蟒剑", "青竹蜂云剑", "噬金虫"]
    locations = ["七玄门", "天南", "乱星海", "灵药园", "洞府"]
    
    # 为每个章节生成事件
    for chapter in range(1, num_chapters+1):
        chapter_id = f"第{chapter}章"
        
        # 每章生成固定数量的事件
        events_per_chapter = num_events // num_chapters
        
        for event_idx in range(1, events_per_chapter+1):
            event_id = f"E{chapter}-{event_idx}"
            
            # 添加高频实体（总是出现）
            event_characters = ["韩立"]  # 韩立是主角，每个事件都有
            
            # 随机添加其他角色
            for char in characters[2:]:  # 跳过前两个高频角色
                if random.random() > 0.7:  # 30%概率添加
                    event_characters.append(char)
            
            # 添加宝物
            if chapter == 1:  # 第一章总是出现"洗灵池"
                event_treasures = ["洗灵池"]
            else:
                event_treasures = []
                for treasure in treasures[1:]:
                    if random.random() > 0.8:  # 20%概率添加
                        event_treasures.append(treasure)
            
            # 生成事件
            event = EventItem(
                event_id=event_id,
                description=f"章节{chapter}的测试事件{event_idx}，涉及{','.join(event_characters)}",
                characters=event_characters,
                treasures=event_treasures,
                location=random.choice(locations),
                result=f"测试结果{event_idx}",
                chapter_id=chapter_id
            )
            
            events.append(event)
    
    return events

def calculate_entity_frequency(events):
    """计算实体频率"""
    entity_freq = {}
    
    for event in events:
        for character in event.characters:
            if character in entity_freq:
                entity_freq[character] += 1
            else:
                entity_freq[character] = 1
        
        for treasure in event.treasures:
            if treasure in entity_freq:
                entity_freq[treasure] += 1
            else:
                entity_freq[treasure] = 1
    
    return entity_freq

def main():
    """主函数"""
    print("测试实体频率权重反向调整功能")
    print("=" * 80)
    
    # 创建测试事件
    events = create_test_events(num_events=50, num_chapters=5)
    print(f"创建了 {len(events)} 个测试事件")
    
    # 计算并显示实体频率
    entity_freq = calculate_entity_frequency(events)
    sorted_entities = sorted(entity_freq.items(), key=lambda x: x[1], reverse=True)
    
    print("\n实体频率统计:")
    for entity, freq in sorted_entities:
        print(f"  {entity}: {freq} 次")
    
    # 创建优化版链接器实例，测试带权重的实体配对
    print("\n1. 使用实体权重反向调整:")
    linker_with_weights = OptimizedCausalLinker(
        api_key="dummy",  # 使用假API密钥，因为不会实际调用API
        model="dummy",
        provider="none",
        max_events_per_chapter=10,
        min_entity_support=1,  # 设为1以确保所有实体都被考虑
        max_chapter_span=99,   # 设为很大以确保不会因章节跨度过滤
        max_candidate_pairs=1000,
        use_entity_weights=True  # 使用实体权重
    )
    
    start_time = time.time()
    entity_pairs_with_weights = linker_with_weights._generate_entity_co_occurrence_pairs(events)
    elapsed = time.time() - start_time
    print(f"使用实体权重的配对完成，耗时: {elapsed:.6f} 秒")
    print(f"生成了 {len(entity_pairs_with_weights)} 对配对")
    
    # 测试不使用权重的实体配对
    print("\n2. 不使用实体权重:")
    linker_without_weights = OptimizedCausalLinker(
        api_key="dummy",
        model="dummy",
        provider="none",
        max_events_per_chapter=10,
        min_entity_support=1,
        max_chapter_span=99,
        max_candidate_pairs=1000,
        use_entity_weights=False  # 不使用实体权重
    )
    
    start_time = time.time()
    entity_pairs_without_weights = linker_without_weights._generate_entity_co_occurrence_pairs(events)
    elapsed = time.time() - start_time
    print(f"不使用实体权重的配对完成，耗时: {elapsed:.6f} 秒")
    print(f"生成了 {len(entity_pairs_without_weights)} 对配对")
    
    # 分析前10个带权重的配对
    print("\n带权重配对的前10个:")
    for i, (id1, id2) in enumerate(entity_pairs_with_weights[:10], 1):
        # 获取事件对象
        event1 = next((e for e in events if e.event_id == id1), None)
        event2 = next((e for e in events if e.event_id == id2), None)
        
        if event1 and event2:
            # 找出共同实体
            common_chars = set(event1.characters) & set(event2.characters)
            common_treasures = set(event1.treasures) & set(event2.treasures)
            common_entities = common_chars | common_treasures
            
            print(f"{i}. {id1} - {id2}")
            print(f"   共享实体: {', '.join(common_entities)}")
            print(f"   实体频率: {', '.join([f'{e}({entity_freq[e]})' for e in common_entities])}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()
