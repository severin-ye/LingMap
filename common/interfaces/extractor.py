from abc import ABC, abstractmethod
from typing import List

from common.models.chapter import Chapter
from common.models.event import EventItem


class AbstractExtractor(ABC):
    """Extractor interface that defines methods for event extraction"""
    
    @abstractmethod
    def extract(self, chapter: Chapter) -> List[EventItem]:
        """
        Extract event list from chapter
        
        Args:
            chapter: Chapter data
            
        Returns:
            List of extracted events
        """
        pass
