from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Treasure:
    """Treasure data structure describing magical treasures, pills and other items in the novel"""
    
    name: str  # Treasure name
    description: Optional[str] = None  # Treasure description
    effects: List[str] = field(default_factory=list)  # Treasure effects
    origin: Optional[str] = None  # Treasure origin
    first_appearance: Optional[str] = None  # Chapter ID where it first appears
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "effects": self.effects,
            "origin": self.origin,
            "first_appearance": self.first_appearance
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create instance from dictionary"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description"),
            effects=data.get("effects", []),
            origin=data.get("origin"),
            first_appearance=data.get("first_appearance")
        )
