from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Treasure:
    """天材地宝数据结构，描述小说中的法宝、丹药等物品"""
    
    name: str  # TODO: Translate - 宝物名称
    description: Optional[str] = None  # TODO: Translate - 宝物描述
    effects: List[str] = field(default_factory=list)  # TODO: Translate - 宝物效用
    origin: Optional[str] = None  # TODO: Translate - 宝物来源
    first_appearance: Optional[str] = None  # TODO: Translate - 首次出现的chapterID
    
    def to_dict(self):
        """转换为字典表示"""
        return {
            "name": self.name,
            "description": self.description,
            "effects": self.effects,
            "origin": self.origin,
            "first_appearance": self.first_appearance
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建实例"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description"),
            effects=data.get("effects", []),
            origin=data.get("origin"),
            first_appearance=data.get("first_appearance")
        )
