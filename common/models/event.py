from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class EventItem:
    """Event data model representing an event extracted from text"""
    
    event_id: str  # Event unique identifier, such as E15-2 (2nd event in Chapter 15)
    description: str  # Event description
    characters: List[str] = field(default_factory=list)  # Characters involved
    treasures: List[str] = field(default_factory=list)  # Treasures/materials involved
    result: Optional[str] = None  # Event result
    location: Optional[str] = None  # Event location
    time: Optional[str] = None  # Event time
    chapter_id: Optional[str] = None  # Associated chapter ID
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "event_id": self.event_id,
            "description": self.description,
            "characters": self.characters,
            "treasures": self.treasures,
            "result": self.result,
            "location": self.location,
            "time": self.time,
            "chapter_id": self.chapter_id
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create instance from dictionary"""
        return cls(
            event_id=data.get("event_id", ""),
            description=data.get("description", ""),
            characters=data.get("characters", []),
            treasures=data.get("treasures", []),
            result=data.get("result"),
            location=data.get("location"),
            time=data.get("time"),
            chapter_id=data.get("chapter_id")
        )
