#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码冗余优化示例脚本

演示如何使用新的统一工具模块，替代原有的重复代码。
"""

import os
import sys
import argparse
from pathlib import Path

# TODO: Translate - Add project root directory to系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# TODO: Translate - Import新的统一IDProcess器
from common.utils.unified_id_processor import UnifiedIdProcessor
# TODO: Translate - Importevent和causal边model
from common.models.event import EventItem
from common.models.causal_edge import CausalEdge


def generate_test_data():
    """生成测试数据"""
    # TODO: Translate - Create一些Testevent
    events = [
        EventItem(
            event_id="E01-01",
            description="事件1",
            characters=["角色A", "角色B"],
            treasures=[],
            result="结果1",
            location="位置1",
            time="时间1",
            chapter_id="1"
        ),
        EventItem(
            event_id="E01-01",  # TODO: Translate - 重复ID
            description="事件2",
            characters=["角色C"],
            treasures=[],
            result="结果2",
            location="位置2",
            time="时间2",
            chapter_id="1"
        ),
        EventItem(
            event_id="E01-03",
            description="事件3",
            characters=["角色D"],
            treasures=[],
            result="结果3",
            location="位置3",
            time="时间3",
            chapter_id="1"
        )
    ]
    
    # TODO: Translate - Create一些Test边
    edges = [
        CausalEdge(
            from_id="E01-01",
            to_id="E01-03",
            strength=0.8,
            reason="原因1"
        )
    ]
    
    return events, edges


def demo_id_processing():
    """演示ID处理功能"""
    print("=== 演示统一ID处理器功能 ===\n")
    
    # TODO: Translate - GenerateTest数据
    events, edges = generate_test_data()
    
    # TODO: Translate - 显示原始数据
    print("原始事件数据:")
    for event in events:
        print(f"  ID: {event.event_id}, 描述: {event.description}")
    
    print("\n原始边数据:")
    for edge in edges:
        print(f"  {edge.from_id} -> {edge.to_id} (强度: {edge.strength})")
    
    # TODO: Translate - 演示1: 确保eventID唯一性
    print("\n1. 确保事件ID唯一性:")
    unique_events = UnifiedIdProcessor.ensure_unique_event_ids(events)
    for event in unique_events:
        print(f"  ID: {event.event_id}, 描述: {event.description}")
    
    # TODO: Translate - 演示2: 确保节点ID唯一性并更新边
    print("\n2. 确保节点ID唯一性并更新边:")
    node_events, node_edges = UnifiedIdProcessor.ensure_unique_node_ids(events, edges)
    
    print("  处理后的事件:")
    for event in node_events:
        print(f"    ID: {event.event_id}, 描述: {event.description}")
    
    print("\n  处理后的边:")
    for edge in node_edges:
        print(f"    {edge.from_id} -> {edge.to_id} (强度: {edge.strength})")
    
    # TODO: Translate - 演示3: 标准化eventID
    print("\n3. 标准化事件ID:")
    
    test_ids = [
        ("", "第一章", 5),
        ("第二章-7", "第二章", 7),
        ("E03-09", "第三章", 9),
        ("第四章事件8", "第四章", 8)
    ]
    
    for original_id, chapter_id, index in test_ids:
        normalized_id = UnifiedIdProcessor.normalize_event_id(original_id, chapter_id, index)
        print(f"  原始ID: '{original_id}', 章节: '{chapter_id}', 索引: {index} => 标准化ID: '{normalized_id}'")
    
    # TODO: Translate - 演示4: SaveTest文件
    print("\n4. 保存和修复测试文件:")
    
    # TODO: Translate - Create临时目录
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # TODO: Translate - Save带有重复ID的event
    import json
    event_file = temp_dir / "duplicate_events_test.json"
    with open(event_file, 'w', encoding='utf-8') as f:
        # TODO: Translate - 将event转换为字典
        event_dicts = [event.__dict__ for event in events]
        json.dump(event_dicts, f, ensure_ascii=False, indent=2)
    
    print(f"  保存了测试文件: {event_file}")
    
    # TODO: Translate - Use统一IDProcess器refine文件
    fixed_file = temp_dir / "fixed_events_test.json"
    UnifiedIdProcessor.fix_duplicate_event_ids(str(event_file), str(fixed_file))
    
    print(f"  修复后的文件: {fixed_file}")
    
    # TODO: Translate - Read并显示refine后的文件
    try:
        with open(fixed_file, 'r', encoding='utf-8') as f:
            fixed_data = json.load(f)
            
        print("\n  修复后的事件数据:")
        for item in fixed_data:
            print(f"    ID: {item['event_id']}, 描述: {item['description']}")
    except Exception as e:
        print(f"  读取修复后的文件失败: {e}")


def main():
    """程序主入口"""
    parser = argparse.ArgumentParser(description="代码优化示例")
    parser.add_argument("--demo", choices=["id"], default="id", help="选择要运行的演示")
    args = parser.parse_args()
    
    if args.demo == "id":
        demo_id_processing()


if __name__ == "__main__":
    main()
