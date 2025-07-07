import argparse
import json
import os
import logging
from typing import Dict, Any, List, Set

from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from common.utils.enhanced_logger import EnhancedLogger
from common.utils.unified_id_processor import UnifiedIdProcessor
from graph_builder.service.mermaid_renderer import MermaidRenderer


def render_graph(input_path: str, output_path: str, options: Dict[str, Any] = {}) -> str:
    """
    将因果关系渲染为Mermaid图谱
    
    Args:
        input_path: 因果关系JSON文件路径
        output_path: Output Mermaid file path
        options: Rendering options
        
    Returns:
        Mermaid格式的图谱字符串
    """
    # TODO: Translate - Create日志记录器
    logger = EnhancedLogger("graph_controller", log_level="INFO")
    
    # TODO: Translate - Load数据
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # TODO: Translate - 解析数据
    events = [EventItem.from_dict(node_data) for node_data in data.get("nodes", [])]
    edges = [CausalEdge.from_dict(edge_data) for edge_data in data.get("edges", [])]
    
    print(f"加载了 {len(events)} 个事件和 {len(edges)} 条因果边")
    
    # TODO: Translate - Check是否有重复ID
    duplicate_ids = _check_duplicate_ids(events)
    if duplicate_ids:
        logger.error(f"严重错误：检测到重复的事件ID: {len(duplicate_ids)}个。上游的ID处理器未正确工作。")
        for dup_id in duplicate_ids:
            count = sum(1 for e in events if e.event_id == dup_id)
            logger.error(f"重复ID '{dup_id}' 出现了 {count} 次")
        
        # TODO: Translate - 由于上游应该已经ProcessID唯一性，这里发现重复很可能是流程Error
        # TODO: Translate - 但为了保证图谱能正常Generate，仍进行一次应急Process
        logger.warning("执行应急ID处理以保证图谱生成，但这不应成为常规流程")
        unique_events, updated_edges = UnifiedIdProcessor.ensure_unique_node_ids(events, edges)
        logger.info(f"应急处理后：{len(unique_events)} 个唯一事件和 {len(updated_edges)} 条更新边")
    else:
        logger.info("ID检查通过：所有事件ID均唯一，上游ID处理器工作正常")
        unique_events, updated_edges = events, edges
    
    # TODO: Translate - Create渲染器
    renderer = MermaidRenderer()
    
    # TODO: Translate - 渲染图谱
    mermaid_text = renderer.render(unique_events, updated_edges, options)
    
    # TODO: Translate - Save结果
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(mermaid_text)
    
    print(f"Mermaid图谱已保存到: {output_path}")
    return mermaid_text


def _check_duplicate_ids(events: List[EventItem]) -> Set[str]:
    """
    检查事件列表中是否存在重复ID
    
    Args:
        events: 事件列表
    
    Returns:
        重复ID的集合
    """
    id_set = set()
    duplicate_ids = set()
    
    for event in events:
        if event.event_id in id_set:
            duplicate_ids.add(event.event_id)
        else:
            id_set.add(event.event_id)
            
    return duplicate_ids


def main():
    """GRAPH_BUILDER 模块执行入口"""
    parser = argparse.ArgumentParser(description="Generate causal graph")
    parser.add_argument("--input", "-i", required=True, help="Input causal relationship JSON file")
    parser.add_argument("--output", "-o", required=True, help="Output Mermaid file path")
    parser.add_argument("--show-legend", action="store_true", help="Show legend")
    parser.add_argument("--show-labels", action="store_true", help="Show labels on edges")
    
    args = parser.parse_args()
    
    # TODO: Translate - Rendering options
    options = {
        "show_legend": args.show_legend,
        "show_edge_labels": args.show_labels,
        "custom_edge_style": True
    }
    
    render_graph(args.input, args.output, options)


if __name__ == "__main__":
    main()
