from abc import ABC, abstractmethod
from typing import List, Tuple

from common.models.causal_edge import CausalEdge
from common.models.event import EventItem


class AbstractLinker(ABC):
    """Linker interface that defines methods for causal relationship identification and linking between events"""
    
    @abstractmethod
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        """
        Identify causal relationships between events
        
        Args:
            events: List of events
            
        Returns:
            List of causal edges between events
        """
        pass
    
    @abstractmethod
    def build_dag(self, events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        Build Directed Acyclic Graph (DAG)
        
        Args:
            events: List of events
            edges: List of causal edges
            
        Returns:
            Processed list of events and causal edges
        """
        pass
