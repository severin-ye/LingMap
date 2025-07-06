#!/usr/bin/env python3
"""
"A Record of a Mortal's Journey to Immortality" Causal Event Graph Generation System - Main Entry File

R2 framework-based causal event graph generation system for automatically extracting events from 
"A Record of a Mortal's Journey to Immortality" novel text and establishing causal relationship graphs.
Supports event extraction, hallucination refinement, causal relationship linking, and graph visualization.

Usage examples:
    python main.py                         # Interactive mode
    python main.py --demo                  # Run demo
    python main.py --input novel/test.txt  # Process specific file
    python main.py --batch novel/          # Batch process directory
"""

import os
import sys
import time
import logging
import argparse
import multiprocessing
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

# Example novel file path
file_name= Path(__file__).parent / "novel" / "test.txt"

# Ensure correct project path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Import parallel processing configuration and thread monitoring
from common.utils.parallel_config import ParallelConfig
from common.utils.thread_monitor import ThreadUsageMonitor

# Initialize parallel configuration
ParallelConfig.initialize()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

# Initialize thread monitoring
thread_monitor = ThreadUsageMonitor.get_instance()


def print_banner():
    """Print system banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║       "A Record of a Mortal's Journey to Immortality" Causal Event Graph    ║
║                             Generation System                                ║
║                                                                              ║
║         R2 Framework-based Intelligent Causal Relationship Graph System     ║
║    Supports Event Extraction, Hallucination Refinement, Causal Analysis,   ║
║                           and Graph Visualization                            ║
║                                                                              ║
║    🧠 Event Extract    🔧 Hallucination Fix    🔗 Causal Analysis    📊 Graph Gen   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def setup_environment():
    """Setup runtime environment"""
    # Try to load .env file
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logger.info("Loaded .env file")
            
            # Ensure API keys are available (uppercase variable names)
            if "openai_api_key" in os.environ:
                os.environ["OPENAI_API_KEY"] = os.environ["openai_api_key"]
                logger.info("Set OpenAI API key")
                
            if "deepseek_api_key" in os.environ:
                os.environ["DEEPSEEK_API_KEY"] = os.environ["deepseek_api_key"]
                logger.info("Set DeepSeek API key")
                
        except ImportError:
            logger.warning("python-dotenv not installed, skipping .env file loading")
    else:
        # Create example .env file if not exists
        env_example = PROJECT_ROOT / ".env.example"
        if env_example.exists() and not env_file.exists():
            logger.info(".env file not found, creating default configuration...")
            try:
                import shutil
                shutil.copy(env_example, env_file)
                logger.info(f".env file created, please edit {env_file} to set your API keys")
            except Exception as e:
                logger.warning(f"Failed to create .env file: {e}")
    
    # Create necessary directories
    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    
    temp_dir = PROJECT_ROOT / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    novel_dir = PROJECT_ROOT / "novel"
    novel_dir.mkdir(exist_ok=True)
    
    # Set system environment variables
    if "MAX_WORKERS" not in os.environ:
        cpu_count = multiprocessing.cpu_count()
        optimal_workers = max(2, min(8, cpu_count))
        os.environ["MAX_WORKERS"] = str(optimal_workers)
    
    if "LLM_PROVIDER" not in os.environ:
        os.environ["LLM_PROVIDER"] = "deepseek"  # Default to DeepSeek
        
    # Initialize parallel configuration
    ParallelConfig.initialize()


def create_example_novel():
    """Create example novel file"""
    test_file = file_name
    example_content = """A Record of a Mortal's Journey to Immortality

Author: Wang Yu

Chapter 1: A Small Village by the Mountain

Er Lengzi opened his eyes wide, staring straight at the black roof made of thatched grass and mud, covered with an old cotton quilt that had turned deep yellow, its original appearance no longer discernible, with a faint musty smell wafting from it.

Right next to him was his second brother Han Zhu, sleeping very soundly, with occasional snoring sounds of varying intensity coming from his body.

About half a zhang away from the bed was a wall made of yellow mud. Due to the passage of time, several inconspicuous thin and long cracks had appeared on the wall. From these cracks came the vague sound of Mother Han's nagging complaints, occasionally mixed with the "pop, pop" sound of Father Han smoking his pipe.

Er Lengzi slowly closed his somewhat dry eyes, forcing himself to fall into deep sleep as soon as possible. He knew very well in his heart that if he didn't sleep honestly, he wouldn't be able to get up early tomorrow, and he wouldn't be able to go into the mountains with his other companions to collect dry firewood.

Er Lengzi's surname was Han and his given name was Li. His parents couldn't come up with such a proper name - it was given by Uncle Zhang in the village, who was asked by his father with two steamed buns made of coarse grain.

Uncle Zhang had worked as a companion book boy for a wealthy family in the city for several years when he was young. He was the only literate person in the village, and more than half of the children's names in the village were given by him.
"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(example_content)
    
    return test_file


def check_environment():
    """Check runtime environment"""
    print("🔍 Checking runtime environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python version too low, requires Python 3.8+")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check required packages
    required_packages = [
        'requests', 'openai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    # Check python-dotenv separately (as it may be installed differently)
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing_packages.append('python-dotenv')
    
    if missing_packages:
        print(f"⚠️ Missing packages: {', '.join(missing_packages)}")
        print("💡 Run: pip install -r requirements.txt")
    else:
        print("✅ All required packages are installed")
    
    # Check API keys
    has_api_key = False
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OpenAI API key detected")
        has_api_key = True
    if os.getenv('DEEPSEEK_API_KEY'):
        print("✅ DeepSeek API key detected")
        has_api_key = True
    
    if not has_api_key:
        print("⚠️ No API key detected, please set environment variables or .env file")
        print("💡 Supported APIs: OPENAI_API_KEY, DEEPSEEK_API_KEY")
    
    # Check configuration file
    config_file = PROJECT_ROOT / "common" / "config" / "config.json"
    if not config_file.exists():
        print(f"⚠️ Configuration file does not exist: {config_file}")
    else:
        print("✅ Configuration file exists")
    
    # Check test data
    test_file = PROJECT_ROOT / "novel" / "test.txt"
    if not test_file.exists():
        print(f"⚠️ Test file does not exist: {test_file}")
    else:
        print("✅ Test file exists")
    
    print("✅ Environment check completed\n")
    return True


def run_demo(provider: str = "deepseek") -> bool:
    """Run demo mode"""
    print("🎬 Running demo mode...")
    
    # Check demo file
    demo_file = PROJECT_ROOT / "novel" / "test.txt"
    if not demo_file.exists():
        print(f"❌ Demo file does not exist: {demo_file}")
        return False
    
    # Run demo
    from api_gateway.main import process_text
    
    output_dir = PROJECT_ROOT / "output" / f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    temp_dir = output_dir / "temp"
    
    try:
        process_text(
            text_path=str(demo_file),
            output_dir=str(output_dir),
            temp_dir=str(temp_dir),
            provider=provider
        )
        print(f"\n🎉 Demo completed! Results saved to: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ Demo execution failed: {e}")
        logger.exception("Demo execution failed")
        return False


def run_tests():
    """Run test suite"""
    print("🧪 Running test suite...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "tests.run_all_tests"
        ], cwd=PROJECT_ROOT)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        logger.exception("Failed to run tests")
        return False


def run_benchmark():
    """Run performance benchmark test"""
    print("⚡ Running performance benchmark test...")
    
    try:
        # Use subprocess to run performance test script
        import subprocess
        benchmark_script = PROJECT_ROOT / "scripts" / "performance_benchmark.py"
        
        if not benchmark_script.exists():
            print(f"❌ Performance test script does not exist: {benchmark_script}")
            return False
            
        result = subprocess.run(
            [sys.executable, str(benchmark_script)],
            cwd=PROJECT_ROOT
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        logger.exception("Performance test failed")
        return False


def process_file(input_file: Path, output_dir: Path, provider: str = "deepseek") -> bool:
    """Process single file"""
    print(f"\n📄 Processing file: {input_file.name}")
    
    if not input_file.exists():
        print(f"❌ File does not exist: {input_file}")
        return False
    
    try:
        from api_gateway.main import process_text
        process_text(
            text_path=str(input_file),
            output_dir=str(output_dir),
            provider=provider
        )
        print(f"✅ Processing completed! Results saved to: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        logger.exception(f"Failed to process file {input_file}")
        return False


def process_directory(input_dir: Path, output_dir: Path, provider: str = "deepseek") -> bool:
    """Batch process directory"""
    print(f"\n📂 Batch processing directory: {input_dir}")
    
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"❌ Directory does not exist: {input_dir}")
        return False
    
    # Get all txt files
    txt_files = list(input_dir.glob("*.txt"))
    if not txt_files:
        print(f"❌ No txt files found in directory: {input_dir}")
        return False
    
    print(f"📚 Found {len(txt_files)} txt files")
    
    try:
        from api_gateway.main import process_directory as api_process_directory
        api_process_directory(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            provider=provider
        )
        print(f"✅ Batch processing completed! Results saved to: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")
        logger.exception(f"Failed to process directory {input_dir}")
        return False


def run_interactive():
    """Run interactive mode"""
    print("🔄 Entering interactive mode...")
    
    # Check if example file exists
    test_file = PROJECT_ROOT / "novel" / "test.txt"
    if not test_file.exists():
        print("\n⚠️  Example file novel/test.txt not found")
        create_test = input("Would you like to create an example novel file? (y/n) [y]: ").strip().lower() or "y"
        if create_test in ["y", "yes"]:
            try:
                create_example_novel()
                print("✅ Example novel file created")
            except Exception as e:
                print(f"❌ Unable to create example file: {e}")
    
    while True:
        print("\n" + "=" * 60)
        print("📋 Available operations:")
        print("1. 🎬 Run demo")
        print("2. 📄 Process single file")
        print("3. 📂 Batch process directory")
        print("4. 🧪 Run tests")
        print("5. ⚡ Performance benchmark test")
        print("6. 🔍 Check environment")
        print("0. 🚪 Exit")
        print("=" * 60)
        
        choice = input("Please enter your choice (0-6): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            provider = input("Choose API provider (deepseek/openai) [default: deepseek]: ").strip() or "deepseek"
            run_demo(provider)
        elif choice == "2":
            run_single_file_interactive()
        elif choice == "3":
            run_batch_interactive()
        elif choice == "4":
            run_tests()
        elif choice == "5":
            run_benchmark()
        elif choice == "6":
            check_environment()
        else:
            print("❌ Invalid choice, please try again")


def run_single_file_interactive():
    """Interactive single file processing"""
    print("\n📄 Single file processing mode")
    
    # List available test files
    novel_dir = PROJECT_ROOT / "novel"
    if novel_dir.exists():
        txt_files = list(novel_dir.glob("*.txt"))
        if txt_files:
            print("\n📚 Available test files:")
            for i, file in enumerate(txt_files, 1):
                print(f"  {i}. {file.name}")
            print(f"  {len(txt_files) + 1}. Custom path")
            
            try:
                choice = int(input(f"\nPlease select file (1-{len(txt_files) + 1}): "))
                if 1 <= choice <= len(txt_files):
                    input_file = txt_files[choice - 1]
                elif choice == len(txt_files) + 1:
                    input_path = input("Please enter file path: ").strip()
                    input_file = Path(input_path)
                else:
                    print("❌ Invalid choice")
                    return
            except ValueError:
                print("❌ Please enter a valid number")
                return
    else:
        input_path = input("Please enter file path: ").strip()
        input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"❌ File does not exist: {input_file}")
        return
    
    # Choose API provider
    provider = input("Choose API provider (deepseek/openai) [default: deepseek]: ").strip() or "deepseek"
    
    # Set output directory
    output_dir = PROJECT_ROOT / "output" / f"{input_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Process file
    process_file(input_file, output_dir, provider)


def run_batch_interactive():
    """Interactive batch processing"""
    print("\n📂 Batch processing mode")
    
    # Default recommend novel directory
    novel_dir = PROJECT_ROOT / "novel"
    if novel_dir.exists():
        print(f"📁 Recommended directory: {novel_dir}")
        use_default = input("Use recommended directory? (y/n) [default: y]: ").strip().lower()
        if use_default in ['', 'y', 'yes']:
            input_dir = novel_dir
        else:
            input_path = input("Please enter directory path: ").strip()
            input_dir = Path(input_path)
    else:
        input_path = input("Please enter directory path: ").strip()
        input_dir = Path(input_path)
    
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"❌ Directory does not exist: {input_dir}")
        return
    
    # Check txt files in directory
    txt_files = list(input_dir.glob("*.txt"))
    if not txt_files:
        print(f"❌ No txt files found in directory: {input_dir}")
        return
    
    print(f"📚 Found {len(txt_files)} txt files")
    for file in txt_files:
        print(f"  - {file.name}")
    
    # Confirm processing
    if input("\nConfirm batch processing these files? (y/n): ").strip().lower() not in ['y', 'yes']:
        print("❌ Cancelled")
        return
    
    # Choose API provider
    provider = input("Choose API provider (deepseek/openai) [default: deepseek]: ").strip() or "deepseek"
    
    # Set output directory
    output_dir = PROJECT_ROOT / "output" / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Batch processing
    process_directory(input_dir, output_dir, provider)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='"A Record of a Mortal\'s Journey to Immortality" Causal Event Graph Generation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python main.py                          # Interactive mode
  python main.py --demo                   # Run demo
  python main.py --input novel/test.txt   # Process specific file
  python main.py --batch novel/           # Batch process directory
  python main.py --test                   # Run test suite
  python main.py --benchmark              # Run performance benchmark test
  python main.py --check-env              # Check environment

Supported API providers:
  - deepseek (default)
  - openai
        """
    )
    
    # Mutually exclusive mode options
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--demo", action="store_true", help="Run demo mode")
    mode_group.add_argument("--test", action="store_true", help="Run test suite")
    mode_group.add_argument("--benchmark", action="store_true", help="Run performance benchmark test")
    mode_group.add_argument("--check-env", action="store_true", help="Check runtime environment")
    
    # File processing options
    parser.add_argument("--input", "-i", help="Input file path")
    parser.add_argument("--output", "-o", help="Output directory path")
    parser.add_argument("--batch", "-b", metavar="DIR", help="Batch process directory")
    parser.add_argument("--provider", "-p", choices=["openai", "deepseek"], 
                       default="deepseek", help="LLM API provider (default: deepseek)")
    
    # Performance options
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel processing")
    parser.add_argument("--threads", type=int, help="Specify number of worker threads")
    
    # Other options
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Set log level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print banner (unless in quiet mode)
    if not args.quiet:
        print_banner()
    
    # Setup environment
    setup_environment()
    
    # Configure parallel processing options
    parallel_options = {
        "enabled": not args.no_parallel,
    }
    if args.threads:
        parallel_options["max_workers"] = args.threads
        
    ParallelConfig.initialize(parallel_options)
    
    if not args.quiet:
        if ParallelConfig.is_enabled():
            max_workers = ParallelConfig.get_max_workers()
            print(f"✅ Parallel processing enabled (worker threads: {max_workers})")
            
            # Record thread configuration for each module
            print("Thread configuration for each module:")
            for module, workers in ParallelConfig._config["default_workers"].items():
                print(f"  - {module}: {workers} threads")
                
            # Record adaptive configuration
            if ParallelConfig._config["adaptive"]["enabled"]:
                io_factor = ParallelConfig._config["adaptive"]["io_bound_factor"]
                cpu_factor = ParallelConfig._config["adaptive"]["cpu_bound_factor"]
                io_threads = int(max_workers * io_factor)
                cpu_threads = int(max_workers * cpu_factor)
                print(f"Adaptive thread configuration enabled:")
                print(f"  - IO-intensive tasks: {io_threads} threads (factor: {io_factor})")
                print(f"  - CPU-intensive tasks: {cpu_threads} threads (factor: {cpu_factor})")
            
            # Record to thread monitoring
            thread_monitor.log_system_thread_usage()
        else:
            print("ℹ️ Parallel processing disabled, using sequential execution mode")
    
    # Check environment
    if args.check_env:
        check_environment()
        return
    
    # Basic environment check
    check_environment()
    
    try:
        # Run corresponding mode
        if args.demo:
            run_demo(args.provider)
        
        elif args.test:
            run_tests()
        
        elif args.benchmark:
            run_benchmark()
        
        elif args.input:
            # Single file processing mode
            input_file = Path(args.input)
            output_dir = Path(args.output) if args.output else \
                        PROJECT_ROOT / "output" / f"{input_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Check if input file exists
            if not input_file.exists():
                print(f"❌ Input file does not exist: {input_file}")
                sys.exit(1)
                
            process_file(input_file, output_dir, args.provider)
        
        elif args.batch:
            # Batch processing mode
            input_dir = Path(args.batch)
            output_dir = Path(args.output) if args.output else \
                        PROJECT_ROOT / "output" / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Check if input directory exists
            if not input_dir.exists() or not input_dir.is_dir():
                print(f"❌ Input directory does not exist: {input_dir}")
                sys.exit(1)
                
            # Check if there are txt files
            if not list(input_dir.glob("*.txt")):
                print(f"❌ No .txt files in directory: {input_dir}")
                print("Please ensure novel text files are saved in .txt format")
                sys.exit(1)
                
            process_directory(input_dir, output_dir, args.provider)
        
        else:
            # Default interactive mode
            run_interactive()
    
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        print("Please ensure all necessary configuration files and directories exist")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  User interrupted operation")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print("💡 Run with --verbose parameter to see detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    main()
