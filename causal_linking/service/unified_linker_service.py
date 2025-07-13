#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified causal linker implementation
Integrates basic and optimized causal linker functionality:
1. Use CandidateGenerator to generate candidate event pairs
2. Use PairAnalyzer to analyze causal relationships between event pairs
3. Implement BaseLinker interface to provide linker functionality
4. Build Directed Acyclic Graph (DAG)

Reduces overall time complexity from O(N²) to O(N·avg_m²) + O(E × k²)
"""

import os
import sys
import time
import itertools
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Tuple, Set

# Add project root directory to Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)

from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from causal_linking.service.base_causal_linker import BaseLinker
from causal_linking.service.candidate_generator import CandidateGenerator
from causal_linking.service.pair_analyzer import PairAnalyzer
from causal_linking.service.graph_filter import GraphFilter
from event_extraction.repository.llm_client import LLMClient


class UnifiedCausalLinker(BaseLinker):
    """
    Unified causal linker combining original and optimized features
    Supports complete legacy functionality while providing optimization strategy options
    """
    
    def __init__(
        self,
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: int = 3,
        strength_mapping: Dict[str, int] = {},
        provider: str = "openai",
        # Optimization parameters, optimization enabled by default
        use_optimization: bool = True,
        max_events_per_chapter: int = 50,  # Significantly increase event count limit per chapter
        min_entity_support: int = 3,  # Maintain moderate entity support requirement
        max_chapter_span: int = 10, 
        max_candidate_pairs: int = 150,  # Appropriately increase candidate pairs limit
        use_entity_weights: bool = True
    ):
        """
        Initialize unified causal linker
        
        Args:
            model: LLM model to use
            prompt_path: Prompt template path
            api_key: API key
            base_url: Custom API base URL
            max_workers: Maximum number of worker threads for parallel processing
            strength_mapping: Causal strength mapping for weight comparison
            provider: API provider, such as "openai" or "deepseek"
            use_optimization: Whether to use optimization strategy, disable to fallback to original full pairing method
            max_events_per_chapter: Maximum events processed per chapter
            min_entity_support: Minimum entity support, entities below this value are not considered for pairing
            max_chapter_span: Maximum chapter span for cross-chapter pairing
            max_candidate_pairs: Maximum number of candidate event pairs
            use_entity_weights: Whether to use entity frequency inverse weights (higher frequency lower weight)
        """
        if not prompt_path:
            # Import path_utils to get configuration file path
            from common.utils.path_utils import get_config_path
            prompt_path = get_config_path("prompt_causal_linking.json")
            
        super().__init__(prompt_path)
        
        # If no API key provided, try to get from environment variables
        if not api_key:
            if provider == "openai":
                api_key_env = os.environ.get("OPENAI_API_KEY")
                if not api_key_env:
                    raise ValueError("Please provide OpenAI API key")
                api_key = api_key_env
            elif provider == "deepseek":
                api_key_env = os.environ.get("DEEPSEEK_API_KEY")
                if not api_key_env:
                    raise ValueError("Please provide DeepSeek API key")
                api_key = api_key_env
            else:
                raise ValueError(f"Unsupported API provider: {provider}")
        
        self.model = model
        self.max_workers = max_workers
        self.provider = provider
        self.use_optimization = use_optimization
        
        # Set strength mapping
        self.strength_mapping = strength_mapping or {
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        # Initialize candidate generator
        self.candidate_generator = CandidateGenerator(
            max_events_per_chapter=max_events_per_chapter,
            min_entity_support=min_entity_support,
            max_chapter_span=max_chapter_span,
            max_candidate_pairs=max_candidate_pairs,
            use_entity_weights=use_entity_weights,
            max_pairs_per_entity=15,  # Each entity generates at most 15 event pairs
            connection_density=0.2    # Coefficient to control connection density
        )
        
        # Initialize pair analyzer
        self.pair_analyzer = PairAnalyzer(
            model=model,
            prompt_path=prompt_path,
            api_key=api_key,
            base_url=base_url,
            max_workers=max_workers,
            provider=provider
        )
        
        # Initialize graph filter
        self.graph_filter = GraphFilter(strength_mapping=self.strength_mapping)
        
        # Initialize LLM client (still needed for analyze_causal_relation method)
        self.llm_client = LLMClient(
            api_key=api_key,
            model=self.model,
            base_url=base_url,
            provider=self.provider
        )
    
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        """
        Identify causal relationships between events
        
        Args:
            events: Event list
            
        Returns:
            List of event causal edges
        """
        start_time = time.time()
        
        if self.use_optimization:
            # Use optimized strategy
            print("Using optimization strategy to generate candidate event pairs...")
            # Generate candidate event pairs through CandidateGenerator
            candidate_pairs = self.candidate_generator.generate_candidates(events)
            
            # Prepare event ID to event object mapping for subsequent queries
            event_map = {event.event_id: event for event in events}
            
            # Convert candidate event pairs (ID pairs) to event object pairs
            event_pairs = []
            for id1, id2 in candidate_pairs:
                if id1 in event_map and id2 in event_map:
                    event_pairs.append((event_map[id1], event_map[id2]))
                else:
                    print(f"Warning: Event ID {id1} or {id2} does not exist in event list")
            
            print(f"Starting analysis of causal relationships for {len(event_pairs)} event pairs...")
            # Use PairAnalyzer to batch analyze event pairs
            edges = self.pair_analyzer.analyze_batch(event_pairs)
            
            # Calculate optimization effect
            original_pairs = len(events) * (len(events) - 1) // 2
            print(f"Number of possible event pairs before optimization: {original_pairs}")
            print(f"Number of event pairs actually analyzed after optimization: {len(event_pairs)}, saved {original_pairs - len(event_pairs)} pairs ({(original_pairs - len(event_pairs)) / original_pairs * 100:.2f}%)")
        else:
            # Use original full pairing strategy
            # Create all possible event pair combinations
            all_event_pairs = list(itertools.combinations(events, 2))
            print(f"Analyzing causal relationships for {len(all_event_pairs)} event pairs...")
            
            # Use PairAnalyzer to batch analyze event pairs
            edges = self.pair_analyzer.analyze_batch(all_event_pairs)
        
        elapsed = time.time() - start_time
        print(f"Found {len(edges)} causal relationships")
        print(f"Total time: {elapsed:.2f} seconds")
        
        return edges
    
    def analyze_causal_relation(self, event1: EventItem, event2: EventItem) -> Optional[CausalEdge]:
        """
        Analyze causal relationship between two events
        
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
        
        if "event1->event2" in direction:
            from_id = event1_id
            to_id = event2_id
        elif "event2->event1" in direction:
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
    
    def build_dag(self, events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        Build Directed Acyclic Graph (DAG)
        
        Args:
            events: Event list
            edges: Causal edge list
            
        Returns:
            Processed event list and causal edge list
        """
        # First, process duplicate node IDs
        unique_events, updated_edges = self._ensure_unique_node_ids(events, edges)
        
        # Use graph filter to process cycles and conflicts
        filtered_edges = self.graph_filter.filter_edges_to_dag(unique_events, updated_edges)
        
        if len(filtered_edges) != len(updated_edges):
            print(f"Cycles detected in graph, removed {len(updated_edges) - len(filtered_edges)} edges to build DAG")
            
        return unique_events, filtered_edges
        
    def _ensure_unique_node_ids(self, events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        Ensure uniqueness of event node IDs and update edge references
        
        Args:
            events: Event list
            edges: Causal edge list
            
        Returns:
            Processed event list and edge list
        """
        # Optimization: First check event ID duplication, if no duplicate IDs, can directly return original data
        # This is a common optimization technique to avoid complex operations when processing is not needed
        event_ids = [event.event_id for event in events]
        if len(event_ids) == len(set(event_ids)):
            # No duplicate IDs, can directly return
            print("No duplicate event IDs detected, skipping ID processing")
            return events, edges
            
        print(f"Duplicate event IDs detected, processing {len(events)} events...")
            
        # Create event ID to event mapping
        event_map = {}
        unique_events = []
        id_counter = {}  # Counter to track occurrence count of each basic ID
        id_mapping = {}  # Mapping from original ID to unique ID
        
        # Process duplicate IDs, assign unique ID for each node
        for event in events:
            original_id = event.event_id
            
            if original_id in event_map:
                # If ID already exists, create unique ID for it
                if original_id not in id_counter:
                    id_counter[original_id] = 1
                    # Create mapping for first occurrence ID as well
                    first_unique_id = f"{original_id}_1"
                    id_mapping[original_id] = first_unique_id
                    
                    # Update previously stored event
                    old_event = event_map[original_id]
                    unique_event = EventItem(
                        event_id=first_unique_id,
                        description=old_event.description,
                        characters=old_event.characters,
                        treasures=old_event.treasures,
                        result=old_event.result,
                        location=old_event.location,
                        time=old_event.time,
                        chapter_id=old_event.chapter_id
                    )
                    
                    # Replace stored event
                    event_map[first_unique_id] = unique_event
                    
                    # Remove original ID mapping
                    del event_map[original_id]
                    
                    # Find and replace in unique_events
                    for i, node in enumerate(unique_events):
                        if node.event_id == original_id:
                            unique_events[i] = unique_event
                            break
                
                # Create unique ID for current event
                id_counter[original_id] += 1
                unique_id = f"{original_id}_{id_counter[original_id]}"
                
                # Create new event with unique ID
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
                
                # Store mapping relationship
                id_mapping[unique_id] = unique_id  # Self-mapping to simplify subsequent lookup
                event_map[unique_id] = unique_event
                unique_events.append(unique_event)
            else:
                # First occurrence of ID
                event_map[original_id] = event
                id_mapping[original_id] = original_id  # Self-mapping to simplify subsequent lookup
                unique_events.append(event)
        
        # Parallel update edge references using unique IDs
        updated_edges = []
        
        # If edge count exceeds threshold, use parallel processing
        if len(edges) > 20:  # Set reasonable threshold, sequential processing is faster below this value
            def process_edge(edge):
                from_id = edge.from_id
                to_id = edge.to_id
                
                # Get mapped ID, use original ID if no mapping exists
                from_id_mapped = id_mapping.get(from_id, from_id)
                to_id_mapped = id_mapping.get(to_id, to_id)
                
                # If source or target node doesn't exist in mapping, return None
                if from_id_mapped not in event_map or to_id_mapped not in event_map:
                    return None
                
                # Create new edge
                return CausalEdge(
                    from_id=from_id_mapped,
                    to_id=to_id_mapped,
                    strength=edge.strength,
                    reason=edge.reason
                )
            
            print(f"Using parallel processing to update {len(edges)} edge references...")
            # Use thread pool to process edges in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all edge processing tasks
                results = list(executor.map(process_edge, edges))
                
            # Filter out invalid edges
            updated_edges = [edge for edge in results if edge is not None]
            
            # Count skipped edges
            skipped_count = len(edges) - len(updated_edges)
            if skipped_count > 0:
                print(f"Warning: {skipped_count} edges referenced non-existent nodes and were skipped")
                
        else:
            # For cases with fewer edges, use sequential processing
            for edge in edges:
                from_id = edge.from_id
                to_id = edge.to_id
                
                # Get mapped ID, use original ID if no mapping exists
                from_id_mapped = id_mapping.get(from_id, from_id)
                to_id_mapped = id_mapping.get(to_id, to_id)
                
                # If source or target node doesn't exist in mapping, skip directly
                if from_id_mapped not in event_map or to_id_mapped not in event_map:
                    print(f"Warning: Edge {from_id} -> {to_id} references non-existent node and will be skipped")
                    continue
                
                # Create new edge
                updated_edge = CausalEdge(
                    from_id=from_id_mapped,
                    to_id=to_id_mapped,
                    strength=edge.strength,
                    reason=edge.reason
                )
                updated_edges.append(updated_edge)
        
        print(f"Processed node ID uniqueness: original event count {len(events)}, processed event count {len(unique_events)}, processed edge count {len(updated_edges)}")
        return unique_events, updated_edges
    
    # The following methods are for maintaining test compatibility
    def _will_form_cycle(self, graph: List[List[int]], from_idx: int, to_idx: int) -> bool:
        """
        Check if adding edge will form a cycle in the graph
        
        Args:
            graph: Current graph's adjacency list
            from_idx: Starting node index of edge
            to_idx: Ending node index of edge
            
        Returns:
            Returns True if cycle will be formed, otherwise False
        """
        # If to_idx can already reach from_idx, adding edge will form cycle
        return self._is_reachable(graph, to_idx, from_idx, set())
    
    def _is_reachable(self, graph: List[List[int]], start: int, end: int, visited: Set[int]) -> bool:
        """
        Check if path exists from start to end in graph
        
        Args:
            graph: Graph's adjacency list
            start: Starting node index
            end: Target node index
            visited: Set of visited nodes
            
        Returns:
            Returns True if path exists, otherwise False
        """
        if start == end:
            return True
            
        visited.add(start)
        
        for neighbor in graph[start]:
            if neighbor not in visited and self._is_reachable(graph, neighbor, end, visited):
                return True
                
        return False
    
    def process_events(self, events: List[EventItem]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        Process event list, complete full workflow from linking to DAG construction
        
        Args:
            events: Event list
            
        Returns:
            Processed event list and causal edge list (DAG)
        """
        # 1. Find causal relationships between events
        edges = self.link_events(events)
        
        # 2. Build directed acyclic graph
        return self.build_dag(events, edges)


# Alias classes for original and optimized linkers for backward compatibility
class CausalLinker(UnifiedCausalLinker):
    """
    Compatibility class for original causal linker
    Actually uses unified version but disables optimization
    """
    def __init__(self, *args, **kwargs):
        # Remove potential optimization parameters
        for param in ['use_optimization', 'max_events_per_chapter', 'min_entity_support', 
                     'max_chapter_span', 'max_candidate_pairs', 'use_entity_weights']:
            if param in kwargs:
                kwargs.pop(param)
        
        # Fixed to use non-optimization mode
        super().__init__(*args, use_optimization=False, **kwargs)
    
    def _will_form_cycle(self, graph, from_idx, to_idx):
        """
        Check if adding edge will form a cycle
        
        Args:
            graph: Current graph's adjacency list
            from_idx: Starting node index of edge
            to_idx: Ending node index of edge
            
        Returns:
            Returns True if cycle will be formed, otherwise False
        """
        # If to_idx can already reach from_idx, adding edge will form cycle
        return self._is_reachable(graph, to_idx, from_idx, set())
    
    def _is_reachable(self, graph, start, end, visited):
        """
        Check if path exists from start to end in graph
        
        Args:
            graph: Graph's adjacency list
            start: Starting node index
            end: Target node index
            visited: Set of visited nodes
            
        Returns:
            Returns True if path exists, otherwise False
        """
        if start == end:
            return True
            
        visited.add(start)
        
        for neighbor in graph[start]:
            if neighbor not in visited and self._is_reachable(graph, neighbor, end, visited):
                return True
                
        return False


class OptimizedCausalLinker(UnifiedCausalLinker):
    """
    Compatibility class for optimized causal linker
    Actually uses unified version with optimization enabled
    """
    def __init__(self, *args, **kwargs):
        # Ensure optimization is enabled
        kwargs['use_optimization'] = True
        super().__init__(*args, **kwargs)


# Test code to execute when running this file directly
if __name__ == "__main__":
    print("Running unified causal linker module test...")
    
    # Simple initialization test - verify module can be loaded and initialized correctly
    try:
        # Create instance without API key (for import verification only)
        # Should provide correct API key for actual use
        linker = UnifiedCausalLinker(prompt_path="", api_key="test_key")
        print("✓ Unified causal linker initialization successful")
        
        # Verify import of other modules
        print("✓ Successfully imported PairAnalyzer")
        print("✓ Successfully imported CandidateGenerator")
        print("✓ Successfully imported GraphFilter")
        
        print("\nAll modules loaded successfully! Module refactoring complete.")
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
