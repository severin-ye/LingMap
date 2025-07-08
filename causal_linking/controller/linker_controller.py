import argparse
import os
import json
from typing import List, Tuple

from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from common.utils.json_loader import JsonLoader
from causal_linking.di.provider import provide_linker


def link_events(events_path: str, output_path: str) -> Tuple[List[EventItem], List[CausalEdge]]:
    """
    # [CN] 分析事件之间的因果关系并构建DAG
    # [EN] Analyze causal relationships between events and build DAG
    
    Args:
        # [CN] events_path: 事件JSON文件路径
        # [EN] events_path: Path to the events JSON file
        # [CN] output_path: 输出因果关系JSON文件路径
        # [EN] output_path: Path to the output causal relationships JSON file
        
    Returns:
        # [CN] 事件列表和因果边列表的元组
        # [EN] Tuple of events list and causal edges list
    """
    # [CN] 加载事件
    # [EN] Load events
    with open(events_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)
        
    events = [EventItem.from_dict(event_data) for event_data in events_data]
    
    # [CN] 获取链接器
    # [EN] Get linker
    linker = provide_linker()
    
    # [CN] 识别因果关系
    # [EN] Identify causal relationships
    print(f"# [CN] 分析 {len(events)} 个事件之间的因果关系...")
    print(f"# [EN] Analyzing causal relationships between {len(events)} events...")
    edges = linker.link_events(events)
    print(f"# [CN] 发现 {len(edges)} 个因果关系")
    print(f"# [EN] Found {len(edges)} causal relationships")
    
    # [CN] 构建DAG
    # [EN] Build DAG
    print("# [CN] 构建有向无环图（DAG）...")
    print("# [EN] Building directed acyclic graph (DAG)...")
    events, dag_edges = linker.build_dag(events, edges)
    print(f"# [CN] DAG构建完成，保留 {len(dag_edges)} 条边")
    print(f"# [EN] DAG construction completed, retained {len(dag_edges)} edges")
    
    # [CN] 保存结果
    # [EN] Save results
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # [CN] 构建输出数据
    # [EN] Build output data
    output_data = {
        "nodes": [event.to_dict() for event in events],
        "edges": [edge.to_dict() for edge in dag_edges]
    }
    
    JsonLoader.save_json(output_data, output_path)
    print(f"# [CN] 因果关系已保存到: {output_path}")
    print(f"# [EN] Causal relationships saved to: {output_path}")
    
    return events, dag_edges


def main():
    """
    # [CN] CAUSAL_LINKING 模块执行入口
    # [EN] CAUSAL_LINKING module execution entry point
    """
    parser = argparse.ArgumentParser(description="# [CN] 分析事件之间的因果关系 # [EN] Analyze causal relationships between events")
    parser.add_argument("--input", "-i", required=True, help="# [CN] 输入事件JSON文件 # [EN] Input events JSON file")
    parser.add_argument("--output", "-o", required=True, help="# [CN] 输出因果关系JSON文件 # [EN] Output causal relationships JSON file")
    
    args = parser.parse_args()
    
    link_events(args.input, args.output)


if __name__ == "__main__":
    main()
