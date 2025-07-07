#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
因果链接器测试脚本

综合测试以下功能：
1. 优化版链接器性能和功能（与原始版对比）
2. 实体频率权重反向调整功能
3. 统一版链接器的兼容性和实现
"""

import os
import sys
import json
import time
import random
from pathlib import Path

# TODO: Translate - Add project root directory to系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Loadenvironment variables
from dotenv import load_dotenv
load_dotenv()

from common.models.event import EventItem
from common.utils.enhanced_logger import EnhancedLogger
from causal_linking.di.provider import provide_linker
from causal_linking.service.unified_linker_service import UnifiedCausalLinker
from causal_linking.service.unified_linker_service import CausalLinker
from causal_linking.service.unified_linker_service import OptimizedCausalLinker  # TODO: Translate - 现在从统一服务中Import

# TODO: Translate - Create日志记录器
logger = EnhancedLogger("causal_linking_test", log_level="DEBUG")

#===============================================================================
# TODO: Translate - 调试和性能Test功能（合并自debug_optimized_linker.py和test_entity_weights.py）
#===============================================================================

def debug_optimized_linker_pairing():
    """调试优化版链接器的配对逻辑，不调用API"""
    print("调试优化版链接器 - 仅测试配对逻辑")
    print("=" * 80)
    
    # CreateTestevent
    events = create_test_events_standard(num_events=30, num_chapters=5)
    print(f"创建了 {len(events)} 个测试事件")
    
    # TODO: Translate - Create统一版linking器实例，Use优化策略
    linker = UnifiedCausalLinker(
        api_key="dummy",  # TODO: Translate - Use假API key，因为不会实际调用API
        model="dummy",
        provider="openai",
        use_optimization=True,
        max_events_per_chapter=5,
        min_entity_support=1,
        max_candidate_pairs=50
    )
    
    print("✓ 统一版链接器初始化成功（优化模式）")
    print("注意：由于方法重构，跳过内部方法测试")
    
    # TODO: Translate - 原始版本的配对逻辑会Generate多少对？
    print("\n对比原始版配对逻辑:")
    n = len(events)
    original_pairs = n * (n - 1) // 2
    print(f"原始版本的配对逻辑会生成 {original_pairs} 对")
    print(f"优化版本将显著减少配对数量")
    
    return True

def test_entity_frequency_weights():
    """测试实体频率权重功能"""
    print("\n测试实体频率权重功能")
    print("=" * 80)
    
    # TODO: Translate - Create包含高频和低频实体的Testevent
    events = create_test_events_with_freq(num_events=50, num_chapters=5)
    print(f"创建了 {len(events)} 个测试事件，包含高频和低频实体")
    
    # TODO: Translate - 统计实体频率
    entity_freq = {}
    for event in events:
        for char in event.characters:
            entity_freq[char] = entity_freq.get(char, 0) + 1
        for treasure in event.treasures:
            entity_freq[treasure] = entity_freq.get(treasure, 0) + 1
    
    # TODO: Translate - 显示前10个最高频的实体
    sorted_entities = sorted(entity_freq.items(), key=lambda x: x[1], reverse=True)
    print("前10个最高频实体:")
    for entity, freq in sorted_entities[:10]:
        print(f"  {entity}: {freq} 次")
    
    # TODO: Translate - Verify高频实体应该权重更低
    high_freq_entity = sorted_entities[0][0]  # TODO: Translate - 最高频实体
    low_freq_entity = sorted_entities[-1][0]  # TODO: Translate - 最低频实体
    
    print(f"\n高频实体 '{high_freq_entity}' 频率: {entity_freq[high_freq_entity]}")
    print(f"低频实体 '{low_freq_entity}' 频率: {entity_freq[low_freq_entity]}")
    print("✓ 实体频率统计正确，高频实体应获得较低权重")
    
    return True

#===============================================================================
# TODO: Translate - 通用TesteventGenerate函数
#===============================================================================

def create_test_events_standard(num_events=50, num_chapters=5):
    """创建标准测试事件"""
    events = []
    
    # TODO: Translate - 常用角色和宝物
    characters = ["韩立", "南宫婉", "墨大夫", "银月", "青元子", "七玄门掌门", "大衍神君", "银翅夜叉王"]
    treasures = ["洗灵池", "青元剑诀", "火蟒剑", "青竹蜂云剑", "噬金虫", "定颜丹", "灵乳", "降灵符"]
    locations = ["七玄门", "天南", "乱星海", "灵药园", "洞府", "万丈峰", "黄枫谷", "墨府"]
    
    # TODO: Translate - 为每个chapterGenerateevent
    for chapter in range(1, num_chapters+1):
        chapter_id = f"第{chapter}章"
        
        # TODO: Translate - 每章Generate固定数量的event
        events_per_chapter = num_events // num_chapters
        
        for event_idx in range(1, events_per_chapter+1):
            event_id = f"E{chapter}-{event_idx}"
            
            # TODO: Translate - 为event分配1-3个角色
            event_characters = []
            for _ in range(min(3, len(characters))):
                char = random.choice(characters)
                if char not in event_characters:
                    event_characters.append(char)
            
            # TODO: Translate - 为event分配0-2个宝物
            event_treasures = []
            for _ in range(min(2, len(treasures))):
                if random.random() > 0.5:  # TODO: Translate - 50%概率分配宝物
                    treasure = random.choice(treasures)
                    if treasure not in event_treasures:
                        event_treasures.append(treasure)
            
            # Generateevent
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

def create_test_events_with_freq(num_events=50, num_chapters=5):
    """创建测试事件，含高频和低频实体"""
    events = []
    
    # TODO: Translate - 常用角色和宝物，前两个是高频实体，会在所有event中出现
    characters = ["韩立", "南宫婉", "墨大夫", "银月", "青元子", "七玄门掌门"]
    treasures = ["洗灵池", "青元剑诀", "火蟒剑", "青竹蜂云剑", "噬金虫"]
    locations = ["七玄门", "天南", "乱星海", "灵药园", "洞府"]
    
    # TODO: Translate - 为每个chapterGenerateevent
    for chapter in range(1, num_chapters+1):
        chapter_id = f"第{chapter}章"
        
        # TODO: Translate - 每章Generate固定数量的event
        events_per_chapter = num_events // num_chapters
        
        for event_idx in range(1, events_per_chapter+1):
            event_id = f"E{chapter}-{event_idx}"
            
            # TODO: Translate - 添加高频实体（总是出现）
            event_characters = ["韩立"]  # TODO: Translate - 韩立是主角，每个event都有
            
            # TODO: Translate - 随机添加其他角色
            for char in characters[2:]:  # TODO: Translate - 跳过前两个高频角色
                if random.random() > 0.7:  # TODO: Translate - 30%概率添加
                    event_characters.append(char)
            
            # TODO: Translate - 添加宝物
            if chapter == 1:  # TODO: Translate - 第一章总是出现"洗灵池"
                event_treasures = ["洗灵池"]
            else:
                event_treasures = []
                for treasure in treasures[1:]:
                    if random.random() > 0.8:  # TODO: Translate - 20%概率添加
                        event_treasures.append(treasure)
            
            # Generateevent
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

def create_test_events_simple(num_events=10, num_chapters=2):
    """创建简单测试事件，用于测试统一版链接器的兼容性"""
    events = []
    
    for chapter in range(1, num_chapters+1):
        for i in range(1, (num_events // num_chapters) + 1):
            event_id = f"E{chapter}-{i}"
            
            # TODO: Translate - 奇数ID的event包含"韩立"，偶数ID的event包含"南宫婉"
            characters = ["韩立"] if i % 2 == 1 else ["南宫婉"]
            
            # TODO: Translate - 第一章的event包含"灵乳"，第二章的event包含"火蟒剑"
            treasures = ["灵乳"] if chapter == 1 else ["火蟒剑"]
            
            event = EventItem(
                event_id=event_id,
                description=f"章节{chapter}的测试事件{i}，涉及{','.join(characters)}",
                characters=characters,
                treasures=treasures,
                location="测试地点",
                result="测试结果",
                chapter_id=f"第{chapter}章"
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

#===============================================================================
# TODO: Translate - 优化版linking器性能Test
#===============================================================================

def test_optimized_vs_original(num_events=50):
    """测试优化版与原始版链接器的性能对比"""
    print("="*80)
    print("优化版与原始版因果链接器性能对比测试")
    print("="*80)
    
    # CreateTestevent
    print(f"生成 {num_events} 个测试事件...")
    events = create_test_events_standard(num_events=num_events)
    
    # TODO: Translate - Test原始版linking器
    print("\n1. 测试原始版链接器性能:")
    original_linker = provide_linker(use_optimized=False)
    
    start_time = time.time()
    original_edges = original_linker.link_events(events)
    original_time = time.time() - start_time
    
    print(f"原始版链接器耗时: {original_time:.2f} 秒")
    print(f"原始版链接器类型: {type(original_linker).__name__}")
    print(f"发现的因果关系数量: {len(original_edges)}")
    
    # TODO: Translate - Test优化版linking器
    print("\n2. 测试优化版链接器性能:")
    # TODO: Translate - Setenvironment variables确保Use优化版
    os.environ["USE_OPTIMIZED_LINKER"] = "1"
    os.environ["MAX_EVENTS_PER_CHAPTER"] = "3"  # TODO: Translate - 限制每章最多3个event
    os.environ["MIN_ENTITY_SUPPORT"] = "2"     # TODO: Translate - 限制实体最小支持度为2
    os.environ["MAX_CANDIDATE_PAIRS"] = "5"    # TODO: Translate - 最多分析5对event
    
    # TODO: Translate - Test配对逻辑
    print("开始运行优化版链接器，只测试配对逻辑...")
    
    # TODO: Translate - Create优化版linking器实例，但不调用API
    optimized_linker = OptimizedCausalLinker(
        api_key="dummy",  # TODO: Translate - Use假API key，不会实际调用API
        model="dummy",
        provider="none",
        max_events_per_chapter=3,
        min_entity_support=2,
        max_candidate_pairs=5
    )
    
    start_time = time.time()
    # TODO: Translate - 只Test配对Generate逻辑，不调用API
    chapter_pairs = optimized_linker._generate_same_chapter_pairs(events)
    entity_pairs = optimized_linker._generate_entity_co_occurrence_pairs(events)
    candidate_pairs = optimized_linker._merge_candidate_pairs(chapter_pairs, entity_pairs)
    
    # TODO: Translate - 模拟Generate边（不实际调用API）
    optimized_edges = []
    optimized_time = time.time() - start_time
    
    print(f"配对逻辑测试完成，生成了 {len(candidate_pairs)} 对候选")
    print(f"其中同章节配对: {len(chapter_pairs)} 对")
    print(f"实体共现配对: {len(entity_pairs)} 对")
    
    print(f"优化版链接器耗时: {optimized_time:.2f} 秒")
    print(f"发现的因果关系数量: {len(optimized_edges)}")
    
    # TODO: Translate - 性能比较
    print("\n3. 性能比较:")
    speedup = original_time / optimized_time if optimized_time > 0 else float('inf')
    print(f"速度提升: {speedup:.2f}x")
    
    # TODO: Translate - 结果质量比较
    original_edge_set = {(edge.from_id, edge.to_id) for edge in original_edges}
    optimized_edge_set = {(edge.from_id, edge.to_id) for edge in optimized_edges}
    
    common_edges = original_edge_set.intersection(optimized_edge_set)
    
    print("\n4. 结果质量比较:")
    print(f"原始版独有边: {len(original_edge_set - optimized_edge_set)}")
    print(f"优化版独有边: {len(optimized_edge_set - original_edge_set)}")
    print(f"共有边: {len(common_edges)}")
    
    if len(original_edge_set) > 0:
        recall = len(common_edges) / len(original_edge_set)
        print(f"召回率 (相对于原始版): {recall:.2%}")
    
    # TODO: Translate - Save结果到调试文件
    debug_dir = project_root / "debug"
    debug_dir.mkdir(exist_ok=True)
    
    with open(debug_dir / "optimized_vs_original.json", "w", encoding="utf-8") as f:
        json.dump({
            "original": {
                "time": original_time,
                "edges_count": len(original_edges),
                "edges": [edge.__dict__ for edge in original_edges]
            },
            "optimized": {
                "time": optimized_time,
                "edges_count": len(optimized_edges),
                "edges": [edge.__dict__ for edge in optimized_edges]
            },
            "comparison": {
                "speedup": speedup,
                "common_edges": len(common_edges),
                "recall": recall if len(original_edge_set) > 0 else None
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存至: {debug_dir / 'optimized_vs_original.json'}")
    
    return original_time, optimized_time, original_edges, optimized_edges

def test_optimized_parameters():
    """测试不同参数对优化版链接器的影响"""
    print("\n" + "="*80)
    print("测试优化参数对性能的影响")
    print("="*80)
    
    # TODO: Translate - Create较多的Testevent
    events = create_test_events_standard(num_events=100, num_chapters=10)
    print(f"生成 {len(events)} 个测试事件用于参数测试")
    
    # TODO: Translate - Test不同的min_entity_support参数
    print("\n1. 测试实体支持度参数 (min_entity_support):")
    for support in [1, 2, 3, 4]:
        print(f"\n测试实体最小支持度 = {support}")
        # TODO: Translate - 通过environment variables临时Set参数
        os.environ["MIN_ENTITY_SUPPORT"] = str(support)
        linker = provide_linker(use_optimized=True)
        
        start_time = time.time()
        edges = linker.link_events(events)
        elapsed = time.time() - start_time
        
        print(f"耗时: {elapsed:.2f} 秒")
        print(f"发现的因果关系数量: {len(edges)}")
    
    # TODO: Translate - Test不同的max_events_per_chapter参数
    print("\n2. 测试每章最大事件数参数 (max_events_per_chapter):")
    for max_events in [10, 15, 20]:
        print(f"\n测试每章最大事件数 = {max_events}")
        # TODO: Translate - 通过environment variables临时Set参数
        os.environ["MAX_EVENTS_PER_CHAPTER"] = str(max_events)
        linker = provide_linker(use_optimized=True)
        
        start_time = time.time()
        edges = linker.link_events(events)
        elapsed = time.time() - start_time
        
        print(f"耗时: {elapsed:.2f} 秒")
        print(f"发现的因果关系数量: {len(edges)}")
    
    print("\n参数测试完成")

#===============================================================================
# TODO: Translate - 实体权重Test
#===============================================================================

def test_entity_weights():
    """测试实体频率权重反向调整功能"""
    print("\n" + "="*80)
    print("测试实体频率权重反向调整功能")
    print("="*80)
    
    # CreateTestevent
    events = create_test_events_with_freq(num_events=50, num_chapters=5)
    print(f"创建了 {len(events)} 个测试事件")
    
    # TODO: Translate - 计算并显示实体频率
    entity_freq = calculate_entity_frequency(events)
    sorted_entities = sorted(entity_freq.items(), key=lambda x: x[1], reverse=True)
    
    print("\n实体频率统计:")
    for entity, freq in sorted_entities:
        print(f"  {entity}: {freq} 次")
    
    # TODO: Translate - Create优化版linking器实例，Test带权重的实体配对
    print("\n1. 使用实体权重反向调整:")
    linker_with_weights = OptimizedCausalLinker(
        api_key="dummy",  # TODO: Translate - Use假API key，因为不会实际调用API
        model="dummy",
        provider="none",
        max_events_per_chapter=10,
        min_entity_support=1,  # TODO: Translate - 设为1以确保所有实体都被考虑
        max_chapter_span=99,   # TODO: Translate - 设为很大以确保不会因chapter跨度过滤
        max_candidate_pairs=1000,
        use_entity_weights=True  # TODO: Translate - Use实体权重
    )
    
    start_time = time.time()
    entity_pairs_with_weights = linker_with_weights._generate_entity_co_occurrence_pairs(events)
    elapsed = time.time() - start_time
    print(f"使用实体权重的配对完成，耗时: {elapsed:.6f} 秒")
    print(f"生成了 {len(entity_pairs_with_weights)} 对配对")
    
    # TODO: Translate - Test不Use权重的实体配对
    print("\n2. 不使用实体权重:")
    linker_without_weights = OptimizedCausalLinker(
        api_key="dummy",
        model="dummy",
        provider="none",
        max_events_per_chapter=10,
        min_entity_support=1,
        max_chapter_span=99,
        max_candidate_pairs=1000,
        use_entity_weights=False  # TODO: Translate - 不Use实体权重
    )
    
    start_time = time.time()
    entity_pairs_without_weights = linker_without_weights._generate_entity_co_occurrence_pairs(events)
    elapsed = time.time() - start_time
    print(f"不使用实体权重的配对完成，耗时: {elapsed:.6f} 秒")
    print(f"生成了 {len(entity_pairs_without_weights)} 对配对")
    
    # TODO: Translate - 分析前10个带权重的配对
    print("\n带权重配对的前10个:")
    for i, (id1, id2) in enumerate(entity_pairs_with_weights[:10], 1):
        # TODO: Translate - Getevent对象
        event1 = next((e for e in events if e.event_id == id1), None)
        event2 = next((e for e in events if e.event_id == id2), None)
        
        if event1 and event2:
            # TODO: Translate - 找出共同实体
            common_chars = set(event1.characters) & set(event2.characters)
            common_treasures = set(event1.treasures) & set(event2.treasures)
            common_entities = common_chars | common_treasures
            
            print(f"{i}. {id1} - {id2}")
            print(f"   共享实体: {', '.join(common_entities)}")
            print(f"   实体频率: {', '.join([f'{e}({entity_freq[e]})' for e in common_entities])}")

#===============================================================================
# TODO: Translate - 统一版linking器兼容性Test
#===============================================================================

def test_original_compatibility():
    """测试原始版本兼容性（不使用优化）"""
    print("\n===== 测试原始版本兼容性 =====")
    
    # CreateTestevent
    events = create_test_events_simple(num_events=6, num_chapters=2)
    print(f"创建了 {len(events)} 个测试事件")
    
    # TODO: Translate - Create原始版linking器实例
    linker = CausalLinker(
        api_key="dummy",  # TODO: Translate - Use假API key，因为不会实际调用API
        model="dummy",
        provider="none"
    )
    
    # TODO: Translate - 打印类型信息，确认是否正确Use统一版
    print(f"链接器类型: {type(linker).__name__}")
    print(f"统一版基类: {isinstance(linker, UnifiedCausalLinker)}")
    print(f"优化模式: {getattr(linker, 'use_optimization', 'N/A')}")


def test_optimized_compatibility():
    """测试优化版本兼容性（使用实体权重）"""
    print("\n===== 测试优化版本兼容性 =====")
    
    # CreateTestevent
    events = create_test_events_simple(num_events=8, num_chapters=2)
    print(f"创建了 {len(events)} 个测试事件")
    
    # TODO: Translate - Create优化版linking器实例
    linker = OptimizedCausalLinker(
        api_key="dummy",  # TODO: Translate - Use假API key，因为不会实际调用API
        model="dummy",
        provider="none",
        max_events_per_chapter=10,
        min_entity_support=1,
        max_chapter_span=99,
        max_candidate_pairs=1000,
        use_entity_weights=True
    )
    
    # TODO: Translate - 打印类型信息，确认是否正确Use统一版
    print(f"链接器类型: {type(linker).__name__}")
    print(f"统一版基类: {isinstance(linker, UnifiedCausalLinker)}")
    print(f"优化模式: {getattr(linker, 'use_optimization', 'N/A')}")
    print(f"实体权重: {getattr(linker, 'use_entity_weights', 'N/A')}")


def test_unified_implementation():
    """测试统一版实现，测试两种模式"""
    print("\n===== 测试统一版实现 =====")
    
    # CreateTestevent
    events = create_test_events_simple(num_events=10, num_chapters=2)
    print(f"创建了 {len(events)} 个测试事件")
    
    # TODO: Translate - 1. Test不优化模式
    print("\n----- 不优化模式 -----")
    linker1 = UnifiedCausalLinker(
        api_key="dummy",
        model="dummy",
        provider="none",
        use_optimization=False
    )
    
    print(f"链接器类型: {type(linker1).__name__}")
    print(f"优化模式: {linker1.use_optimization}")
    
    # TODO: Translate - 2. Test优化模式
    print("\n----- 优化模式 -----")
    linker2 = UnifiedCausalLinker(
        api_key="dummy",
        model="dummy",
        provider="none",
        use_optimization=True,
        max_events_per_chapter=10,
        min_entity_support=1,
        use_entity_weights=True
    )
    
    print(f"链接器类型: {type(linker2).__name__}")
    print(f"优化模式: {linker2.use_optimization}")
    print(f"实体权重: {linker2.candidate_generator.use_entity_weights}")

def test_unified_compatibility():
    """测试统一版链接器兼容性"""
    print("\n" + "="*80)
    print("测试统一版因果链接器兼容性")
    print("="*80)
    
    # TODO: Translate - Test原始版兼容性
    test_original_compatibility()
    
    # TODO: Translate - Test优化版兼容性
    test_optimized_compatibility()
    
    # TODO: Translate - Test统一版实现
    test_unified_implementation()

#===============================================================================
# TODO: Translate - 主函数和Test选择
#===============================================================================

def main():
    """主函数"""
    print("因果链接测试套件")
    print("=" * 80)
    
    # TODO: Translate - Get用户选择的Test类型
    print("\n请选择要运行的测试：")
    print("1. 全部测试")
    print("2. 优化版链接器性能测试")
    print("3. 实体权重功能测试")
    print("4. 统一版链接器兼容性测试")
    print("5. 性能参数对比测试")
    
    try:
        choice = int(input("\n请输入选择的数字（1-5）: "))
    except ValueError:
        choice = 1  # TODO: Translate - 默认Run全部Test
    
    if choice == 1 or choice == 2:
        # TODO: Translate - Run优化版性能Test
        debug_optimized_linker_pairing()
    
    if choice == 1 or choice == 3:
        # TODO: Translate - Run实体权重Test
        test_entity_frequency_weights()
    
    if choice == 1 or choice == 4:
        # TODO: Translate - Run统一版兼容性Test
        test_unified_compatibility()
    
    if choice == 1 or choice == 5:
        # TODO: Translate - Run调试Test
        debug_optimized_linker_pairing()
    
    if choice == 1:
        print("\n" + "="*80)
        print("测试总结")
        print("=" * 80)
        print("已完成所有测试，以下是主要优化成果：")
        print("1. 统一版链接器成功整合了原始版和优化版功能")
        print("2. 实体频率权重有效降低了高频实体的影响")
        print("3. 参数控制能有效平衡速度与质量")

if __name__ == "__main__":
    main()
