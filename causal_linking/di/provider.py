import os
import sys
from pathlib import Path

# [CN] 将项目根目录添加到系统路径
# [EN] Add project root directory to system path
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from common.interfaces.linker import AbstractLinker
# [CN] 导入统一版链接器以及兼容类
# [EN] Import unified linker and compatible classes
from causal_linking.service.unified_linker_service import UnifiedCausalLinker, CausalLinker, OptimizedCausalLinker
from common.utils.path_utils import get_config_path
from common.utils.parallel_config import ParallelConfig
from common.utils.thread_monitor import log_thread_usage
from dotenv import load_dotenv

# [CN] 加载.env文件中的环境变量
# [EN] Load environment variables from .env file
load_dotenv()

def provide_linker(use_optimized: bool = True) -> AbstractLinker:
    """
    # [CN] 提供因果链接器实例
    # [EN] Provide causal linker instance
    
    Args:
        # [CN] use_optimized: 是否使用优化版链接器，默认True
        # [EN] use_optimized: Whether to use optimized linker, default True
        
    Returns:
        # [CN] 因果链接器实例
        # [EN] Causal linker instance
    """
    
    # [CN] 检查API提供商环境变量
    # [EN] Check API provider environment variable
    provider = os.environ.get("LLM_PROVIDER", "deepseek")
    
    # [CN] 根据提供商获取相应的API密钥
    # [EN] Get corresponding API key based on provider
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        model = "gpt-4o"
    else:  # deepseek
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        model = "deepseek-chat"
    
    # [CN] 使用path_utils获取配置文件路径
    # [EN] Use path_utils to get configuration file path
    prompt_path = get_config_path("prompt_causal_linking.json")
    
    # [CN] 强度映射
    # [EN] Strength mapping
    strength_mapping = {
        "高": 3,
        "中": 2,
        "低": 1
    }
    
    # [CN] 从环境变量或默认值获取优化参数
    # [EN] Get optimization parameters from environment variables or default values
    max_events_per_chapter = int(os.environ.get("MAX_EVENTS_PER_CHAPTER", "50"))  # [CN] 大幅增加单章事件数量限制 # [EN] Significantly increase single chapter event count limit
    min_entity_support = int(os.environ.get("MIN_ENTITY_SUPPORT", "3"))  # [CN] 保持中等实体支持度要求 # [EN] Maintain moderate entity support requirements
    max_chapter_span = int(os.environ.get("MAX_CHAPTER_SPAN", "10")) 
    max_candidate_pairs = int(os.environ.get("MAX_CANDIDATE_PAIRS", "150"))  # [CN] 适当增加最大候选对数量 # [EN] Appropriately increase maximum candidate pairs count
    
    # [CN] 根据并行配置获取工作线程数
    # [EN] Get worker thread count based on parallel configuration
    # [CN] 因果分析是IO和CPU混合型任务，使用默认线程配置
    # [EN] Causal analysis is a mixed IO and CPU task, use default thread configuration
    if ParallelConfig.is_enabled():
        max_workers = ParallelConfig.get_max_workers("causal_linking")  # [CN] 指定模块名获取特定配置 # [EN] Specify module name to get specific configuration
        if max_workers is None:
            max_workers = 3  # [CN] 默认值 # [EN] Default value
    else:
        max_workers = 1
    
    print(f"# [CN] 因果链接器使用工作线程数: {max_workers}")
    print(f"# [EN] Causal linker using worker threads: {max_workers}")
    
    # [CN] 记录线程使用情况
    # [EN] Log thread usage
    log_thread_usage("causal_linking", max_workers, "default")
    
    use_entity_weights = os.environ.get("USE_ENTITY_WEIGHTS", "1").lower() in ["1", "true", "yes"]
    
    # [CN] 根据参数选择使用优化模式还是原始模式
    # [EN] Choose to use optimized mode or original mode based on parameters
    if use_optimized:
        # [CN] 使用优化版链接器
        # [EN] Use optimized linker
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
        # [CN] 使用原始版链接器
        # [EN] Use original linker
        return CausalLinker(
            model=model,
            prompt_path=prompt_path,
            api_key=api_key,
            max_workers=3,
            strength_mapping=strength_mapping,
            provider=provider
        )
