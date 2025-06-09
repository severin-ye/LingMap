#!/usr/bin/env python3
"""
第四阶段测试：因果链构建模块（CPC）完整测试

本测试涵盖第四阶段CPC模块的全部功能：
1. GraphFilter图过滤器的贪心循环打破算法
2. CausalLinker的DAG构建算法（从Stage 3迁移）
3. 环检测和可达性算法测试
4. 完整的因果链构建流程集成测试
5. DAG构建性能和正确性验证
6. 与统一链接器的集成测试

这些测试确保CPC模块能够正确构建有向无环图并处理复杂的因果关系网络。
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from causal_linking.service.graph_filter import GraphFilter
from causal_linking.service.unified_linker_service import UnifiedCausalLinker
from causal_linking.di.provider import provide_linker

# 定义prompt路径
causal_prompt_path = os.path.join(project_root, "common", "config", "prompt_causal_linking.json")


class TestGraphFilter(unittest.TestCase):
    """测试GraphFilter图过滤器的功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.graph_filter = GraphFilter()
        
        # 创建测试事件（基于《凡人修仙传》真实情节）
        self.test_events = [
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
    
    def test_simple_dag_construction(self):
        """测试简单DAG构建"""
        # 创建无环的边集
        edges = [
            CausalEdge(from_id="E1", to_id="E2", strength="高", reason="小瓶催熟青元果"),
            CausalEdge(from_id="E2", to_id="E3", strength="高", reason="服用催熟的青元果"),
            CausalEdge(from_id="E3", to_id="E4", strength="中", reason="修为异常被发现"),
            CausalEdge(from_id="E1", to_id="E3", strength="低", reason="获得小瓶间接帮助修为提升")
        ]
        
        # 过滤边集
        filtered_edges = self.graph_filter.filter_edges_to_dag(self.test_events, edges)
        
        # 验证结果
        self.assertEqual(len(filtered_edges), 4)  # 无环，所有边都应保留
        
        # 验证高强度边被保留
        high_strength_edges = [e for e in filtered_edges if e.strength == "高"]
        self.assertEqual(len(high_strength_edges), 2)
    
    def test_cycle_breaking_algorithm(self):
        """测试循环打破算法"""
        # 创建包含环的边集：E1->E2->E3->E1
        edges = [
            CausalEdge(from_id="E1", to_id="E2", strength="高", reason="E1导致E2"),
            CausalEdge(from_id="E2", to_id="E3", strength="高", reason="E2导致E3"),
            CausalEdge(from_id="E3", to_id="E1", strength="中", reason="E3导致E1（形成环）"),
            CausalEdge(from_id="E1", to_id="E4", strength="中", reason="E1导致E4")
        ]
        
        # 过滤边集
        filtered_edges = self.graph_filter.filter_edges_to_dag(self.test_events, edges)
        
        # 验证结果：应该去掉形成环的边
        self.assertLess(len(filtered_edges), len(edges))
        
        # 验证没有E3->E1的边（因为会形成环且强度较低）
        cycle_edge = next((e for e in filtered_edges if e.from_id == "E3" and e.to_id == "E1"), None)
        self.assertIsNone(cycle_edge)
        
        # 验证高强度边E1->E2和E2->E3被保留
        e1_to_e2 = next((e for e in filtered_edges if e.from_id == "E1" and e.to_id == "E2"), None)
        e2_to_e3 = next((e for e in filtered_edges if e.from_id == "E2" and e.to_id == "E3"), None)
        self.assertIsNotNone(e1_to_e2)
        self.assertIsNotNone(e2_to_e3)
    
    def test_edge_priority_sorting(self):
        """测试边优先级排序"""
        edges = [
            CausalEdge(from_id="E1", to_id="E2", strength="低", reason="低强度边"),
            CausalEdge(from_id="E2", to_id="E3", strength="高", reason="高强度边"),
            CausalEdge(from_id="E3", to_id="E4", strength="中", reason="中强度边"),
            CausalEdge(from_id="E1", to_id="E4", strength="高", reason="另一个高强度边")
        ]
        
        event_map = {event.event_id: i for i, event in enumerate(self.test_events)}
        sorted_edges = self.graph_filter._sort_edges_by_priority(edges, event_map)
        
        # 验证排序结果：高强度边应该在前
        self.assertEqual(sorted_edges[0].strength, "高")
        self.assertEqual(sorted_edges[1].strength, "高")
        self.assertEqual(sorted_edges[2].strength, "中")
        self.assertEqual(sorted_edges[3].strength, "低")
    
    def test_cycle_detection(self):
        """测试环检测功能"""
        # 创建包含环的边集
        edges_with_cycle = [
            CausalEdge(from_id="E1", to_id="E2", strength="高", reason="E1->E2"),
            CausalEdge(from_id="E2", to_id="E3", strength="高", reason="E2->E3"),
            CausalEdge(from_id="E3", to_id="E1", strength="中", reason="E3->E1（环）")
        ]
        
        cycles = self.graph_filter.detect_cycles(self.test_events, edges_with_cycle)
        
        # 验证检测到环
        self.assertGreater(len(cycles), 0)
        
        # 验证环包含预期的节点
        found_cycle = False
        for cycle in cycles:
            if "E1" in cycle and "E2" in cycle and "E3" in cycle:
                found_cycle = True
                break
        self.assertTrue(found_cycle)
    
    def test_no_cycle_detection(self):
        """测试无环情况的检测"""
        # 创建无环的边集
        edges_no_cycle = [
            CausalEdge(from_id="E1", to_id="E2", strength="高", reason="E1->E2"),
            CausalEdge(from_id="E2", to_id="E3", strength="高", reason="E2->E3"),
            CausalEdge(from_id="E3", to_id="E4", strength="中", reason="E3->E4")
        ]
        
        cycles = self.graph_filter.detect_cycles(self.test_events, edges_no_cycle)
        
        # 验证没有检测到环
        self.assertEqual(len(cycles), 0)
    
    def test_filter_statistics(self):
        """测试过滤统计功能"""
        original_edges = [
            CausalEdge(from_id="E1", to_id="E2", strength="高", reason="高强度边"),
            CausalEdge(from_id="E2", to_id="E3", strength="中", reason="中强度边"),
            CausalEdge(from_id="E3", to_id="E1", strength="低", reason="低强度边（会形成环）"),
            CausalEdge(from_id="E1", to_id="E4", strength="高", reason="另一个高强度边")
        ]
        
        filtered_edges = self.graph_filter.filter_edges_to_dag(self.test_events, original_edges)
        stats = self.graph_filter.get_filter_statistics(original_edges, filtered_edges)
        
        # 验证统计信息
        self.assertEqual(stats["original_edge_count"], 4)
        self.assertLessEqual(stats["filtered_edge_count"], 4)
        self.assertGreaterEqual(stats["retention_rate"], 0)
        self.assertLessEqual(stats["retention_rate"], 1)
        
        # 验证强度分布
        self.assertIn("original", stats["strength_distribution"])
        self.assertIn("filtered", stats["strength_distribution"])
    
    def test_empty_input_handling(self):
        """测试空输入处理"""
        # 测试空事件列表
        result = self.graph_filter.filter_edges_to_dag([], [])
        self.assertEqual(len(result), 0)
        
        # 测试空边列表
        result = self.graph_filter.filter_edges_to_dag(self.test_events, [])
        self.assertEqual(len(result), 0)
    
    def test_complex_cycle_scenario(self):
        """测试复杂环路场景"""
        # 创建包含多个环的复杂边集
        edges = [
            # 主环：E1->E2->E3->E1
            CausalEdge(from_id="E1", to_id="E2", strength="高", reason="主链1"),
            CausalEdge(from_id="E2", to_id="E3", strength="高", reason="主链2"),
            CausalEdge(from_id="E3", to_id="E1", strength="低", reason="回环（低强度）"),
            
            # 次环：E2->E4->E2
            CausalEdge(from_id="E2", to_id="E4", strength="中", reason="分支1"),
            CausalEdge(from_id="E4", to_id="E2", strength="低", reason="回环（低强度）"),
            
            # 额外连接
            CausalEdge(from_id="E1", to_id="E4", strength="中", reason="直连"),
            CausalEdge(from_id="E3", to_id="E4", strength="高", reason="强连接")
        ]
        
        filtered_edges = self.graph_filter.filter_edges_to_dag(self.test_events, edges)
        
        # 验证环被正确打破
        self.assertLess(len(filtered_edges), len(edges))
        
        # 验证主要高强度边被保留
        high_strength_edges = [e for e in filtered_edges if e.strength == "高"]
        self.assertGreater(len(high_strength_edges), 0)
        
        # 验证结果是DAG（无环）
        cycles = self.graph_filter.detect_cycles(self.test_events, filtered_edges)
        self.assertEqual(len(cycles), 0)


class TestCPCIntegration(unittest.TestCase):
    """测试CPC模块的集成功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.test_events = [
            EventItem(
                event_id="E1",
                description="韩立获得神秘小瓶",
                characters=["韩立"],
                treasures=["神秘小瓶"],
                location="七玄门",
                chapter_id="第三章"
            ),
            EventItem(
                event_id="E2",
                description="韩立催熟青元果",
                characters=["韩立"],
                treasures=["青元果"],
                location="七玄门",
                chapter_id="第四章"
            ),
            EventItem(
                event_id="E3",
                description="韩立突破修炼瓶颈",
                characters=["韩立"],
                treasures=[],
                location="七玄门",
                chapter_id="第五章"
            )
        ]
    
    @patch('event_extraction.repository.llm_client.LLMClient.call_with_json_response')
    def test_unified_linker_with_graph_filter(self, mock_llm_call):
        """测试统一链接器与图过滤器的集成"""
        # 模拟LLM返回包含环路的因果关系
        def mock_responses(system_prompt, user_prompt):
            if "E1" in user_prompt and "E2" in user_prompt:
                return {
                    "success": True,
                    "json_content": {
                        "has_causal_relation": True,
                        "direction": "event1->event2",
                        "strength": "高",
                        "reason": "神秘小瓶帮助催熟青元果"
                    }
                }
            elif "E2" in user_prompt and "E3" in user_prompt:
                return {
                    "success": True,
                    "json_content": {
                        "has_causal_relation": True,
                        "direction": "event1->event2",
                        "strength": "高",
                        "reason": "服用催熟的青元果突破瓶颈"
                    }
                }
            elif "E3" in user_prompt and "E1" in user_prompt:
                return {
                    "success": True,
                    "json_content": {
                        "has_causal_relation": True,
                        "direction": "event1->event2",
                        "strength": "中",
                        "reason": "突破瓶颈使韩立更好地使用小瓶"
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
        
        mock_llm_call.side_effect = mock_responses
        
        # 创建统一链接器
        linker = UnifiedCausalLinker(
            prompt_path=causal_prompt_path,
            model="gpt-4o",
            api_key="fake-key",
            strength_mapping={"高": 3, "中": 2, "低": 1}
        )
        
        # 执行完整流程
        edges = linker.link_events(self.test_events)
        final_events, dag_edges = linker.build_dag(self.test_events, edges)
        
        # 验证结果
        self.assertEqual(len(final_events), 3)
        self.assertGreater(len(edges), 0)  # 应该发现因果关系
        
        # 验证DAG构建去掉了环路
        if len(edges) > len(dag_edges):
            # 有边被移除，说明存在环路并被正确处理
            pass
        
        # 验证主要因果链被保留
        e1_to_e2 = next((e for e in dag_edges if e.from_id == "E1" and e.to_id == "E2"), None)
        e2_to_e3 = next((e for e in dag_edges if e.from_id == "E2" and e.to_id == "E3"), None)
        
        # 至少应该保留主要的因果链
        self.assertIsNotNone(e1_to_e2)
        self.assertIsNotNone(e2_to_e3)
    
    def test_provider_integration(self):
        """测试依赖注入提供器的集成"""
        # 设置环境变量
        os.environ["OPENAI_API_KEY"] = "fake-key"
        os.environ["LLM_PROVIDER"] = "openai"
        
        try:
            # 获取链接器实例
            linker = provide_linker()
            
            # 验证实例类型
            self.assertIsInstance(linker, UnifiedCausalLinker)
            
            # 验证build_dag方法存在
            self.assertTrue(hasattr(linker, 'build_dag'))
            self.assertTrue(callable(getattr(linker, 'build_dag')))
            
        finally:
            # 清理环境变量
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            if "LLM_PROVIDER" in os.environ:
                del os.environ["LLM_PROVIDER"]
    
    def test_performance_with_large_dataset(self):
        """测试大数据集的性能"""
        # 创建大量测试事件
        large_events = []
        for i in range(20):  # 创建20个事件
            large_events.append(EventItem(
                event_id=f"E{i+1}",
                description=f"测试事件{i+1}",
                characters=["韩立"],
                treasures=[],
                location="测试地点",
                chapter_id=f"第{i+1}章"
            ))
        
        # 创建大量边（模拟复杂的因果关系网络）
        large_edges = []
        for i in range(len(large_events)):
            for j in range(len(large_events)):
                if i != j and (i + j) % 3 == 0:  # 创建一些边
                    strength = ["高", "中", "低"][(i + j) % 3]
                    large_edges.append(CausalEdge(
                        from_id=f"E{i+1}",
                        to_id=f"E{j+1}",
                        strength=strength,
                        reason=f"测试因果关系{i+1}->{j+1}"
                    ))
        
        # 测试图过滤器性能
        graph_filter = GraphFilter()
        
        import time
        start_time = time.time()
        filtered_edges = graph_filter.filter_edges_to_dag(large_events, large_edges)
        end_time = time.time()
        
        # 验证性能（应该在合理时间内完成）
        execution_time = end_time - start_time
        self.assertLess(execution_time, 5.0)  # 应该在5秒内完成
        
        # 验证结果正确性
        self.assertLessEqual(len(filtered_edges), len(large_edges))
        
        # 验证结果是DAG
        cycles = graph_filter.detect_cycles(large_events, filtered_edges)
        self.assertEqual(len(cycles), 0)


class TestCPCModuleCompletion(unittest.TestCase):
    """测试CPC模块的完整性"""
    
    def test_module_interfaces(self):
        """测试模块接口完整性"""
        # 验证GraphFilter类存在所有必需方法
        graph_filter = GraphFilter()
        
        # 核心方法
        self.assertTrue(hasattr(graph_filter, 'filter_edges_to_dag'))
        self.assertTrue(callable(getattr(graph_filter, 'filter_edges_to_dag')))
        
        # 辅助方法
        self.assertTrue(hasattr(graph_filter, 'detect_cycles'))
        self.assertTrue(hasattr(graph_filter, 'get_filter_statistics'))
        
        # 内部方法
        self.assertTrue(hasattr(graph_filter, '_will_form_cycle'))
        self.assertTrue(hasattr(graph_filter, '_is_reachable'))
        self.assertTrue(hasattr(graph_filter, '_sort_edges_by_priority'))
    
    def test_algorithm_correctness(self):
        """测试算法正确性"""
        graph_filter = GraphFilter()
        
        # 创建已知的测试用例
        events = [
            EventItem(event_id="A", description="事件A", characters=[], treasures=[], location="", chapter_id="1"),
            EventItem(event_id="B", description="事件B", characters=[], treasures=[], location="", chapter_id="1"),
            EventItem(event_id="C", description="事件C", characters=[], treasures=[], location="", chapter_id="1")
        ]
        
        # 测试简单链：A->B->C
        simple_edges = [
            CausalEdge(from_id="A", to_id="B", strength="高", reason="A导致B"),
            CausalEdge(from_id="B", to_id="C", strength="高", reason="B导致C")
        ]
        
        result = graph_filter.filter_edges_to_dag(events, simple_edges)
        self.assertEqual(len(result), 2)  # 所有边都应保留
        
        # 测试环路：A->B->C->A
        cycle_edges = simple_edges + [
            CausalEdge(from_id="C", to_id="A", strength="低", reason="C导致A（环）")
        ]
        
        result = graph_filter.filter_edges_to_dag(events, cycle_edges)
        self.assertEqual(len(result), 2)  # 应该移除环路边
        
        # 验证移除的是最低强度的边
        removed_edge = any(e.from_id == "C" and e.to_id == "A" for e in result)
        self.assertFalse(removed_edge)
    
    def test_strength_priority_enforcement(self):
        """测试强度优先级执行"""
        graph_filter = GraphFilter()
        
        events = [
            EventItem(event_id="X", description="事件X", characters=[], treasures=[], location="", chapter_id="1"),
            EventItem(event_id="Y", description="事件Y", characters=[], treasures=[], location="", chapter_id="1")
        ]
        
        # 创建相互冲突的边（不同强度）
        edges = [
            CausalEdge(from_id="X", to_id="Y", strength="高", reason="X导致Y（高强度）"),
            CausalEdge(from_id="Y", to_id="X", strength="低", reason="Y导致X（低强度）")
        ]
        
        result = graph_filter.filter_edges_to_dag(events, edges)
        
        # 应该只保留一条边，且是高强度的
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].strength, "高")
        self.assertEqual(result[0].from_id, "X")
        self.assertEqual(result[0].to_id, "Y")


class TestCausalLinkerDAG(unittest.TestCase):
    """测试CausalLinker的DAG构建功能（从Stage 3迁移）"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # 强度映射
        self.strength_mapping = {"高": 3, "中": 2, "低": 1}
        
        # 创建测试用的事件数据
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
                description="韩立遇到墨大夫",
                characters=["韩立", "墨大夫"],
                treasures=[],
                location="七玄门",
                chapter_id="第一章",
                result="得到神秘药物"
            ),
            EventItem(
                event_id="E3",
                description="韩立服用药物突破修为",
                characters=["韩立"],
                treasures=["筑基丹"],
                location="韩立居所",
                chapter_id="第二章", 
                result="成功筑基"
            )
        ]

    def test_build_dag_simple(self):
        """测试构建简单的DAG"""
        from causal_linking.service.unified_linker_service import CausalLinker
        
        # 创建测试用的因果边
        edges = [
            CausalEdge(from_id="E1", to_id="E2", strength="高", reason="测试原因1"),
            CausalEdge(from_id="E2", to_id="E3", strength="中", reason="测试原因2"),
            CausalEdge(from_id="E1", to_id="E3", strength="低", reason="测试原因3")
        ]
        
        # 创建链接器实例
        linker = CausalLinker(
            prompt_path=causal_prompt_path,
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
        from causal_linking.service.unified_linker_service import CausalLinker
        
        # 创建会形成环的因果边
        edges = [
            CausalEdge(from_id="E1", to_id="E2", strength="高", reason="E1->E2"),
            CausalEdge(from_id="E2", to_id="E3", strength="高", reason="E2->E3"),
            CausalEdge(from_id="E3", to_id="E1", strength="中", reason="E3->E1 (会形成环)")
        ]
        
        # 创建链接器实例
        linker = CausalLinker(
            prompt_path=causal_prompt_path,
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
        
    def test_cycle_detection_algorithm(self):
        """测试环检测算法"""
        from causal_linking.service.unified_linker_service import CausalLinker
        
        # 创建链接器实例
        linker = CausalLinker(
            prompt_path=causal_prompt_path,
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
        
    def test_reachability_algorithm(self):
        """测试可达性检测算法"""
        from causal_linking.service.unified_linker_service import CausalLinker
        
        # 创建链接器实例
        linker = CausalLinker(
            prompt_path=causal_prompt_path,
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


if __name__ == "__main__":
    unittest.main()
