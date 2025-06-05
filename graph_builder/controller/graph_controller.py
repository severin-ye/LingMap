import argparse
import json
import os
from typing import Dict, Any

from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from graph_builder.service.mermaid_renderer import MermaidRenderer


def render_graph(input_path: str, output_path: str, options: Dict[str, Any] = None) -> str:
    """
    将因果关系渲染为Mermaid图谱
    
    Args:
        input_path: 因果关系JSON文件路径
        output_path: 输出Mermaid文件路径
        options: 渲染选项
        
    Returns:
        Mermaid格式的图谱字符串
    """
    # 加载数据
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 解析数据
    events = [EventItem.from_dict(node_data) for node_data in data.get("nodes", [])]
    edges = [CausalEdge.from_dict(edge_data) for edge_data in data.get("edges", [])]
    
    print(f"加载了 {len(events)} 个事件和 {len(edges)} 条因果边")
    
    # 创建渲染器
    renderer = MermaidRenderer()
    
    # 渲染图谱
    mermaid_text = renderer.render(events, edges, options)
    
    # 保存结果
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(mermaid_text)
    
    print(f"Mermaid图谱已保存到: {output_path}")
    return mermaid_text


def main():
    """GRAPH_BUILDER 模块执行入口"""
    parser = argparse.ArgumentParser(description="生成因果图谱")
    parser.add_argument("--input", "-i", required=True, help="输入因果关系JSON文件")
    parser.add_argument("--output", "-o", required=True, help="输出Mermaid文件路径")
    parser.add_argument("--show-legend", action="store_true", help="显示图例")
    parser.add_argument("--show-labels", action="store_true", help="在边上显示标签")
    
    args = parser.parse_args()
    
    # 渲染选项
    options = {
        "show_legend": args.show_legend,
        "show_edge_labels": args.show_labels,
        "custom_edge_style": True
    }
    
    render_graph(args.input, args.output, options)


if __name__ == "__main__":
    main()
