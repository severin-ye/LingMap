from abc import ABC
from typing import List, Dict, Any
import json

from common.interfaces.refiner import AbstractRefiner
from common.models.event import EventItem
from common.utils.json_loader import JsonLoader


class BaseRefiner(AbstractRefiner, ABC):
    """幻觉修复基类"""
    
    def __init__(self, prompt_path: str):
        """
        初始化精修器
        
        Args:
            prompt_path: 提示词模板路径
        """
        self.prompt_template = JsonLoader.load_json(prompt_path)
    
    def format_prompt(self, event: EventItem, context: str) -> Dict[str, Any]:
        """
        格式化提示模板
        
        Args:
            event: 待精修的事件
            context: 支持精修的上下文信息
            
        Returns:
            格式化后的提示词字典
        """
        system_prompt = self.prompt_template.get('system', '')
        instruction = self.prompt_template.get('instruction', '').format(
            event=json.dumps(event.to_dict(), ensure_ascii=False),
            context=context
        )
        
        return {
            'system': system_prompt,
            'instruction': instruction
        }
    
    def parse_response(self, response: Dict[str, Any], original_event: EventItem) -> EventItem:
        """
        解析LLM响应，更新事件
        
        Args:
            response: LLM响应
            original_event: 原始事件
            
        Returns:
            精修后的事件
        """
        raise NotImplementedError("子类必须实现该方法")
