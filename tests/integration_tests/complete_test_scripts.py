#!/usr/bin/env python3
"""
Complete workflow test script

Used to test the entire system workflow, including event extraction, hallucination refinement, causal linking and graph generation
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root directory to system path
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from common.utils.path_utils import get_project_root, get_novel_path, get_output_path
from common.utils.enhanced_logger import EnhancedLogger
from common.models.chapter import Chapter

from text_ingestion.chapter_loader import ChapterLoader
from event_extraction.di.provider import provide_extractor
from hallucination_refine.di.provider import provide_refiner
from causal_linking.di.provider import provide_linker
from graph_builder.service.mermaid_renderer import MermaidRenderer

# Create logger
logger = EnhancedLogger("complete_test", log_level="DEBUG")

def main():
    """Run complete workflow test"""
    print("="*80)
    print("A Record of a Mortal's Journey to Immortality - Causal Event Graph Generation System - Complete Workflow Test")
    print("="*80)
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = get_output_path(f"test_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Output directory: {output_dir}")
    
    # Load chapter
    chapter_path = get_novel_path("test.txt")
    if not os.path.exists(chapter_path):
        print(f"Error: Chapter file not found: {chapter_path}")
        return
    
    print("\n1. Loading chapter data...")
    loader = ChapterLoader()
    with open(chapter_path, 'r', encoding='utf-8') as f:
        content = f.read()
    chapter = Chapter(chapter_id="Chapter 1", title="Chapter 1", content=content)
    print(f"  ✓ Successfully loaded chapter: {chapter.title}, {len(chapter.content)} characters")
    
    # Event extraction
    print("\n2. Extracting events...")
    extractor = provide_extractor()
    events = extractor.extract(chapter)
    
    if not events:
        print("  ❌ Event extraction failed, no events extracted")
        return
    
    print(f"  ✓ Successfully extracted {len(events)} events")
    
    # Save original events
    events_path = os.path.join(temp_dir, f"{chapter.chapter_id}_events.json")
    with open(events_path, 'w', encoding='utf-8') as f:
        json.dump([event.to_dict() for event in events], f, ensure_ascii=False, indent=2)
    
    print(f"  Original events saved to: {events_path}")
    
    # Hallucination refinement
    print("\n3. Hallucination refinement...")
    refiner = provide_refiner()
    refined_events = refiner.refine(events, chapter.content)
    
    # Save refined events
    refined_events_path = os.path.join(temp_dir, f"{chapter.chapter_id}_refined_events.json")
    with open(refined_events_path, 'w', encoding='utf-8') as f:
        json.dump([event.to_dict() for event in refined_events], f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ Hallucination refinement completed, {len(refined_events)} events remaining")
    print(f"  Refined events saved to: {refined_events_path}")
    
    # Causal linking
    print("\n4. Generating causal links...")
    linker = provide_linker()
    causal_links = linker.link_events(refined_events)
    
    # Save causal links
    causal_path = os.path.join(temp_dir, f"{chapter.chapter_id}_causal.json")
    with open(causal_path, 'w', encoding='utf-8') as f:
        json.dump([link.to_dict() for link in causal_links], f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ Successfully generated {len(causal_links)} causal links")
    print(f"  Causal links saved to: {causal_path}")
    
    # Generate graph
    print("\n5. Generating graph...")
    renderer = MermaidRenderer()
    graph = renderer.render(refined_events, causal_links)
    
    # Save graph
    graph_path = os.path.join(output_dir, f"{chapter.chapter_id}_graph.mmd")
    with open(graph_path, 'w', encoding='utf-8') as f:
        f.write("```mermaid\n")
        f.write(graph)
        f.write("\n```")
    
    print(f"  ✓ Graph generated")
    print(f"  Graph saved to: {graph_path}")
    
    print("\nComplete workflow test finished!")
    print(f"All output files located at: {output_dir}")

if __name__ == "__main__":
    main()
