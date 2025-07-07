from abc import ABC
from typing import List, Dict, Any, Tuple, Optional
import json

from common.interfaces.linker import AbstractLinker
from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from common.utils.json_loader import JsonLoader


class BaseLinker(AbstractLinker, ABC):
    """Causal linker base class"""
    
    def __init__(self, prompt_path: str):
        """
        Initialize linker
        
        Args:
            prompt_path: Prompt template path
        """
        self.prompt_template = JsonLoader.load_json(prompt_path)
    
    def format_prompt(self, event1: EventItem, event2: EventItem) -> Dict[str, Any]:
        """
        Format prompt template
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            Formatted prompt dictionary
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
        Parse LLM response to extract causal relationships
        
        Args:
            response: LLM response
            event1_id: First event ID
            event2_id: Second event ID
            
        Returns:
            Causal edge object, returns None if no causal relationship exists
        """
        raise NotImplementedError("Subclasses must implement this method")
