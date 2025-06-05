from abc import ABC
from typing import List, Dict, Any, Tuple, Optional
import json

from common.interfaces.linker import AbstractLinker
from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from common.utils.json_loader import JsonLoader


class BaseLinker(AbstractLinker, ABC):
    """因果链接器基类"""
    
    def __init__(self, prompt_path: str):
        """
        初始化链接器
        
        Args:
            prompt_path: 提示词模板路径
        """
        self.prompt_template = JsonLoader.load_json(prompt_path)
    
    def format_prompt(self, event1: EventItem, event2: EventItem) -> Dict[str, Any]:
        """
        格式化提示模板
        
        Args:
            event1: 第一个事件
            event2: 第二个事件
            
        Returns:
            格式化后的提示词字典
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
        解析LLM响应，提取因果关系
        
        Args:
            response: LLM响应
            event1_id: 第一个事件ID
            event2_id: 第二个事件ID
            
        Returns:
            因果边对象，如果不存在因果关系则返回None
        """
        raise NotImplementedError("子类必须实现该方法")
