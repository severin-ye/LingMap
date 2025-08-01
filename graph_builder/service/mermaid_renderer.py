from typing import List, Dict, Any, Optional, Set
import os
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from common.interfaces.graph_renderer import AbstractGraphRenderer
from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from graph_builder.domain.base_renderer import BaseRenderer
from graph_builder.utils.color_map import ColorMap
from common.utils.parallel_config import ParallelConfig


class MermaidRenderer(BaseRenderer):
    """Mermaid graph renderer implementation class"""
    
    def __init__(self, default_options: Dict[str, Any] = {}):
        """
        Initialize Mermaid renderer
        
        Args:
            default_options: Default rendering options
        """
        super().__init__(default_options)
        
        # Use module-specific configuration to determine thread count (ensure consistency with module-specific configuration)
        if ParallelConfig.is_enabled():
            module_specific_workers = ParallelConfig._config["default_workers"]["graph_builder"]
            self.max_workers = module_specific_workers
        else:
            self.max_workers = 1
            
        # Record the number of threads used
        logging.info(f"Graph builder module using worker threads: {self.max_workers}")
        
        # Use thread monitoring tool to record
        from common.utils.thread_monitor import log_thread_usage
        log_thread_usage("graph_builder", self.max_workers, "cpu_bound")
        
    def render(self, events: List[EventItem], edges: List[CausalEdge], format_options: Dict[str, Any] = {}) -> str:
        """
        Render event graph as Mermaid format
        
        Args:
            events: Event list
            edges: Event causal edge list
            format_options: Format options such as colors, styles, etc.
                - connect_isolated_nodes: Whether to automatically connect isolated nodes, default True
            
        Returns:
            Mermaid format graph string
        """
        # Merge options
        options = {**self.default_options, **(format_options or {})}
        
        # Process duplicate node IDs: detect and rename duplicate node IDs
        events, edges = self._handle_duplicate_ids(events, edges)
        
        # Create mapping from event ID to event
        event_map = {event.event_id: event for event in events}
        
        # Detect and connect isolated nodes
        if options.get("connect_isolated_nodes", True):  # Default enable this feature
            edges = self._connect_isolated_nodes(events, edges)
            
        # Generate Mermaid graph definition header
        mermaid = ["```mermaid", "graph TD"]
        
        # Generate node definitions in parallel
        node_definitions = []
        
        def process_node(event):
            # Get node color
            colors = ColorMap.get_node_color(
                event.description,
                event.treasures,
                event.characters
            )
            
            # Node definition
            node_def = f'    {event.event_id}["{self._escape_text(event.description)}"]'
            
            # Node style
            style = f'    style {event.event_id} fill:{colors["fill"]},stroke:{colors["stroke"]}'
            
            return (node_def, style)
        
        # Get thread count from module-specific configuration
        module_workers = ParallelConfig._config["default_workers"]["graph_builder"]
        actual_workers = module_workers if ParallelConfig.is_enabled() else 1
        logging.info(f"Graph rendering node processing using threads: {actual_workers} (module config: {module_workers})")
        
        # Update instance variable for consistency
        self.max_workers = actual_workers
        
        # Use thread pool to process nodes in parallel
        with ThreadPoolExecutor(max_workers=actual_workers) as executor:
            # Submit all tasks
            future_to_event = {executor.submit(process_node, event): event for event in events}
            
            # Collect results
            for future in as_completed(future_to_event):
                try:
                    node_def, style = future.result()
                    mermaid.append(node_def)
                    mermaid.append(style)
                except Exception as e:
                    print(f"Error processing node: {e}")
        
        # Generate edge definitions
        link_style_index = 0
        for edge in edges:
            # Get edge style
            edge_style = ColorMap.get_edge_style(edge.strength)
            
            # Create basic edge
            edge_def = f'    {edge.from_id} --> {edge.to_id}'
            
            # If there are edge labels (strength or reason)
            if options.get("show_edge_labels", True) and edge.reason:
                # Use short reason as label
                short_reason = self._truncate_text(edge.reason, 20)
                edge_def = f'    {edge.from_id} -->|"{short_reason}"| {edge.to_id}'
            
            # Add edge definition
            mermaid.append(edge_def)
            
            # If custom edge style is needed
            if options.get("custom_edge_style", True):
                # Assign unique ID to edge
                linkStyle = f'    linkStyle {link_style_index} stroke:{edge_style["stroke"]},stroke-width:{edge_style["stroke_width"]}'
                
                if edge_style["style"] == "dashed":
                    linkStyle += ",stroke-dasharray:5 5"
                
                mermaid.append(linkStyle)
                link_style_index += 1
        
        # Add legend
        if options.get("show_legend", False):
            mermaid.extend(self._generate_legend())
        
        # End Mermaid definition
        mermaid.append("```")
        
        return "\n".join(mermaid)
    
    def _generate_legend(self) -> List[str]:
        """Generate legend"""
        legend = [
            "    subgraph Legend",
            "    legend_character[Character Events]",
            "    legend_treasure[Treasure Events]",
            "    legend_conflict[Conflict Events]",
            "    legend_cultivation[Cultivation Events]",
            "    end",
            f'    style legend_character fill:{ColorMap.DEFAULT_COLORS["character"]},stroke:{ColorMap.get_node_color("", [], ["character"])["stroke"]}',
            f'    style legend_treasure fill:{ColorMap.DEFAULT_COLORS["treasure"]},stroke:{ColorMap.get_node_color("", ["treasure"], [])["stroke"]}',
            f'    style legend_conflict fill:{ColorMap.DEFAULT_COLORS["conflict"]},stroke:{ColorMap.get_node_color("battle", [], [])["stroke"]}',
            f'    style legend_cultivation fill:{ColorMap.DEFAULT_COLORS["cultivation"]},stroke:{ColorMap.get_node_color("cultivate", [], [])["stroke"]}'
        ]
        
        return legend
    
    def _escape_text(self, text: str) -> str:
        """
        Escape special characters in Mermaid text
        
        Args:
            text: Original text
            
        Returns:
            Escaped text
        """
        # Escape common special characters
        escaped = text.replace('"', '\\"')
        return escaped
    
    def _truncate_text(self, text: str, max_length: int = 20) -> str:
        """
        Truncate text to specified length
        
        Args:
            text: Original text
            max_length: Maximum length
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
        
    def _connect_isolated_nodes(self, events: List[EventItem], edges: List[CausalEdge]) -> List[CausalEdge]:
        """
        Detect isolated nodes and connect them in chronological order
        
        Args:
            events: Event list
            edges: Existing edge list
            
        Returns:
            Updated edge list including new edges connecting isolated nodes
        """
        # Build node connection graph (find connected nodes)
        connected_nodes = set()
        for edge in edges:
            connected_nodes.add(edge.from_id)
            connected_nodes.add(edge.to_id)
            
        # Get all node IDs
        all_node_ids = {event.event_id for event in events}
        
        # Find isolated nodes
        isolated_nodes = all_node_ids - connected_nodes
        
        if isolated_nodes:
            logging.info(f"Detected {len(isolated_nodes)} isolated nodes, preparing to connect in chronological order")
            
            # Get all isolated events
            isolated_events = [e for e in events if e.event_id in isolated_nodes]
            
            # Sort by event ID, assuming format "Echapter-sequence"
            # First sort by chapter number, then by sequence number
            def extract_chapter_and_sequence(event_id):
                # Assume format: Echapter_number-sequence or Echapter_number-sequence_sub_sequence
                parts = event_id.strip('E').split('-')
                if len(parts) >= 2:
                    chapter = int(parts[0]) if parts[0].isdigit() else 0
                    # Process sequence part that may contain underscores
                    seq_parts = parts[1].split('_')
                    sequence = int(seq_parts[0]) if seq_parts[0].isdigit() else 0
                    return (chapter, sequence)
                return (0, 0)  # Default value
                
            # Sort by extracted chapter and sequence numbers
            isolated_events.sort(key=lambda e: extract_chapter_and_sequence(e.event_id))
            
            # Apply same sorting to all events
            all_events_sorted = sorted(events, key=lambda e: extract_chapter_and_sequence(e.event_id))
            
            # Connect isolated nodes
            new_edges = []
            
            # Create edges from each isolated node to the next node
            for event in isolated_events:
                # Find the position of current event in the sorted list
                current_index = next((idx for idx, e in enumerate(all_events_sorted) if e.event_id == event.event_id), -1)
                
                # If current event is found and not the last event
                if current_index != -1 and current_index < len(all_events_sorted) - 1:
                    # Get next event
                    next_event = all_events_sorted[current_index + 1]
                    
                    # Create new edge
                    new_edge = CausalEdge(
                        from_id=event.event_id,
                        to_id=next_event.event_id,
                        strength="temporal",  # Use special "temporal" strength, indicating time sequence rather than causal relationship
                        reason="Chronological connection"
                    )
                    
                    new_edges.append(new_edge)
                    logging.info(f"Created chronological connection: {event.event_id} -> {next_event.event_id}")
            
            # Add new edges to existing edge list
            edges.extend(new_edges)
            logging.info(f"Added {len(new_edges)} new edges to connect isolated nodes")
                
        return edges
    
    def _handle_duplicate_ids(self, events: List[EventItem], edges: List[CausalEdge]) -> tuple[List[EventItem], List[CausalEdge]]:
        """
        Process duplicate node IDs
        
        Args:
            events: Event list
            edges: Causal edge list
            
        Returns:
            Processed event list and edge list
        """
        # Check if there are duplicate IDs
        event_id_count = {}
        for event in events:
            if event.event_id in event_id_count:
                event_id_count[event.event_id] += 1
            else:
                event_id_count[event.event_id] = 1
        
        # If no duplicate IDs, return original data directly
        if all(count == 1 for count in event_id_count.values()):
            return events, edges
        
        # Process duplicate IDs
        id_map = {}  # Mapping from original ID to new ID
        updated_events = []
        
        for event in events:
            original_id = event.event_id
            if event_id_count[original_id] > 1:
                # Create new ID for duplicate ID (e.g. E1 -> E1_1, E1_2, E1_3)
                if original_id not in id_map:
                    id_map[original_id] = []
                
                # Assign new ID to current event
                new_id = f"{original_id}_{len(id_map[original_id]) + 1}"
                id_map[original_id].append(new_id)
                
                # Create updated event
                updated_event = EventItem(
                    event_id=new_id,
                    description=event.description,
                    characters=event.characters,
                    treasures=event.treasures,
                    result=event.result,
                    location=event.location,
                    time=event.time,
                    chapter_id=event.chapter_id
                )
                updated_events.append(updated_event)
            else:
                # Non-duplicate ID, keep unchanged
                updated_events.append(event)
                # Add to mapping table for later edge processing
                if original_id not in id_map:
                    id_map[original_id] = [original_id]
        
        # Update edge references
        updated_edges = []
        for edge in edges:
            original_from_id = edge.from_id
            original_to_id = edge.to_id
            
            # If edge references duplicate ID, need to process multiple possible edges
            # Use simple strategy here: create edges for each possible source node to each possible target node
            for from_id in id_map.get(original_from_id, [original_from_id]):
                for to_id in id_map.get(original_to_id, [original_to_id]):
                    updated_edge = CausalEdge(
                        from_id=from_id,
                        to_id=to_id,
                        strength=edge.strength,
                        reason=edge.reason
                    )
                    updated_edges.append(updated_edge)
        
        return updated_events, updated_edges
