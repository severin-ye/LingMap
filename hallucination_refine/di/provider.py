import os
import sys
from pathlib import Path

# 将项目根目录添加到系统路径
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from common.interfaces.refiner import AbstractRefiner
from hallucination_refine.service.har_service import HallucinationRefiner
from common.utils.path_utils import get_config_path
from common.utils.parallel_config import ParallelConfig
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

def provide_refiner() -> AbstractRefiner:
    """提供幻觉修复器实例"""
    
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
    prompt_path = get_config_path("prompt_hallucination_refine.json")
    
    # 根据并行配置获取工作线程数
    # 幻觉修复是IO密集型任务，适合使用更多线程
    if ParallelConfig.is_enabled():
        max_workers = ParallelConfig.get_max_workers("io_bound")
    else:
        max_workers = 1
        
    print(f"幻觉修复器使用工作线程数: {max_workers}")
    
    return HallucinationRefiner(
        model=model,
        prompt_path=prompt_path,
        api_key=api_key,
        max_workers=max_workers,
        max_iterations=2,
        provider=provider
    )
