#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parallel processing testing and reporting tool

Integrated features:
1. Parallel configuration testing
2. Performance benchmark testing
3. Parallel configuration report generation
"""

import os
import sys
import time
import json
import argparse
import logging
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Add project root directory to system path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from common.utils.parallel_config import ParallelConfig
from common.utils.config_writer import ConfigWriter
from common.utils.thread_monitor import ThreadUsageMonitor
from common.utils.json_loader import JsonLoader


class ParallelToolMode(Enum):
    """Parallel tool running modes"""
    TEST = "test"         # Test mode: Verify configuration
    BENCHMARK = "bench"   # Benchmark test mode: Compare performance
    REPORT = "report"     # Report mode: Generate configuration report
    ALL = "all"           # Run all


def setup_logging(log_filename=None):
    """
    Setup logging
    
    Args:
        log_filename: Log filename, if None, generate by date
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    if log_filename is None:
        log_filename = f"parallel_tool_{datetime.now().strftime('%Y%m%d')}.log"
    
    log_file = log_dir / log_filename
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )
    
    return logging.getLogger("parallel_tool")


def format_duration(seconds):
    """
    Format time duration to readable form
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} hours"


def run_module_test(module_name, test_func, *args, **kwargs):
    """
    Run module test
    
    Args:
        module_name: Module name
        test_func: Test function
        args: Positional arguments
        kwargs: Keyword arguments
        
    Returns:
        Test result and execution time
    """
    print(f"\nTesting module: {module_name}")
    start_time = time.time()
    try:
        result = test_func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"✅ {module_name} test successful, duration: {format_duration(duration)}")
        return result, duration
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ {module_name} test failed: {e}")
        import traceback
        traceback.print_exc()
        return None, duration


#--------------------------------------------------------------------
# Configuration testing related functions
#--------------------------------------------------------------------
def test_parallel_config_consistency(logger=None):
    """
    Test parallel configuration consistency
    
    Args:
        logger: Logger instance
    """
    if logger is None:
        logger = logging.getLogger()

    # Initialize ParallelConfig
    ParallelConfig.initialize()
    
    # Log configuration information
    logger.info("====== Parallel Configuration Test ======")
    logger.info(f"Parallel processing enabled status: {ParallelConfig.is_enabled()}")
    logger.info(f"Global maximum thread count: {ParallelConfig._config['max_workers']}")
    
    # Log module-specific configurations
    logger.info("Module-specific configurations:")
    for module, workers in ParallelConfig._config["default_workers"].items():
        logger.info(f"  - {module}: {workers}")
    
    # Test module instantiation
    logger.info("\nTesting module instantiation:")
    
    try:
        # Event extraction
        logger.info("Creating event extractor...")
        from event_extraction.di.provider import provide_extractor
        extractor = provide_extractor()
        
        # Hallucination refinement
        logger.info("Creating hallucination refiner...")
        from hallucination_refine.di.provider import provide_refiner
        refiner = provide_refiner()
        
        # Causal linking
        logger.info("Creating causal linker...")
        from causal_linking.di.provider import provide_linker
        linker = provide_linker()
        
        # Graph builder
        logger.info("Creating graph renderer...")
        from graph_builder.service.mermaid_renderer import MermaidRenderer
        renderer = MermaidRenderer()
        
        logger.info("All modules initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Module initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_config_updates(logger=None):
    """
    Test configuration updates
    
    Args:
        logger: Logger instance
    
    Returns:
        Whether test was successful
    """
    if logger is None:
        logger = logging.getLogger()
    
    try:
        logger.info("\n====== Configuration Update Test ======")
        
        # Log original configuration
        original_max = ParallelConfig._config["max_workers"]
        original_graph = ParallelConfig._config["default_workers"]["graph_builder"]
        logger.info(f"Original thread configuration: Global={original_max}, Graph Builder={original_graph}")
        
        # Update configuration
        test_updates = {
            "max_workers": original_max + 2,
            "default_workers": {
                "graph_builder": original_graph + 1
            }
        }
        logger.info(f"Update configuration: {test_updates}")
        
        # Apply updates
        ConfigWriter.update_parallel_config(test_updates)
        
        # Verify updated configuration
        logger.info(f"Updated configuration: Global={ParallelConfig._config['max_workers']}, " +
                   f"Graph Builder={ParallelConfig._config['default_workers']['graph_builder']}")
        
        # Restore original configuration
        restore_updates = {
            "max_workers": original_max,
            "default_workers": {
                "graph_builder": original_graph
            }
        }
        logger.info(f"Restore original configuration: {restore_updates}")
        ConfigWriter.update_parallel_config(restore_updates)
        
        # Confirm successful restoration
        logger.info(f"Restored configuration: Global={ParallelConfig._config['max_workers']}, " +
                   f"Graph Builder={ParallelConfig._config['default_workers']['graph_builder']}")
        return True
    except Exception as e:
        logger.error(f"Configuration update test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


#--------------------------------------------------------------------
# Report generation related functions
#--------------------------------------------------------------------
def generate_parallel_report():
    """
    Generate parallel configuration report
    
    Returns:
        Report file path
    """
    # Initialize parallel configuration
    ParallelConfig.initialize()
    
    # Initialize thread monitor
    thread_monitor = ThreadUsageMonitor.get_instance()
    
    # Create report directory
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    report_file = report_dir / f"parallel_config_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    # Collect configuration information
    config_info = {
        "enabled": ParallelConfig.is_enabled(),
        "max_workers": ParallelConfig._config["max_workers"],
        "adaptive": ParallelConfig._config["adaptive"],
        "default_workers": ParallelConfig._config["default_workers"]
    }
    
    # Generate parallel configuration report
    logging.info("Generating parallel configuration report...")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# System Parallel Processing Configuration Report\n\n")
        f.write(f"Generation time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Basic configuration
        f.write("# Basic Configuration\n\n")
        f.write(f"- Parallel processing status: {'Enabled' if config_info['enabled'] else 'Disabled'}\n")
        f.write(f"- Global maximum thread count: {config_info['max_workers']}\n")
        
        # Adaptive configuration
        f.write("\n# Adaptive Thread Configuration\n\n")
        adaptive = config_info['adaptive']
        f.write(f"- Adaptive mode: {'Enabled' if adaptive['enabled'] else 'Disabled'}\n")
        if adaptive['enabled']:
            f.write(f"- IO-bound task factor: {adaptive['io_bound_factor']}\n")
            f.write(f"- CPU-bound task factor: {adaptive['cpu_bound_factor']}\n")
            
            io_threads = int(config_info['max_workers'] * adaptive['io_bound_factor'])
            cpu_threads = int(config_info['max_workers'] * adaptive['cpu_bound_factor'])
            
            f.write(f"- IO-bound task thread count: {io_threads}\n")
            f.write(f"- CPU-bound task thread count: {cpu_threads}\n")
        
        # Module-specific configuration
        f.write("\n# Module-Specific Configuration\n\n")
        f.write("| Module | Configured Thread Count |\n")
        f.write("|--------|------------------------|\n")
        
        for module, workers in config_info['default_workers'].items():
            f.write(f"| {module} | {workers} |\n")
        
        # Initialize modules and record thread usage
        f.write("\n# Actual Thread Usage\n\n")
        f.write("Now starting to test actual thread count used by each module...\n\n")
        
        # Event extraction
        logging.info("Testing event extraction module...")
        f.write("# Event Extraction Module\n\n")
        try:
            from event_extraction.di.provider import provide_extractor
            extractor = provide_extractor()
            f.write("✅ Event extraction module initialized successfully\n\n")
        except Exception as e:
            f.write(f"❌ Event extraction module initialization failed: {e}\n\n")
        
        # Hallucination refinement
        logging.info("Testing hallucination refinement module...")
        f.write("\n# Hallucination Refinement Module\n\n")
        try:
            from hallucination_refine.di.provider import provide_refiner
            refiner = provide_refiner()
            f.write("✅ Hallucination refinement module initialized successfully\n\n")
        except Exception as e:
            f.write(f"❌ Hallucination refinement module initialization failed: {e}\n\n")
        
        # Causal linking
        logging.info("Testing causal linking module...")
        f.write("\n# Causal Linking Module\n\n")
        try:
            from causal_linking.di.provider import provide_linker
            linker = provide_linker()
            f.write("✅ Causal linking module initialized successfully\n\n")
        except Exception as e:
            f.write(f"❌ Causal linking module initialization failed: {e}\n\n")
        
        # Graph builder
        logging.info("Testing graph builder module...")
        f.write("\n# Graph Builder Module\n\n")
        try:
            from graph_builder.service.mermaid_renderer import MermaidRenderer
            renderer = MermaidRenderer()
            f.write("✅ Graph builder module initialized successfully\n\n")
        except Exception as e:
            f.write(f"❌ Graph builder module initialization failed: {e}\n\n")
        
        # Get and record thread monitor information
        usage_info = thread_monitor.thread_usage
        
        f.write("\n# Thread Usage Summary\n\n")
        f.write("| Module | Configured Thread Count | Actual Thread Count | Task Type |\n")
        f.write("|--------|-------------------------|---------------------|----------|\n")
        
        for module, workers in config_info['default_workers'].items():
            actual_workers = usage_info.get(module, {}).get("thread_count", "Unknown")
            task_type = usage_info.get(module, {}).get("task_type", "Unknown")
            f.write(f"| {module} | {workers} | {actual_workers} | {task_type} |\n")
        
        # Conclusions and recommendations
        f.write("\n# Conclusions and Recommendations\n\n")
        
        # Check for modules not using centralized configuration
        unconfigured_modules = set(usage_info.keys()) - set(config_info['default_workers'].keys())
        if unconfigured_modules:
            f.write("⚠️ The following modules are not using centralized configuration:\n\n")
            for module in unconfigured_modules:
                f.write(f"- {module}\n")
            f.write("\nIt is recommended to add these modules to the centralized configuration.\n\n")
        
        # Check consistency between configuration and usage
        inconsistent_modules = []
        for module, info in usage_info.items():
            if module in config_info['default_workers']:
                expected = config_info['default_workers'][module]
                actual = info.get("thread_count", 0)
                if expected != actual and ParallelConfig.is_enabled():
                    inconsistent_modules.append((module, expected, actual))
                    
        if inconsistent_modules:
            f.write("⚠️ The following modules have inconsistent thread usage with configuration:\n\n")
            for module, expected, actual in inconsistent_modules:
                f.write(f"- {module}: Expected {expected}, Actual {actual}\n")
            f.write("\nIt is recommended to check if these modules correctly use ParallelConfig in their parallel implementation.\n\n")
        
        # Adaptive recommendations
        f.write("# Optimization Recommendations\n\n")
        f.write("Based on different module task characteristics, the following thread configurations are recommended:\n\n")
        f.write("- IO-intensive tasks (such as API calls): CPU cores x 1.5\n")
        f.write("- CPU-intensive tasks (such as graph rendering): CPU cores x 0.8\n")
        f.write("- Mixed tasks: Equivalent to CPU cores\n\n")
        
        f.write("Classification in current system:\n\n")
        f.write("- IO-intensive: event_extraction, hallucination_refine\n")
        f.write("- CPU-intensive: graph_builder\n")
        f.write("- Mixed: causal_linking\n")
    
    logging.info(f"Report generated: {report_file}")
    print(f"📊 Parallel configuration report generated: {report_file}")
    
    return report_file


#--------------------------------------------------------------------
# Benchmark testing related functions
#--------------------------------------------------------------------
def test_event_extraction(chapter_file):
    """
    Test event extraction module
    
    Args:
        chapter_file: Chapter file path
        
    Returns:
        Extracted events
    """
    from text_ingestion.chapter_loader import ChapterLoader
    from event_extraction.di.provider import provide_extractor
    
    # Load chapter
    loader = ChapterLoader(segment_size=800)
    chapter = loader.load_from_json(chapter_file)
    
    if not chapter:
        raise ValueError("Failed to load chapter")
    
    # Extract events
    extractor = provide_extractor()
    print(f"Extracting events from chapter {chapter.chapter_id}...")
    events = extractor.extract(chapter)
    print(f"Successfully extracted {len(events)} events")
    
    return events


def test_hallucination_refine(events, context):
    """
    Test hallucination refinement module
    
    Args:
        events: Event list
        context: Context information
        
    Returns:
        Refined events
    """
    from hallucination_refine.di.provider import provide_refiner
    
    refiner = provide_refiner()
    print(f"Performing hallucination detection and refinement on {len(events)} events...")
    refined_events = refiner.refine(events, context=context)
    print(f"Refinement completed, total {len(refined_events)} events")
    
    return refined_events


def test_causal_linking(events):
    """
    Test causal analysis module
    
    Args:
        events: Event list
        
    Returns:
        Tuple of events and edges
    """
    from causal_linking.di.provider import provide_linker
    
    linker = provide_linker(use_optimized=True)
    print(f"Analyzing causal relationships between {len(events)} events...")
    edges = linker.link_events(events)
    print(f"Found {len(edges)} causal relationships")
    
    # Build DAG
    print("Building directed acyclic graph (DAG)...")
    events, dag_edges = linker.build_dag(events, edges)
    print(f"DAG construction completed, retained {len(dag_edges)} edges")
    
    return events, dag_edges


def test_graph_rendering(events, edges):
    """
    Test graph rendering module
    
    Args:
        events: Event list
        edges: Edge list
        
    Returns:
        Rendered Mermaid text
    """
    from graph_builder.service.mermaid_renderer import MermaidRenderer
    
    renderer = MermaidRenderer()
    options = {
        "show_legend": True,
        "show_edge_labels": True,
        "custom_edge_style": True
    }
    
    print(f"Rendering {len(events)} event nodes and {len(edges)} edges...")
    mermaid_text = renderer.render(events, edges, options)
    
    return mermaid_text


def run_benchmark(args):
    """
    Run performance benchmark testing
    
    Args:
        args: Command line arguments
        
    Returns:
        Test report file path
    """
    # Set input file path
    if args.input:
        chapter_file = args.input
    else:
        # Find test data
        temp_dir = os.path.join(project_root, "temp")
        output_dirs = [d for d in os.listdir(os.path.join(project_root, "output")) 
                       if os.path.isdir(os.path.join(project_root, "output", d))]
        
        if output_dirs:
            # Use the latest output directory
            latest_dir = sorted(output_dirs)[-1]
            temp_dir = os.path.join(project_root, "output", latest_dir, "temp")
            
        # Find chapter JSON files
        json_files = [f for f in os.listdir(temp_dir) 
                     if os.path.isfile(os.path.join(temp_dir, f))
                     and f.endswith('.json') and 'chapter' in f.lower()]
        
        if not json_files:
            # Try to find any JSON files
            json_files = [f for f in os.listdir(temp_dir) 
                         if os.path.isfile(os.path.join(temp_dir, f))
                         and f.endswith('.json')]
            
        if not json_files:
            raise FileNotFoundError("Cannot find chapter JSON files for testing")
            
        # Use the first JSON file found
        chapter_file = os.path.join(temp_dir, json_files[0])
        
    print(f"Using test data: {chapter_file}")
    
    # Run parallel mode test
    print("===== Parallel Mode Test =====")
    
    # Ensure parallel mode is enabled
    ParallelConfig.initialize({"enabled": True})
    print(f"Parallel mode: Enabled, maximum thread count: {ParallelConfig._config['max_workers']}")
    
    # Save execution time for each test phase
    parallel_results = {}
    
    # Event extraction phase
    events, duration = run_module_test("Event Extraction", test_event_extraction, chapter_file)
    parallel_results["Event Extraction"] = duration
    
    if not events:
        print("Event extraction failed, unable to continue testing")
        return
    
    # Extract chapter context for hallucination detection
    context = "Test context"
    try:
        with open(chapter_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and "content" in data:
                context = data["content"][:500] + "..." if len(data["content"]) > 500 else data["content"]
    except:
        print("Failed to extract context, using default context")
    
    # Hallucination refinement phase
    refined_events, duration = run_module_test("Hallucination Refinement", test_hallucination_refine, events, context)
    parallel_results["Hallucination Refinement"] = duration
    
    if not refined_events:
        refined_events = events
    
    # Causal linking phase
    linking_result, duration = run_module_test("Causal Linking", test_causal_linking, refined_events)
    parallel_results["Causal Linking"] = duration
    
    if not linking_result:
        print("Causal linking failed, unable to continue testing")
        return
        
    events, edges = linking_result
    
    # Graph rendering phase
    mermaid_text, duration = run_module_test("Graph Rendering", test_graph_rendering, events, edges)
    parallel_results["Graph Rendering"] = duration
    
    # If not skipping sequential test, perform sequential mode test
    sequential_results = {}
    if not args.skip_sequential:
        print("\n===== Sequential Mode Test =====")
        
        # Switch to sequential mode
        ParallelConfig.initialize({"enabled": False})
        print("Sequential mode: Enabled")
        
        # Same test process
        events, duration = run_module_test("Event Extraction (Sequential)", test_event_extraction, chapter_file)
        sequential_results["Event Extraction"] = duration
        
        if not events:
            print("Event extraction failed, unable to continue testing")
            return
        
        # Hallucination refinement phase
        refined_events, duration = run_module_test("Hallucination Refinement (Sequential)", test_hallucination_refine, events, context)
        sequential_results["Hallucination Refinement"] = duration
        
        if not refined_events:
            refined_events = events
        
        # Causal linking phase
        linking_result, duration = run_module_test("Causal Linking (Sequential)", test_causal_linking, refined_events)
        sequential_results["Causal Linking"] = duration
        
        if not linking_result:
            print("Causal linking failed, unable to continue testing")
            return
            
        events, edges = linking_result
        
        # Graph rendering phase
        mermaid_text, duration = run_module_test("Graph Rendering (Sequential)", test_graph_rendering, events, edges)
        sequential_results["Graph Rendering"] = duration
    
    # Re-enable parallel mode
    ParallelConfig.initialize({"enabled": True})
    
    # Generate report
    report_content = generate_benchmark_report(parallel_results, sequential_results)
    
    # Create report directory
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    # Write report
    report_file = None
    if args.output:
        report_file = args.output
    else:
        report_file = report_dir / f"parallel_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\nReport saved to: {report_file}")
    return report_file


def generate_benchmark_report(parallel_results, sequential_results):
    """
    Generate performance comparison report
    
    Args:
        parallel_results: Parallel mode test results
        sequential_results: Sequential mode test results
        
    Returns:
        Report text content
    """
    report = []
    report.append("# Parallel Processing Performance Benchmark Test Report")
    report.append(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Performance summary
    report.append("# Performance Summary")
    total_parallel = sum(parallel_results.values())
    total_sequential = sum(sequential_results.values()) if sequential_results else 0
    
    report.append(f"- Parallel processing total duration: {format_duration(total_parallel)}")
    if sequential_results:
        speedup = (total_sequential / total_parallel) if total_parallel > 0 else 0
        report.append(f"- Sequential processing total duration: {format_duration(total_sequential)}")
        report.append(f"- Speedup ratio: {speedup:.2f}x")
        report.append(f"- Performance improvement: {(speedup - 1) * 100:.2f}%")
    else:
        report.append("- Sequential processing test was skipped")
    report.append("")
    
    # Module performance comparison
    if sequential_results:
        report.append("# Module Performance Comparison")
        report.append("| Module | Parallel Processing Duration | Sequential Processing Duration | Speedup Ratio | Improvement Percentage |")
        report.append("| --- | ------- | ------- | ----- | ------- |")
        
        for module in parallel_results.keys():
            par_time = parallel_results[module]
            seq_time = sequential_results.get(module, 0)
            if seq_time > 0 and par_time > 0:
                mod_speedup = seq_time / par_time
                improvement = (mod_speedup - 1) * 100
                report.append(f"| {module} | {format_duration(par_time)} | {format_duration(seq_time)} | {mod_speedup:.2f}x | {improvement:.2f}% |")
    else:
        report.append("# Parallel Mode Execution Time")
        report.append("| Module | Parallel Processing Duration |")
        report.append("| --- | ------- |")
        for module, time in parallel_results.items():
            report.append(f"| {module} | {format_duration(time)} |")
    
    report.append("")
    report.append("# Test Configuration")
    report.append(f"- CPU core count: {os.cpu_count()}")
    report.append(f"- Parallel mode worker thread count:")
    report.append(f"  - Event extraction: {ParallelConfig.get_max_workers('io_bound')}")
    report.append(f"  - Hallucination refinement: {ParallelConfig.get_max_workers('io_bound')}")
    report.append(f"  - Causal analysis: {ParallelConfig.get_max_workers()}")
    report.append(f"  - Graph rendering: {ParallelConfig.get_max_workers('cpu_bound')}")
    
    return '\n'.join(report)


def main():
    """Program main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Parallel processing tool")
    parser.add_argument("mode", choices=["test", "bench", "report", "all"], default="all", 
                        nargs="?", help="Run mode: test-configuration test, bench-performance test, report-generate report, all-run all")
    parser.add_argument("--input", "-i", help="Input file path (for performance testing)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--skip-sequential", action="store_true", help="Skip sequential processing test")
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    logger.info(f"Running parallel processing tool, mode: {args.mode}")
    
    # Record start time
    start_time = time.time()
    
    # Run different functions based on mode
    try:
        mode = ParallelToolMode(args.mode)
        
        if mode in [ParallelToolMode.TEST, ParallelToolMode.ALL]:
            logger.info("==== Running parallel configuration test ====")
            test_result = test_parallel_config_consistency(logger)
            if test_result:
                config_result = test_config_updates(logger)
                if config_result:
                    print("✅ Configuration test successful")
                else:
                    print("❌ Configuration update test failed")
            else:
                print("❌ Configuration consistency test failed")
                
        if mode in [ParallelToolMode.REPORT, ParallelToolMode.ALL]:
            logger.info("==== Generating parallel configuration report ====")
            report_file = generate_parallel_report()
            print(f"✅ Report generation successful: {report_file}")
            
        if mode in [ParallelToolMode.BENCHMARK, ParallelToolMode.ALL]:
            logger.info("==== Running performance benchmark test ====")
            benchmark_file = run_benchmark(args)
            print(f"✅ Benchmark test completed: {benchmark_file}")
            
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"❌ Execution failed: {e}")
        
    # Record total execution time
    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"Total execution time: {format_duration(duration)}")
    print(f"Total execution time: {format_duration(duration)}")


if __name__ == "__main__":
    main()
