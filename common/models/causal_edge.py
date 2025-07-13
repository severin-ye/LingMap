from dataclasses import dataclass
from typing import Optional


@dataclass
class CausalEdge:
    """Data structure for event causal edge, describing causal relationship between two events"""
    
    from_id: str  # Source event ID
    to_id: str  # Target event ID
    strength: str  # Causal strength, such as "high", "medium", "low"
    reason: Optional[str] = None  # Causal relationship explanation
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "from": self.from_id,
            "to": self.to_id,
            "strength": self.strength,
            "reason": self.reason
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create instance from dictionary"""
        return cls(
            from_id=data.get("from", ""),
            to_id=data.get("to", ""),
            strength=data.get("strength", ""),
            reason=data.get("reason")
        )
