from abc import ABC
from typing import List, Dict, Any

from common.interfaces.extractor import AbstractExtractor
from common.models.chapter import Chapter
from common.models.event import EventItem
from common.utils.json_loader import JsonLoader


class BaseExtractor(AbstractExtractor, ABC):
    """Event extractor base class"""
    
    def __init__(self, prompt_path: str):
        """
        Initialize extractor
        
        Args:
            prompt_path: Prompt template path
        """
        self.prompt_template = JsonLoader.load_json(prompt_path)
        
    def format_prompt(self, text: str) -> Dict[str, Any]:
        """
        Format prompt template
        
        Args:
            text: Text to process
            
        Returns:
            Formatted prompt dictionary
        """
        system_prompt = self.prompt_template.get('system', '')
        instruction = self.prompt_template.get('instruction', '').format(text=text)
        
        return {
            'system': system_prompt,
            'instruction': instruction
        }
        
    def parse_response(self, response: Dict[str, Any], chapter_id: str, segment_id: str) -> List[EventItem]:
        """
        Parse LLM response to extract events
        
        Args:
            response: LLM response
            chapter_id: Chapter ID
            segment_id: Segment ID
            
        Returns:
            List of extracted events
        """
        raise NotImplementedError("Subclasses must implement this method")
