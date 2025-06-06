#!/usr/bin/env python3
"""
事件抽取模块测试

本文件包含对事件抽取模块的测试用例，主要测试：
1. EventExtractor 是否能正确从章节中抽取事件
2. LLMClient 是否能正常调用和处理返回
3. 事件结构化处理是否正确
"""

import sys
import os
import unittest
import json
from unittest.mock import patch, MagicMock

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from common.models.chapter import Chapter
from common.models.event import EventItem
from event_extraction.service.extractor_service import EventExtractor
from common.utils.json_loader import JsonLoader


class TestEventExtractor(unittest.TestCase):
    """测试事件抽取器功能"""
    
    def setUp(self):
        """测试前的准备工作，使用真实数据"""
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # 使用真实的测试数据文件
        real_test_file = os.path.join(project_root, "novel", "test.txt")
        
        # 加载真实章节数据
        from text_ingestion.chapter_loader import ChapterLoader
        loader = ChapterLoader(segment_size=800)
        
        # 如果文件存在，使用真实数据；否则使用模拟数据
        if os.path.exists(real_test_file):
            real_chapter = loader.load_from_txt(real_test_file)
            if real_chapter and real_chapter.segments:
                # 使用真实数据的前两个段落作为测试数据
                self.test_chapter = Chapter(
                    chapter_id=real_chapter.chapter_id,
                    title=real_chapter.title,
                    content=real_chapter.segments[0]["text"] if real_chapter.segments else "测试内容",
                    segments=real_chapter.segments[:2]  # 使用前两个段落
                )
            else:
                # 如果加载失败，使用备用数据
                self.test_chapter = Chapter(
                    chapter_id="第一章",
                    title="山边小村",
                    content="韩立在七玄门学习炼药，遇到了南宫婉。",
                    segments=[
                        {"seg_id": "第一章-1", "text": "韩立在七玄门学习炼药"},
                        {"seg_id": "第一章-2", "text": "遇到了南宫婉"}
                    ]
                )
        else:
            # 备用测试数据
            self.test_chapter = Chapter(
                chapter_id="第一章",
                title="山边小村", 
                content="韩立在七玄门学习炼药，遇到了南宫婉。",
                segments=[
                    {"seg_id": "第一章-1", "text": "韩立在七玄门学习炼药"},
                    {"seg_id": "第一章-2", "text": "遇到了南宫婉"}
                ]
            )
        
        # 基于真实数据的模拟事件提取结果
        self.mock_event_result = [
            {
                "event_id": "第一章-1",
                "description": "韩立睁眼观察周围环境",
                "characters": ["韩立", "韩铸"],
                "treasures": [],
                "time": "夜晚",
                "location": "茅草屋",
                "chapter_id": self.test_chapter.chapter_id
            },
            {
                "event_id": "第一章-2", 
                "description": "韩立准备进山拣干柴",
                "characters": ["韩立"],
                "treasures": [],
                "time": "明天",
                "location": "山村",
                "chapter_id": self.test_chapter.chapter_id
            }
        ]
    
    @patch('event_extraction.repository.llm_client.LLMClient.call_with_json_response')
    @patch('common.utils.json_loader.JsonLoader.load_json')
    def test_extract_events(self, mock_load_json, mock_extract):
        """测试事件抽取功能，使用模拟的LLM调用"""
        # 模拟加载提示词模板
        mock_load_json.return_value = {
            "system": "你是一个事件抽取助手",
            "user": "请从以下文本中抽取事件：{text}",
            "instruction": "请从以下文本中抽取事件：{text}"
        }
        
        # 模拟call_with_json_response的返回值
        mock_extract.return_value = {
            "success": True,
            "json_content": self.mock_event_result[0]
        }
        
        # 创建抽取器实例
        extractor = EventExtractor(
            model="test-model",
            prompt_path="fake_path.json",
            api_key="fake-key"
        )
        
        # 执行事件抽取
        events = extractor.extract(self.test_chapter)
        
        # 验证结果
        self.assertGreater(len(events), 0)  # 验证有事件被提取出来
        self.assertIsInstance(events[0], EventItem)
        
        # 检查提取的事件属性是否符合预期
        event_descriptions = [e.description for e in events]
        self.assertTrue(len(event_descriptions) > 0)  # 确保有事件被提取
        
        # 验证事件内容合理性（基于真实数据）
        for event in events:
            self.assertIsNotNone(event.description)
            self.assertGreater(len(event.description), 0)
            self.assertIsNotNone(event.characters)
            self.assertIsInstance(event.characters, list)
            
            # 验证事件包含真实的角色信息
            if "韩立" in str(event.characters):
                self.assertIn("韩立", event.characters)
                break
    
    @patch('event_extraction.repository.llm_client.LLMClient')
    @patch('common.utils.json_loader.JsonLoader.load_json')
    def test_extraction_error_handling(self, mock_load_json, mock_llm_client):
        """测试事件抽取错误处理"""
        # 模拟加载提示词模板
        mock_load_json.return_value = {
            "system": "你是一个事件抽取助手",
            "user": "请从以下文本中抽取事件：{text}",
            "instruction": "请从以下文本中抽取事件：{text}"
        }
        
        # 设置模拟的LLM调用抛出异常
        mock_instance = MagicMock()
        mock_instance.extract_events_from_segment.side_effect = Exception("API调用失败")
        mock_llm_client.return_value = mock_instance
        
        # 创建抽取器实例
        extractor = EventExtractor(
            model="test-model",
            prompt_path="fake_path.json",
            api_key="fake-key"
        )
        
        # 执行事件抽取，应该返回空列表而非抛出异常
        events = extractor.extract(self.test_chapter)
        self.assertEqual(len(events), 0)
    
    @patch('event_extraction.repository.llm_client.LLMClient.call_with_json_response')
    @patch('common.utils.json_loader.JsonLoader.load_json')
    def test_extract_events_from_real_data(self, mock_load_json, mock_extract):
        """测试从真实数据中提取事件"""
        # 模拟加载提示词模板
        mock_load_json.return_value = {
            "system": "你是一个专业的事件抽取助手",
            "user": "请从以下《凡人修仙传》文本中抽取事件：{text}",
            "instruction": "请分析以下文本并提取其中的关键事件"
        }
        
        # 模拟基于真实数据的LLM响应
        mock_extract.return_value = {
            "success": True,
            "json_content": {
                "events": [
                    {
                        "event_id": "第一章-1",
                        "description": "韩立夜晚躺在床上思考明天进山的事情",
                        "characters": ["韩立", "韩铸"],
                        "treasures": [],
                        "time": "夜晚",
                        "location": "茅草屋",
                        "chapter_id": self.test_chapter.chapter_id
                    }
                ]
            }
        }
        
        # 创建抽取器实例
        extractor = EventExtractor(
            model="test-model",
            prompt_path="fake_path.json",
            api_key="fake-key"
        )
        
        # 执行事件抽取
        events = extractor.extract(self.test_chapter)
        
        # 验证结果
        self.assertGreater(len(events), 0)
        
        # 验证事件内容的真实性
        first_event = events[0]
        self.assertIsInstance(first_event, EventItem)
        self.assertIn("韩立", first_event.characters)
        self.assertIsNotNone(first_event.description)
        self.assertGreater(len(first_event.description), 5)  # 描述应该有一定长度
        
        # 验证章节关联正确
        self.assertEqual(first_event.chapter_id, self.test_chapter.chapter_id)


if __name__ == "__main__":
    unittest.main()
