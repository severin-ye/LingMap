import os
import sys
from pathlib import Path

# Add project root directory to system path
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from common.interfaces.refiner import AbstractRefiner
from hallucination_refine.service.har_service import HallucinationRefiner
from common.utils.path_utils import get_config_path
from common.utils.parallel_config import ParallelConfig
from common.utils.thread_monitor import log_thread_usage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def provide_refiner() -> AbstractRefiner:
    """Provide hallucination refiner instance"""
    
    # Check API provider environment variable
    provider = os.environ.get("LLM_PROVIDER", "deepseek")
    
    # Get the corresponding API key according to the provider
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        model = "gpt-4o"
    else:  # deepseek
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        model = "deepseek-chat"
    
    # Use path_utils to get config file path
    prompt_path = get_config_path("prompt_hallucination_refine.json")
    
    # Get the number of worker threads according to parallel configuration
    # Hallucination repair is an IO-intensive task, suitable for using more threads
    if ParallelConfig.is_enabled():
        max_workers = ParallelConfig.get_max_workers("io_bound")
    else:
        max_workers = 1
        
    print(f"Hallucination refiner using worker threads: {max_workers}")
    
    # Log thread usage
    log_thread_usage("hallucination_refine", max_workers, "io_bound")
    
    return HallucinationRefiner(
        model=model,
        prompt_path=prompt_path,
        api_key=api_key,
        max_workers=max_workers,
        max_iterations=2,
        provider=provider
    )
