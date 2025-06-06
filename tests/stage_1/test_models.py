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
    
    def setUp(self):
        """测试前准备，加载真实小说数据以提取事件相关信息"""
        novel_path = os.path.join(project_root, "novel", "test.txt")
        with open(novel_path, 'r', encoding='utf-8') as f:
            novel_text = f.read()
            
        # 从小说中提取可能的人物、地点等信息
        self.characters = ["韩立", "韩铸", "韩父", "韩母", "老张叔", "墨大夫", "三叔"]
        self.locations = ["莫家村", "青牛镇", "神手谷", "彩霞山", "赤水峰"]
        self.times = ["幼年", "少年", "成年"]
        
        # 提取第一章标识
        chapter_start = novel_text.find("第一章")
        if chapter_start != -1:
            self.chapter_id = novel_text[chapter_start:novel_text.find("\n", chapter_start)].strip()
        else:
            self.chapter_id = "第一章"
    
    def test_event_creation(self):
        """测试创建EventItem对象：使用小说中的真实场景"""
        event = EventItem(
            event_id="event-001",
            description="韩立和同伴一起进山拣干柴",
            characters=["韩立"],
            location="莫家村附近的山上",
            time="幼年",
            chapter_id=self.chapter_id
        )
        
        self.assertEqual(event.event_id, "event-001")
        self.assertEqual(event.description, "韩立和同伴一起进山拣干柴")
        self.assertEqual(event.characters, ["韩立"])
        
    def test_event_to_dict(self):
        """测试EventItem转换为字典：使用小说中的真实场景"""
        event = EventItem(
            event_id="event-001",
            description="韩立得知三叔来访会改变他的一生",
            characters=["韩立", "三叔"],
            location="莫家村",
            time="幼年",
            chapter_id=self.chapter_id
        )
        
        event_dict = event.to_dict()
        self.assertIsInstance(event_dict, dict)
        self.assertEqual(event_dict["event_id"], "event-001")
        self.assertEqual(event_dict["description"], "韩立得知三叔来访会改变他的一生")
        
    def test_event_from_dict(self):
        """测试从字典创建EventItem：使用小说中的真实场景"""
        event_dict = {
            "event_id": "event-002",
            "description": "韩立被三叔带去参加七玄门的考验",
            "characters": ["韩立", "三叔"],
            "location": "青牛镇",
            "time": "少年",
            "chapter_id": self.chapter_id
        }
        
        event = EventItem.from_dict(event_dict)
        self.assertEqual(event.event_id, "event-002")
        self.assertEqual(event.description, "韩立被三叔带去参加七玄门的考验")
        self.assertEqual(len(event.characters), 2)


class TestChapterModel(unittest.TestCase):
    """测试Chapter数据模型"""
    
    def setUp(self):
        """测试前准备，加载真实小说数据"""
        novel_path = os.path.join(project_root, "novel", "test.txt")
        with open(novel_path, 'r', encoding='utf-8') as f:
            self.novel_text = f.read()
        
        # 提取第一章内容
        chapter_start = self.novel_text.find("第一章")
        chapter_end = self.novel_text.find("第二章")
        if chapter_end == -1:  # 如果找不到第二章，则使用全文
            self.chapter_text = self.novel_text[chapter_start:]
        else:
            self.chapter_text = self.novel_text[chapter_start:chapter_end]
        
        # 提取章节标题
        title_start = self.chapter_text.find("第一章")
        title_end = self.chapter_text.find("\n", title_start)
        self.chapter_title = self.chapter_text[title_start:title_end].strip()
    
    def test_chapter_creation(self):
        """测试创建Chapter对象：使用真实小说文本"""
        chapter = Chapter(
            chapter_id="第一章",
            title=self.chapter_title,
            content=self.chapter_text
        )
        
        self.assertEqual(chapter.chapter_id, "第一章")
        self.assertEqual(chapter.title, self.chapter_title)
        self.assertEqual(chapter.content, self.chapter_text)
        
    def test_chapter_with_segments(self):
        """测试带有段落的Chapter对象：使用真实文本生成的段落"""
        # 使用TextSplitter生成真实段落
        segments = TextSplitter.split_chapter(self.chapter_text, seg_size=200)
        
        chapter = Chapter(
            chapter_id="第一章",
            title=self.chapter_title,
            content=self.chapter_text,
            segments=segments
        )
        
        # 验证分段数量（不固定为2，因为真实小说文本的分段结果可能随内容变化）
        self.assertGreater(len(chapter.segments), 0)
        self.assertEqual(chapter.segments[0]["seg_id"], "1")  # TextSplitter生成的段落ID格式为数字
        
    def test_chapter_to_dict(self):
        """测试Chapter转换为字典：使用真实小说文本"""
        chapter = Chapter(
            chapter_id="第一章",
            title=self.chapter_title,
            content=self.chapter_text
        )
        
        chapter_dict = chapter.to_dict()
        self.assertIsInstance(chapter_dict, dict)
        self.assertEqual(chapter_dict["chapter_id"], "第一章")
        self.assertEqual(chapter_dict["title"], self.chapter_title)
        self.assertEqual(chapter_dict["content"], self.chapter_text)


class TestCausalEdgeModel(unittest.TestCase):
    """测试CausalEdge数据模型"""
    
    def test_causal_edge_creation(self):
        """测试创建CausalEdge对象：使用小说中的真实因果关系"""
        edge = CausalEdge(
            from_id="event-001",
            to_id="event-002",
            strength="高",
            reason="三叔介绍韩立参加七玄门考核，导致韩立离开家乡踏上修仙之路"
        )
        
        self.assertEqual(edge.from_id, "event-001")
        self.assertEqual(edge.to_id, "event-002")
        self.assertEqual(edge.strength, "高")
        
    def test_causal_edge_to_dict(self):
        """测试CausalEdge转换为字典：使用小说中的真实因果关系"""
        edge = CausalEdge(
            from_id="event-001",
            to_id="event-002",
            strength="中",
            reason="墨大夫选中韩立作为炼药童子，使韩立学习了无名口诀"
        )
        
        edge_dict = edge.to_dict()
        self.assertIsInstance(edge_dict, dict)
        self.assertEqual(edge_dict["from"], "event-001")
        self.assertEqual(edge_dict["to"], "event-002")


class TestTreasureModel(unittest.TestCase):
    """测试Treasure数据模型"""
    
    def setUp(self):
        """测试前准备，加载小说数据以确定真实的宝物/法宝信息"""
        novel_path = os.path.join(project_root, "novel", "test.txt")
        with open(novel_path, 'r', encoding='utf-8') as f:
            self.novel_text = f.read()
            
        # 从小说中提取可能的宝物信息
        self.treasures = [
            {
                "name": "铁皮指功",
                "description": "莫家村墨大夫传授给韩立的入门功法，修炼后指尖如铁",
                "effects": ["强化手指力量", "初级攻击功法"],
                "origin": "墨大夫传授",
                "first_appearance": "第一章"
            },
            {
                "name": "三阶丹药",
                "description": "墨大夫珍藏的珍贵丹药，可用于七玄门测试",
                "effects": ["增强灵力", "提高修行资质"],
                "origin": "墨大夫珍藏",
                "first_appearance": "第一章"
            }
        ]
    
    def test_treasure_creation(self):
        """测试创建Treasure对象：使用小说中的真实法宝信息"""
        treasure_data = self.treasures[0]  # 使用铁皮指功作为测试
        
        treasure = Treasure(
            name=treasure_data["name"],
            description=treasure_data["description"],
            effects=treasure_data["effects"],
            origin=treasure_data["origin"],
            first_appearance=treasure_data["first_appearance"]
        )
        
        self.assertEqual(treasure.name, "铁皮指功")
        self.assertEqual(treasure.description, "莫家村墨大夫传授给韩立的入门功法，修炼后指尖如铁")
        self.assertEqual(len(treasure.effects), 2)
        
    def test_treasure_to_dict(self):
        """测试Treasure转换为字典：使用小说中的真实法宝信息"""
        treasure_data = self.treasures[1]  # 使用三阶丹药作为测试
        
        treasure = Treasure(
            name=treasure_data["name"],
            description=treasure_data["description"],
            effects=treasure_data["effects"],
            origin=treasure_data["origin"],
            first_appearance=treasure_data["first_appearance"]
        )
        
        treasure_dict = treasure.to_dict()
        self.assertIsInstance(treasure_dict, dict)
        self.assertEqual(treasure_dict["name"], "三阶丹药")
        self.assertEqual(treasure_dict["description"], "墨大夫珍藏的珍贵丹药，可用于七玄门测试")
        self.assertEqual(len(treasure_dict["effects"]), 2)


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
        """测试章节分段：使用小说真实文本"""
        # 加载真实小说数据
        novel_path = os.path.join(project_root, "novel", "test.txt")
        with open(novel_path, 'r', encoding='utf-8') as f:
            novel_text = f.read()
        
        # 提取第一章内容进行测试
        chapter_start = novel_text.find("第一章")
        chapter_end = novel_text.find("第二章")
        if chapter_end == -1:  # 如果找不到第二章，则使用全文
            chapter_text = novel_text[chapter_start:]
        else:
            chapter_text = novel_text[chapter_start:chapter_end]
            
        # 使用TextSplitter进行分段
        segments = TextSplitter.split_chapter(chapter_text, seg_size=200)
        
        # 验证分段结果
        self.assertGreaterEqual(len(segments), 3)  # 应该有多个段落
        self.assertTrue("seg_id" in segments[0])
        self.assertTrue("text" in segments[0])
        
        # 验证分段内容是否包含原文的关键信息
        all_text = " ".join([seg["text"] for seg in segments])
        self.assertIn("韩立", all_text)
        self.assertIn("二愣子", all_text)
        

if __name__ == '__main__':
    unittest.main()
