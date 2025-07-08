from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class EventItem:
    """
    # [CN] 事件数据模型，表示从文本中提取的一个事件
    # [EN] Event data model representing an event extracted from text
    """
    
    event_id: str  # [CN] 事件唯一标识符，如 E15-2（第15章第2个事件） [EN] Event unique identifier, e.g., E15-2 (2nd event in Chapter 15)
    description: str  # [CN] 事件描述 [EN] Event description
    characters: List[str] = field(default_factory=list)  # [CN] 涉及的角色 [EN] Characters involved
    treasures: List[str] = field(default_factory=list)  # [CN] 涉及的天材地宝 [EN] Treasures involved
    result: Optional[str] = None  # [CN] 事件结果 [EN] Event result
    location: Optional[str] = None  # [CN] 事件发生地点 [EN] Event location
    time: Optional[str] = None  # [CN] 事件发生时间 [EN] Event time
    chapter_id: Optional[str] = None  # [CN] 关联的章节ID [EN] Associated chapter ID
    
    def to_dict(self):
        """
        # [CN] 转换为字典表示
        # [EN] Convert to dictionary representation
        """
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
        """
        # [CN] 从字典创建实例
        # [EN] Create instance from dictionary
        """
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
