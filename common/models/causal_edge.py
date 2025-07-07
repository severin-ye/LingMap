from dataclasses import dataclass
from typing import Optional


@dataclass
class CausalEdge:
    """事件因果边数据结构，描述两个事件之间的因果关系"""
    
    from_id: str  # Source event ID
    to_id: str  # Target event ID
    strength: str  # Causal strength, such as "high", "medium", "low"
    reason: Optional[str] = None  # TODO: Translate - causal关系解释
    
    def to_dict(self):
        """转换为字典表示"""
        return {
            "from": self.from_id,
            "to": self.to_id,
            "strength": self.strength,
            "reason": self.reason
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(
            from_id=data.get("from", ""),
            to_id=data.get("to", ""),
            strength=data.get("strength", ""),
            reason=data.get("reason")
        )
