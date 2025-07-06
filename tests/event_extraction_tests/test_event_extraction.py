#!/usr/bin/env python3
"""
Event extraction module test script

Test the complete functionality of the event extraction service, including text loading, event extraction, and result verification
"""

import os
import sys
import json
from pathlib import Path

# Add project root directory to system path
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from common.models.chapter import Chapter
from common.utils.path_utils import get_novel_path, get_config_path
from common.utils.json_loader import JsonLoader
from common.utils.enhanced_logger import EnhancedLogger
from event_extraction.di.provider import provide_extractor
from event_extraction.service.enhanced_extractor_service import EnhancedEventExtractor

# Create logger
logger = EnhancedLogger("event_extraction_test", log_level="DEBUG")

def load_test_chapter():
    """Load test chapter data"""
    print("="*80)
    print("1. Load test chapter data")
    print("="*80)
    
    # Try to load test file
    test_novel_path = get_novel_path("test.txt")
    print(f"Check test file: {test_novel_path}")
    
    if os.path.exists(test_novel_path):
        with open(test_novel_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ Loaded {len(content)} characters from test file")
        source = "test.txt"
    else:
        # If test file does not exist, use chapter 1
        chapter_path = get_novel_path("1.txt")
        print(f"Test file does not exist, try loading: {chapter_path}")
        
        if not os.path.exists(chapter_path):
            print(f"❌ No novel file found")
            return None, None
        
        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read(2000)  # Only read the first 2000 characters for testing
        print(f"✓ Loaded {len(content)} characters from chapter 1")
        source = "1.txt (first 2000 characters)"
    
    # Create Chapter object
    chapter = Chapter(
        chapter_id="First Chapter",
        title="First Chapter",
        content=content,
        segments=[]  # Let the extractor segment automatically
    )
    
    print(f"Chapter information:")
    print(f"  - ID: {chapter.chapter_id}")
    print(f"  - Title: {chapter.title}")
    print(f"  - Content length: {len(chapter.content)} characters")
    print(f"  - Source: {source}")
    
    return chapter, source

def test_extractor_initialization():
    """Test event extractor initialization"""
    print("\n" + "="*80)
    print("2. Event extractor initialization test")
    print("="*80)
    
    try:
        # Use provider to get extractor
        extractor = provide_extractor()
        
        print(f"✓ Event extractor initialization successful")
        print(f"  - Provider: {getattr(extractor, 'provider', 'Unknown')}")
        print(f"  - Model: {getattr(extractor, 'model', 'Unknown')}")
        print(f"  - API key prefix: {getattr(extractor, 'api_key', '')[:10] if getattr(extractor, 'api_key', '') else 'Unknown'}...")
        print(f"  - Maximum worker threads: {getattr(extractor, 'max_workers', 'Unknown')}")
        print(f"  - Debug mode: {getattr(extractor, 'debug_mode', False)}")
        
        return True, extractor
    except Exception as e:
        print(f"❌ Event extractor initialization failed: {str(e)}")
        return False, None

def test_prompt_template():
    """Test event extraction prompt template"""
    print("\n" + "="*80)
    print("3. Event extraction prompt template test")
    print("="*80)
    
    # Load prompt template
    prompt_path = get_config_path("prompt_event_extraction.json")
    print(f"Prompt template path: {prompt_path}")
    
    try:
        template = JsonLoader.load_json(prompt_path)
        print(f"✓ Successfully loaded prompt template")
        
        # Check required fields
        required_fields = ["system", "instruction", "output_format"]
        missing_fields = [field for field in required_fields if field not in template]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print(f"✓ Contains all required fields: {required_fields}")
        
        # Check instruction template
        instruction = template.get("instruction", "")
        if "{text}" in instruction:
            print(f"✓ Instruction template contains text placeholder")
        else:
            print(f"❌ Instruction template missing {{text}} placeholder")
            return False
        
        # Check output format
        output_format = template.get("output_format", {})
        if isinstance(output_format, dict) and output_format:
            print(f"✓ Output format definition complete")
            print(f"   Output format fields: {list(output_format.keys())}")
        else:
            print(f"❌ Output format definition incomplete")
            return False
        
        # Test formatting function
        sample_text = "Han Li took out a piece of spiritual milk from his storage bag, and swallowed it with great care..."
        try:
            formatted_instruction = instruction.format(text=sample_text)
            print(f"✓ Template formatting function normal")
        except Exception as e:
            print(f"❌ Template formatting failed: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Prompt template test failed: {e}")
        return False

def test_direct_extraction():
    """Test direct event extraction functionality"""
    print("\n" + "="*80)
    print("4. Direct event extraction test")
    print("="*80)
    
    # Get test chapter
    chapter, source = load_test_chapter()
    if not chapter:
        return False
    
    # Initialize extractor
    success, extractor = test_extractor_initialization()
    if not success:
        return False
    
    print(f"\nStarting event extraction...")
    print(f"Input text length: {len(chapter.content)} characters")
    
    try:
        # Check if extractor is None
        if not extractor:
            print(f"\n❌ Extractor initialization failed")
            return False
            
        events = extractor.extract(chapter)
        
        if events:
            print(f"\n✓ Successfully extracted {len(events)} events")
            
            # Show details of the first 3 events
            for i, event in enumerate(events[:3], 1):
                print(f"\nEvent {i}:")
                print(f"  ID: {event.event_id}")
                print(f"   Description: {event.description}")
                print(f"   Characters: {', '.join(event.characters) if event.characters else 'None'}")
                print(f"   Treasures: {', '.join(event.treasures) if event.treasures else 'None'}")
                print(f"   Location: {event.location or 'None'}")
                print(f"   Time: {event.time or 'None'}")
                print(f"   Result: {event.result or 'None'}")
            
            if len(events) > 3:
                print(f"\n... {len(events) - 3} more events")
            
            # Save events to debug file
            debug_dir = project_root / "debug"
            debug_dir.mkdir(exist_ok=True)
            
            events_file = debug_dir / "extracted_events_test.json"
            with open(events_file, 'w', encoding='utf-8') as f:
                json.dump([event.to_dict() for event in events], f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ Events saved to: {events_file}")
            
            return True
        else:
            print(f"\n❌ No events extracted")
            return False
            
    except Exception as e:
        print(f"\n❌ Event extraction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_extraction_quality():
    """Test event extraction quality"""
    print("\n" + "="*80)
    print("5. Event extraction quality assessment")
    print("="*80)
    
    # Load saved event data
    debug_dir = project_root / "debug"
    events_file = debug_dir / "extracted_events_test.json"
    
    if not events_file.exists():
        print("❌ No event data file found, please run event extraction test first")
        return False
    
    try:
        with open(events_file, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        
        print(f"✓ Loaded {len(events_data)} events")
        
        # Quality check metrics
        total_events = len(events_data)
        events_with_description = sum(1 for e in events_data if e.get('description'))
        events_with_characters = sum(1 for e in events_data if e.get('characters'))
        events_with_treasures = sum(1 for e in events_data if e.get('treasures'))
        events_with_location = sum(1 for e in events_data if e.get('location'))
        events_with_result = sum(1 for e in events_data if e.get('result'))
        
        print(f"\nQuality metrics:")
        print(f"   Events with description: {events_with_description}/{total_events} ({events_with_description/total_events*100:.1f}%)")
        print(f"   Events with characters: {events_with_characters}/{total_events} ({events_with_characters/total_events*100:.1f}%)")
        print(f"   Events with treasures: {events_with_treasures}/{total_events} ({events_with_treasures/total_events*100:.1f}%)")
        print(f"   Events with location: {events_with_location}/{total_events} ({events_with_location/total_events*100:.1f}%)")
        print(f"   Events with result: {events_with_result}/{total_events} ({events_with_result/total_events*100:.1f}%)")
        
        # Check uniqueness of event IDs
        event_ids = [e.get('event_id') for e in events_data if e.get('event_id')]
        unique_ids = set(event_ids)
        
        if len(event_ids) == len(unique_ids):
            print(f"  ✓ Event ID uniqueness: Passed")
        else:
            print(f"  ❌ Event ID uniqueness: Failed ({len(event_ids)} vs {len(unique_ids)})")
        
        # Basic quality score
        quality_score = (
            (events_with_description / total_events) * 0.3 +
            (events_with_characters / total_events) * 0.25 +
            (events_with_location / total_events) * 0.15 +
            (events_with_result / total_events) * 0.2 +
            (len(unique_ids) / len(event_ids) if event_ids else 0) * 0.1
        ) * 100
        
        print(f"\nOverall quality score: {quality_score:.1f}/100")
        
        if quality_score >= 80:
            print("✓ Extraction quality excellent")
        elif quality_score >= 60:
            print("⚠️   Extraction quality good")
        else:
            print("❌ Extraction quality needs improvement")
        
        return quality_score >= 60
        
    except Exception as e:
        print(f"❌ Quality assessment failed: {e}")
        return False

def main():
    """Run event extraction module test"""
    print("Event extraction module test suite")
    print("="*80)
    
    tests = [
        ("Load test chapter", lambda: load_test_chapter()[0] is not None),
        ("Extractor initialization", lambda: test_extractor_initialization()[0]),
        ("Prompt template", test_prompt_template),
        ("Direct event extraction", test_direct_extraction),
        ("Extraction quality assessment", test_extraction_quality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\nRunning test: {test_name}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed: {str(e)}")
            results.append((test_name, False))
    
    # Output test summary
    print("\n" + "="*80)
    print("Test summary")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ Passed" if result else "❌ Failed"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All event extraction tests passed!")
    else:
        print("⚠️   Some tests failed, please check configuration and implementation")

if __name__ == "__main__":
    main()
