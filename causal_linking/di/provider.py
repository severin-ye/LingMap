import os
import sys
from pathlib import Path

# TODO: Translate - Add project root directory to系统路径
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from common.interfaces.linker import AbstractLinker
# TODO: Translate - Import统一版linking器以及兼容类
from causal_linking.service.unified_linker_service import UnifiedCausalLinker, CausalLinker, OptimizedCausalLinker
from common.utils.path_utils import get_config_path
from common.utils.parallel_config import ParallelConfig
from common.utils.thread_monitor import log_thread_usage
from dotenv import load_dotenv

# TODO: Translate - Load.env文件中的environment variables
load_dotenv()

def provide_linker(use_optimized: bool = True) -> AbstractLinker:
    """
    提供因果链接器实例
    
    Args:
        use_optimized: 是否使用优化版链接器，默认True
        
    Returns:
        因果链接器实例
    """
    
    # CheckAPIproviderenvironment variables
    provider = os.environ.get("LLM_PROVIDER", "deepseek")
    
    # TODO: Translate - 根据providerGet相应的API key
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        model = "gpt-4o"
    else:  # deepseek
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        model = "deepseek-chat"
    
    # TODO: Translate - Usepath_utilsGetConfigure文件路径
    prompt_path = get_config_path("prompt_causal_linking.json")
    
    # TODO: Translate - 强度映射
    strength_mapping = {
        "高": 3,
        "中": 2,
        "低": 1
    }
    
    # TODO: Translate - 从environment variables或默认值Get优化参数
    max_events_per_chapter = int(os.environ.get("MAX_EVENTS_PER_CHAPTER", "50"))  # TODO: Translate - 大幅增加单章event数量限制
    min_entity_support = int(os.environ.get("MIN_ENTITY_SUPPORT", "3"))  # TODO: Translate - 保持中等实体支持度要求
    max_chapter_span = int(os.environ.get("MAX_CHAPTER_SPAN", "10")) 
    max_candidate_pairs = int(os.environ.get("MAX_CANDIDATE_PAIRS", "150"))  # TODO: Translate - 适当增加最大候选对数量
    
    # TODO: Translate - 根据parallelConfigureGet工作thread数
    # TODO: Translate - causal分析是IO和CPU混合型任务，Use默认threadConfigure
    if ParallelConfig.is_enabled():
        max_workers = ParallelConfig.get_max_workers("causal_linking")  # TODO: Translate - 指定模块名Get特定Configure
        if max_workers is None:
            max_workers = 3  # TODO: Translate - 默认值
    else:
        max_workers = 1
    
    print(f"因果链接器使用工作线程数: {max_workers}")
    
    # TODO: Translate - 记录threadUse情况
    log_thread_usage("causal_linking", max_workers, "default")
    
    use_entity_weights = os.environ.get("USE_ENTITY_WEIGHTS", "1").lower() in ["1", "true", "yes"]
    
    # TODO: Translate - 根据参数选择Use优化模式还是原始模式
    if use_optimized:
        # TODO: Translate - Use优化版linking器
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
        # TODO: Translate - Use原始版linking器
        return CausalLinker(
            model=model,
            prompt_path=prompt_path,
            api_key=api_key,
            max_workers=3,
            strength_mapping=strength_mapping,
            provider=provider
        )
