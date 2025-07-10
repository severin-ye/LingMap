#!/usr/bin/env python3
"""
数据模型单元测试

测试common/models中的所有数据模型类：
- Chapter
- EventItem
- CausalEdge
- Treasure
"""

import pytest
import json
from pathlib import Path
import sys
import os

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from common.models.chapter import Chapter
from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from common.models.treasure import Treasure

class TestChapterModel:
    """Chapter模型测试"""
    
    def test_chapter_creation(self):
        """测试章节创建"""
        chapter = Chapter(
            chapter_id="test_1",
            title="测试章节",
            content="这是一个测试章节的内容"
        )
        
        assert chapter.chapter_id == "test_1"
        assert chapter.title == "测试章节"
        assert chapter.content == "这是一个测试章节的内容"
        assert chapter.segments == []
    
    def test_chapter_to_dict(self):
        """测试章节转字典"""
        chapter = Chapter(
            chapter_id="test_1",
            title="测试章节", 
            content="测试内容",
            segments=[{"id": 1, "text": "段落1"}]
        )
        
        chapter_dict = chapter.to_dict()
        assert isinstance(chapter_dict, dict)
        assert chapter_dict["chapter_id"] == "test_1"
        assert chapter_dict["title"] == "测试章节"
        assert len(chapter_dict["segments"]) == 1
    
    def test_chapter_from_dict(self):
        """测试从字典创建章节"""
        data = {
            "chapter_id": "test_2",
            "title": "从字典创建",
            "content": "字典内容",
            "segments": [{"id": 1}]
        }
        
        chapter = Chapter.from_dict(data)
        assert chapter.chapter_id == "test_2"
        assert chapter.title == "从字典创建"
        assert len(chapter.segments) == 1

class TestEventItemModel:
    """EventItem模型测试"""
    
    def test_event_creation(self):
        """测试事件创建"""
        event = EventItem(
            event_id="E001",
            description="张三参加考试",
            characters=["张三"],
            treasures=["墨宝"],
            location="京城",
            time="明朝"
        )
        
        assert event.event_id == "E001"
        assert event.description == "张三参加考试"
        assert "张三" in event.characters
        assert "墨宝" in event.treasures
        assert event.location == "京城"
        assert event.time == "明朝"
    
    def test_event_to_dict(self):
        """测试事件转字典"""
        event = EventItem(
            event_id="E002",
            description="测试事件",
            characters=["角色A", "角色B"],
            result="成功"
        )
        
        event_dict = event.to_dict()
        assert isinstance(event_dict, dict)
        assert event_dict["event_id"] == "E002"
        assert event_dict["description"] == "测试事件"
        assert len(event_dict["characters"]) == 2
        assert event_dict["result"] == "成功"
    
    def test_event_from_dict(self):
        """测试从字典创建事件"""
        data = {
            "event_id": "E003",
            "description": "字典事件",
            "characters": ["用户"],
            "treasures": [],
            "location": "测试地点"
        }
        
        event = EventItem.from_dict(data)
        assert event.event_id == "E003"
        assert event.description == "字典事件"
        assert len(event.characters) == 1
        assert event.location == "测试地点"

class TestCausalEdgeModel:
    """CausalEdge模型测试"""
    
    def test_causal_edge_creation(self):
        """测试因果边创建"""
        edge = CausalEdge(
            from_id="E001",
            to_id="E002", 
            strength="高",
            reason="基于时间顺序"
        )
        
        assert edge.from_id == "E001"
        assert edge.to_id == "E002"
        assert edge.strength == "高"
        assert edge.reason == "基于时间顺序"
    
    def test_causal_edge_to_dict(self):
        """测试因果边转字典"""
        edge = CausalEdge(
            from_id="E003",
            to_id="E004",
            strength="中"
        )
        
        edge_dict = edge.to_dict()
        assert isinstance(edge_dict, dict)
        assert edge_dict["from"] == "E003"
        assert edge_dict["to"] == "E004"
        assert edge_dict["strength"] == "中"
    
    def test_causal_edge_from_dict(self):
        """测试从字典创建因果边"""
        data = {
            "from": "E005",
            "to": "E006",
            "strength": "低",
            "reason": "推测关系"
        }
        
        edge = CausalEdge.from_dict(data)
        assert edge.from_id == "E005"
        assert edge.to_id == "E006"
        assert edge.strength == "低"

class TestTreasureModel:
    """Treasure模型测试"""
    
    def test_treasure_creation(self):
        """测试宝物创建"""
        treasure = Treasure(
            name="九阳神功",
            description="武林绝学",
            effects=["内功提升", "阳刚之气"],
            origin="张无忌修炼"
        )
        
        assert treasure.name == "九阳神功"
        assert treasure.description == "武林绝学"
        assert "内功提升" in treasure.effects
        assert treasure.origin == "张无忌修炼"
    
    def test_treasure_to_dict(self):
        """测试宝物转字典"""
        treasure = Treasure(
            name="测试宝物",
            effects=["测试效果"]
        )
        
        treasure_dict = treasure.to_dict()
        assert isinstance(treasure_dict, dict)
        assert treasure_dict["name"] == "测试宝物"
        assert len(treasure_dict["effects"]) == 1
    
    def test_treasure_from_dict(self):
        """测试从字典创建宝物"""
        data = {
            "name": "字典宝物",
            "description": "从字典创建",
            "effects": ["治疗", "提升"],
            "origin": "测试来源"
        }
        
        treasure = Treasure.from_dict(data)
        assert treasure.name == "字典宝物"
        assert treasure.description == "从字典创建"
        assert len(treasure.effects) == 2
        assert treasure.origin == "测试来源"

def test_all_models_json_serialization():
    """测试所有模型的JSON序列化"""
    # 创建测试数据
    chapter = Chapter(chapter_id="test", title="测试", content="内容")
    event = EventItem(event_id="E001", description="事件", characters=["角色"])
    edge = CausalEdge(from_id="E001", to_id="E002", strength="高")
    treasure = Treasure(name="宝物", description="测试宝物")
    
    # 测试序列化
    models_data = {
        "chapter": chapter.to_dict(),
        "event": event.to_dict(), 
        "edge": edge.to_dict(),
        "treasure": treasure.to_dict()
    }
    
    # 确保可以JSON序列化
    json_str = json.dumps(models_data, ensure_ascii=False)
    assert len(json_str) > 0
    
    # 确保可以反序列化
    loaded_data = json.loads(json_str)
    assert "chapter" in loaded_data
    assert "event" in loaded_data
    assert "edge" in loaded_data
    assert "treasure" in loaded_data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
