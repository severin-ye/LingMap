import argparse
import json
import os

from text_ingestion.chapter_loader import ChapterLoader
from common.utils.json_loader import JsonLoader


def main():
    """TEXT_INGESTION module execution entry point"""
    parser = argparse.ArgumentParser(description="Load novel text and convert to chapter JSON")
    parser.add_argument("--input", "-i", required=True, help="Input TXT file or directory")
    parser.add_argument("--output", "-o", required=True, help="Output JSON file or directory")
    parser.add_argument("--segment_size", "-s", type=int, default=800, help="Segment size")
    parser.add_argument("--batch", "-b", action="store_true", help="Batch processing mode")
    
    args = parser.parse_args()
    
    loader = ChapterLoader(segment_size=args.segment_size)
    
    if args.batch:
        # Batch processing mode
        if not os.path.isdir(args.input):
            print(f"Error: Input path {args.input} is not a directory")
            return
        
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        
        chapters = loader.load_multiple_txt(args.input)
        print(f"Successfully loaded {len(chapters)} chapters")
        
        for chapter in chapters:
            output_file = os.path.join(args.output, f"{chapter.chapter_id}.json")
            JsonLoader.save_json(chapter.to_dict(), output_file)
            print(f"Saved chapter: {output_file}")
    else:
        # Single file mode
        if not os.path.isfile(args.input):
            print(f"Error: Input path {args.input} is not a file")
            return
        
        chapter = loader.load_from_txt(args.input)
        if chapter:
            JsonLoader.save_json(chapter.to_dict(), args.output)
            print(f"Saved chapter: {args.output}")
            # Print some statistics
            print(f"Chapter ID: {chapter.chapter_id}")
            print(f"Chapter title: {chapter.title}")
            print(f"Number of segments: {len(chapter.segments)}")
        else:
            print("Failed to load chapter")


if __name__ == "__main__":
    main()
