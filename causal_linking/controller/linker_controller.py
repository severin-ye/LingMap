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
    分析事件之间的因果关系并构建DAG
    
    Args:
        events_path: 事件JSON文件路径
        output_path: 输出因果关系JSON文件路径
        
    Returns:
        事件列表和因果边列表的元组
    """
    # 加载事件
    with open(events_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)
        
    events = [EventItem.from_dict(event_data) for event_data in events_data]
    
    # 获取链接器
    linker = provide_linker()
    
    # 识别因果关系
    print(f"分析 {len(events)} 个事件之间的因果关系...")
    edges = linker.link_events(events)
    print(f"发现 {len(edges)} 个因果关系")
    
    # 构建DAG
    print("构建有向无环图（DAG）...")
    events, dag_edges = linker.build_dag(events, edges)
    print(f"DAG构建完成，保留 {len(dag_edges)} 条边")
    
    # 保存结果
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 构建输出数据
    output_data = {
        "nodes": [event.to_dict() for event in events],
        "edges": [edge.to_dict() for edge in dag_edges]
    }
    
    JsonLoader.save_json(output_data, output_path)
    print(f"因果关系已保存到: {output_path}")
    
    return events, dag_edges


def main():
    """CAUSAL_LINKING 模块执行入口"""
    parser = argparse.ArgumentParser(description="分析事件之间的因果关系")
    parser.add_argument("--input", "-i", required=True, help="输入事件JSON文件")
    parser.add_argument("--output", "-o", required=True, help="输出因果关系JSON文件")
    
    args = parser.parse_args()
    
    link_events(args.input, args.output)


if __name__ == "__main__":
    main()
