from abc import ABC, abstractmethod
from typing import List

from common.models.event import EventItem


class AbstractRefiner(ABC):
    """Refiner interface that defines methods for refining extracted events (fixing hallucinations)"""
    
    @abstractmethod
    def refine(self, events: List[EventItem], context: str = "") -> List[EventItem]:
        """
        Perform hallucination detection and correction on extracted events
        
        Args:
            events: List of events to be refined
            context: Context information supporting refinement
            
        Returns:
            List of refined events
        """
        pass
