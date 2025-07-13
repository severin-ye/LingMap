from typing import List, Dict, Any, Optional
import os
import re
from concurrent.futures import ThreadPoolExecutor

from common.interfaces.extractor import AbstractExtractor
from common.models.chapter import Chapter
from common.models.event import EventItem
from event_extraction.domain.base_extractor import BaseExtractor
from event_extraction.repository.llm_client import LLMClient


class EventExtractor(BaseExtractor):
    """Event extractor implementation class that uses LLM to extract events"""
    
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
        Initialize event extractor
        
        Args:
            model: LLM model to use
            prompt_path: Prompt template path
            api_key: API key
            base_url: Custom API base URL
            max_workers: Maximum number of worker threads for parallel processing
            provider: API provider, "openai" or "deepseek"
        """
        if not prompt_path:
            # Import path_utils to get config file path
            from common.utils.path_utils import get_config_path
            prompt_path = get_config_path("prompt_event_extraction.json")
            
        super().__init__(prompt_path)
        
        self.provider = provider
        
        # If no API key provided, try to get from environment variables
        if not api_key:
            if provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
                if not self.api_key:
                    raise ValueError("Please provide OpenAI API key")
            else:  # deepseek
                self.api_key = os.environ.get("DEEPSEEK_API_KEY")
                if not self.api_key:
                    raise ValueError("Please provide DeepSeek API key")
        else:
            self.api_key = api_key
            
        self.model = model
        self.base_url = base_url
        self.max_workers = max_workers
        
        # Initialize LLM client
        self.llm_client = LLMClient(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            provider=self.provider
        )
        
    def extract(self, chapter: Chapter) -> List[EventItem]:
        """
        Extract events from chapter
        
        Args:
            chapter: Chapter data
            
        Returns:
            List of extracted events
        """
        if not chapter.segments:
            # If chapter has no predefined segment text, create segment text
            from common.utils.text_splitter import TextSplitter
            chapter.segments = TextSplitter.split_chapter(chapter.content)
            
        all_events = []
        
        # Use thread pool to process each paragraph in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for segment in chapter.segments:
                future = executor.submit(
                    self.extract_from_segment,
                    segment["text"],
                    chapter.chapter_id,
                    segment["seg_id"]
                )
                futures.append(future)
                
            # Collect all results
            for future in futures:
                events = future.result()
                if events:
                    all_events.extend(events)
                    
        return all_events
    
    def extract_from_segment(self, text: str, chapter_id: str, segment_id: str) -> List[EventItem]:
        """
        Extract events from a single text segment
        
        Args:
            text: Text segment
            chapter_id: Chapter ID
            segment_id: Segment ID
            
        Returns:
            List of extracted events
        """
        prompt = self.format_prompt(text)
        response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
        
        if response["success"] and "json_content" in response:
            return self.parse_response(response["json_content"], chapter_id, segment_id)
        else:
            print(f"Event extraction failed for segment {segment_id}: {response.get('error', 'Unknown error')}")
            return []
            
    def parse_response(self, response: Dict[str, Any], chapter_id: str, segment_id: str) -> List[EventItem]:
        """
        Parse LLM response and extract events
        
        Args:
            response: LLM response
            chapter_id: Chapter ID
            segment_id: Segment ID
            
        Returns:
            List of extracted events
        """
        events = []
        
        # Process various possible formats in response
        if isinstance(response, list):
            # If response is directly an event list
            event_list = response
        elif "events" in response:
            # If response contains events field
            event_list = response["events"]
        else:
            # Assume response itself is a single event
            event_list = [response]
            
        for i, event_data in enumerate(event_list):
            # Check if it's valid event data
            if not isinstance(event_data, dict) or not event_data.get("description"):
                continue
                
            # Generate event ID if not provided
            if not event_data.get("event_id"):
                # Extract chapter part from segment_id, e.g., extract "第一章" from "第一章-1"
                chapter_match = re.search(r'(第[^-]+章)', segment_id)
                chapter_part = chapter_match.group(1) if chapter_match else segment_id.split('-')[0]
                event_data["event_id"] = f"{chapter_part}-{i+1}"
                
            # Ensure chapter_id is set
            event_data["chapter_id"] = chapter_id
            
            # Create EventItem object
            event = EventItem.from_dict(event_data)
            events.append(event)
            
        return events
