#!/usr/bin/env python3
"""
Environment testing script to verify dependencies are correctly installed and API keys are valid
"""

import os
import sys
import importlib
import platform

# Set colored output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'


def print_success(message):
    """Print success message"""
    print(f"{GREEN}[✓] {message}{ENDC}")


def print_error(message):
    """Print error message"""
    print(f"{RED}[✗] {message}{ENDC}")


def print_warning(message):
    """Print warning message"""
    print(f"{YELLOW}[!] {message}{ENDC}")


def print_info(message):
    """Print info message"""
    print(f"{BLUE}[i] {message}{ENDC}")


def check_python_version():
    """Check Python version"""
    print_info("Checking Python version...")
    version = platform.python_version()
    major, minor, _ = version.split('.')
    
    if int(major) >= 3 and int(minor) >= 8:
        print_success(f"Python version {version} meets requirements (3.8+)")
        return True
    else:
        print_error(f"Python version {version} does not meet requirements (need 3.8+)")
        return False


def check_dependencies():
    """Check if dependencies are installed"""
    print_info("Checking dependencies...")
    required_packages = [
        "openai",
        "tenacity",
        "numpy",
        "tqdm"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print_success(f"Dependency {package} is installed")
        except ImportError:
            print_error(f"Dependency {package} is not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print_warning(f"Missing dependencies: {', '.join(missing_packages)}")
        print_info("Please run: pip install -r requirements.txt to install dependencies")
        return False
    
    return True


def check_api_key():
    """Check if API keys are set"""
    print_info("Checking API keys...")
    openai_key = os.environ.get("OPENAI_API_KEY")
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    
    openai_status = False
    deepseek_status = False
    
    # Check OpenAI API key
    if openai_key:
        print_success("OpenAI API key is set")
        
        # Try to verify API key (optional)
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print_success("OpenAI API key is valid, API call successful")
            openai_status = True
        except Exception as e:
            print_error(f"OpenAI API key is invalid or call failed: {str(e)}")
    else:
        print_warning("OpenAI API key is not set")
        print_info("To use OpenAI, please set environment variable: export OPENAI_API_KEY=\"your-api-key\"")
    
    # Check DeepSeek API key
    if deepseek_key:
        print_success("DeepSeek API key is set")
        
        # Try to verify API key
        try:
            import openai
            client = openai.OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com/v1")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print_success("DeepSeek API key is valid, API call successful")
            deepseek_status = True
        except Exception as e:
            print_error(f"DeepSeek API key is invalid or call failed: {str(e)}")
    else:
        print_warning("DeepSeek API key is not set")
        print_info("To use DeepSeek, please set environment variable: export DEEPSEEK_API_KEY=\"your-api-key\"")
            
    # If any API is valid, return success
    if openai_status or deepseek_status:
        return True
    else:
        print_error("All API keys are invalid or not set")
        return False


def check_project_structure():
    """Check if project structure is complete"""
    print_info("Checking project structure...")
    
    # Get project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Check required directories
    required_dirs = [
        "common",
        "text_ingestion",
        "event_extraction",
        "hallucination_refine",
        "causal_linking",
        "graph_builder",
        "api_gateway"
    ]
    
    missing_dirs = []
    
    for directory in required_dirs:
        dir_path = os.path.join(project_root, directory)
        if os.path.isdir(dir_path):
            print_success(f"Directory {directory} exists")
        else:
            print_error(f"Directory {directory} does not exist")
            missing_dirs.append(directory)
    
    if missing_dirs:
        print_warning(f"Project structure is incomplete, missing directories: {', '.join(missing_dirs)}")
        return False
    
    return True


def check_system_config():
    """Check system configuration files and path utilities"""
    print_info("Checking system configuration...")
    
    try:
        # Add project root directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        import sys
        sys.path.insert(0, project_root)
        
        from common.utils.path_utils import get_project_root, get_config_path, get_novel_path
        from common.utils.json_loader import JsonLoader
        
        # Test project root directory
        project_root = get_project_root()
        print_success(f"Project root directory: {project_root}")
        
        # Test configuration files
        config_files = [
            "config.json",
            "prompt_event_extraction.json", 
            "prompt_hallucination_refine.json",
            "prompt_causal_linking.json"
        ]
        
        config_ok = True
        for config_file in config_files:
            try:
                config_path = get_config_path(config_file)
                if os.path.exists(config_path):
                    print_success(f"Configuration file {config_file} exists")
                    
                    # Try to load JSON configuration
                    if config_file.endswith('.json'):
                        try:
                            JsonLoader.load_json(config_path)
                            print_success(f"Configuration file {config_file} format is correct")
                        except Exception as e:
                            print_error(f"Configuration file {config_file} format error: {str(e)}")
                            config_ok = False
                else:
                    print_warning(f"Configuration file {config_file} does not exist")
                    config_ok = False
            except Exception as e:
                print_error(f"Error checking configuration file {config_file}: {str(e)}")
                config_ok = False
        
        # Test novel file directory
        try:
            test_novel = get_novel_path("test.txt")
            if os.path.exists(test_novel):
                print_success("Test novel file test.txt exists")
            else:
                print_warning("Test novel file test.txt does not exist")
        except Exception as e:
            print_error(f"Error checking novel file: {str(e)}")
            config_ok = False
        
        return config_ok
    except Exception as e:
        print_error(f"System configuration check failed: {str(e)}")
        return False


def main():
    """Main function"""
    print_info("=== Tales of Demons and Gods Causal Graph Generation System - Environment Check ===")
    
    # Check Python version
    python_ok = check_python_version()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check API keys
    api_ok = check_api_key()
    
    # Check project structure
    structure_ok = check_project_structure()
    
    # Check system configuration
    config_ok = check_system_config()
    
    # Output summary
    print_info("\n=== Check Results Summary ===")
    all_passed = python_ok and deps_ok and api_ok and structure_ok and config_ok
    
    if all_passed:
        print_success("All checks passed! System is ready.")
        print_info("You can run python scripts/demo_run.py to test the system.")
    else:
        print_warning("Some checks failed, please resolve the above issues and try again.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
