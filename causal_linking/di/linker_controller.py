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
    Analyze causal relationships between events and build a DAG
    
    Args:
        events_path: Path to the event JSON file
        output_path: Path to the output causal relationship JSON file
        
    Returns:
        Tuple containing the list of events and the list of causal edges
    """
    # Load events
    with open(events_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)
        
    events = [EventItem.from_dict(event_data) for event_data in events_data]
    
    # Get linker
    linker = provide_linker()
    
    # Identify causal relationships
    print(f"Analyzing causal relationships between {len(events)} events...")
    edges = linker.link_events(events)
    print(f"Found {len(edges)} causal relationships")
    
    # Build DAG
    print("Building Directed Acyclic Graph (DAG)...")
    events, dag_edges = linker.build_dag(events, edges)
    print(f"DAG built, {len(dag_edges)} edges retained")
    
    # Save results
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Build output data
    output_data = {
        "nodes": [event.to_dict() for event in events],
        "edges": [edge.to_dict() for edge in dag_edges]
    }
    
    JsonLoader.save_json(output_data, output_path)
    print(f"Causal relationships saved to: {output_path}")
    
    return events, dag_edges


def main():
    """CAUSAL_LINKING module entry point"""
    parser = argparse.ArgumentParser(description="Analyze causal relationships between events")
    parser.add_argument("--input", "-i", required=True, help="Input event JSON file")
    parser.add_argument("--output", "-o", required=True, help="Output causal relationship JSON file")
    
    args = parser.parse_args()
    
    link_events(args.input, args.output)


if __name__ == "__main__":
    main()
