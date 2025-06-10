import os
import sys
from pathlib import Path

# 将项目根目录添加到系统路径
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from common.interfaces.linker import AbstractLinker
# 导入统一版链接器以及兼容类
from causal_linking.service.unified_linker_service import UnifiedCausalLinker, CausalLinker, OptimizedCausalLinker
from common.utils.path_utils import get_config_path
from common.utils.parallel_config import ParallelConfig
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

def provide_linker(use_optimized: bool = True) -> AbstractLinker:
    """
    提供因果链接器实例
    
    Args:
        use_optimized: 是否使用优化版链接器，默认True
        
    Returns:
        因果链接器实例
    """
    
    # 检查API提供商环境变量
    provider = os.environ.get("LLM_PROVIDER", "deepseek")
    
    # 根据提供商获取相应的API密钥
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        model = "gpt-4o"
    else:  # deepseek
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        model = "deepseek-chat"
    
    # 使用path_utils获取配置文件路径
    prompt_path = get_config_path("prompt_causal_linking.json")
    
    # 强度映射
    strength_mapping = {
        "高": 3,
        "中": 2,
        "低": 1
    }
    
    # 从环境变量或默认值获取优化参数
    max_events_per_chapter = int(os.environ.get("MAX_EVENTS_PER_CHAPTER", "20"))
    min_entity_support = int(os.environ.get("MIN_ENTITY_SUPPORT", "2"))
    max_chapter_span = int(os.environ.get("MAX_CHAPTER_SPAN", "10"))
    max_candidate_pairs = int(os.environ.get("MAX_CANDIDATE_PAIRS", "10000"))
    
    # 根据并行配置获取工作线程数
    # 因果分析是IO和CPU混合型任务，使用默认线程配置
    if ParallelConfig.is_enabled():
        max_workers = ParallelConfig.get_max_workers()
    else:
        max_workers = 1
    
    print(f"因果链接器使用工作线程数: {max_workers}")
    
    use_entity_weights = os.environ.get("USE_ENTITY_WEIGHTS", "1").lower() in ["1", "true", "yes"]
    
    # 根据参数选择使用优化模式还是原始模式
    if use_optimized:
        # 使用优化版链接器
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
        # 使用原始版链接器
        return CausalLinker(
            model=model,
            prompt_path=prompt_path,
            api_key=api_key,
            max_workers=3,
            strength_mapping=strength_mapping,
            provider=provider
        )
