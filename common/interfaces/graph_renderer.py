from abc import ABC, abstractmethod
from typing import List, Dict, Any

from common.models.causal_edge import CausalEdge
from common.models.event import EventItem


class AbstractGraphRenderer(ABC):
    """图谱渲染器接口，定义将因果事件转化为可视化图谱的方法"""
    
    @abstractmethod
    def render(self, events: List[EventItem], edges: List[CausalEdge], format_options: Dict[str, Any] = {}) -> str:
        """
        将事件图谱渲染为指定格式（如Mermaid）
        
        Args:
            events: 事件列表
            edges: 事件因果边列表
            format_options: 格式选项，如颜色、样式等
            
        Returns:
            渲染后的图谱字符串
        """
        pass
