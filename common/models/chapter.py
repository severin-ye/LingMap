from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Chapter:
    """Chapter data model representing information of a chapter"""
    
    chapter_id: str  # Chapter ID, such as "Chapter 15"
    title: str  # Chapter title, such as "Spirit Gathering Pill"
    content: str  # Complete chapter content
    segments: List[dict] = field(default_factory=list)  # Chapter segment text, split by paragraphs/events
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "chapter_id": self.chapter_id,
            "title": self.title,
            "content": self.content,
            "segments": self.segments
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create instance from dictionary"""
        return cls(
            chapter_id=data.get("chapter_id", ""),
            title=data.get("title", ""),
            content=data.get("content", ""),
            segments=data.get("segments", [])
        )
