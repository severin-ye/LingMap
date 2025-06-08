#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试优化版链接器，只测试配对逻辑，不调用API
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
from causal_linking.di.provider import provide_linker

# 创建测试事件
def create_test_events(num_events=30, num_chapters=5):
    """创建测试事件"""
    import random
    
    events = []
    
    # 常用角色和宝物
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
            
            # 为事件分配1-3个角色
            event_characters = []
            for _ in range(min(3, len(characters))):
                char = random.choice(characters)
                if char not in event_characters:
                    event_characters.append(char)
            
            # 为事件分配0-2个宝物
            event_treasures = []
            for _ in range(min(2, len(treasures))):
                if random.random() > 0.5:  # 50%概率分配宝物
                    treasure = random.choice(treasures)
                    if treasure not in event_treasures:
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

def main():
    """主函数"""
    print("调试优化版链接器 - 仅测试配对逻辑")
    print("=" * 80)
    
    # 创建测试事件
    events = create_test_events(num_events=30, num_chapters=5)
    print(f"创建了 {len(events)} 个测试事件")
    
    # 创建优化版链接器实例
    linker = OptimizedCausalLinker(
        api_key="dummy",  # 使用假API密钥，因为不会实际调用API
        model="dummy",
        provider="none",
        max_events_per_chapter=5,
        min_entity_support=1,
        max_candidate_pairs=50
    )
    
    # 测试同章节配对
    print("\n1. 测试同章节事件配对:")
    start_time = time.time()
    chapter_pairs = linker._generate_same_chapter_pairs(events)
    elapsed = time.time() - start_time
    print(f"同章节事件配对完成，耗时: {elapsed:.6f} 秒")
    print(f"生成了 {len(chapter_pairs)} 对配对")
    print(f"前5个配对: {chapter_pairs[:5]}")
    
    # 测试实体共现配对
    print("\n2. 测试实体共现跨章配对:")
    start_time = time.time()
    entity_pairs = linker._generate_entity_co_occurrence_pairs(events)
    elapsed = time.time() - start_time
    print(f"实体共现跨章配对完成，耗时: {elapsed:.6f} 秒")
    print(f"生成了 {len(entity_pairs)} 对配对")
    print(f"前5个配对: {entity_pairs[:5]}")
    
    # 测试合并候选对
    print("\n3. 测试合并候选对:")
    start_time = time.time()
    merged_pairs = linker._merge_candidate_pairs(chapter_pairs, entity_pairs)
    elapsed = time.time() - start_time
    print(f"合并候选对完成，耗时: {elapsed:.6f} 秒")
    print(f"合并后有 {len(merged_pairs)} 对配对")
    print(f"前5个配对: {merged_pairs[:5]}")
    
    # 原始版本的配对逻辑会生成多少对？
    print("\n4. 对比原始版配对逻辑:")
    n = len(events)
    original_pairs = n * (n - 1) // 2
    print(f"原始版本的配对逻辑会生成 {original_pairs} 对")
    print(f"优化版本的配对逻辑生成 {len(merged_pairs)} 对")
    print(f"减少了 {original_pairs - len(merged_pairs)} 对 ({(original_pairs - len(merged_pairs)) / original_pairs * 100:.2f}%)")
    
    print("\n调试完成!")

if __name__ == "__main__":
    main()
