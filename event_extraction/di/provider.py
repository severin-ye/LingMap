from common.interfaces.extractor import AbstractExtractor
from event_extraction.service.extractor_service import EventExtractor

import os


def provide_extractor() -> AbstractExtractor:
    """提供事件抽取器实例"""
    
    # 检查API提供商环境变量
    provider = os.environ.get("LLM_PROVIDER", "openai")
    
    # 根据提供商获取相应的API密钥
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        model = "gpt-4o"
    else:  # deepseek
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        model = "deepseek-chat"  # DeepSeek模型名称
    
    # 默认提示词模板路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    prompt_path = os.path.join(
        project_root, 
        "common", 
        "config", 
        "prompt_event_extraction.json"
    )
    
    return EventExtractor(
        model=model,
        prompt_path=prompt_path,
        api_key=api_key,
        max_workers=3,
        provider=provider
    )
