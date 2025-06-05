from abc import ABC, abstractmethod
from typing import List

from common.models.chapter import Chapter
from common.models.event import EventItem


class AbstractExtractor(ABC):
    """抽取器接口，定义事件抽取的方法"""
    
    @abstractmethod
    def extract(self, chapter: Chapter) -> List[EventItem]:
        """
        从章节中抽取事件列表
        
        Args:
            chapter: 章节数据
            
        Returns:
            抽取的事件列表
        """
        pass
