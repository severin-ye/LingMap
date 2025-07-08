from abc import ABC
from typing import List, Dict, Any

from common.interfaces.extractor import AbstractExtractor
from common.models.chapter import Chapter
from common.models.event import EventItem
from common.utils.json_loader import JsonLoader


class BaseExtractor(AbstractExtractor, ABC):
    # [CN] 事件抽取器基类
    # [EN] Event extractor base class
    """事件抽取器基类"""
    
    def __init__(self, prompt_path: str):
        """
        # [CN] 初始化抽取器
        # [EN] Initialize extractor
        初始化抽取器
        
        Args:
            # [CN] prompt_path: 提示词模板路径
            # [EN] prompt_path: Prompt template path
            prompt_path: 提示词模板路径
        """
        self.prompt_template = JsonLoader.load_json(prompt_path)
        
    def format_prompt(self, text: str) -> Dict[str, Any]:
        """
        # [CN] 格式化提示模板
        # [EN] Format prompt template
        格式化提示模板
        
        Args:
            # [CN] text: 待处理文本
            # [EN] text: Text to process
            text: 待处理文本
            
        Returns:
            # [CN] 格式化后的提示词字典
            # [EN] Formatted prompt dictionary
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
        # [CN] 解析 LLM 响应，提取事件
        # [EN] Parse LLM response to extract events
        解析 LLM 响应，提取事件
        
        Args:
            # [CN] response: LLM 响应
            # [EN] response: LLM response
            response: LLM 响应
            # [CN] chapter_id: 章节 ID
            # [EN] chapter_id: Chapter ID
            chapter_id: 章节 ID
            # [CN] segment_id: 段落 ID
            # [EN] segment_id: Segment ID
            segment_id: 段落 ID
            
        Returns:
            # [CN] 提取的事件列表
            # [EN] List of extracted events
            提取的事件列表
        """
        # [CN] 子类必须实现该方法
        # [EN] Subclasses must implement this method
        raise NotImplementedError("子类必须实现该方法")
