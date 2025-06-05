from abc import ABC, abstractmethod
from typing import List, Tuple

from common.models.causal_edge import CausalEdge
from common.models.event import EventItem


class AbstractLinker(ABC):
    """链接器接口，定义事件因果关系识别和链接的方法"""
    
    @abstractmethod
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        """
        识别事件之间的因果关系
        
        Args:
            events: 事件列表
            
        Returns:
            事件因果边列表
        """
        pass
    
    @abstractmethod
    def build_dag(self, events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        构建有向无环图（DAG）
        
        Args:
            events: 事件列表
            edges: 因果边列表
            
        Returns:
            处理后的事件列表和因果边列表
        """
        pass
