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
    Render causal relationships as Mermaid graph
    
    Args:
        input_path: Causal relationship JSON file path
        output_path: Output Mermaid file path
        options: Rendering options
        
    Returns:
        Mermaid format graph string
    """
    # Create logger
    logger = EnhancedLogger("graph_controller", log_level="INFO")
    
    # Load data
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Parse data
    events = [EventItem.from_dict(node_data) for node_data in data.get("nodes", [])]
    edges = [CausalEdge.from_dict(edge_data) for edge_data in data.get("edges", [])]
    
    print(f"Loaded {len(events)} events and {len(edges)} causal edges")
    
    # Check for duplicate IDs
    duplicate_ids = _check_duplicate_ids(events)
    if duplicate_ids:
        logger.error(f"Critical error: Detected duplicate event IDs: {len(duplicate_ids)} duplicates. Upstream ID processor not working correctly.")
        for dup_id in duplicate_ids:
            count = sum(1 for e in events if e.event_id == dup_id)
            logger.error(f"Duplicate ID '{dup_id}' appears {count} times")
        
        # Since upstream should have already processed ID uniqueness, finding duplicates here is likely a process error
        # But to ensure the graph can be generated normally, still perform emergency processing
        logger.warning("Performing emergency ID processing to ensure graph generation, but this should not be a regular process")
        unique_events, updated_edges = UnifiedIdProcessor.ensure_unique_node_ids(events, edges)
        logger.info(f"After emergency processing: {len(unique_events)} unique events and {len(updated_edges)} updated edges")
    else:
        logger.info("ID check passed: All event IDs are unique, upstream ID processor working correctly")
        unique_events, updated_edges = events, edges
    
    # Create renderer
    renderer = MermaidRenderer()
    
    # Render graph
    mermaid_text = renderer.render(unique_events, updated_edges, options)
    
    # Save results
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(mermaid_text)
    
    print(f"Mermaid graph saved to: {output_path}")
    return mermaid_text


def _check_duplicate_ids(events: List[EventItem]) -> Set[str]:
    """
    Check if there are duplicate IDs in the event list
    
    Args:
        events: Event list
    
    Returns:
        Set of duplicate IDs
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
    """GRAPH_BUILDER module execution entry point"""
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
