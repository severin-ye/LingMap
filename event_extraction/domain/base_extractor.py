from abc import ABC
from typing import List, Dict, Any

from common.interfaces.extractor import AbstractExtractor
from common.models.chapter import Chapter
from common.models.event import EventItem
from common.utils.json_loader import JsonLoader


class BaseExtractor(AbstractExtractor, ABC):
    """事件抽取器基类"""
    
    def __init__(self, prompt_path: str):
        """
        初始化抽取器
        
        Args:
            prompt_path: 提示词模板路径
        """
        self.prompt_template = JsonLoader.load_json(prompt_path)
        
    def format_prompt(self, text: str) -> Dict[str, Any]:
        """
        格式化提示模板
        
        Args:
            text: 待处理文本
            
        Returns:
            格式化后的提示词字典
        """
        system_prompt = self.prompt_template.get('system', '')
        instruction = self.prompt_template.get('instruction', '').format(text=text)
        
        return {
            'system': system_prompt,
            'instruction': instruction
        }
        
    def parse_response(self, response: Dict[str, Any], chapter_id: str, segment_id: str) -> List[EventItem]:
        """
        解析 LLM 响应，提取事件
        
        Args:
            response: LLM 响应
            chapter_id: 章节 ID
            segment_id: 段落 ID
            
        Returns:
            提取的事件列表
        """
        raise NotImplementedError("子类必须实现该方法")
