#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base causal linker
Implements basic causal linker functionality, this module will be inherited by unified linkers
"""

import json
import os
from typing import Dict, Any, List, Tuple

from common.interfaces.linker import AbstractLinker
from common.models.causal_edge import CausalEdge
from common.models.event import EventItem


class BaseLinker(AbstractLinker):
    """
    Base causal linker
    Provides basic prompt template loading and interface implementation
    """
    
    def __init__(self, prompt_path: str = ""):
        """
        Initialize base linker
        
        Args:
            prompt_path: Prompt template path
        """
        self.prompt_path = prompt_path
        
        # Load prompt template
        if prompt_path and os.path.exists(prompt_path):
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    self.prompt_template = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Cannot parse prompt template {prompt_path}, will use default template")
                self._init_default_prompt_template()
        else:
            self._init_default_prompt_template()
    
    def _init_default_prompt_template(self):
        """Initialize default prompt template"""
        self.prompt_template = {
            "system": "You are a causal relationship analysis assistant. You need to analyze whether there is a causal relationship between two events.",
            "instruction": "Please analyze whether there is a causal relationship between the following two events:\n\nEvent 1: {event1}\n\nEvent 2: {event2}\n\nPlease answer in JSON format with the following fields:\n- has_causal_relation: Boolean value indicating whether a causal relationship exists\n- direction: If a causal relationship exists, please specify the direction (Event 1→Event 2 or Event 2→Event 1)\n- strength: Causal relationship strength (High/Medium/Low)\n- reason: Reason for the relationship's existence or explanation for its absence"
        }
    
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        """
        Identify causal relationships between events
        
        Args:
            events: Event list
            
        Returns:
            List of event causal edges
            
        Note:
            This is an implementation of the AbstractLinker interface, but is empty in the base class
            Subclasses need to override this method to provide concrete implementation
        """
        raise NotImplementedError("Subclasses must implement the link_events method")
    
    def build_dag(self, events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        Build Directed Acyclic Graph (DAG)
        
        Args:
            events: Event list
            edges: Causal edge list
            
        Returns:
            Processed event list and causal edge list
            
        Note:
            This is an implementation of the AbstractLinker interface, but is empty in the base class
            Subclasses need to override this method to provide concrete implementation
        """
        raise NotImplementedError("Subclasses must implement the build_dag method")
    
    def format_prompt(self, event1: EventItem, event2: EventItem) -> Dict[str, str]:
        """
        Format prompt
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            Formatted prompt dictionary, containing system and instruction
        """
        # Format event1 description
        event1_desc = f"""
Event ID: {event1.event_id}
Description: {event1.description}
Related Characters: {', '.join(event1.characters) if event1.characters else 'None'}
Related Treasures: {', '.join(event1.treasures) if event1.treasures else 'None'}
Location: {event1.location or 'Unknown'}
Chapter: {event1.chapter_id or 'Unknown'}
Result: {event1.result or 'Unknown'}
        """.strip()
        
        # Format event2 description
        event2_desc = f"""
Event ID: {event2.event_id}
Description: {event2.description}
Related Characters: {', '.join(event2.characters) if event2.characters else 'None'}
Related Treasures: {', '.join(event2.treasures) if event2.treasures else 'None'}
Location: {event2.location or 'Unknown'}
Chapter: {event2.chapter_id or 'Unknown'}
Result: {event2.result or 'Unknown'}
        """.strip()
        
        # Get system prompt and instruction from template
        system_prompt = self.prompt_template.get("system", "")
        instruction = self.prompt_template.get("instruction", "").format(
            event1=event1_desc,
            event2=event2_desc
        )
        
        return {
            "system": system_prompt,
            "instruction": instruction
        }
