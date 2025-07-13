#!/usr/bin/env python3
"""
Complete demo script for one-click demonstration of all functions in A Record of a Mortal's Journey to Immortality causal graph generation system
"""

import os
import sys
import argparse
import time
from pathlib import Path

# Get project root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import related modules
from api_gateway.main import setup_env, process_text
from scripts.check_env import check_python_version, check_dependencies, check_api_key


def run_complete_demo():
    """Run complete demonstration"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="A Record of a Mortal's Journey to Immortality causal graph generation system complete demo")
    parser.add_argument("--provider", "-p", choices=["openai", "deepseek"], default="deepseek",
                      help="LLM API provider (default: deepseek)")
    parser.add_argument("--input", "-i", default="test.txt",
                      help="Input filename, located in novel directory (default: test.txt)")
    parser.add_argument("--output", "-o", default=None,
                      help="Output directory name (default: output_YYYY-MM-DD_HH-MM-SS)")
    args = parser.parse_args()
    
    # Set environment variables
    setup_env()
    
    print("\n" + "=" * 60)
    print(f"A Record of a Mortal's Journey to Immortality Causal Graph Generation System - Complete Demo")
    print("=" * 60)
    
    # Step 1: Check environment
    print("\n【Step 1】Checking environment...")
    python_ok = check_python_version()
    deps_ok = check_dependencies()
    api_ok = check_api_key()
    
    if not (python_ok and deps_ok and api_ok):
        print("\nEnvironment check failed, please resolve the above issues before trying again.")
        return 1
    
    # Step 2: Prepare input and output paths
    print("\n【Step 2】Preparing input and output paths...")
    
    # Input file
    novel_dir = os.path.join(project_root, "novel")
    input_file = os.path.join(novel_dir, args.input)
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        return 1
    
    # Output directory
    if args.output:
        output_dir = os.path.join(project_root, args.output)
    else:
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join(project_root, f"output_{timestamp}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Input file: {input_file}")
    print(f"Output directory: {output_dir}")
    print(f"API provider: {args.provider}")
    
    # Step 3: Process text
    print("\n【Step 3】Starting text processing...")
    try:
        process_text(input_file, output_dir, provider=args.provider)
    except Exception as e:
        print(f"Error occurred during processing: {str(e)}")
        return 1
    
    # Step 4: Verify output
    print("\n【Step 4】Verifying output files...")
    
    # Check generated Mermaid files
    mermaid_files = list(Path(output_dir).glob("*.mmd"))
    if mermaid_files:
        print("\nSuccessfully generated the following graph files:")
        for mmd_file in mermaid_files:
            print(f"- {mmd_file.name}")
            
        print("\nYou can view the generated graphs at the following websites:")
        print("- Mermaid Live Editor: https://mermaid.live/")
        print("- Or use VS Code Mermaid extension")
    else:
        print("Warning: No generated graph files found")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(run_complete_demo())
