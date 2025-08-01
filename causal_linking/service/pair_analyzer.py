#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event pair causal relationship analyzer
Responsible for analyzing causal relationships between event pairs, including:
1. Generate question prompts
2. Call LLM to analyze causal relationships
3. Parse LLM responses
"""

import os
from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor

from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from event_extraction.repository.llm_client import LLMClient


class PairAnalyzer:
    """
    Event pair causal relationship analyzer
    Responsible for analyzing causal relationships between event pairs
    """
    
    def __init__(
        self,
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: int = 3,
        provider: str = "openai"
    ):
        """
        Initialize event pair analyzer
        
        Args:
            model: LLM model to use
            prompt_path: Prompt template path
            api_key: API key
            base_url: Custom API base URL
            max_workers: Maximum number of worker threads for parallel processing
            provider: API provider, such as "openai" or "deepseek"
        """
        # If no API key provided, try to get from environment variables
        if not api_key:
            if provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
                if not self.api_key:
                    raise ValueError("Please provide OpenAI API key")
            elif provider == "deepseek":
                self.api_key = os.environ.get("DEEPSEEK_API_KEY")
                if not self.api_key:
                    raise ValueError("Please provide DeepSeek API key")
            else:
                raise ValueError(f"Unsupported API provider: {provider}")
        else:
            self.api_key = api_key
        
        self.model = model
        self.base_url = base_url
        self.max_workers = max_workers
        self.provider = provider
        self.prompt_path = prompt_path
        
        # Load prompt template
        self.prompt_template = self._load_prompt_template(prompt_path)
        
        # Initialize LLM client
        self.llm_client = LLMClient(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            provider=self.provider
        )
    
    def _load_prompt_template(self, prompt_path: str) -> Dict[str, str]:
        """
        Load prompt template
        
        Args:
            prompt_path: Prompt template file path
            
        Returns:
            Prompt template dictionary
        """
        import json
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to load prompt template: {e}")
            return {
                "system": "You are a causal relationship analysis assistant. You need to analyze whether there is a causal relationship between two events.",
                "instruction": "Please analyze whether there is a causal relationship between the following two events:\n\nEvent 1: {event1}\n\nEvent 2: {event2}\n\nPlease answer in JSON format with the following fields:\n- has_causal_relation: Boolean value indicating whether a causal relationship exists\n- direction: If a causal relationship exists, please specify the direction (Event 1→Event 2 or Event 2→Event 1)\n- strength: Causal relationship strength (High/Medium/Low)\n- reason: Reason for the relationship's existence or explanation for its absence"
            }
    
    def analyze_batch(self, event_pairs: List[Tuple[EventItem, EventItem]]) -> List[CausalEdge]:
        """
        Batch analyze causal relationships of event pairs
        
        Args:
            event_pairs: List of event pairs
            
        Returns:
            List of causal edges
        """
        edges = []
        
        # Use thread pool to process event pairs in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for event1, event2 in event_pairs:
                future = executor.submit(self.analyze_pair, event1, event2)
                futures.append(future)
            
            # Collect all results
            for future in futures:
                edge = future.result()
                if edge:
                    edges.append(edge)
        
        return edges
    
    def analyze_pair(self, event1: EventItem, event2: EventItem) -> Optional[CausalEdge]:
        """
        Analyze causal relationship of one event pair
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            Causal edge object, returns None if no causal relationship exists
        """
        # Format prompt
        prompt = self.format_prompt(event1, event2)
        
        # Call LLM
        response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
        
        if not response["success"] or "json_content" not in response:
            print(f"Causal analysis failed for events {event1.event_id} and {event2.event_id}: {response.get('error', 'Unknown error')}")
            return None
            
        # Parse response
        edge = self.parse_response(response["json_content"], event1.event_id, event2.event_id)
        
        if edge:
            print(f"Found causal relationship: {edge.from_id} -> {edge.to_id}, strength: {edge.strength}")
            
        return edge
    
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
        # Check if causal relationship exists
        has_causal = response.get("has_causal_relation", False)
        if not has_causal:
            return None
        
        # Get causal direction
        direction = response.get("direction", "")
        
        if direction == "event1->event2":
            from_id = event1_id
            to_id = event2_id
        elif direction == "event2->event1":
            from_id = event2_id
            to_id = event1_id
        else:
            print(f"Unable to parse causal direction: {direction}")
            return None
        
        # Get causal strength and reason
        strength = response.get("strength", "medium")
        reason = response.get("reason", "")
        
        return CausalEdge(
            from_id=from_id,
            to_id=to_id,
            strength=strength,
            reason=reason
        )
