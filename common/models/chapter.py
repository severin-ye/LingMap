from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Chapter:
    """章节数据模型，表示一个章节的信息"""
    
    chapter_id: str  # 章节ID，如 "第十五章"
    title: str  # 章节标题，如 "聚灵丹"
    content: str  # 章节完整内容
    segments: List[dict] = field(default_factory=list)  # 章节分段，按段落/事件切分
    
    def to_dict(self):
        """转换为字典表示"""
        return {
            "chapter_id": self.chapter_id,
            "title": self.title,
            "content": self.content,
            "segments": self.segments
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(
            chapter_id=data.get("chapter_id", ""),
            title=data.get("title", ""),
            content=data.get("content", ""),
            segments=data.get("segments", [])
        )
