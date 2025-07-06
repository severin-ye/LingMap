import argparse
import os
import sys
import logging
import multiprocessing
from typing import List, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from common.utils.path_utils import get_project_root, get_config_path, get_novel_path, get_output_path

from text_ingestion.chapter_loader import ChapterLoader
from common.models.chapter import Chapter
from common.utils.json_loader import JsonLoader
from event_extraction.di.provider import provide_extractor
from hallucination_refine.di.provider import provide_refiner
from causal_linking.di.provider import provide_linker
from graph_builder.service.mermaid_renderer import MermaidRenderer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api_gateway")


def setup_env():
    """Setup environment variables"""
    # Check if .env file exists and try to load it
    env_file = os.path.join(project_root, ".env")
    if os.path.exists(env_file):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logger.info("Loaded .env file")
            
            # Set API keys - ensure uppercase variable names are available
            if "deepseek_api_key" in os.environ:
                os.environ["DEEPSEEK_API_KEY"] = os.environ["deepseek_api_key"]
                logger.info("Set DeepSeek API key")
            
            if "openai_api_key" in os.environ:
                os.environ["OPENAI_API_KEY"] = os.environ["openai_api_key"]
                logger.info("Set OpenAI API key")
                
        except ImportError:
            logger.warning("python-dotenv library not found, unable to load .env file")
    else:
        logger.warning(".env file not found")


def process_text(text_path: str, output_dir: str, temp_dir: str = "", provider: str = "openai"):
    """
    Process novel text and generate causal graph
    
    Args:
        text_path: Novel text file path
        output_dir: Output directory
        temp_dir: Temporary file directory
        provider: LLM API provider, "openai" or "deepseek"
    """
    # Set LLM provider environment variable
    os.environ["LLM_PROVIDER"] = provider
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create temporary directory
    if temp_dir is None:
        temp_dir = os.path.join(output_dir, "temp")
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    print("=== Step 1: Load and segment chapters ===")
    # Load chapters
    loader = ChapterLoader(segment_size=800)
    print(f"Loading chapters from {text_path}...")
    chapter = loader.load_from_txt(text_path)
    
    if not chapter:
        print("Failed to load chapters")
        return
    
    # Save chapter JSON
    chapter_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}.json")
    JsonLoader.save_json(chapter.to_dict(), chapter_json_path)
    print(f"Chapter saved to: {chapter_json_path}")
    
    print("\n=== Step 2: Extract events ===")
    # Extract events
    extractor = provide_extractor()
    print(f"Extracting events from chapter {chapter.chapter_id}...")
    events = extractor.extract(chapter)
    print(f"Successfully extracted {len(events)} events")
    
    # Save events JSON
    events_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}_events.json")
    events_dict = [event.to_dict() for event in events]
    JsonLoader.save_json(events_dict, events_json_path)
    print(f"Events saved to: {events_json_path}")
    
    print("\n=== Step 3: Refine hallucinations ===")
    # Refine hallucinations
    refiner = provide_refiner()
    print(f"Detecting and refining hallucinations for {len(events)} events...")
    refined_events = refiner.refine(events, context=chapter.content)
    print(f"Refinement completed, total {len(refined_events)} events")
    
    # Save refined events JSON
    refined_events_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}_refined_events.json")
    refined_events_dict = [event.to_dict() for event in refined_events]
    JsonLoader.save_json(refined_events_dict, refined_events_json_path)
    print(f"Refined events saved to: {refined_events_json_path}")
    
    print("\n=== Step 4: Analyze causal relationships ===")
    # Analyze causal relationships
    linker = provide_linker()
    print(f"Analyzing causal relationships between {len(refined_events)} events...")
    edges = linker.link_events(refined_events)
    print(f"Found {len(edges)} causal relationships")
    
    # Build DAG
    print("Building Directed Acyclic Graph (DAG)...")
    events, dag_edges = linker.build_dag(refined_events, edges)
    print(f"DAG construction completed, retained {len(dag_edges)} edges")
    
    # Save causal relationships JSON
    causal_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}_causal.json")
    causal_data = {
        "nodes": [event.to_dict() for event in events],
        "edges": [edge.to_dict() for edge in dag_edges]
    }
    JsonLoader.save_json(causal_data, causal_json_path)
    print(f"Causal relationships saved to: {causal_json_path}")
    
    print("\n=== Step 5: Generate Mermaid graph ===")
    # Generate Mermaid graph
    renderer = MermaidRenderer()
    options = {
        "show_legend": True,
        "show_edge_labels": True,
        "custom_edge_style": True
    }
    
    mermaid_text = renderer.render(events, dag_edges, options)
    
    # Save Mermaid file
    mermaid_path = os.path.join(output_dir, f"{chapter.chapter_id}_graph.mmd")
    with open(mermaid_path, 'w', encoding='utf-8') as f:
        f.write(mermaid_text)
    print(f"Mermaid graph saved to: {mermaid_path}")
    
    print("\n=== Processing completed ===")
    print(f"Processing results saved to directory: {output_dir}")


def process_directory(input_dir: str, output_dir: str, provider: str = "openai", parallel: bool = True):
    """
    Process all text files in a directory
    
    Args:
        input_dir: Input directory
        output_dir: Output directory
        provider: LLM API provider, "openai" or "deepseek"
        parallel: Whether to process files in parallel
    """
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get all TXT files
    import glob
    txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
    
    if not parallel:
        # Sequential processing
        for txt_file in txt_files:
            file_name = os.path.basename(txt_file)
            file_output_dir = os.path.join(output_dir, file_name.replace(".txt", ""))
            
            print(f"\nProcessing file: {file_name}")
            process_text(txt_file, file_output_dir, provider=provider)
    else:
        # Parallel processing
        print(f"Enabling parallel processing for {len(txt_files)} files...")
        
        # Determine appropriate number of threads
        cpu_count = multiprocessing.cpu_count()
        # Use half of system CPU cores, at least 2, at most 8
        max_workers = max(2, min(8, cpu_count // 2))
        print(f"Using {max_workers} worker threads for parallel processing")
        
        def process_file_task(txt_file):
            try:
                file_name = os.path.basename(txt_file)
                file_output_dir = os.path.join(output_dir, file_name.replace(".txt", ""))
                
                print(f"Starting to process file: {file_name}")
                process_text(txt_file, file_output_dir, provider=provider)
                print(f"Successfully completed file: {file_name}")
                return (True, file_name, None)
            except Exception as e:
                print(f"Error processing file {os.path.basename(txt_file)}: {str(e)}")
                return (False, os.path.basename(txt_file), str(e))
        
        # Use thread pool for parallel file processing
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {executor.submit(process_file_task, txt_file): txt_file for txt_file in txt_files}
            
            # Collect results
            for future in as_completed(future_to_file):
                txt_file = future_to_file[future]
                try:
                    success, file_name, error = future.result()
                    results.append((success, file_name, error))
                except Exception as e:
                    results.append((False, os.path.basename(txt_file), str(e)))
        
        # Summarize results
        success_count = sum(1 for success, _, _ in results if success)
        failed_count = len(results) - success_count
        
        print("\n=== Processing Results Summary ===")
        print(f"Successfully processed: {success_count} files")
        print(f"Processing failed: {failed_count} files")
        
        if failed_count > 0:
            print("\nFailed files:")
            for success, file_name, error in results:
                if not success:
                    print(f"- {file_name}: {error}")


def main():
    """Main entry function"""
    parser = argparse.ArgumentParser(description='"A Record of a Mortal\'s Journey to Immortality" Causal Graph Generation System')
    parser.add_argument("--input", "-i", required=True, help="Input novel text file or directory")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--batch", "-b", action="store_true", help="Batch processing mode (process all files in directory)")
    parser.add_argument("--provider", "-p", choices=["openai", "deepseek"], default="deepseek",
                        help="LLM API provider (default: deepseek)")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel processing")
    
    args = parser.parse_args()
    
    # Setup environment variables
    setup_env()
    
    # Set LLM provider
    os.environ["LLM_PROVIDER"] = args.provider
    logger.info(f"Using LLM provider: {args.provider}")
    
    if args.batch:
        # Batch processing mode
        if not os.path.isdir(args.input):
            logger.error(f"Error: Input path {args.input} is not a directory")
            return
        
        process_directory(args.input, args.output, provider=args.provider, parallel=not args.no_parallel)
    else:
        # Single file mode
        if not os.path.isfile(args.input):
            logger.error(f"Error: Input path {args.input} is not a file")
            return
        
        process_text(args.input, args.output, provider=args.provider)


if __name__ == "__main__":
    main()
