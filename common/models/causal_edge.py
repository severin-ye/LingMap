from dataclasses import dataclass
from typing import Optional


@dataclass
class CausalEdge:
    """
    # [CN] 事件因果边数据结构，描述两个事件之间的因果关系
    # [EN] Event causal edge data structure describing causal relationships between two events
    """
    
    from_id: str  # [CN] 起始事件ID [EN] Source event ID
    to_id: str  # [CN] 目标事件ID [EN] Target event ID
    strength: str  # [CN] 因果强度，如 "高", "中", "低" [EN] Causal strength, e.g., "High", "Medium", "Low"
    reason: Optional[str] = None  # [CN] 因果关系解释 [EN] Causal relationship explanation
    
    def to_dict(self):
        """
        # [CN] 转换为字典表示
        # [EN] Convert to dictionary representation
        """
        return {
            "from": self.from_id,
            "to": self.to_id,
            "strength": self.strength,
            "reason": self.reason
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """
        # [CN] 从字典创建实例
        # [EN] Create instance from dictionary
        """
        return cls(
            from_id=data.get("from", ""),
            to_id=data.get("to", ""),
            strength=data.get("strength", ""),
            reason=data.get("reason")
        )
