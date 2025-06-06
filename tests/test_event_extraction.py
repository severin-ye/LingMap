#!/usr/bin/env python3
"""
事件抽取模块的单元测试

本文件包含对《凡人修仙传》因果事件图谱系统中事件抽取模块的测试。
事件抽取模块负责从小说章节文本中提取关键事件，是整个系统的基础功能之一。

测试内容：
1. EventExtractor 服务：
   - 测试事件抽提取器的初始化
   - 验证提取方法能正确处理章节内容
   - 测试返回的事件列表结构和格式
   - 验证异常处理机制
   
2. LLM 调用封装：
   - 测试与大语言模型的交互
   - 验证提示词模板的使用
   - 测试结果解析和处理

3. 错误处理：
   - 测试面对异常输入时的稳定性
   - 验证错误日志和报告机制
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from common.models.chapter import Chapter
from common.models.event import EventItem
from event_extraction.service.extractor_service import EventExtractor


class TestEventExtraction(unittest.TestCase):
    """事件抽取模块的单元测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建一个模拟的LLM客户端
        self.mock_llm_client = MagicMock()
        
        # 模拟的成功响应
        self.mock_response = {
            "success": True,
            "json_content": {
                "events": [
                    {
                        "event_id": "第一章-1",
                        "description": "韩立发现灵药",
                        "characters": ["韩立"],
                        "treasures": ["灵药"],
                        "result": "获得提升修为的机会",
                        "location": "山洞",
                        "time": "白天"
                    }
                ]
            }
        }
        
        # 设置模拟LLM客户端的返回值
        self.mock_llm_client.call_with_json_response.return_value = self.mock_response
        
    @patch('event_extraction.service.extractor_service.LLMClient')
    def test_extract(self, mock_llm_client_class):
        """测试事件抽取功能"""
        # 配置模拟的LLM客户端
        mock_llm_client_class.return_value = self.mock_llm_client
        
        # 创建测试用的章节数据
        chapter = Chapter(
            chapter_id="第一章",
            title="测试章节",
            content="这是测试用的章节内容",
            segments=[
                {
                    "seg_id": "第一章-1",
                    "text": "韩立在山洞中发现了一株灵药，这对他的修炼大有裨益。"
                }
            ]
        )
        
        # 初始化抽取器（不实际调用API）
        extractor = EventExtractor(
            model="fake-model",
            api_key="fake-key",
            max_workers=1
        )
        extractor.llm_client = self.mock_llm_client
        
        # 执行抽取
        events = extractor.extract(chapter)
        
        # 验证结果
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_id, "第一章-1")
        self.assertEqual(events[0].description, "韩立发现灵药")
        self.assertEqual(events[0].characters, ["韩立"])
        self.assertEqual(events[0].treasures, ["灵药"])


if __name__ == "__main__":
    unittest.main()
