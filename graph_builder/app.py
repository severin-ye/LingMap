import argparse
import os
import sys

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_builder.controller.graph_controller import render_graph


def main():
    """Main entry point for GRAPH_BUILDER module"""
    parser = argparse.ArgumentParser(description="Generate causal graph")
    parser.add_argument("--input", "-i", required=True, help="Input causal relationship JSON file")
    parser.add_argument("--output", "-o", required=True, help="Output Mermaid file path")
    parser.add_argument("--show-legend", action="store_true", help="Show legend")
    parser.add_argument("--show-labels", action="store_true", help="Show labels on edges")
    
    args = parser.parse_args()
    
    # Rendering options
    options = {
        "show_legend": args.show_legend,
        "show_edge_labels": args.show_labels,
        "custom_edge_style": True
    }
    
    render_graph(args.input, args.output, options)


if __name__ == "__main__":
    main()
