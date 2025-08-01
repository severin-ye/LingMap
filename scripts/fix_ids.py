#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ID repair tool

Use unified ID processor to fix duplicate ID issues in events and graph nodes.
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root directory to system path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from common.utils.unified_id_processor import UnifiedIdProcessor


def main():
    """Program main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ID repair tool")
    parser.add_argument("--input", "-i", required=True, help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--type", "-t", choices=["event", "node"], default="event", 
                        help="ID type: event-event ID, node-node ID")
    args = parser.parse_args()
    
    try:
        print(f"Processing file: {args.input}")
        
        # Ensure input file exists
        if not os.path.exists(args.input):
            print(f"Error: File does not exist: {args.input}")
            return 1
        
        # Set output path
        output_path = args.output
        if not output_path:
            # If output path not specified, generate based on input path
            input_path = Path(args.input)
            output_path = str(input_path.parent / f"{input_path.stem}_fixed{input_path.suffix}")
        
        # Use unified ID processor to fix IDs
        UnifiedIdProcessor.fix_duplicate_event_ids(args.input, str(output_path))
        print(f"IDs fixed and saved to: {output_path}")
        return 0
        
    except Exception as e:
        print(f"Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
