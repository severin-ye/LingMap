#!/usr/bin/env python3
"""
阶段一测试：数据模型与工具类测试

本文件包含针对《凡人修仙传》因果事件图谱系统数据模型和工具类的单元测试。

测试内容：
1. EventItem 模型：测试事件项的创建、属性设置和字典转换功能
   - test_event_creation: 测试创建事件对象及其属性
   - test_event_to_dict: 测试事件对象转换为字典格式
   - test_event_from_dict: 测试从字典创建事件对象

2. Chapter 模型：测试章节数据模型的功能
   - test_chapter_creation: 测试创建章节对象
   - test_chapter_with_segments: 测试带有段落的章节对象
   - test_chapter_to_dict: 测试章节对象转换为字典格式

3. CausalEdge 模型：测试因果边的功能
   - test_causal_edge_creation: 测试创建因果关系边对象
   - test_causal_edge_to_dict: 测试因果边转换为字典格式

4. Treasure 模型：测试法宝/物品模型的功能
   - test_treasure_creation: 测试创建法宝对象
   - test_treasure_to_dict: 测试法宝对象转换为字典格式

5. JsonLoader 工具类：测试JSON数据加载和保存功能
   - test_load_json: 测试加载JSON文件功能
   - test_save_json: 测试保存JSON文件功能

6. TextSplitter 工具类：测试文本分段功能
   - test_split_chapter: 测试章节文本分段功能
"""

import unittest
import os
import sys
import json
from typing import Dict, List, Any

# 将项目根目录添加到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from common.models.event import EventItem
from common.models.chapter import Chapter
from common.models.causal_edge import CausalEdge
from common.models.treasure import Treasure
from common.utils.json_loader import JsonLoader
from common.utils.text_splitter import TextSplitter


class TestEventModel(unittest.TestCase):
    """测试EventItem数据模型"""
    
    def test_event_creation(self):
        """测试创建EventItem对象"""
        event = EventItem(
            event_id="event-001",
            description="韩立在莫家村练习铁皮指功",
            characters=["韩立"],
            location="莫家村",
            time="幼年",
            chapter_id="chapter-001"
        )
        
        self.assertEqual(event.event_id, "event-001")
        self.assertEqual(event.description, "韩立在莫家村练习铁皮指功")
        self.assertEqual(event.characters, ["韩立"])
        
    def test_event_to_dict(self):
        """测试EventItem转换为字典"""
        event = EventItem(
            event_id="event-001",
            description="韩立在莫家村练习铁皮指功",
            characters=["韩立"],
            location="莫家村",
            time="幼年",
            chapter_id="chapter-001"
        )
        
        event_dict = event.to_dict()
        self.assertIsInstance(event_dict, dict)
        self.assertEqual(event_dict["event_id"], "event-001")
        self.assertEqual(event_dict["description"], "韩立在莫家村练习铁皮指功")
        
    def test_event_from_dict(self):
        """测试从字典创建EventItem"""
        event_dict = {
            "event_id": "event-002",
            "description": "韩立获得了《七修符箓》",
            "characters": ["韩立", "墨老"],
            "location": "莫家村",
            "time": "少年",
            "chapter_id": "chapter-001"
        }
        
        event = EventItem.from_dict(event_dict)
        self.assertEqual(event.event_id, "event-002")
        self.assertEqual(event.description, "韩立获得了《七修符箓》")
        self.assertEqual(len(event.characters), 2)


class TestChapterModel(unittest.TestCase):
    """测试Chapter数据模型"""
    
    def test_chapter_creation(self):
        """测试创建Chapter对象"""
        # 根据实际Chapter类的定义
        content = "韩立出生在莫家村的一户普通农家，父亲韩明典，母亲王氏..."
        chapter = Chapter(
            chapter_id="第一章",
            title="莫家村韩立",
            content=content
        )
        
        self.assertEqual(chapter.chapter_id, "第一章")
        self.assertEqual(chapter.content, content)
        
    def test_chapter_with_segments(self):
        """测试带有段落的Chapter对象"""
        segments = [
            {"seg_id": "第一章-1", "text": "韩立出生在莫家村的一户普通农家..."},
            {"seg_id": "第一章-2", "text": "韩立从小聪明伶俐，但体弱多病..."}
        ]
        
        chapter = Chapter(
            chapter_id="第一章",
            title="莫家村韩立",
            content="韩立出生在莫家村的一户普通农家，父亲韩明典，母亲王氏...",
            segments=segments
        )
        
        self.assertEqual(len(chapter.segments), 2)
        self.assertEqual(chapter.segments[0]["seg_id"], "第一章-1")
        
    def test_chapter_to_dict(self):
        """测试Chapter转换为字典"""
        content = "韩立出生在莫家村的一户普通农家，父亲韩明典，母亲王氏..."
        chapter = Chapter(
            chapter_id="第一章",
            title="莫家村韩立",
            content=content
        )
        
        chapter_dict = chapter.to_dict()
        self.assertIsInstance(chapter_dict, dict)
        self.assertEqual(chapter_dict["chapter_id"], "第一章")
        self.assertEqual(chapter_dict["content"], content)


class TestCausalEdgeModel(unittest.TestCase):
    """测试CausalEdge数据模型"""
    
    def test_causal_edge_creation(self):
        """测试创建CausalEdge对象"""
        edge = CausalEdge(
            from_id="event-001",
            to_id="event-002",
            strength="高",
            reason="韩立练习铁皮指功，为后来修炼七修符箓打下基础"
        )
        
        self.assertEqual(edge.from_id, "event-001")
        self.assertEqual(edge.to_id, "event-002")
        self.assertEqual(edge.strength, "高")
        
    def test_causal_edge_to_dict(self):
        """测试CausalEdge转换为字典"""
        edge = CausalEdge(
            from_id="event-001",
            to_id="event-002",
            strength="高",
            reason="韩立练习铁皮指功，为后来修炼七修符箓打下基础"
        )
        
        edge_dict = edge.to_dict()
        self.assertIsInstance(edge_dict, dict)
        self.assertEqual(edge_dict["from"], "event-001")
        self.assertEqual(edge_dict["to"], "event-002")


class TestTreasureModel(unittest.TestCase):
    """测试Treasure数据模型"""
    
    def test_treasure_creation(self):
        """测试创建Treasure对象"""
        treasure = Treasure(
            name="七修符箓",
            description="记载符箓修炼方法的入门典籍",
            effects=["符箓修炼"],
            origin="墨老赠送",
            first_appearance="第一章"
        )
        
        self.assertEqual(treasure.name, "七修符箓")
        self.assertEqual(treasure.description, "记载符箓修炼方法的入门典籍")
        
    def test_treasure_to_dict(self):
        """测试Treasure转换为字典"""
        treasure = Treasure(
            name="七修符箓",
            description="记载符箓修炼方法的入门典籍",
            effects=["符箓修炼"],
            origin="墨老赠送",
            first_appearance="第一章"
        )
        
        treasure_dict = treasure.to_dict()
        self.assertIsInstance(treasure_dict, dict)
        self.assertEqual(treasure_dict["name"], "七修符箓")
        self.assertEqual(treasure_dict["description"], "记载符箓修炼方法的入门典籍")


class TestJsonLoader(unittest.TestCase):
    """测试JsonLoader工具类"""
    
    def setUp(self):
        """测试前准备，创建临时JSON文件"""
        self.temp_file = os.path.join(current_dir, "test_data.json")
        self.test_data = {
            "name": "韩立",
            "age": 15,
            "skills": ["铁皮指功", "符箓"]
        }
        
        # 写入测试数据
        with open(self.temp_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, ensure_ascii=False)
            
    def tearDown(self):
        """测试后清理，删除临时文件"""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            
    def test_load_json(self):
        """测试加载JSON文件"""
        data = JsonLoader.load_json(self.temp_file)
        self.assertEqual(data["name"], "韩立")
        self.assertEqual(data["age"], 15)
        self.assertEqual(len(data["skills"]), 2)
        
    def test_save_json(self):
        """测试保存JSON文件"""
        new_data = {"name": "墨老", "age": 60}
        JsonLoader.save_json(new_data, self.temp_file)
        
        # 再次加载确认保存成功
        loaded_data = JsonLoader.load_json(self.temp_file)
        self.assertEqual(loaded_data["name"], "墨老")
        self.assertEqual(loaded_data["age"], 60)


class TestTextSplitter(unittest.TestCase):
    """测试TextSplitter工具类"""
    
    def test_split_chapter(self):
        """测试章节分段"""
        text = """第一章 莫家村
        韩立出生在莫家村的一户普通农家，父亲韩明典，母亲王氏。
        
        韩立从小聪明伶俐，但体弱多病，经常生病。
        
        墨老给了韩立一本《铁皮指》的功法秘籍。"""
        
        segments = TextSplitter.split_chapter(text, seg_size=100)
        
        self.assertGreaterEqual(len(segments), 1)  # 至少应该有一段
        self.assertTrue("seg_id" in segments[0])
        self.assertTrue("text" in segments[0])
        

if __name__ == '__main__':
    unittest.main()
