import os
import sys
from pathlib import Path

# 将项目根目录添加到系统路径
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from common.interfaces.extractor import AbstractExtractor
from event_extraction.service.enhanced_extractor_service import EnhancedEventExtractor
from common.utils.path_utils import get_config_path
from common.utils.parallel_config import ParallelConfig
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

def provide_extractor() -> AbstractExtractor:
    """提供事件抽取器实例"""
    
    # 检查API提供商环境变量
    provider = os.environ.get("LLM_PROVIDER", "deepseek")
    
    # 根据提供商获取相应的API密钥
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        model = "gpt-4o"
    else:  # deepseek
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        model = "deepseek-chat"  # DeepSeek模型名称
    
    # 使用path_utils获取配置文件路径
    prompt_path = get_config_path("prompt_event_extraction.json")
    
    # 使用增强型事件抽取器
    import multiprocessing
    
    # 根据并行配置选择工作线程数
    # 事件抽取是IO密集型任务，适合使用更多线程
    if ParallelConfig.is_enabled():
        optimal_workers = ParallelConfig.get_max_workers("io_bound")
    else:
        optimal_workers = 1
        
    print(f"事件抽取器使用工作线程数: {optimal_workers}")
    
    return EnhancedEventExtractor(
        model=model,
        prompt_path=prompt_path,
        api_key=api_key,
        max_workers=optimal_workers,  # 根据系统资源和配置动态设置并发数
        provider=provider,
        debug_mode=True  # 启用调试模式以记录详细日志
    )
