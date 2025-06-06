#!/usr/bin/env python3
"""
事件抽取模块测试

本文件包含对事件抽取模块的测试用例，主要测试：
1. EventExtractor 是否能正确从章节中抽取事件
2. LLMClient 是否能正常调用和处理返回
3. 事件结构化处理是否正确
"""

import unittest
import json
import os
from unittest.mock import patch, MagicMock

from common.models.chapter import Chapter
from common.models.event import EventItem
from event_extraction.service.extractor_service import EventExtractor
from common.utils.json_loader import JsonLoader


class TestEventExtractor(unittest.TestCase):
    """测试事件抽取器功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试用的章节对象
        self.test_chapter = Chapter(
            chapter_id="test_chapter",
            title="测试章节",
            content="韩立在七玄门学习炼药，遇到了南宫婉。",
            segments=[
                {"seg_id": "1", "text": "韩立在七玄门学习炼药，"},
                {"seg_id": "2", "text": "遇到了南宫婉。"}
            ]
        )
        
        # 模拟事件提取结果
        self.mock_event_result = [
            {
                "event_id": "e1",
                "description": "韩立在七玄门学习炼药",
                "characters": ["韩立"],
                "treasures": [],
                "time": "未知",
                "location": "七玄门",
                "chapter_id": "test_chapter"
            },
            {
                "event_id": "e2",
                "description": "韩立遇到了南宫婉",
                "characters": ["韩立", "南宫婉"],
                "treasures": [],
                "time": "未知",
                "location": "七玄门",
                "chapter_id": "test_chapter"
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
        self.assertIn("韩立在七玄门学习炼药", event_descriptions)
        
        # 查找包含特定描述的事件用于详细验证
        for event in events:
            if event.description == "韩立在七玄门学习炼药":
                self.assertEqual(event.location, "七玄门")
                self.assertEqual(event.characters, ["韩立"])
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


if __name__ == "__main__":
    unittest.main()
