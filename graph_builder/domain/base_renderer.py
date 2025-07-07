from abc import ABC
from typing import List, Dict, Any

from common.interfaces.graph_renderer import AbstractGraphRenderer
from common.models.causal_edge import CausalEdge
from common.models.event import EventItem


class BaseRenderer(AbstractGraphRenderer, ABC):
    """Graph renderer base class"""
    
    def __init__(self, default_options: Dict[str, Any] = {}):
        """
        Initialize renderer
        
        Args:
            default_options: Default rendering options
        """
        self.default_options = default_options or {}
