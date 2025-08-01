#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Candidate event pair generator
Implements different candidate event pair generation strategies:
1. Same chapter event pairing
2. Entity co-occurrence event pairing
3. Merge strategy results
"""

import math
import itertools
from typing import List, Dict, Tuple, DefaultDict, Set
from collections import defaultdict

from common.models.event import EventItem


class CandidateGenerator:
    """
    Candidate event pair generator
    Implements multiple different candidate event pair generation strategies
    """
    
    def __init__(
        self,
        max_events_per_chapter: int = 50,  # Significantly increase event count limit per chapter
        min_entity_support: int = 3,
        max_chapter_span: int = 10,
        max_candidate_pairs: int = 150,  # Appropriately increase maximum candidate pairs limit
        use_entity_weights: bool = True,
        max_pairs_per_entity: int = 15,  # Increase maximum event pairs generated per entity
        connection_density: float = 0.2  # New parameter: controls connection density coefficient (between 0-1)
    ):
        """
        Initialize event pair generator
        
        Args:
            max_events_per_chapter: Maximum events processed per chapter
            min_entity_support: Minimum entity support, entities below this value are not considered for pairing
            max_chapter_span: Maximum chapter span for cross-chapter pairing
            max_candidate_pairs: Maximum number of candidate event pairs
            use_entity_weights: Whether to use entity frequency inverse weights
            max_pairs_per_entity: Maximum event pairs generated per entity
            connection_density: Connection density coefficient, controls density of generated event pairs
        """
        self.max_events_per_chapter = max_events_per_chapter
        self.min_entity_support = min_entity_support
        self.max_chapter_span = max_chapter_span
        self.max_candidate_pairs = max_candidate_pairs
        self.use_entity_weights = use_entity_weights
        self.max_pairs_per_entity = max_pairs_per_entity
        self.connection_density = min(1.0, max(0.1, connection_density))  # Ensure between 0.1-1
    
    def generate_candidates(self, events: List[EventItem]) -> List[Tuple[str, str]]:
        """
        Generate candidate event pairs
        
        Args:
            events: Event list
            
        Returns:
            Event ID pair list [(event_id1, event_id2), ...]
        """
        # Display current configuration parameters
        print(f"Candidate generator config: max events per chapter={self.max_events_per_chapter}, min entity support={self.min_entity_support}, "
              f"max chapter span={self.max_chapter_span}, max candidate pairs={self.max_candidate_pairs}, "
              f"max pairs per entity={self.max_pairs_per_entity}")
        
        # 1. Same chapter event pairing
        print("Executing strategy 1: Same chapter event pairing...")
        chapter_pairs = self._generate_same_chapter_pairs(events)
        print(f"Same chapter event pairing completed, generated {len(chapter_pairs)} candidate pairs")
        
        # 2. Entity co-occurrence cross-chapter pairing
        print("Executing strategy 2: Entity co-occurrence cross-chapter pairing...")
        entity_pairs = self._generate_entity_co_occurrence_pairs(events)
        print(f"Entity co-occurrence cross-chapter pairing completed, generated {len(entity_pairs)} candidate pairs")
        
        # 3. Merge candidate event pairs and remove duplicates
        candidate_pairs = self._merge_candidate_pairs(chapter_pairs, entity_pairs)
        print(f"Merged and deduplicated candidate event pairs: {len(candidate_pairs)} pairs")
        
        return candidate_pairs
    
    def _generate_same_chapter_pairs(self, events: List[EventItem]) -> List[Tuple[str, str]]:
        """
        Generate same chapter event pairs
        
        Args:
            events: Event list
            
        Returns:
            Event ID pair list [(event_id1, event_id2), ...]
        """
        # Group events by chapter
        chapter_events: Dict[str, List[EventItem]] = defaultdict(list)
        for event in events:
            if event.chapter_id:
                chapter_events[event.chapter_id].append(event)
        
        # Generate same chapter event pairs
        pairs = []
        for chapter_id, chapter_event_list in chapter_events.items():
            chapter_size = len(chapter_event_list)
            
            # Limit events processed per chapter, but maintain a high threshold
            if chapter_size > self.max_events_per_chapter:
                print(f"Warning: Chapter {chapter_id} event count {chapter_size} exceeds limit {self.max_events_per_chapter}, will be truncated")
                chapter_event_list = chapter_event_list[:self.max_events_per_chapter]
                chapter_size = len(chapter_event_list)
            
            # Dynamically adjust connection density based on chapter size
            # Small chapters (less than 10 events): maintain full connectivity
            # Medium chapters (10-30 events): reduce connections based on density coefficient
            # Large chapters (30+ events): further reduce density
            if chapter_size <= 10:
                density_factor = 1.0  # Maintain full connectivity
            elif chapter_size <= 30:
                density_factor = self.connection_density * 1.5  # Appropriately increase connection density for small chapters
            else:
                density_factor = self.connection_density  # Large chapters use standard density
            
            # Calculate target connection count
            all_possible_pairs = (chapter_size * (chapter_size - 1)) // 2
            target_pairs_count = max(10, int(all_possible_pairs * density_factor))
            
            # Generate chapter-internal pairwise combinations, normalize direction (maintain index order)
            chapter_pairs = []
            # Prioritize connecting adjacent events (temporal proximity more likely to have causal relationships)
            for i in range(len(chapter_event_list) - 1):
                event1 = chapter_event_list[i]
                for j in range(i + 1, min(i + 4, len(chapter_event_list))):
                    event2 = chapter_event_list[j]
                    if event1.event_id < event2.event_id:
                        chapter_pairs.append((event1.event_id, event2.event_id))
                    else:
                        chapter_pairs.append((event2.event_id, event1.event_id))
            
            # If target count not yet reached, add random event pairs
            if len(chapter_pairs) < target_pairs_count:
                # Combine all possible event pairs
                all_pairs = []
                for event1, event2 in itertools.combinations(chapter_event_list, 2):
                    pair = (event1.event_id, event2.event_id) if event1.event_id < event2.event_id else (event2.event_id, event1.event_id)
                    if pair not in chapter_pairs:  # Avoid duplicating already added adjacent event pairs
                        all_pairs.append(pair)
                
                # Randomly select remaining event pairs
                import random
                remaining_needed = min(target_pairs_count - len(chapter_pairs), len(all_pairs))
                if remaining_needed > 0 and all_pairs:
                    random_pairs = random.sample(all_pairs, remaining_needed)
                    chapter_pairs.extend(random_pairs)
            
            pairs.extend(chapter_pairs)
            print(f"Chapter {chapter_id}: {chapter_size} events, generated {len(chapter_pairs)} connections (target: {target_pairs_count}, max possible: {all_possible_pairs})")
        
        return list(set(pairs))  # Remove duplicates
    
    def _get_chapter_num(self, event: EventItem) -> int:
        """
        Extract chapter number from event
        
        Args:
            event: Event object
            
        Returns:
            Chapter number, returns 0 if cannot be parsed
        """
        if not event.chapter_id:
            return 0
            
        try:
            # Process different chapter ID formats
            chapter_id = event.chapter_id
            # Process "第X章" format
            if "第" in chapter_id and "章" in chapter_id:
                chapter_id = chapter_id.replace("第", "").replace("章", "")
            # Process "EXX-Y" format (like E01-2)
            elif chapter_id.startswith("E") and "-" in chapter_id:
                chapter_id = chapter_id.split("-")[0][1:]
            
            # Try to convert to integer
            return int(chapter_id)
        except (ValueError, TypeError):
            return 0
    
    def _generate_entity_co_occurrence_pairs(self, events: List[EventItem]) -> List[Tuple[str, str]]:
        """
        Generate cross-chapter event pairs based on entity co-occurrence
        
        Args:
            events: Event list
            
        Returns:
            Event ID pair list [(event_id1, event_id2), ...]
        """
        # Create entity to event inverted index
        character_to_events: DefaultDict[str, List[EventItem]] = defaultdict(list)
        treasure_to_events: DefaultDict[str, List[EventItem]] = defaultdict(list)
        
        # Build entity-event inverted index
        for event in events:
            for character in event.characters:
                character_to_events[character].append(event)
            for treasure in event.treasures:
                treasure_to_events[treasure].append(event)
        
        # Calculate entity frequency
        entity_freq = {
            entity: len(events_list) 
            for entity, events_list in {**character_to_events, **treasure_to_events}.items()
        }
        
        # Entity support filtering
        candidate_entities = {
            entity: events_list 
            for entity, events_list in {**character_to_events, **treasure_to_events}.items() 
            if len(events_list) >= self.min_entity_support
        }
        
        if not self.use_entity_weights:
            # Don't use weights, simply generate pairs
            pairs = []
            for entity, entity_events in candidate_entities.items():
                # Sort events by chapter_id to apply chapter span limits
                entity_events.sort(key=lambda e: e.chapter_id if e.chapter_id else "")
                
                for event1, event2 in itertools.combinations(entity_events, 2):
                    # Check chapter span
                    if self._check_chapter_span(event1, event2):
                        # Ensure event pairs are sorted by ID to avoid duplicates
                        if event1.event_id < event2.event_id:
                            pairs.append((event1.event_id, event2.event_id))
                        else:
                            pairs.append((event2.event_id, event1.event_id))
            
            return list(set(pairs))  # Remove duplicates and return
        else:
            # Calculate entity inverse weights: higher frequency, lower weight
            # Use weight = 1 / log(frequency + 1.1) formula
            entity_weights = {
                entity: 1.0 / math.log(freq + 1.1)  # Avoid log(1) = 0
                for entity, freq in entity_freq.items()
            }
            
            print(f"Entity frequency examples: {dict(list(entity_freq.items())[:5])}")
            print(f"Entity weight examples: {dict(list(entity_weights.items())[:5])}")
            
            # Use weights, generate weighted pairs and sort
            weighted_pairs = []
            # Sort entities by frequency, process low-frequency entities first (lower frequency more likely to contain key information)
            sorted_entities = sorted(
                candidate_entities.items(),
                key=lambda x: entity_freq[x[0]]  # Sort by frequency
            )
            
            # Calculate total entity pair quota that can be generated
            total_quota = min(self.max_candidate_pairs * 2, sum(1 for e in candidate_entities.values() for _ in itertools.combinations(e, 2)))
            remaining_quota = total_quota
            
            for entity, entity_events in sorted_entities:
                # Sort events by chapter_id to apply chapter span limits
                entity_events.sort(key=lambda e: e.chapter_id if e.chapter_id else "")
                
                entity_weight = entity_weights[entity]
                entity_freq_count = entity_freq[entity]
                
                # Dynamically adjust quota for each entity, ensure rare entities have higher quota
                # But reverse logic for high-frequency entities: protagonist-level entities although appearing frequently, are often key story drivers
                if entity_freq_count > 30:  # Very high-frequency protagonist entities
                    # Moderately increase protagonist quota, but still maintain relative limits
                    entity_quota = min(int(self.max_pairs_per_entity * 0.7), 12)
                    # Process them by chapter, select several key events per chapter
                    chapter_groups = {}
                    for event in entity_events:
                        if event.chapter_id:
                            if event.chapter_id not in chapter_groups:
                                chapter_groups[event.chapter_id] = []
                            chapter_groups[event.chapter_id].append(event)
                    
                    # Select several key event points per chapter
                    chapter_events = []
                    for chapter_id, events_list in chapter_groups.items():
                        if len(events_list) > 3:
                            # Select chapter start, middle and end events
                            chapter_events.append(events_list[0])  # First
                            chapter_events.append(events_list[len(events_list)//2])  # Middle
                            chapter_events.append(events_list[-1])  # Last
                        else:
                            chapter_events.extend(events_list)
                    
                    # Replace original full events with filtered key events
                    entity_events = chapter_events
                    print(f"Entity '{entity}' has very high frequency ({entity_freq_count}), filtered to {len(entity_events)} key event points")
                    
                elif entity_freq_count > 15:  # Important supporting characters
                    entity_quota = min(int(self.max_pairs_per_entity * 0.8), 10)
                else:  # Common or rare entities (often have more information value)
                    entity_quota = self.max_pairs_per_entity
                
                # Calculate total possible pairs for this entity
                possible_entity_pairs = len(entity_events) * (len(entity_events) - 1) // 2
                
                # Limit event pairs generated per entity, but ensure sufficient samples
                entity_pairs_count = 0
                valid_combinations = []
                
                # Pre-collect all valid event pairs
                for event1, event2 in itertools.combinations(entity_events, 2):
                    if self._check_chapter_span(event1, event2):
                        # Determine event pair order
                        pair = (event1, event2) if event1.event_id < event2.event_id else (event2, event1)
                        valid_combinations.append(pair)
                
                # Prioritize event pairs with close chapters (higher probability)
                valid_combinations.sort(key=lambda pair: abs(self._get_chapter_num(pair[0]) - self._get_chapter_num(pair[1])))
                
                # Select event pairs based on quota
                quota_to_use = min(entity_quota, len(valid_combinations))
                for event1, event2 in valid_combinations[:quota_to_use]:
                    # Ensure event pairs are sorted by ID
                    if event1.event_id < event2.event_id:
                        weighted_pairs.append((event1.event_id, event2.event_id, entity_weight))
                    else:
                        weighted_pairs.append((event2.event_id, event1.event_id, entity_weight))
                    
                    entity_pairs_count += 1
                    remaining_quota -= 1
                
                print(f"Entity '{entity}' (frequency:{entity_freq_count}): added {entity_pairs_count}/{possible_entity_pairs} event pairs (quota:{quota_to_use})")
                
                # If total quota is exhausted, stop processing more entities
                if remaining_quota <= 0:
                    print(f"Entity event pair generation quota exhausted, stop processing more entities")
                    break
            
            # Merge weights for event pairs sharing multiple entities
            pair_weights = {}
            for id1, id2, weight in weighted_pairs:
                pair_key = (id1, id2)
                if pair_key in pair_weights:
                    pair_weights[pair_key] += weight  # Accumulate weights
                else:
                    pair_weights[pair_key] = weight
            
            # Sort by weight
            sorted_pairs = sorted(
                [(id1, id2) for (id1, id2) in pair_weights.keys()],
                key=lambda pair: pair_weights[pair],
                reverse=True  # High weight priority
            )
            
            return sorted_pairs
    
    def _check_chapter_span(self, event1: EventItem, event2: EventItem) -> bool:
        """
        Check if chapter span between two events is within allowed range
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            Returns True if chapter span is valid, otherwise False
        """
        if event1.chapter_id and event2.chapter_id:
            try:
                ch1 = int(event1.chapter_id.replace("第", "").replace("章", ""))
                ch2 = int(event2.chapter_id.replace("第", "").replace("章", ""))
                if abs(ch1 - ch2) > self.max_chapter_span:
                    return False
            except (ValueError, AttributeError):
                # If chapter ID is not numeric format, skip span check
                pass
        return True
    
    def _merge_candidate_pairs(
        self, 
        chapter_pairs: List[Tuple[str, str]], 
        entity_pairs: List[Tuple[str, str]]
    ) -> List[Tuple[str, str]]:
        """
        Merge candidate event pairs from two sources and remove duplicates
        
        Args:
            chapter_pairs: Same chapter event pairing results
            entity_pairs: Entity co-occurrence pairing results (already sorted by weight)
            
        Returns:
            Merged and deduplicated candidate event pair list
        """
        # First check if same chapter pairs count already exceeds maximum limit
        if len(chapter_pairs) >= self.max_candidate_pairs:
            print(f"Same chapter pairs count {len(chapter_pairs)} already exceeds limit {self.max_candidate_pairs}, truncating")
            result_pairs = list(chapter_pairs[:self.max_candidate_pairs])
            print(f"Final candidate pairs: {len(result_pairs)} pairs, all from same chapter pairing")
            return result_pairs
        
        # First put same chapter pairs into result list
        result_pairs = list(chapter_pairs)
        remaining_slots = self.max_candidate_pairs - len(result_pairs)
        
        # If there are remaining slots, add entity co-occurrence pairs (avoid duplicates)
        if remaining_slots > 0:
            chapter_pairs_set = set(chapter_pairs)
            added_entity_pairs = 0
            
            for pair in entity_pairs:
                if pair not in chapter_pairs_set:
                    result_pairs.append(pair)
                    added_entity_pairs += 1
                
                # If candidate pair count has reached limit, stop adding
                if added_entity_pairs >= remaining_slots:
                    print(f"Reached candidate pair limit {self.max_candidate_pairs}, stop adding more candidates")
                    break
            
            print(f"After merging total {len(result_pairs)} candidate pairs, including same chapter {len(chapter_pairs)} pairs, entity co-occurrence {added_entity_pairs} pairs (original entity co-occurrence pairs {len(entity_pairs)})")
        else:
            print(f"Same chapter pairs count {len(chapter_pairs)} has occupied all quota, no entity co-occurrence pairs added")
        return result_pairs
