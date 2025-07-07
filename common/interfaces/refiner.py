from abc import ABC, abstractmethod
from typing import List

from common.models.event import EventItem


class AbstractRefiner(ABC):
    """精修器接口，定义对抽取事件进行精修（修复幻觉）的方法"""
    
    @abstractmethod
    def refine(self, events: List[EventItem], context: str = "") -> List[EventItem]:
        """
        对抽取的事件进行幻觉检测和修复
        
        Args:
            events: Event to be refined列表
            context: Context information supporting refinement
            
        Returns:
            Refined event列表
        """
        pass
