from abc import ABC
from typing import List, Dict, Any
import json

from common.interfaces.refiner import AbstractRefiner
from common.models.event import EventItem
from common.utils.json_loader import JsonLoader


class BaseRefiner(AbstractRefiner, ABC):
    """Hallucination refiner base class"""
    
    def __init__(self, prompt_path: str):
        """
        Initialize refiner
        
        Args:
            prompt_path: Prompt template path
        """
        self.prompt_template = JsonLoader.load_json(prompt_path)
    
    def format_prompt(self, event: EventItem, context: str) -> Dict[str, Any]:
        """
        Format prompt template
        
        Args:
            event: Event to be refined
            context: Context information supporting refinement
            
        Returns:
            Formatted prompt dictionary
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
        Parse LLM response to update event
        
        Args:
            response: LLM response
            original_event: Original event
            
        Returns:
            Refined event
        """
        raise NotImplementedError("Subclasses must implement this method")
