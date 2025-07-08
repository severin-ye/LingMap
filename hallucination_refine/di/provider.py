import os
import sys
from pathlib import Path

# [CN] 将项目根目录添加到系统路径
# [EN] Add project root directory to system path
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from common.interfaces.refiner import AbstractRefiner
from hallucination_refine.service.har_service import HallucinationRefiner
from common.utils.path_utils import get_config_path
from common.utils.parallel_config import ParallelConfig
from common.utils.thread_monitor import log_thread_usage
from dotenv import load_dotenv

# [CN] 加载.env文件中的环境变量
# [EN] Load environment variables from .env file
load_dotenv()

def provide_refiner() -> AbstractRefiner:
    """
    # [CN] 提供幻觉修复器实例
    # [EN] Provide hallucination refiner instance
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
    prompt_path = get_config_path("prompt_hallucination_refine.json")
    
    # [CN] 根据并行配置获取工作线程数
    # [CN] 幻觉修复是IO密集型任务，适合使用更多线程
    # [EN] Get number of worker threads based on parallel configuration
    # [EN] Hallucination refinement is IO-intensive task, suitable for using more threads
    if ParallelConfig.is_enabled():
        max_workers = ParallelConfig.get_max_workers("io_bound")
    else:
        max_workers = 1
        
    # [CN] 幻觉修复器使用工作线程数
    # [EN] Number of worker threads used by hallucination refiner
    print(f"# [CN] 幻觉修复器使用工作线程数: {max_workers}")
    print(f"# [EN] Number of worker threads used by hallucination refiner: {max_workers}")
    
    # [CN] 记录线程使用情况
    # [EN] Record thread usage
    log_thread_usage("hallucination_refine", max_workers, "io_bound")
    
    return HallucinationRefiner(
        model=model,
        prompt_path=prompt_path,
        api_key=api_key,
        max_workers=max_workers,
        max_iterations=2,
        provider=provider
    )
