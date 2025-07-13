import argparse
import os
import sys

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from event_extraction.controller.extractor_controller import extract_events_from_chapter


def main():
    """Main entry point for EVENT_EXTRACTION module"""
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
        
        for chapter_file in chapter_files:
            filename = os.path.basename(chapter_file)
            output_file = os.path.join(args.output, filename)
            extract_events_from_chapter(chapter_file, output_file)
    else:
        # Single file mode
        extract_events_from_chapter(args.input, args.output)


if __name__ == "__main__":
    main()
