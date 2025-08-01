import os
import sys
from pathlib import Path

# Add project root directory to system path
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from common.interfaces.linker import AbstractLinker
# Import unified linker and compatible classes
from causal_linking.service.unified_linker_service import UnifiedCausalLinker, CausalLinker, OptimizedCausalLinker
from common.utils.path_utils import get_config_path
from common.utils.parallel_config import ParallelConfig
from common.utils.thread_monitor import log_thread_usage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def provide_linker(use_optimized: bool = True) -> AbstractLinker:
    """
    Provide causal linker instance
    
    Args:
        use_optimized: Whether to use optimized linker, default True
        
    Returns:
        Causal linker instance
    """
    
    # Check API provider environment variables
    provider = os.environ.get("LLM_PROVIDER", "deepseek")
    
    # Get corresponding API key based on provider
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        model = "gpt-4o"
    else:  # deepseek
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        model = "deepseek-chat"
    
    # Use path_utils to get configuration file path
    prompt_path = get_config_path("prompt_causal_linking.json")
    
    # Strength mapping
    strength_mapping = {
        "高": 3,
        "中": 2,
        "低": 1
    }
    
    # Get optimization parameters from environment variables or default values
    max_events_per_chapter = int(os.environ.get("MAX_EVENTS_PER_CHAPTER", "50"))  # Significantly increase event count limit per chapter
    min_entity_support = int(os.environ.get("MIN_ENTITY_SUPPORT", "3"))  # Maintain moderate entity support requirement
    max_chapter_span = int(os.environ.get("MAX_CHAPTER_SPAN", "10")) 
    max_candidate_pairs = int(os.environ.get("MAX_CANDIDATE_PAIRS", "150"))  # Appropriately increase maximum candidate pairs
    
    # Get worker thread count based on parallel configuration
    # Causal analysis is a mixed IO and CPU task, use default thread configuration
    if ParallelConfig.is_enabled():
        max_workers = ParallelConfig.get_max_workers("causal_linking")  # Get specific configuration by module name
        if max_workers is None:
            max_workers = 3  # Default value
    else:
        max_workers = 1
    
    print(f"Causal linker using worker threads: {max_workers}")
    
    # Log thread usage status
    log_thread_usage("causal_linking", max_workers, "default")
    
    use_entity_weights = os.environ.get("USE_ENTITY_WEIGHTS", "1").lower() in ["1", "true", "yes"]
    
    # Choose optimized or original mode based on parameters
    if use_optimized:
        # Use optimized linker
        return OptimizedCausalLinker(
            model=model,
            prompt_path=prompt_path,
            api_key=api_key,
            max_workers=max_workers,
            strength_mapping=strength_mapping,
            provider=provider,
            max_events_per_chapter=max_events_per_chapter,
            min_entity_support=min_entity_support,
            max_chapter_span=max_chapter_span,
            max_candidate_pairs=max_candidate_pairs,
            use_entity_weights=use_entity_weights
        )
    else:
        # Use original linker
        return CausalLinker(
            model=model,
            prompt_path=prompt_path,
            api_key=api_key,
            max_workers=3,
            strength_mapping=strength_mapping,
            provider=provider
        )
