"""
Enhanced event extraction service

Adds detailed logging and error handling for debugging event extraction issues
"""

from typing import List, Dict, Any, Optional, Union
import os
import re
import json
import time
import random
import multiprocessing
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from common.interfaces.extractor import AbstractExtractor
from common.models.chapter import Chapter
from common.models.event import EventItem
from common.utils.enhanced_logger import EnhancedLogger
from common.utils.unified_id_processor import UnifiedIdProcessor
from event_extraction.domain.base_extractor import BaseExtractor
from event_extraction.repository.llm_client import LLMClient


class EnhancedEventExtractor(BaseExtractor):
    """Enhanced event extractor with detailed logging and error handling"""
    
    def __init__(
        self, 
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: int = 20, # This parameter controls the maximum number of worker threads for parallel processing
        provider: str = "openai",
        debug_mode: bool = False
    ):
        """
        Initialize enhanced event extractor
        
        Args:
            model: LLM model to use
            prompt_path: Prompt template path
            api_key: API key
            base_url: Custom API base URL
            max_workers: Maximum number of worker threads for parallel processing
            provider: API provider, "openai" or "deepseek"
            debug_mode: Whether to enable debug mode
        """
        # Create dedicated logger
        self.logger = EnhancedLogger("event_extractor", log_level="DEBUG" if debug_mode else "INFO")
        self.debug_mode = debug_mode
        
        # Record initialization information
        self.logger.info("Initializing enhanced event extractor", 
                        model=model, 
                        provider=provider,
                        max_workers=max_workers,
                        debug_mode=debug_mode)
        
        if not prompt_path:
            # Import path_utils to get config file path
            from common.utils.path_utils import get_config_path
            prompt_path = get_config_path("prompt_event_extraction.json")
            self.logger.debug(f"Using default prompt template path: {prompt_path}")
            
        super().__init__(prompt_path)
        
        self.provider = provider
        self.model = model
        
        # If no API key provided, try to get from environment variables
        if not api_key:
            if provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
                if not self.api_key:
                    self.logger.error("OpenAI API key not provided")
                    raise ValueError("Please provide OpenAI API key")
            else:  # deepseek
                self.api_key = os.environ.get("DEEPSEEK_API_KEY")
                if not self.api_key:
                    self.logger.error("DeepSeek API key not provided")
                    raise ValueError("Please provide DeepSeek API key")
        else:
            self.api_key = api_key
            
        self.base_url = base_url
        self.max_workers = max_workers
        
        # Initialize LLM client
        self.llm_client = LLMClient(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            provider=self.provider
        )
        
        # Create debug directory
        if debug_mode:
            from pathlib import Path
            from common.utils.path_utils import get_project_root
            
            self.debug_dir = Path(get_project_root()) / "debug" / "event_extraction"
            self.debug_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Debug information will be saved to: {self.debug_dir}")
        
    def extract(self, chapter: Chapter) -> List[EventItem]:
        """
        Extract events from chapter
        
        Args:
            chapter: Chapter data
            
        Returns:
            List of extracted events
        """
        self.logger.info(f"Starting event extraction from chapter", chapter_id=chapter.chapter_id, title=chapter.title)
        
        if not chapter.segments:
            # If chapter has no predefined segment text, create segment text
            from common.utils.text_splitter import TextSplitter
            self.logger.debug("Chapter has no predefined segments, creating segments")
            chapter.segments = TextSplitter.split_chapter(chapter.content)
            self.logger.info(f"Created {len(chapter.segments)} text segments")
        
        # Adjust actual worker thread count based on system resources and settings
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        # Ensure thread count suits CPU hyperthreading capability, minimum 6 threads
        effective_workers = max(6, min(self.max_workers, len(chapter.segments), cpu_count * 5))
        self.logger.info(f"Using {effective_workers} parallel threads to process {len(chapter.segments)} segments (CPU cores: {cpu_count})")
            
        all_events = []
        failed_segments = []
        processed_count = 0
        api_failures = 0
        
        try:
            # Import tqdm for progress bar (if available)
            try:
                from tqdm import tqdm
                has_tqdm = True
            except ImportError:
                has_tqdm = False
                
            # Consider whether to use batch processing
            should_batch = self._should_batch_segments(segments=chapter.segments)
            if should_batch:
                self.logger.info("Enabling batch processing mode, merging multiple short segments for processing")
                # Implement batch processing logic - group every 2-3 segments
                batch_size = 3  # Number of segments to process per batch
                batch_segments = []
                batched_futures = {}
                
                # Use thread pool to process batches in parallel
                with ThreadPoolExecutor(max_workers=effective_workers) as executor:
                    # Submit tasks by batch
                    for i, segment in enumerate(chapter.segments):
                        batch_segments.append(segment)
                        
                        # When reaching batch size or last segment, submit task
                        if len(batch_segments) >= batch_size or i == len(chapter.segments) - 1:
                            # Generate batch ID
                            first_id = batch_segments[0]["seg_id"]
                            last_id = batch_segments[-1]["seg_id"]
                            batch_id = f"{first_id}~{last_id}"
                            
                            # Submit batch processing task
                            future = executor.submit(
                                self._process_segments_in_batch,
                                batch_segments.copy(),
                                chapter.chapter_id
                            )
                            batched_futures[future] = (batch_id, batch_segments.copy())
                            batch_segments = []  # Clear current batch
                    
                    # Set progress bar
                    total = len(batched_futures)
                    if has_tqdm:
                        pbar = tqdm(total=total, desc="Extracting events (batch)", unit="batch")
                    
                    # Process completed batches in real time
                    import concurrent.futures
                    for future in concurrent.futures.as_completed(batched_futures):
                        batch_id, segments = batched_futures[future]
                        processed_count += len(segments)
                        
                        try:
                            events = future.result()
                            if events:
                                self.logger.info(f"Extracted {len(events)} events from batch {batch_id}")
                                all_events.extend(events)
                            else:
                                self.logger.warning(f"No events extracted from batch {batch_id}")
                                api_failures += 1
                                for segment in segments:
                                    failed_segments.append(segment["seg_id"])
                        except Exception as e:
                            self.logger.error(f"Error processing batch {batch_id}: {str(e)}")
                            api_failures += 1
                            for segment in segments:
                                failed_segments.append(segment["seg_id"])
                        
                        # Update progress
                        if has_tqdm:
                            pbar.update(1)
                        else:
                            percent = (len(all_events) / total) * 100
                            self.logger.info(f"Event extraction progress: {len(all_events)}/{total} ({percent:.1f}%)")
                    
                    # Close progress bar
                    if has_tqdm:
                        pbar.close()
            else:
                # Traditional paragraph-by-paragraph parallel processing
                with ThreadPoolExecutor(max_workers=effective_workers) as executor:
                    # Submit all tasks
                    future_to_segment = {
                        executor.submit(
                            self.extract_from_segment,
                            segment["text"],
                            chapter.chapter_id,
                            segment["seg_id"]
                        ): (segment["seg_id"], i)
                        for i, segment in enumerate(chapter.segments)
                    }
                    
                    # Set progress bar
                    total = len(future_to_segment)
                    completed = 0
                    
                    if has_tqdm:
                        pbar = tqdm(total=total, desc="Extracting events", unit="segment")
                    
                    # Process completed tasks in real time, use as_completed to get the first completed task results
                    import concurrent.futures
                    for future in concurrent.futures.as_completed(future_to_segment):
                        seg_id, idx = future_to_segment[future]
                        processed_count += 1
                        
                        try:
                            events = future.result()
                            if events:
                                self.logger.info(f"Extracted {len(events)} events from segment {seg_id}")
                                all_events.extend(events)
                            else:
                                self.logger.warning(f"No events extracted from segment {seg_id}")
                                failed_segments.append(seg_id)
                                api_failures += 1
                                
                                # If API failure rate is too high, switch to batch processing mode midway
                                failure_rate = api_failures / processed_count
                                if not should_batch and processed_count > 5 and self._should_batch_segments(failure_rate=failure_rate):
                                    self.logger.warning(f"High API failure rate ({failure_rate:.2%}), consider using batch processing for subsequent runs")
                                    # Will enable batch processing on next run
                                
                        except Exception as e:
                            self.logger.error(f"Error processing segment {seg_id}: {str(e)}")
                            failed_segments.append(seg_id)
                            api_failures += 1
                        
                        # Update progress
                        completed += 1
                        if has_tqdm:
                            pbar.update(1)
                        else:
                            percent = (completed / total) * 100
                            self.logger.info(f"Event extraction progress: {completed}/{total} ({percent:.1f}%)")
                    
                    # Close progress bar
                    if has_tqdm:
                        pbar.close()
        
        except Exception as e:
            self.logger.error(f"Error occurred during event extraction: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
        # Handle complete failure case - try using backup method
        if len(all_events) == 0 and len(failed_segments) > 0:
            self.logger.warning(f"All segments failed processing, trying backup method...")
            try:
                # Try processing the entire chapter as one large segment
                if len(chapter.content) > 0:
                    self.logger.info("Trying to process entire chapter as one segment")
                    events = self.extract_from_segment(
                        chapter.content, 
                        chapter.chapter_id, 
                        f"{chapter.chapter_id}-full"
                    )
                    if events:
                        self.logger.info(f"Extracted {len(events)} events from entire chapter")
                        all_events.extend(events)
            except Exception as e:
                self.logger.error(f"Backup processing method failed: {str(e)}")
                 # Perform unique ID processing in extraction service (this is the earliest upstream processing point, ensuring all subsequent processing uses unique IDs)
        if all_events:
            # Perform forced ID uniqueness processing
            original_count = len(all_events)
            event_ids = [e.event_id for e in all_events]
            unique_id_count = len(set(event_ids))
            
            if len(event_ids) != unique_id_count:
                self.logger.warning(f"Duplicate IDs detected: total {original_count} events, only {unique_id_count} unique IDs")
                
                # Record duplicate ID details to help debugging
                id_counts = {}
                for e_id in event_ids:
                    id_counts[e_id] = id_counts.get(e_id, 0) + 1
                duplicate_ids = [id for id, count in id_counts.items() if count > 1]
                for dup_id in duplicate_ids[:5]:  # Only record first 5 to avoid long logs
                    self.logger.warning(f"Duplicate ID '{dup_id}' appears {id_counts[dup_id]} times")
                if len(duplicate_ids) > 5:
                    self.logger.warning(f"... {len(duplicate_ids) - 5} more duplicate IDs not shown")
            
            all_events = UnifiedIdProcessor.ensure_unique_event_ids(all_events)
            final_count = len(all_events)
            
            if final_count != original_count:
                self.logger.warning(f"ID processing merged some duplicate events: {original_count} -> {final_count}")
            
            self.logger.info(f"ID uniqueness processing completed, final event count: {final_count}, all downstream processing will use unique IDs")
        
        # Report processing results
        failure_rate = len(failed_segments) / len(chapter.segments) if chapter.segments else 0
        self.logger.info(
            f"Chapter event extraction completed", 
            chapter_id=chapter.chapter_id,
            total_events=len(all_events),
            successful_segments=len(chapter.segments) - len(failed_segments),
            failed_segments=len(failed_segments),
            failure_rate=f"{failure_rate:.2%}"
        )
                    
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
        self.logger.debug(f"Starting to process segment {segment_id}", text_length=len(text))
        
        # Filter text that is too short
        if len(text.strip()) < 10:
            self.logger.warning(f"Segment {segment_id} content too short, skipping processing")
            return []
        
        try:
            # Format prompt
            prompt = self.format_prompt(text)
            
            # Add more detailed format description and extraction guidance
            if isinstance(prompt, dict) and "instruction" in prompt and "output_format" in self.prompt_template:
                # Add clear format guidance
                format_guidance = (
                    f"\n\nOutput format: {self.prompt_template['output_format']}\n"
                    f"Important note: Please ensure the returned content is valid JSON format."
                    f"If there are no obvious events in the paragraph, please try to extract any possible plot developments or state changes."
                    f"Please ensure each event contains at least 'event_id', 'description', 'result', 'characters' fields."
                )
                prompt["instruction"] += format_guidance
            
            # Save debugging information
            if self.debug_mode:
                debug_file = self.debug_dir / f"{segment_id}_prompt.json"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump(prompt, f, ensure_ascii=False, indent=2)
            
            # Call LLM API (with retry mechanism)
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                self.logger.debug(f"Sending LLM request for segment {segment_id} (attempt {retry_count+1}/{max_retries})")
                response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
                
                if response["success"] and "json_content" in response:
                    break  # Successfully got response
                
                error_msg = response.get('error', 'Unknown error')
                self.logger.warning(f"Segment {segment_id} API call attempt {retry_count+1} failed: {error_msg}")
                last_error = error_msg
                retry_count += 1
                
                # Add random delay
                delay = random.uniform(1, 3)
                time.sleep(delay)
            
            # Save API response
            if self.debug_mode and "json_content" in response:
                debug_file = self.debug_dir / f"{segment_id}_response.json"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump(response, f, ensure_ascii=False, indent=2)
            
            if response["success"] and "json_content" in response:
                # Parse response
                events = self.parse_response(response["json_content"], chapter_id, segment_id)
                self.logger.debug(f"Segment {segment_id} extracted {len(events)} events")
                
                # Save parsed events
                if self.debug_mode:
                    debug_file = self.debug_dir / f"{segment_id}_events.json"
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        json.dump([event.to_dict() for event in events], f, ensure_ascii=False, indent=2)
                
                return events
            else:
                error_msg = last_error or response.get('error', 'Unknown error')
                self.logger.error(f"API call failed for segment {segment_id}: {error_msg}")
                return []
                
        except Exception as e:
            self.logger.error(f"Exception occurred while processing segment {segment_id}", error=str(e), traceback=traceback.format_exc())
            return []
            
    def _should_batch_segments(self, segments=None, failure_rate=None) -> bool:
        """
        Determine whether segments should be processed in batches
        
        Args:
            segments: List of segments to process
            failure_rate: Current API call failure rate
            
        Returns:
            Whether batch processing should be enabled
        """
        # Priority batch processing conditions
        # 1. If there are many segments with moderate text length, batch processing can improve efficiency
        if segments and len(segments) > 3:
            # Calculate average segment length
            avg_length = sum(len(s.get('text', '')) for s in segments) / len(segments)
            # If average length is moderate (less than 600 characters), enable batch processing
            if avg_length < 600:
                self.logger.debug(f"Enabling batch processing: average segment length ({avg_length:.1f} chars) suitable for batching, total segments: {len(segments)}")
                return True
                
        # 2. If API failure rate is high, try batch processing to reduce API call frequency
        if failure_rate is not None and failure_rate > 0.2:
            self.logger.debug(f"Enabling batch processing: API failure rate ({failure_rate:.2%}) is high")
            return True
            
        # 3. If total segments exceed 30, automatically enable batch processing to reduce API load
        if segments and len(segments) > 30:
            self.logger.debug(f"Enabling batch processing: too many segments ({len(segments)} segments)")
            return True
        
        # Get environment variable configuration, if user explicitly set to enable batch processing
        import os
        if os.environ.get("ENABLE_BATCH_PROCESSING", "").lower() in ["true", "1", "yes"]:
            self.logger.debug("Enabling batch processing: environment variable ENABLE_BATCH_PROCESSING set to enable")
            return True
            
        return False  # Default to not enable batch processing

    def _process_segments_in_batch(self, segments: List[Dict], chapter_id: str) -> List[EventItem]:
        """
        Process multiple segments in batches
        Combine multiple small segments into one request to reduce API call frequency
        
        Args:
            segments: List of segments to process
            chapter_id: Chapter ID
            
        Returns
            List of extracted events
        """
        # To improve processing efficiency, ensure appropriate batch size
        # If there are too many segments, prompts may become too long, split into smaller batches
        MAX_BATCH_SIZE = 5  # Maximum batch size
        MAX_CHARS = 4000    # Maximum characters per batch
        
        if len(segments) > MAX_BATCH_SIZE:
            # Split segments into multiple small batches for processing
            self.logger.info(f"Number of segments ({len(segments)}) exceeds batch limit ({MAX_BATCH_SIZE}), splitting into multiple small batches")
            result_events = []
            # Split segments by MAX_BATCH_SIZE
            for i in range(0, len(segments), MAX_BATCH_SIZE):
                batch = segments[i:i+MAX_BATCH_SIZE]
                batch_events = self._process_segments_in_batch(batch, chapter_id)
                if batch_events:
                    result_events.extend(batch_events)
            return result_events
            
        # Check total character count of batch
        total_chars = sum(len(s.get('text', '')) for s in segments)
        if total_chars > MAX_CHARS:
            self.logger.info(f"Total batch characters ({total_chars}) exceed limit ({MAX_CHARS}), splitting into smaller batches")
            # Find an appropriate split point to make both parts have similar character counts
            mid = len(segments) // 2
            batch1 = segments[:mid]
            batch2 = segments[mid:]
            
            # Recursively process two batches
            events1 = self._process_segments_in_batch(batch1, chapter_id)
            events2 = self._process_segments_in_batch(batch2, chapter_id)
            
            # Merge results
            return events1 + events2
        
        # Merge text using separators to clearly distinguish different segments
        segment_texts = []
        for i, segment in enumerate(segments):
            # Add segment numbers and separators to help the model identify different segments
            segment_texts.append(f"[Segment {i+1}]\n{segment['text']}\n")
        
        combined_text = "\n---\n".join(segment_texts)
        segment_ids = [s["seg_id"] for s in segments]
        combined_id = f"{segment_ids[0]}~{segment_ids[-1]}"
        
        self.logger.debug(f"Batch processing segments {combined_id}, total {len(segments)} segments, total characters: {len(combined_text)}")
        
        # Extract events
        all_batch_events = self.extract_from_segment(combined_text, chapter_id, combined_id)
        
        # No events extracted, return empty list directly
        if not all_batch_events:
            return []
            
        # Intelligently assign events to original segments
        result_events = []
        
        # Based on keywords in event descriptions, try to map events to corresponding segments
        for event in all_batch_events:
            # Look for segment number indicators in event description, such as "[Segment 1]", "Segment 2", etc.
            segment_idx = None
            desc = event.description.lower()
            
            # Check if there are explicit segment markers
            for i in range(len(segments)):
                markers = [f"[segment{i+1}]", f"segment{i+1}", f"segment {i+1}"]
                for marker in markers:
                    if marker.lower() in desc:
                        segment_idx = i
                        break
                if segment_idx is not None:
                    break
            
            # If no explicit markers found, try content-based matching
            if segment_idx is None:
                # Find the segment that best matches the event description among all segments
                max_overlap = 0
                best_idx = 0
                
                for i, segment in enumerate(segments):
                    # Calculate overlap between event description and segment content
                    text = segment["text"].lower()
                    # Simple calculation of overlapping word count
                    words = set(desc.split()) & set(text.split())
                    overlap = len(words)
                    
                    if overlap > max_overlap:
                        max_overlap = overlap
                        best_idx = i
                
                segment_idx = best_idx
            
            # Update event ID to reflect the correct segment
            if segment_idx is not None:
                segment = segments[segment_idx]
                event_id_parts = event.event_id.split('-')
                if len(event_id_parts) >= 2:
                    new_id = f"{segment['seg_id'].split('-')[0]}-{event_id_parts[-1]}"
                    event.event_id = new_id
                    
            result_events.append(event)
        
        return result_events
            
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
        self.logger.debug(f"Parsing response for segment {segment_id}")
        events = []
        
        try:
            # Try to process various possible response formats
            event_list = []
            
            # Process various possible formats in the response
            if isinstance(response, list):
                # If response is directly an event list
                event_list = response
                self.logger.debug("Response is in event list format")
            elif isinstance(response, dict):
                if "events" in response:
                    # If response contains an events field
                    event_list = response["events"]
                    self.logger.debug("Response is in dictionary format containing events field")
                elif any(key in response for key in ["description", "event_id", "characters"]):
                    # If response itself looks like an event
                    event_list = [response]
                    self.logger.debug("Response itself is in single event format")
                else:
                    # Process other possible dictionary formats, look for possible event lists
                    for key, value in response.items():
                        if isinstance(value, list) and len(value) > 0:
                            # Check if the first element of the list looks like an event object
                            first_item = value[0]
                            if isinstance(first_item, dict) and any(k in first_item for k in ["description", "event_id"]):
                                event_list = value
                                self.logger.debug(f"Found event list from '{key}' field in response")
                                break
            
            # If no event list found, try to create default event
            if not event_list:
                self.logger.warning(f"No valid event list format found for segment {segment_id}, trying to build default event")
                
                # Try to extract text content from response as event description
                description = ""
                if isinstance(response, dict):
                    # Look for fields that might contain descriptions
                    for field in ["content", "text", "summary", "description"]:
                        if field in response and isinstance(response[field], str) and len(response[field]) > 10:
                            description = response[field]
                            break
                elif isinstance(response, str) and len(response) > 10:
                    description = response
                
                if description:
                    # Create default event
                    default_event = {
                        "event_id": f"{segment_id}-1",
                        "description": description[:200],  # Limit length
                        "characters": [],
                        "result": "Unclear",
                        "chapter_id": chapter_id
                    }
                    event_list = [default_event]
                    self.logger.debug("Built default event")
                    
            # Process each event
            for i, event_data in enumerate(event_list):
                # Check if it's valid event data
                if not isinstance(event_data, dict):
                    self.logger.warning(f"Skipping non-dictionary format event data: {event_data}")
                    continue
                    
                # Ensure event contains description
                if not event_data.get("description"):
                    self.logger.warning(f"Skipping event data missing description: {event_data}")
                    continue
                    
                # Generate event ID if not provided
                if not event_data.get("event_id"):
                    # Extract chapter part from segment_id, e.g. extract "第一章" from "第一章-1"
                    chapter_match = re.search(r'(第[^-~]+章)', segment_id)
                    chapter_part = chapter_match.group(1) if chapter_match else segment_id.split('-')[0]
                    
                    # Use UnifiedIdProcessor to standardize ID
                    event_id = f"{chapter_part}-{i+1}"
                    normalized_id = UnifiedIdProcessor.normalize_event_id(event_id, chapter_id, i+1)
                    
                    event_data["event_id"] = normalized_id
                    self.logger.debug(f"Generated standardized ID for event: {event_data['event_id']}")
                    
                # Ensure necessary fields exist
                required_fields = {
                    "chapter_id": chapter_id,
                    "characters": [],
                    "result": "Unknown",
                    "location": "Unspecified",
                    "time": "Unspecified"
                }
                
                for field, default_value in required_fields.items():
                    if field not in event_data or not event_data[field]:
                        event_data[field] = default_value
                
                # Create EventItem object
                try:
                    event = EventItem.from_dict(event_data)
                    events.append(event)
                    short_desc = (event.description[:30] + "...") if len(event.description) > 30 else event.description
                    self.logger.debug(f"Successfully created event: {event.event_id} - {short_desc}")
                except Exception as e:
                    self.logger.error(f"Failed to create event object", error=str(e), event_data=event_data)
        except Exception as e:
            self.logger.error(f"Exception occurred while parsing response", error=str(e), traceback=traceback.format_exc())
            
        return events
