import argparse
import os
import sys

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hallucination_refine.controller.har_controller import refine_events


def main():
    """Main entry point for HALLUCINATION_REFINE module"""
    parser = argparse.ArgumentParser(description="Perform hallucination detection and refinement on events")
    parser.add_argument("--input", "-i", required=True, help="Input event JSON file")
    parser.add_argument("--output", "-o", required=True, help="Output refined event JSON file")
    parser.add_argument("--context", "-c", help="Context file to support refinement (optional)")
    
    args = parser.parse_args()
    
    refine_events(args.input, args.output, args.context)


if __name__ == "__main__":
    main()
