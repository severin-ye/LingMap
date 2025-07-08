from abc import ABC
from typing import List, Dict, Any, Tuple, Optional
import json

from common.interfaces.linker import AbstractLinker
from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from common.utils.json_loader import JsonLoader


class BaseLinker(AbstractLinker, ABC):
    """
    # [CN] 因果链接器基类
    # [EN] Base class for causal linkers
    """
    
    def __init__(self, prompt_path: str):
        """
        # [CN] 初始化链接器
        # [EN] Initialize linker
        
        Args:
            # [CN] prompt_path: 提示词模板路径
            # [EN] prompt_path: Path to prompt template
        """
        self.prompt_template = JsonLoader.load_json(prompt_path)
    
    def format_prompt(self, event1: EventItem, event2: EventItem) -> Dict[str, Any]:
        """
        # [CN] 格式化提示模板
        # [EN] Format prompt template
        
        Args:
            # [CN] event1: 第一个事件
            # [EN] event1: First event
            # [CN] event2: 第二个事件
            # [EN] event2: Second event
        Returns:
            # [CN] 格式化后的提示词字典
            # [EN] Formatted prompt dictionary
        """
        system_prompt = self.prompt_template.get('system', '')
        instruction = self.prompt_template.get('instruction', '').format(
            event1=json.dumps(event1.to_dict(), ensure_ascii=False),
            event2=json.dumps(event2.to_dict(), ensure_ascii=False)
        )
        
        return {
            'system': system_prompt,
            'instruction': instruction
        }
    
    def parse_response(self, response: Dict[str, Any], event1_id: str, event2_id: str) -> Optional[CausalEdge]:
        """
        # [CN] 解析LLM响应，提取因果关系
        # [EN] Parse LLM response and extract causal relationship
        
        Args:
            # [CN] response: LLM响应
            # [EN] response: LLM response
            # [CN] event1_id: 第一个事件ID
            # [EN] event1_id: First event ID
            # [CN] event2_id: 第二个事件ID
            # [EN] event2_id: Second event ID
        Returns:
            # [CN] 因果边对象，如果不存在因果关系则返回None
            # [EN] CausalEdge object, or None if no causal relationship exists
        """
        raise NotImplementedError("# [CN] 子类必须实现该方法 # [EN] Subclasses must implement this method")
