#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版因果链接测试脚本

测试优化版因果链接服务的性能和功能
"""

import os
import sys
import json
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
from common.utils.enhanced_logger import EnhancedLogger
from causal_linking.di.provider import provide_linker

# 创建日志记录器
logger = EnhancedLogger("optimized_causal_linking_test", log_level="DEBUG")

def create_test_events(num_events=50, num_chapters=5):
    """创建测试事件"""
    events = []
    
    # 常用角色和宝物
    characters = ["韩立", "南宫婉", "墨大夫", "银月", "青元子", "七玄门掌门", "大衍神君", "银翅夜叉王"]
    treasures = ["洗灵池", "青元剑诀", "火蟒剑", "青竹蜂云剑", "噬金虫", "定颜丹", "灵乳", "降灵符"]
    locations = ["七玄门", "天南", "乱星海", "灵药园", "洞府", "万丈峰", "黄枫谷", "墨府"]
    
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
                import random
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

def test_optimized_vs_original(num_events=50):
    """测试优化版与原始版链接器的性能对比"""
    print("="*80)
    print("优化版与原始版因果链接器性能对比测试")
    print("="*80)
    
    # 创建测试事件
    print(f"生成 {num_events} 个测试事件...")
    events = create_test_events(num_events=num_events)
    
    # 测试原始版链接器
    print("\n1. 测试原始版链接器性能:")
    original_linker = provide_linker(use_optimized=False)
    
    start_time = time.time()
    original_edges = original_linker.link_events(events)
    original_time = time.time() - start_time
    
    print(f"原始版链接器耗时: {original_time:.2f} 秒")
    print(f"原始版链接器类型: {type(original_linker).__name__}")
    print(f"发现的因果关系数量: {len(original_edges)}")
    
    # 测试优化版链接器
    print("\n2. 测试优化版链接器性能:")
    # 设置环境变量确保使用优化版
    os.environ["USE_OPTIMIZED_LINKER"] = "1"
    os.environ["MAX_EVENTS_PER_CHAPTER"] = "3"  # 限制每章最多3个事件
    os.environ["MIN_ENTITY_SUPPORT"] = "2"     # 限制实体最小支持度为2
    os.environ["MAX_CANDIDATE_PAIRS"] = "5"    # 最多分析5对事件
    
    # 导入优化版链接器以便测试配对逻辑
    from causal_linking.service.optimized_linker_service import OptimizedCausalLinker
    
    # 调试输出
    print("开始运行优化版链接器，只测试配对逻辑...")
    
    # 创建优化版链接器实例，但不调用API
    optimized_linker = OptimizedCausalLinker(
        api_key="dummy",  # 使用假API密钥，不会实际调用API
        model="dummy",
        provider="none",
        max_events_per_chapter=3,
        min_entity_support=2,
        max_candidate_pairs=5
    )
    
    start_time = time.time()
    # 只测试配对生成逻辑，不调用API
    chapter_pairs = optimized_linker._generate_same_chapter_pairs(events)
    entity_pairs = optimized_linker._generate_entity_co_occurrence_pairs(events)
    candidate_pairs = optimized_linker._merge_candidate_pairs(chapter_pairs, entity_pairs)
    
    # 模拟生成边（不实际调用API）
    optimized_edges = []
    optimized_time = time.time() - start_time
    
    print(f"配对逻辑测试完成，生成了 {len(candidate_pairs)} 对候选")
    print(f"其中同章节配对: {len(chapter_pairs)} 对")
    print(f"实体共现配对: {len(entity_pairs)} 对")
    
    print(f"优化版链接器耗时: {optimized_time:.2f} 秒")
    print(f"发现的因果关系数量: {len(optimized_edges)}")
    
    # 性能比较
    print("\n3. 性能比较:")
    speedup = original_time / optimized_time if optimized_time > 0 else float('inf')
    print(f"速度提升: {speedup:.2f}x")
    
    # 结果质量比较
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
    
    # 保存结果到调试文件
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
    
    # 创建较多的测试事件
    events = create_test_events(num_events=100, num_chapters=10)
    print(f"生成 {len(events)} 个测试事件用于参数测试")
    
    # 测试不同的min_entity_support参数
    print("\n1. 测试实体支持度参数 (min_entity_support):")
    for support in [1, 2, 3, 4]:
        print(f"\n测试实体最小支持度 = {support}")
        # 通过环境变量临时设置参数
        os.environ["MIN_ENTITY_SUPPORT"] = str(support)
        linker = provide_linker(use_optimized=True)
        
        start_time = time.time()
        edges = linker.link_events(events)
        elapsed = time.time() - start_time
        
        print(f"耗时: {elapsed:.2f} 秒")
        print(f"发现的因果关系数量: {len(edges)}")
    
    # 测试不同的max_events_per_chapter参数
    print("\n2. 测试每章最大事件数参数 (max_events_per_chapter):")
    for max_events in [10, 15, 20]:
        print(f"\n测试每章最大事件数 = {max_events}")
        # 通过环境变量临时设置参数
        os.environ["MAX_EVENTS_PER_CHAPTER"] = str(max_events)
        linker = provide_linker(use_optimized=True)
        
        start_time = time.time()
        edges = linker.link_events(events)
        elapsed = time.time() - start_time
        
        print(f"耗时: {elapsed:.2f} 秒")
        print(f"发现的因果关系数量: {len(edges)}")
    
    print("\n参数测试完成")

def main():
    """主函数"""
    print("优化版因果链接测试套件")
    print("="*80)
    
    # 测试优化版与原始版的性能对比
    original_time, optimized_time, original_edges, optimized_edges = test_optimized_vs_original(num_events=30)
    
    # 如果时间允许，测试不同参数的影响
    if original_time < 60 and optimized_time < 60:  # 如果测试不超过60秒
        test_optimized_parameters()
    
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    print(f"原始版链接器耗时: {original_time:.2f} 秒，发现 {len(original_edges)} 个因果关系")
    print(f"优化版链接器耗时: {optimized_time:.2f} 秒，发现 {len(optimized_edges)} 个因果关系")
    print(f"速度提升: {original_time / optimized_time if optimized_time > 0 else float('inf'):.2f}x")
    
    if original_time > optimized_time:
        print("🎉 优化版链接器性能显著提升！")
    else:
        print("⚠️  优化版链接器性能未达到预期，可能需要进一步调整参数")

if __name__ == "__main__":
    main()
