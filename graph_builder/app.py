import argparse
import os
import sys

# [CN] 将项目根目录添加到路径中
# [EN] Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_builder.controller.graph_controller import render_graph


def main():
    """
    # [CN] GRAPH_BUILDER 模块的主入口
    # [EN] Main entry point for GRAPH_BUILDER module
    """
    parser = argparse.ArgumentParser(description="# [CN] 生成因果图谱 # [EN] Generate causal graph")
    parser.add_argument("--input", "-i", required=True, help="# [CN] 输入因果关系JSON文件 # [EN] Input causal relationships JSON file")
    parser.add_argument("--output", "-o", required=True, help="# [CN] 输出Mermaid文件路径 # [EN] Output Mermaid file path")
    parser.add_argument("--show-legend", action="store_true", help="# [CN] 显示图例 # [EN] Show legend")
    parser.add_argument("--show-labels", action="store_true", help="# [CN] 在边上显示标签 # [EN] Show labels on edges")
    
    args = parser.parse_args()
    
    # [CN] 渲染选项
    # [EN] Render options
    options = {
        "show_legend": args.show_legend,
        "show_edge_labels": args.show_labels,
        "custom_edge_style": True
    }
    
    render_graph(args.input, args.output, options)


if __name__ == "__main__":
    main()
