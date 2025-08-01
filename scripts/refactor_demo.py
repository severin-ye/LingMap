#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code redundancy optimization demo script

Demonstrates how to use the new unified tool modules to replace redundant code.
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root directory to system path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Import the new unified ID processor
from common.utils.unified_id_processor import UnifiedIdProcessor
# Import event and causal edge models
from common.models.event import EventItem
from common.models.causal_edge import CausalEdge


def generate_test_data():
    """Generate test data"""
    # Create some test events
    events = [
        EventItem(
            event_id="E01-01",
            description="Event 1",
            characters=["Character A", "Character B"],
            treasures=[],
            result="Result 1",
            location="Location 1",
            time="Time 1",
            chapter_id="1"
        ),
        EventItem(
            event_id="E01-01",  # Duplicate ID
            description="Event 2",
            characters=["Character C"],
            treasures=[],
            result="Result 2",
            location="Location 2",
            time="Time 2",
            chapter_id="1"
        ),
        EventItem(
            event_id="E01-03",
            description="Event 3",
            characters=["Character D"],
            treasures=[],
            result="Result 3",
            location="Location 3",
            time="Time 3",
            chapter_id="1"
        )
    ]
    
    # Create some test edges
    edges = [
        CausalEdge(
            from_id="E01-01",
            to_id="E01-03",
            strength=0.8,
            reason="Reason 1"
        )
    ]
    
    return events, edges


def demo_id_processing():
    """Demonstrate ID processing functionality"""
    print("=== Demonstrating unified ID processor functionality ===\n")
    
    # Generate test data
    events, edges = generate_test_data()
    
    # Display original data
    print("Original event data:")
    for event in events:
        print(f"  ID: {event.event_id}, Description: {event.description}")
    
    print("\nOriginal edge data:")
    for edge in edges:
        print(f"  {edge.from_id} -> {edge.to_id} (Strength: {edge.strength})")
    
    # Demo 1: Ensure event ID uniqueness
    print("\n1. Ensure event ID uniqueness:")
    unique_events = UnifiedIdProcessor.ensure_unique_event_ids(events)
    for event in unique_events:
        print(f"  ID: {event.event_id}, Description: {event.description}")
    
    # Demo 2: Ensure node ID uniqueness and update edges
    print("\n2. Ensure node ID uniqueness and update edges:")
    node_events, node_edges = UnifiedIdProcessor.ensure_unique_node_ids(events, edges)
    
    print("  Processed events:")
    for event in node_events:
        print(f"    ID: {event.event_id}, Description: {event.description}")
    
    print("\n  Processed edges:")
    for edge in node_edges:
        print(f"    {edge.from_id} -> {edge.to_id} (Strength: {edge.strength})")
    
    # Demo 3: Standardize event IDs
    print("\n3. Standardize event IDs:")
    
    test_ids = [
        ("", "Chapter 1", 5),
        ("Chapter 2-7", "Chapter 2", 7),
        ("E03-09", "Chapter 3", 9),
        ("Chapter 4 Event 8", "Chapter 4", 8)
    ]
    
    for original_id, chapter_id, index in test_ids:
        normalized_id = UnifiedIdProcessor.normalize_event_id(original_id, chapter_id, index)
        print(f"  Original ID: '{original_id}', Chapter: '{chapter_id}', Index: {index} => Normalized ID: '{normalized_id}'")
    
    # Demo 4: Save test file
    print("\n4. Save and fix test file:")
    
    # Create temporary directory
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Save events with duplicate IDs
    import json
    event_file = temp_dir / "duplicate_events_test.json"
    with open(event_file, 'w', encoding='utf-8') as f:
        # Convert events to dictionaries
        event_dicts = [event.__dict__ for event in events]
        json.dump(event_dicts, f, ensure_ascii=False, indent=2)
    
    print(f"  Saved test file: {event_file}")
    
    # Use unified ID processor to fix file
    fixed_file = temp_dir / "fixed_events_test.json"
    UnifiedIdProcessor.fix_duplicate_event_ids(str(event_file), str(fixed_file))
    
    print(f"  Fixed file: {fixed_file}")
    
    # Read and display fixed file
    try:
        with open(fixed_file, 'r', encoding='utf-8') as f:
            fixed_data = json.load(f)
            
        print("\n  Fixed event data:")
        for item in fixed_data:
            print(f"    ID: {item['event_id']}, Description: {item['description']}")
    except Exception as e:
        print(f"  Failed to read fixed file: {e}")


def main():
    """Program main entry point"""
    parser = argparse.ArgumentParser(description="Code optimization demo")
    parser.add_argument("--demo", choices=["id"], default="id", help="Select demo to run")
    args = parser.parse_args()
    
    if args.demo == "id":
        demo_id_processing()


if __name__ == "__main__":
    main()
