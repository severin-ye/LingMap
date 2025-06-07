import os
import sys
from pathlib import Path

# 将项目根目录添加到系统路径
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from common.interfaces.linker import AbstractLinker
from causal_linking.service.linker_service import CausalLinker
from common.utils.path_utils import get_config_path


def provide_linker() -> AbstractLinker:
    """提供因果链接器实例"""
    
    # 检查API提供商环境变量
    provider = os.environ.get("LLM_PROVIDER", "openai")
    
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
    
    return CausalLinker(
        model=model,
        prompt_path=prompt_path,
        api_key=api_key,
        max_workers=3,
        strength_mapping=strength_mapping,
        provider=provider
    )
