from abc import ABC
from typing import List, Dict, Any

from common.interfaces.graph_renderer import AbstractGraphRenderer
from common.models.causal_edge import CausalEdge
from common.models.event import EventItem


class BaseRenderer(AbstractGraphRenderer, ABC):
    """图谱渲染器基类"""
    
    def __init__(self, default_options: Dict[str, Any] = None):
        """
        初始化渲染器
        
        Args:
            default_options: 默认渲染选项
        """
        self.default_options = default_options or {}
