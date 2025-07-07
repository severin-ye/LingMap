import argparse
import os
import json
from typing import List

from common.models.event import EventItem
from common.utils.json_loader import JsonLoader
from hallucination_refine.di.provider import provide_refiner


def refine_events(events_path: str, output_path: str, context_path: str = "") -> List[EventItem]:
    """
    Perform hallucination detection and repair for event list
    
    Args:
        events_path: Event JSON file path
        output_path: Output JSON file path
        context_path: Context file path (optional)
        
    Returns:
        Refined event list
    """
    # Load events
    with open(events_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)
        
    events = [EventItem.from_dict(event_data) for event_data in events_data]
    
    # Load context (if provided)
    context = ""
    if context_path and os.path.exists(context_path):
        with open(context_path, 'r', encoding='utf-8') as f:
            context = f.read()
    
    # Get refiner
    refiner = provide_refiner()
    
    # Refine events
    print(f"Performing hallucination detection and repair for {len(events)} events...")
    refined_events = refiner.refine(events, context)
    print(f"Refinement completed, total {len(refined_events)} events")
    
    # Save results
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    refined_events_dict = [event.to_dict() for event in refined_events]
    JsonLoader.save_json(refined_events_dict, output_path)
    print(f"Refined events saved to: {output_path}")
    
    return refined_events


def main():
    """HALLUCINATION_REFINE module execution entry point"""
    parser = argparse.ArgumentParser(description="Perform hallucination detection and repair for events")
    parser.add_argument("--input", "-i", required=True, help="Input event JSON file")
    parser.add_argument("--output", "-o", required=True, help="Output refined event JSON file")
    parser.add_argument("--context", "-c", help="Context file supporting refinement (optional)")
    
    args = parser.parse_args()
    
    refine_events(args.input, args.output, args.context)


if __name__ == "__main__":
    main()
