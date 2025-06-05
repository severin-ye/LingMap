import argparse
import os
import sys

# 将项目根目录添加到路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_builder.controller.graph_controller import render_graph


def main():
    """GRAPH_BUILDER 模块的主入口"""
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
