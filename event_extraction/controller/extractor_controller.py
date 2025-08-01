import argparse
import os
import json
from typing import List

from common.models.chapter import Chapter
from common.models.event import EventItem
from common.utils.json_loader import JsonLoader
from common.utils.unified_id_processor import UnifiedIdProcessor
from event_extraction.di.provider import provide_extractor


def extract_events_from_chapter(chapter_path: str, output_path: str) -> List[EventItem]:
    """
    Extract events from chapter JSON file and save results
    
    Args:
        chapter_path: Chapter JSON file path
        output_path: Output JSON file path
        
    Returns:
        List of extracted events
    """
    # Load chapter
    chapter = JsonLoader.load_chapter_json(chapter_path)
    
    # Get extractor
    extractor = provide_extractor()
    
    # Extract events
    print(f"Extracting events from chapter {chapter.chapter_id}...")
    events = extractor.extract(chapter)
    print(f"Successfully extracted {len(events)} events")
    
    # Note: Event ID uniqueness is already processed in extraction service, no need to reprocess here
    # Check if event IDs are unique (for verification only)
    event_ids = [e.event_id for e in events]
    unique_ids = set(event_ids)
    if len(event_ids) != len(unique_ids):
        print(f"Warning: Duplicate IDs found in extracted events, original {len(events)} events, only {len(unique_ids)} unique IDs")
    
    # Save results
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    events_dict = [event.to_dict() for event in events]
    JsonLoader.save_json(events_dict, output_path)
    print(f"Events saved to: {output_path}")
    
    return events


def main():
    """EVENT_EXTRACTION module execution entry point"""
    parser = argparse.ArgumentParser(description="Extract events from chapters")
    parser.add_argument("--input", "-i", required=True, help="Input chapter JSON file or directory")
    parser.add_argument("--output", "-o", required=True, help="Output event JSON file or directory")
    parser.add_argument("--batch", "-b", action="store_true", help="Batch processing mode")
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch processing mode
        if not os.path.isdir(args.input):
            print(f"Error: Input path {args.input} is not a directory")
            return
        
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        
        # Get all JSON files
        import glob
        chapter_files = glob.glob(os.path.join(args.input, "*.json"))
        
        total_events = []
        for chapter_file in chapter_files:
            filename = os.path.basename(chapter_file)
            output_file = os.path.join(args.output, filename)
            events = extract_events_from_chapter(chapter_file, output_file)
            total_events.extend(events)
        
        # Check if cross-chapter event IDs are unique (for verification only)
        event_ids = [e.event_id for e in total_events]
        unique_ids = set(event_ids)
        if len(event_ids) != len(unique_ids):
            print(f"Warning: Duplicate IDs found after cross-chapter merge, original {len(total_events)} events, only {len(unique_ids)} unique IDs")
            
        # Before merged output, ensure event ID uniqueness (this is multi-chapter merge processing, quite special)
        # Only needed in this cross-chapter merge scenario for additional processing
        original_count = len(total_events)
        total_events = UnifiedIdProcessor.ensure_unique_event_ids(total_events)
        if len(total_events) != original_count:
            print(f"Merge deduplication processing: reduced from {original_count} events to {len(total_events)} unique events")
        else:
            print(f"All cross-chapter event IDs are unique, total {len(total_events)} events")
        
        # Save all events to a merged file
        all_events_path = os.path.join(args.output, "all_events.json")
        all_events_dict = [event.to_dict() for event in total_events]
        JsonLoader.save_json(all_events_dict, all_events_path)
        print(f"All events merged and saved to: {all_events_path}")
    else:
        # Single file mode
        extract_events_from_chapter(args.input, args.output)


if __name__ == "__main__":
    main()
