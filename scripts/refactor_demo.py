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

# 将项目根目录添加到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 导入新的统一ID处理器
from common.utils.unified_id_processor import UnifiedIdProcessor
# 导入事件和因果边模型
from common.models.event import EventItem
from common.models.causal_edge import CausalEdge


def generate_test_data():
    """生成测试数据"""
    # 创建一些测试事件
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
            event_id="E01-01",  # 重复ID
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
    
    # 创建一些测试边
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
    
    # 生成测试数据
    events, edges = generate_test_data()
    
    # 显示原始数据
    print("原始事件数据:")
    for event in events:
        print(f"  ID: {event.event_id}, 描述: {event.description}")
    
    print("\n原始边数据:")
    for edge in edges:
        print(f"  {edge.from_id} -> {edge.to_id} (强度: {edge.strength})")
    
    # 演示1: 确保事件ID唯一性
    print("\n1. 确保事件ID唯一性:")
    unique_events = UnifiedIdProcessor.ensure_unique_event_ids(events)
    for event in unique_events:
        print(f"  ID: {event.event_id}, 描述: {event.description}")
    
    # 演示2: 确保节点ID唯一性并更新边
    print("\n2. 确保节点ID唯一性并更新边:")
    node_events, node_edges = UnifiedIdProcessor.ensure_unique_node_ids(events, edges)
    
    print("  处理后的事件:")
    for event in node_events:
        print(f"    ID: {event.event_id}, 描述: {event.description}")
    
    print("\n  处理后的边:")
    for edge in node_edges:
        print(f"    {edge.from_id} -> {edge.to_id} (强度: {edge.strength})")
    
    # 演示3: 标准化事件ID
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
    
    # 演示4: 保存测试文件
    print("\n4. 保存和修复测试文件:")
    
    # 创建临时目录
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # 保存带有重复ID的事件
    import json
    event_file = temp_dir / "duplicate_events_test.json"
    with open(event_file, 'w', encoding='utf-8') as f:
        # 将事件转换为字典
        event_dicts = [event.__dict__ for event in events]
        json.dump(event_dicts, f, ensure_ascii=False, indent=2)
    
    print(f"  保存了测试文件: {event_file}")
    
    # 使用统一ID处理器修复文件
    fixed_file = temp_dir / "fixed_events_test.json"
    UnifiedIdProcessor.fix_duplicate_event_ids(str(event_file), str(fixed_file))
    
    print(f"  修复后的文件: {fixed_file}")
    
    # 读取并显示修复后的文件
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
