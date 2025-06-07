#!/usr/bin/env python3
"""
因果链构建模块测试

本文件包含对因果链构建模块的测试用例，主要测试：
1. CausalLinker 是否能正确识别事件间的因果关系
2. DAG 构建算法是否正确（去环、权重处理）
3. LLM 调用和响应解析是否正常
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

from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from causal_linking.service.linker_service import CausalLinker
from causal_linking.di.provider import provide_linker


class TestCausalLinker(unittest.TestCase):
    """测试 CausalLinker 类的功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # 创建测试用的事件数据（基于《凡人修仙传》真实情节）
        self.test_events = [
            EventItem(
                event_id="E1",
                description="韩立上山采集浆果",
                characters=["韩立"],
                treasures=[],
                location="七玄门附近山林",
                chapter_id="第一章",
                result="采集到野果"
            ),
            EventItem(
                event_id="E2",
                description="韩立归来后遇到三叔",
                characters=["韩立", "三叔"],
                treasures=[],
                location="山村",
                chapter_id="第一章",
                result="三叔告知七玄门招收弟子"
            ),
            EventItem(
                event_id="E3",
                description="韩立参加七玄门入门测试",
                characters=["韩立"],
                treasures=[],
                location="七玄门",
                chapter_id="第二章",
                result="通过测试成为杂役弟子"
            ),
            EventItem(
                event_id="E4",
                description="韩立获得神秘小瓶",
                characters=["韩立"],
                treasures=["神秘小瓶"],
                location="七玄门",
                chapter_id="第三章",
                result="发现小瓶能加速植物生长"
            )
        ]
        
        # 强度映射
        self.strength_mapping = {
            "高": 3,
            "中": 2,
            "低": 1
        }
        
    @patch('causal_linking.service.linker_service.LLMClient.call_with_json_response')
    def test_analyze_causal_relation(self, mock_llm_call):
        """测试分析两个事件之间的因果关系"""
        # 模拟LLM返回存在因果关系的响应
        mock_response = {
            "success": True,
            "json_content": {
                "has_causal_relation": True,
                "direction": "event1->event2",
                "strength": "高",
                "reason": "韩立上山采集归来后遇到三叔，是一个自然的时间顺序和因果关系"
            }
        }
        mock_llm_call.return_value = mock_response
        
        # 创建链接器实例
        linker = CausalLinker(
            model="gpt-4o",
            api_key="fake-key",
            strength_mapping=self.strength_mapping
        )
        
        # 分析因果关系
        edge = linker.analyze_causal_relation(self.test_events[0], self.test_events[1])
        
        # 验证结果
        self.assertIsNotNone(edge)
        self.assertEqual(edge.from_id, "E1")
        self.assertEqual(edge.to_id, "E2")
        self.assertEqual(edge.strength, "高")
        self.assertIn("自然的时间顺序", edge.reason)
        
        # 验证LLM被正确调用
        mock_llm_call.assert_called_once()
        
    @patch('causal_linking.service.linker_service.LLMClient.call_with_json_response')
    def test_no_causal_relation(self, mock_llm_call):
        """测试不存在因果关系的情况"""
        # 模拟LLM返回不存在因果关系的响应
        mock_response = {
            "success": True,
            "json_content": {
                "has_causal_relation": False,
                "direction": "",
                "strength": "",
                "reason": "两个事件之间没有直接的因果关系"
            }
        }
        mock_llm_call.return_value = mock_response
        
        # 创建链接器实例
        linker = CausalLinker(
            model="gpt-4o",
            api_key="fake-key",
            strength_mapping=self.strength_mapping
        )
        
        # 分析因果关系
        edge = linker.analyze_causal_relation(self.test_events[0], self.test_events[3])
        
        # 验证结果为None
        self.assertIsNone(edge)
        
    @patch('causal_linking.service.linker_service.LLMClient.call_with_json_response')
    def test_link_events_batch(self, mock_llm_call):
        """测试批量链接事件"""
        # 模拟不同事件对的LLM响应
        def mock_llm_side_effect(system_prompt, user_prompt):
            # 根据事件内容返回不同的响应
            if "E1" in user_prompt and "E2" in user_prompt:
                return {
                    "success": True,
                    "json_content": {
                        "has_causal_relation": True,
                        "direction": "event1->event2",
                        "strength": "高",
                        "reason": "E1导致E2"
                    }
                }
            elif "E2" in user_prompt and "E3" in user_prompt:
                return {
                    "success": True,
                    "json_content": {
                        "has_causal_relation": True,
                        "direction": "event1->event2",
                        "strength": "中",
                        "reason": "E2导致E3"
                    }
                }
            else:
                return {
                    "success": True,
                    "json_content": {
                        "has_causal_relation": False,
                        "direction": "",
                        "strength": "",
                        "reason": "无因果关系"
                    }
                }
        
        mock_llm_call.side_effect = mock_llm_side_effect
        
        # 创建链接器实例
        linker = CausalLinker(
            model="gpt-4o",
            api_key="fake-key",
            max_workers=2,
            strength_mapping=self.strength_mapping
        )
        
        # 批量链接事件（使用前3个事件）
        edges = linker.link_events(self.test_events[:3])
        
        # 验证结果
        self.assertGreater(len(edges), 0)
        
        # 验证有E1->E2的边
        e1_to_e2 = next((e for e in edges if e.from_id == "E1" and e.to_id == "E2"), None)
        self.assertIsNotNone(e1_to_e2)
        self.assertEqual(e1_to_e2.strength, "高")
        
    def test_build_dag_simple(self):
        """测试构建简单的DAG"""
        # 创建测试用的因果边
        edges = [
            CausalEdge(from_id="E1", to_id="E2", strength="高", reason="测试原因1"),
            CausalEdge(from_id="E2", to_id="E3", strength="中", reason="测试原因2"),
            CausalEdge(from_id="E1", to_id="E3", strength="低", reason="测试原因3")
        ]
        
        # 创建链接器实例
        linker = CausalLinker(
            model="gpt-4o",
            api_key="fake-key",
            strength_mapping=self.strength_mapping
        )
        
        # 构建DAG
        events, dag_edges = linker.build_dag(self.test_events[:3], edges)
        
        # 验证结果
        self.assertEqual(len(events), 3)
        self.assertGreater(len(dag_edges), 0)
        self.assertLessEqual(len(dag_edges), len(edges))
        
        # 验证高强度边被保留
        high_strength_edges = [e for e in dag_edges if e.strength == "高"]
        self.assertGreater(len(high_strength_edges), 0)
        
    def test_build_dag_with_cycle(self):
        """测试包含环的情况下构建DAG"""
        # 创建会形成环的因果边
        edges = [
            CausalEdge(from_id="E1", to_id="E2", strength="高", reason="E1->E2"),
            CausalEdge(from_id="E2", to_id="E3", strength="高", reason="E2->E3"),
            CausalEdge(from_id="E3", to_id="E1", strength="中", reason="E3->E1 (会形成环)")
        ]
        
        # 创建链接器实例
        linker = CausalLinker(
            model="gpt-4o",
            api_key="fake-key",
            strength_mapping=self.strength_mapping
        )
        
        # 构建DAG
        events, dag_edges = linker.build_dag(self.test_events[:3], edges)
        
        # 验证结果：应该去掉形成环的边
        self.assertEqual(len(events), 3)
        self.assertLess(len(dag_edges), len(edges))  # 应该有边被移除
        
        # 验证没有E3->E1的边（因为会形成环）
        cycle_edge = next((e for e in dag_edges if e.from_id == "E3" and e.to_id == "E1"), None)
        self.assertIsNone(cycle_edge)
        
    def test_cycle_detection(self):
        """测试环检测算法"""
        # 创建链接器实例
        linker = CausalLinker(
            model="gpt-4o",
            api_key="fake-key",
            strength_mapping=self.strength_mapping
        )
        
        # 测试简单图：0->1->2
        graph = [[] for _ in range(3)]
        graph[0].append(1)
        graph[1].append(2)
        
        # 添加0->2不会形成环
        self.assertFalse(linker._will_form_cycle(graph, 0, 2))
        
        # 添加2->0会形成环
        self.assertTrue(linker._will_form_cycle(graph, 2, 0))
        
    def test_reachability(self):
        """测试可达性检测算法"""
        # 创建链接器实例
        linker = CausalLinker(
            model="gpt-4o",
            api_key="fake-key",
            strength_mapping=self.strength_mapping
        )
        
        # 创建图：0->1->2
        graph = [[] for _ in range(3)]
        graph[0].append(1)
        graph[1].append(2)
        
        # 测试可达性
        self.assertTrue(linker._is_reachable(graph, 0, 2, set()))  # 0可以到达2
        self.assertFalse(linker._is_reachable(graph, 2, 0, set()))  # 2不能到达0
        self.assertTrue(linker._is_reachable(graph, 1, 1, set()))   # 自己到自己
        
    @patch('causal_linking.service.linker_service.LLMClient.call_with_json_response')
    def test_llm_call_failure(self, mock_llm_call):
        """测试LLM调用失败的情况"""
        # 模拟LLM调用失败
        mock_response = {
            "success": False,
            "error": "API调用失败"
        }
        mock_llm_call.return_value = mock_response
        
        # 创建链接器实例
        linker = CausalLinker(
            model="gpt-4o",
            api_key="fake-key",
            strength_mapping=self.strength_mapping
        )
        
        # 分析因果关系
        edge = linker.analyze_causal_relation(self.test_events[0], self.test_events[1])
        
        # 验证返回None（因为调用失败）
        self.assertIsNone(edge)
        
    def test_provider_integration(self):
        """测试依赖注入提供器"""
        # 设置环境变量
        os.environ["OPENAI_API_KEY"] = "fake-key"
        os.environ["LLM_PROVIDER"] = "openai"
        
        # 获取链接器实例
        linker = provide_linker()
        
        # 验证实例类型
        self.assertIsInstance(linker, CausalLinker)
        
        # 清理环境变量
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        if "LLM_PROVIDER" in os.environ:
            del os.environ["LLM_PROVIDER"]


class TestCausalEdgeResponseParsing(unittest.TestCase):
    """测试因果边响应解析功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.linker = CausalLinker(
            model="gpt-4o",
            api_key="fake-key",
            strength_mapping={"高": 3, "中": 2, "低": 1}
        )
        
    def test_parse_valid_response_direction1(self):
        """测试解析有效响应（方向：event1->event2）"""
        response = {
            "has_causal_relation": True,
            "direction": "event1->event2",
            "strength": "高",
            "reason": "事件1导致事件2"
        }
        
        edge = self.linker.parse_response(response, "E1", "E2")
        
        self.assertIsNotNone(edge)
        self.assertEqual(edge.from_id, "E1")
        self.assertEqual(edge.to_id, "E2")
        self.assertEqual(edge.strength, "高")
        self.assertEqual(edge.reason, "事件1导致事件2")
        
    def test_parse_valid_response_direction2(self):
        """测试解析有效响应（方向：event2->event1）"""
        response = {
            "has_causal_relation": True,
            "direction": "event2->event1",
            "strength": "中",
            "reason": "事件2导致事件1"
        }
        
        edge = self.linker.parse_response(response, "E1", "E2")
        
        self.assertIsNotNone(edge)
        self.assertEqual(edge.from_id, "E2")
        self.assertEqual(edge.to_id, "E1")
        self.assertEqual(edge.strength, "中")
        
    def test_parse_no_causal_relation(self):
        """测试解析无因果关系的响应"""
        response = {
            "has_causal_relation": False,
            "direction": "",
            "strength": "",
            "reason": "无因果关系"
        }
        
        edge = self.linker.parse_response(response, "E1", "E2")
        
        self.assertIsNone(edge)
        
    def test_parse_invalid_direction(self):
        """测试解析无效方向的响应"""
        response = {
            "has_causal_relation": True,
            "direction": "invalid_direction",
            "strength": "高",
            "reason": "测试原因"
        }
        
        edge = self.linker.parse_response(response, "E1", "E2")
        
        self.assertIsNone(edge)


class TestCausalLinkingIntegration(unittest.TestCase):
    """测试因果链构建的集成功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建更复杂的测试场景
        self.complex_events = [
            EventItem(
                event_id="E1",
                description="韩立发现神秘小瓶",
                characters=["韩立"],
                treasures=["神秘小瓶"],
                location="七玄门",
                chapter_id="第三章",
                result="获得法宝"
            ),
            EventItem(
                event_id="E2",
                description="韩立使用小瓶催熟青元果",
                characters=["韩立"],
                treasures=["青元果"],
                location="七玄门药园",
                chapter_id="第四章",
                result="成功催熟灵药"
            ),
            EventItem(
                event_id="E3",
                description="韩立服用青元果突破瓶颈",
                characters=["韩立"],
                treasures=[],
                location="七玄门洞府",
                chapter_id="第五章",
                result="修为提升"
            ),
            EventItem(
                event_id="E4",
                description="墨大夫发现韩立修为异常",
                characters=["韩立", "墨大夫"],
                treasures=[],
                location="七玄门",
                chapter_id="第六章",
                result="引起怀疑"
            )
        ]
        
    @patch('causal_linking.service.linker_service.LLMClient.call_with_json_response')
    def test_complete_pipeline(self, mock_llm_call):
        """测试完整的因果链构建流程"""
        # 模拟复杂的因果关系网络
        def mock_complex_responses(system_prompt, user_prompt):
            if "E1" in user_prompt and "E2" in user_prompt:
                return {
                    "success": True,
                    "json_content": {
                        "has_causal_relation": True,
                        "direction": "event1->event2",
                        "strength": "高",
                        "reason": "获得小瓶使得催熟灵药成为可能"
                    }
                }
            elif "E2" in user_prompt and "E3" in user_prompt:
                return {
                    "success": True,
                    "json_content": {
                        "has_causal_relation": True,
                        "direction": "event1->event2",
                        "strength": "高",
                        "reason": "服用催熟的青元果导致修为突破"
                    }
                }
            elif "E3" in user_prompt and "E4" in user_prompt:
                return {
                    "success": True,
                    "json_content": {
                        "has_causal_relation": True,
                        "direction": "event1->event2",
                        "strength": "中",
                        "reason": "修为异常提升引起墨大夫注意"
                    }
                }
            else:
                return {
                    "success": True,
                    "json_content": {
                        "has_causal_relation": False,
                        "direction": "",
                        "strength": "",
                        "reason": "无直接因果关系"
                    }
                }
        
        mock_llm_call.side_effect = mock_complex_responses
        
        # 创建链接器实例
        linker = CausalLinker(
            model="gpt-4o",
            api_key="fake-key",
            max_workers=2,
            strength_mapping={"高": 3, "中": 2, "低": 1}
        )
        
        # 执行完整流程：链接事件 -> 构建DAG
        edges = linker.link_events(self.complex_events)
        final_events, dag_edges = linker.build_dag(self.complex_events, edges)
        
        # 验证结果
        self.assertEqual(len(final_events), 4)
        self.assertGreater(len(dag_edges), 0)
        
        # 验证主要因果链：E1->E2->E3->E4
        e1_to_e2 = next((e for e in dag_edges if e.from_id == "E1" and e.to_id == "E2"), None)
        e2_to_e3 = next((e for e in dag_edges if e.from_id == "E2" and e.to_id == "E3"), None)
        e3_to_e4 = next((e for e in dag_edges if e.from_id == "E3" and e.to_id == "E4"), None)
        
        self.assertIsNotNone(e1_to_e2)
        self.assertIsNotNone(e2_to_e3)
        self.assertIsNotNone(e3_to_e4)
        
        # 验证强度
        self.assertEqual(e1_to_e2.strength, "高")
        self.assertEqual(e2_to_e3.strength, "高")
        self.assertEqual(e3_to_e4.strength, "中")


if __name__ == "__main__":
    unittest.main()
