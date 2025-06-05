from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class EventItem:
    """事件数据模型，表示从文本中提取的一个事件"""
    
    event_id: str  # 事件唯一标识符，如 E15-2（第15章第2个事件）
    description: str  # 事件描述
    characters: List[str] = field(default_factory=list)  # 涉及的角色
    treasures: List[str] = field(default_factory=list)  # 涉及的天材地宝
    result: Optional[str] = None  # 事件结果
    location: Optional[str] = None  # 事件发生地点
    time: Optional[str] = None  # 事件发生时间
    chapter_id: Optional[str] = None  # 关联的章节ID
    
    def to_dict(self):
        """转换为字典表示"""
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
        """从字典创建实例"""
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
