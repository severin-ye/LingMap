from typing import List, Dict, Any, Optional
import json
import os
from concurrent.futures import ThreadPoolExecutor

from common.interfaces.refiner import AbstractRefiner
from common.models.event import EventItem
from hallucination_refine.domain.base_refiner import BaseRefiner
from event_extraction.repository.llm_client import LLMClient


class HallucinationRefiner(BaseRefiner):
    """Hallucination refiner implementation class that uses HAR algorithm to fix possible hallucinations in LLM output"""
    
    def __init__(
        self, 
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: int = 3,
        max_iterations: int = 2,
        provider: str = "openai"
    ):
        """
        Initialize hallucination refiner
        
        Args:
            model: LLM model to use
            prompt_path: Prompt template path
            api_key: OpenAI API key
            base_url: Custom API base URL
            max_workers: Maximum number of worker threads for parallel processing
            max_iterations: Maximum number of iterations to prevent infinite loops
        """
        if not prompt_path:
            # Import path_utils to get config file path
            from common.utils.path_utils import get_config_path
            prompt_path = get_config_path("prompt_hallucination_refine.json")
            
        super().__init__(prompt_path)
        
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
        self.max_iterations = max_iterations
        self.provider = provider
        
        # Initialize LLM client
        self.llm_client = LLMClient(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            provider=self.provider
        )
    
    def refine(self, events: List[EventItem], context: str = "") -> List[EventItem]:
        """
        Perform hallucination detection and refinement on event list
        
        Args:
            events: List of events to be refined
            context: Context information to support refinement
            
        Returns:
            List of refined events
        """
        if not context:
            context = "Please detect possible hallucinations or errors in the following events based on your knowledge of 'A Record of a Mortal's Journey to Immortality'."
            
        refined_events = []
        
        # Use thread pool to process each event in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Optimized implementation - use as_completed to wait for completed tasks
            # Submit all event processing tasks simultaneously
            future_to_event = {executor.submit(self.refine_event, event, context): event for event in events}
            
            print(f"Processing {len(events)} events in parallel using {self.max_workers} worker threads")
            
            # Count completed tasks
            completed = 0
            total = len(events)
            
            # Collect completed task results in real time
            from concurrent.futures import as_completed
            for future in as_completed(future_to_event):
                original_event = future_to_event[future]
                completed += 1
                
                try:
                    refined_event = future.result()
                    refined_events.append(refined_event)
                    
                    # Print progress
                    if completed % max(1, total // 10) == 0 or completed == total:
                        print(f"Hallucination refinement progress: {completed}/{total} ({(completed/total)*100:.1f}%)")
                        
                except Exception as e:
                    print(f"Error processing event {original_event.event_id}: {str(e)}")
                    # If processing fails, keep the original event
                    refined_events.append(original_event)
                    
        return refined_events
    
    def refine_event(self, event: EventItem, context: str) -> EventItem:
        """
        Perform hallucination detection and refinement on a single event
        
        Args:
            event: Event to be refined
            context: Context information to support refinement
            
        Returns:
            Refined event
        """
        current_event = event
        iterations = 0
        
        while iterations < self.max_iterations:
            print(f"Performing refinement iteration {iterations+1} on event {event.event_id}...")
            
            # Format prompt
            prompt = self.format_prompt(current_event, context)
            
            # Call LLM
            response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
            
            if not response["success"] or "json_content" not in response:
                print(f"Refinement request failed for event {event.event_id}: {response.get('error', 'Unknown error')}")
                break
                
            # Parse response
            refined_event = self.parse_response(response["json_content"], current_event)
            
            # Check if there are still hallucinations
            has_hallucination = response["json_content"].get("has_hallucination", False)
            
            if not has_hallucination:
                # If no hallucination detected, return current version
                print(f"Event {event.event_id} refinement completed, no hallucinations")
                return refined_event
                
            # Update event for next iteration
            current_event = refined_event
            iterations += 1
            
            # Print correction information
            if "issues" in response["json_content"]:
                for issue in response["json_content"]["issues"]:
                    print(f"- Correction: {issue.get('field')} from '{issue.get('original')}' to '{issue.get('corrected')}'")
        
        # If maximum iterations reached, return final version
        if iterations == self.max_iterations:
            print(f"Event {event.event_id} reached maximum iterations {self.max_iterations}, returning current version")
            
        return current_event
    
    def parse_response(self, response: Dict[str, Any], original_event: EventItem) -> EventItem:
        """
        Parse LLM response and update event
        
        Args:
            response: LLM response
            original_event: Original event
            
        Returns:
            Refined event
        """
        # Check if response contains refined event
        if "refined_event" in response and isinstance(response["refined_event"], dict):
            # Use refined event to create new EventItem object
            refined_event_data = response["refined_event"]
            
            # Ensure event ID and chapter ID remain unchanged
            refined_event_data["event_id"] = original_event.event_id
            if not refined_event_data.get("chapter_id") and original_event.chapter_id:
                refined_event_data["chapter_id"] = original_event.chapter_id
            
            # For incomplete responses, fill missing fields with original event fields
            original_data = original_event.to_dict()
            for field, value in original_data.items():
                if field not in refined_event_data or refined_event_data[field] is None:
                    refined_event_data[field] = value
                
            return EventItem.from_dict(refined_event_data)
        
        # If no refined event, check if there are correction lists
        if "issues" in response and isinstance(response["issues"], list):
            # Create copy of original event
            refined_data = original_event.to_dict()
            
            # Apply corrections
            for issue in response["issues"]:
                field = issue.get("field")
                corrected = issue.get("corrected")
                
                if field and corrected is not None:
                    # Apply correction to corresponding field
                    refined_data[field] = corrected
                    
            return EventItem.from_dict(refined_data)
            
        # If no correction information, return original event
        return original_event
