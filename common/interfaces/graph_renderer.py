from abc import ABC, abstractmethod
from typing import List, Dict, Any

from common.models.causal_edge import CausalEdge
from common.models.event import EventItem


class AbstractGraphRenderer(ABC):
    """Graph renderer interface that defines methods for converting causal events into visualized graphs"""
    
    @abstractmethod
    def render(self, events: List[EventItem], edges: List[CausalEdge], format_options: Dict[str, Any] = {}) -> str:
        """
        Render event graph to specified format (such as Mermaid)
        
        Args:
            events: List of events
            edges: List of causal edges between events
            format_options: Format options such as colors, styles, etc.
            
        Returns:
            Rendered graph string
        """
        pass
