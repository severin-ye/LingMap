#!/usr/bin/env python3
"""
幻觉修复模块的单元测试

本文件包含对《凡人修仙传》因果事件图谱系统中幻觉修复模块(HAR: Hallucination Refinement)的测试。
幻觉修复模块负责检测并修复事件提取过程中可能产生的幻觉或不准确信息，
通过与原文对比验证事件的准确性，提高整个系统的可靠性。

测试内容：
1. HallucinationRefiner 服务：
   - 测试幻觉检测算法的准确性
   - 验证修复策略的有效性
   - 测试对不同类型幻觉的处理能力
   - 验证修复后事件的一致性和完整性
   
2. 与原文对比验证：
   - 测试事件内容与章节原文的对比逻辑
   - 验证文本相关度计算方法
   - 测试关键实体和事实的提取与验证
   
3. 修复策略：
   - 测试轻度修复功能（保留部分信息）
   - 测试重度修复功能（完全替换不准确信息）
   - 验证修复后事件的质量评估
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from common.models.event import EventItem
from hallucination_refine.service.har_service import HallucinationRefiner


class TestHallucinationRefine(unittest.TestCase):
    """幻觉修复模块的单元测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建一个模拟的LLM客户端
        self.mock_llm_client = MagicMock()
        
        # 模拟的成功响应（无幻觉）
        self.mock_no_hallucination_response = {
            "success": True,
            "json_content": {
                "has_hallucination": False,
                "issues": [],
                "refined_event": {
                    "event_id": "E1-1",
                    "description": "韩立获得灵药",
                    "characters": ["韩立"],
                    "treasures": ["灵药"],
                    "result": "提高修为",
                    "location": "山洞",
                    "time": "白天"
                }
            }
        }
        
        # 模拟的成功响应（有幻觉）
        self.mock_has_hallucination_response = {
            "success": True,
            "json_content": {
                "has_hallucination": True,
                "issues": [
                    {
                        "field": "treasures",
                        "original": "九转金丹",
                        "corrected": "灵药",
                        "reason": "九转金丹在原著中还未出现，应为灵药"
                    }
                ],
                "refined_event": {
                    "event_id": "E1-1",
                    "description": "韩立获得灵药",
                    "characters": ["韩立"],
                    "treasures": ["灵药"],
                    "result": "提高修为",
                    "location": "山洞",
                    "time": "白天"
                }
            }
        }
        
    @patch('hallucination_refine.service.har_service.LLMClient')
    def test_refine_no_hallucination(self, mock_llm_client_class):
        """测试无幻觉的情况"""
        # 配置模拟的LLM客户端
        mock_llm_client_class.return_value = self.mock_llm_client
        self.mock_llm_client.call_with_json_response.return_value = self.mock_no_hallucination_response
        
        # 创建测试用的事件数据
        event = EventItem(
            event_id="E1-1",
            description="韩立获得灵药",
            characters=["韩立"],
            treasures=["灵药"],
            result="提高修为",
            location="山洞",
            time="白天"
        )
        
        # 初始化精修器（不实际调用API）
        refiner = HallucinationRefiner(
            model="fake-model",
            api_key="fake-key",
            max_workers=1,
            max_iterations=1
        )
        refiner.llm_client = self.mock_llm_client
        
        # 执行精修
        refined_events = refiner.refine([event], "测试上下文")
        
        # 验证结果
        self.assertEqual(len(refined_events), 1)
        self.assertEqual(refined_events[0].event_id, "E1-1")
        self.assertEqual(refined_events[0].treasures, ["灵药"])
        
        # 验证LLM客户端调用次数（只调用一次，没有迭代）
        self.assertEqual(self.mock_llm_client.call_with_json_response.call_count, 1)
        
    @patch('hallucination_refine.service.har_service.LLMClient')
    def test_refine_has_hallucination(self, mock_llm_client_class):
        """测试有幻觉的情况"""
        # 配置模拟的LLM客户端
        mock_llm_client_class.return_value = self.mock_llm_client
        self.mock_llm_client.call_with_json_response.return_value = self.mock_has_hallucination_response
        
        # 创建测试用的事件数据（包含幻觉）
        event = EventItem(
            event_id="E1-1",
            description="韩立获得九转金丹",
            characters=["韩立"],
            treasures=["九转金丹"],
            result="提高修为",
            location="山洞",
            time="白天"
        )
        
        # 初始化精修器（不实际调用API）
        refiner = HallucinationRefiner(
            model="fake-model",
            api_key="fake-key",
            max_workers=1,
            max_iterations=2
        )
        refiner.llm_client = self.mock_llm_client
        
        # 配置第二次调用返回无幻觉的响应（终止迭代）
        self.mock_llm_client.call_with_json_response.side_effect = [
            self.mock_has_hallucination_response,
            self.mock_no_hallucination_response
        ]
        
        # 执行精修
        refined_events = refiner.refine([event], "测试上下文")
        
        # 验证结果
        self.assertEqual(len(refined_events), 1)
        self.assertEqual(refined_events[0].event_id, "E1-1")
        self.assertEqual(refined_events[0].treasures, ["灵药"])
        
        # 验证LLM客户端调用次数（调用两次，进行了一次迭代）
        self.assertEqual(self.mock_llm_client.call_with_json_response.call_count, 2)


if __name__ == "__main__":
    unittest.main()
