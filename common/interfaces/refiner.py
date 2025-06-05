from abc import ABC, abstractmethod
from typing import List

from common.models.event import EventItem


class AbstractRefiner(ABC):
    """精修器接口，定义对抽取事件进行精修（修复幻觉）的方法"""
    
    @abstractmethod
    def refine(self, events: List[EventItem], context: str = None) -> List[EventItem]:
        """
        对抽取的事件进行幻觉检测和修复
        
        Args:
            events: 待精修的事件列表
            context: 支持精修的上下文信息
            
        Returns:
            精修后的事件列表
        """
        pass
