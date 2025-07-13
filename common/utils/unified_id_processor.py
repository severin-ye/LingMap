#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified ID processing tool module

Provides integrated ID processing functionality, including:
1. Event ID uniqueness guarantee
2. Graph node ID processing
3. ID format standardization
"""

import re
from typing import Dict, List, Tuple, Any, Set
from common.models.event import EventItem
from common.models.causal_edge import CausalEdge


class UnifiedIdProcessor:
    """Unified ID processor that manages uniqueness and standardization of all IDs in the system"""
    
    @staticmethod
    def check_id_uniqueness(events: List[EventItem]) -> Dict[str, Any]:
        """
        Check ID uniqueness in event list
        
        Args:
            events: Event list
            
        Returns:
            Dictionary containing uniqueness check results, including:
            - unique: Whether all IDs are unique
            - total_count: Total number of events
            - unique_count: Number of unique IDs
            - duplicate_ids: List of duplicate IDs
            - duplicate_counts: Occurrence count for each duplicate ID
        """
        if not events:
            return {
                "unique": True,
                "total_count": 0,
                "unique_count": 0,
                "duplicate_ids": [],
                "duplicate_counts": {}
            }
        
        event_ids = [event.event_id for event in events]
        id_counts = {}
        
        # Calculate occurrence count for each ID
        for event_id in event_ids:
            id_counts[event_id] = id_counts.get(event_id, 0) + 1
        
        # Find duplicate IDs
        duplicate_ids = [id for id, count in id_counts.items() if count > 1]
        duplicate_counts = {id: count for id, count in id_counts.items() if count > 1}
        
        return {
            "unique": len(duplicate_ids) == 0,
            "total_count": len(events),
            "unique_count": len(set(event_ids)),
            "duplicate_ids": duplicate_ids,
            "duplicate_counts": duplicate_counts
        }

    @staticmethod
    def ensure_unique_event_ids(events: List[EventItem]) -> List[EventItem]:
        """
        Ensure uniqueness of event IDs

        Args:
            events: Event list

        Returns:
            Processed event list with unique IDs
        """
        # Create ID counter to track occurrence count of each basic ID
        id_counter: Dict[str, int] = {}
        # Record existing IDs
        existing_ids: Set[str] = set()
        # Return list of events with unique IDs
        unique_events: List[EventItem] = []

        for event in events:
            original_id = event.event_id
            
            # If ID already exists, create unique variant for it
            if original_id in existing_ids:
                if original_id not in id_counter:
                    # First time encountering duplicate, initialize counter to 1
                    id_counter[original_id] = 1
                
                # Increment counter
                id_counter[original_id] += 1
                
                # Create unique ID with sequence number
                unique_id = f"{original_id}_{id_counter[original_id]}"
                
                # Create new event object with unique ID
                unique_event = EventItem(
                    event_id=unique_id,
                    description=event.description,
                    characters=event.characters,
                    treasures=event.treasures,
                    result=event.result,
                    location=event.location,
                    time=event.time,
                    chapter_id=event.chapter_id
                )
                
                unique_events.append(unique_event)
                existing_ids.add(unique_id)
            else:
                # ID is not duplicate, use directly
                existing_ids.add(original_id)
                unique_events.append(event)
        
        return unique_events

    @staticmethod
    def normalize_event_id(event_id: str, chapter_id: str, index: int) -> str:
        """
        Standardize event ID to ensure consistent format

        Args:
            event_id: Original event ID
            chapter_id: Chapter ID
            index: Event index

        Returns:
            Standardized event ID
        """
        # If no event ID, generate based on chapter ID and index
        if not event_id:
            normalized_chapter_id = re.sub(r'[章节]', '', chapter_id)
            try:
                chapter_num = int(normalized_chapter_id)
                return f"E{chapter_num:02d}-{index}"
            except ValueError:
                # If cannot convert to integer, use original value directly
                return f"E{normalized_chapter_id}-{index}"
        
        # If event ID already exists, check format
        if re.match(r'E\d+-\d+', event_id):
            return event_id
        
        # Try to extract chapter and index information from existing ID
        match = re.search(r'第([一二三四五六七八九十百千万零]+|\d+)章-(\d+)', event_id)
        if match:
            chapter_number = match.group(1)
            event_number = match.group(2)
            
            # Process Chinese numbers
            chinese_numbers = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
                              '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
            try:
                if chapter_number in chinese_numbers:
                    chapter_number = chinese_numbers[chapter_number]
                else:
                    chapter_number = int(chapter_number)
            except ValueError:
                # Process compound Chinese numbers, simplified processing here
                chapter_number = 1  # Default value
                
            return f"E{chapter_number:02d}-{event_number}"
        
        # Default case, use original ID
        return event_id

    @staticmethod
    def ensure_unique_node_ids(events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        Ensure unique node IDs in the graph and update edge references
        
        Args:
            events: Event list
            edges: Causal edge list
            
        Returns:
            Processed event list and edge list
        """
        # Create mapping from event ID to event
        event_map = {}
        unique_events = []
        duplicate_ids = set()  # Store duplicate IDs
        id_counter = {}  # Counter to track occurrences of each base ID
        
        # First pass: detect duplicate IDs
        for event in events:
            if event.event_id in event_map:
                duplicate_ids.add(event.event_id)
            else:
                event_map[event.event_id] = event
        
        # Clear event mapping table and rebuild
        event_map.clear()
        
        # Second pass: process all nodes, assign unique IDs to nodes with duplicate IDs
        for event in events:
            original_id = event.event_id
            
            if original_id in duplicate_ids:
                # This is a duplicate ID
                if original_id not in id_counter:
                    id_counter[original_id] = 0
                
                # Increment counter
                id_counter[original_id] += 1
                
                # Create unique ID
                unique_id = f"{original_id}_{id_counter[original_id]}"
                
                # Create new event object
                unique_event = EventItem(
                    event_id=unique_id,
                    description=event.description,
                    characters=event.characters,
                    treasures=event.treasures,
                    result=event.result,
                    location=event.location,
                    time=event.time,
                    chapter_id=event.chapter_id
                )
                
                # Add to mapping
                event_map[unique_id] = unique_event
                unique_events.append(unique_event)
            else:
                # Non-duplicate ID, use directly
                event_map[original_id] = event
                unique_events.append(event)
        
        # Create mapping for updating edges, mapping original IDs to unique ID lists
        original_to_unique_ids = {}
        for unique_event in unique_events:
            event_id = unique_event.event_id
            if "_" in event_id:
                # This is a unique ID with suffix
                original_id = event_id.rsplit("_", 1)[0]
                if original_id not in original_to_unique_ids:
                    original_to_unique_ids[original_id] = []
                original_to_unique_ids[original_id].append(event_id)
            else:
                # Non-duplicate ID, self-mapping
                if event_id not in original_to_unique_ids:
                    original_to_unique_ids[event_id] = [event_id]
        
        # Update edge references
        updated_edges = []
        for edge in edges:
            from_id = edge.from_id
            to_id = edge.to_id
            
            # Get all possible unique IDs
            from_unique_ids = original_to_unique_ids.get(from_id, [from_id])
            to_unique_ids = original_to_unique_ids.get(to_id, [to_id])
            
            # Create edges for each pair of unique IDs
            for from_unique_id in from_unique_ids:
                for to_unique_id in to_unique_ids:
                    if from_unique_id in event_map and to_unique_id in event_map:
                        updated_edge = CausalEdge(
                            from_id=from_unique_id,
                            to_id=to_unique_id,
                            strength=edge.strength,
                            reason=edge.reason
                        )
                        updated_edges.append(updated_edge)
        
        print(f"Processed node ID uniqueness: original events {len(events)}, processed events {len(unique_events)}, duplicate IDs {len(duplicate_ids)}")
        return unique_events, updated_edges

    @staticmethod
    def fix_duplicate_event_ids(input_path: str, output_path: str = None) -> None:
        """
        Fix duplicate event IDs in file
        
        Args:
            input_path: Input file path
            output_path: Output file path, overwrite input file if None
        """
        import json
        
        # If no output path specified, overwrite input file
        if output_path is None:
            output_path = input_path
            
        try:
            # Read file
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                # Assume file contains event list
                try:
                    from common.models.event import EventItem
                    events = [EventItem(**item) if isinstance(item, dict) else item for item in data]
                    unique_events = UnifiedIdProcessor.ensure_unique_event_ids(events)
                    # Convert back to original format
                    result = [event.__dict__ for event in unique_events]
                except Exception as e:
                    print(f"Failed to parse event data: {e}, trying other formats")
                    result = data
            elif isinstance(data, dict) and "events" in data:
                # Assume file contains dictionary with events key
                try:
                    from common.models.event import EventItem
                    events = [EventItem(**item) if isinstance(item, dict) else item for item in data["events"]]
                    unique_events = UnifiedIdProcessor.ensure_unique_event_ids(events)
                    # Update events key
                    data["events"] = [event.__dict__ for event in unique_events]
                    result = data
                except Exception as e:
                    print(f"Failed to parse nested event data: {e}, keeping original data")
                    result = data
            else:
                print("Unrecognized data format, keeping unchanged")
                result = data
                
            # Write back to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
            print(f"Processed file and saved to {output_path}")
            
        except Exception as e:
            import traceback
            print(f"Error processing file: {e}")
            traceback.print_exc()
