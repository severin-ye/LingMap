#!/usr/bin/env python3
"""
阶段一测试：抽象接口定义测试

本文件包含针对《凡人修仙传》因果事件图谱系统基础接口的单元测试。
测试采用模拟类（Mock）实现各个接口，验证接口定义的正确性和功能的完整性。

测试内容：
1. AbstractExtractor 抽象提取器接口：
   - test_extractor_interface: 测试事件提取接口的功能实现
   - 验证接口能够从章节内容中提取事件信息
   - 确认返回的事件数据结构符合 EventItem 模型

2. AbstractRefiner 抽象优化器接口：
   - test_refiner_interface: 测试事件优化接口的功能实现
   - 验证接口能够优化和过滤事件列表
   - 确认返回的优化后事件仍符合 EventItem 模型要求

3. AbstractLinker 抽象链接器接口：
   - test_linker_interface: 测试事件链接功能实现
   - 验证接口能够在事件之间建立因果关系
   - 确认返回的边数据结构符合 CausalEdge 模型
   
   - test_build_dag_interface: 测试构建有向无环图(DAG)功能
   - 验证接口能够处理事件和边，构建有效的图结构
   - 确认返回的数据结构符合预期格式

4. AbstractGraphRenderer 抽象图渲染器接口：
   - test_graph_renderer_interface: 测试图形渲染接口的功能实现
   - 验证接口能够将事件和边渲染为有效的图表表示（如Mermaid格式）
   - 确认返回的字符串格式符合渲染要求
"""

import unittest
import os
import sys
from typing import List, Dict, Any, Tuple
from unittest.mock import MagicMock

# 将项目根目录添加到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from common.interfaces.extractor import AbstractExtractor
from common.interfaces.refiner import AbstractRefiner
from common.interfaces.linker import AbstractLinker
from common.interfaces.graph_renderer import AbstractGraphRenderer

from common.models.event import EventItem
from common.models.chapter import Chapter
from common.models.causal_edge import CausalEdge


class MockExtractor(AbstractExtractor):
    """AbstractExtractor接口的模拟实现"""
    
    def __init__(self):
        """初始化"""
        self.mock_extract = MagicMock()
        
    def extract(self, chapter: Chapter) -> List[EventItem]:
        """模拟提取事件"""
        self.mock_extract(chapter)
        # 返回一些测试事件
        return [
            EventItem(
                event_id="event-001",
                chapter_id=chapter.chapter_id,
                description="韩立在莫家村练习铁皮指功",
                characters=["韩立"],
                location="莫家村",
                time="幼年"
            )
        ]


class MockRefiner(AbstractRefiner):
    """AbstractRefiner接口的模拟实现"""
    
    def __init__(self):
        """初始化"""
        self.mock_refine = MagicMock()
        
    def refine(self, events: List[EventItem], chapter: Chapter) -> List[EventItem]:
        """模拟优化事件"""
        self.mock_refine(events, chapter)
        # 简单返回输入的事件
        return events


class MockLinker(AbstractLinker):
    """AbstractLinker接口的模拟实现"""
    
    def __init__(self):
        """初始化"""
        self.mock_link_events = MagicMock()
        self.mock_build_dag = MagicMock()
        
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        """模拟链接事件"""
        self.mock_link_events(events)
        # 返回一个测试边
        if len(events) >= 2:
            return [
                CausalEdge(
                    from_id=events[0].event_id,
                    to_id=events[1].event_id,
                    strength="高",
                    reason="事件关系描述"
                )
            ]
        return []
        
    def build_dag(self, events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """模拟构建DAG"""
        self.mock_build_dag(events, edges)
        # 简单返回输入
        return events, edges


class MockGraphRenderer(AbstractGraphRenderer):
    """AbstractGraphRenderer接口的模拟实现"""
    
    def __init__(self):
        """初始化"""
        self.mock_render = MagicMock()
        
    def render(self, events: List[EventItem], edges: List[CausalEdge]) -> str:
        """模拟渲染图谱"""
        self.mock_render(events, edges)
        # 返回简单的Mermaid字符串
        return "graph TD;\n  event-001-->event-002;"


class TestExtractorInterface(unittest.TestCase):
    """测试AbstractExtractor接口"""
    
    def test_extractor_interface(self):
        """测试提取器接口"""
        extractor = MockExtractor()
        chapter = Chapter(chapter_id="第一章", title="莫家村韩立", content="韩立出生在莫家村...")
        
        events = extractor.extract(chapter)
        
        # 验证模拟方法被调用
        extractor.mock_extract.assert_called_once_with(chapter)
        # 验证返回类型
        self.assertIsInstance(events, list)
        self.assertTrue(all(isinstance(event, EventItem) for event in events))


class TestRefinerInterface(unittest.TestCase):
    """测试AbstractRefiner接口"""
    
    def test_refiner_interface(self):
        """测试优化器接口"""
        refiner = MockRefiner()
        events = [
            EventItem(
                event_id="event-001",
                chapter_id="第一章",
                description="韩立在莫家村练习铁皮指功",
                characters=["韩立"]
            )
        ]
        chapter = Chapter(chapter_id="第一章", title="莫家村韩立", content="韩立出生在莫家村...")
        
        refined_events = refiner.refine(events, chapter)
        
        # 验证模拟方法被调用
        refiner.mock_refine.assert_called_once()
        # 验证返回类型
        self.assertIsInstance(refined_events, list)
        self.assertTrue(all(isinstance(event, EventItem) for event in refined_events))


class TestLinkerInterface(unittest.TestCase):
    """测试AbstractLinker接口"""
    
    def test_linker_interface(self):
        """测试链接器接口"""
        linker = MockLinker()
        events = [
            EventItem(event_id="event-001", description="事件1", chapter_id="第一章"),
            EventItem(event_id="event-002", description="事件2", chapter_id="第一章")
        ]
        
        edges = linker.link_events(events)
        
        # 验证模拟方法被调用
        linker.mock_link_events.assert_called_once_with(events)
        # 验证返回类型
        self.assertIsInstance(edges, list)
        self.assertTrue(all(isinstance(edge, CausalEdge) for edge in edges))
        
        # 验证边的属性
        if edges:
            self.assertEqual(edges[0].from_id, "event-001")
            self.assertEqual(edges[0].to_id, "event-002")
    
    def test_build_dag_interface(self):
        """测试构建DAG接口"""
        linker = MockLinker()
        events = [
            EventItem(event_id="event-001", description="事件1", chapter_id="第一章"),
            EventItem(event_id="event-002", description="事件2", chapter_id="第一章")
        ]
        edges = [
            CausalEdge(
                from_id="event-001",
                to_id="event-002",
                strength="高",
                reason="描述"
            )
        ]
        
        result_events, result_edges = linker.build_dag(events, edges)
        
        # 验证模拟方法被调用
        linker.mock_build_dag.assert_called_once_with(events, edges)
        # 验证返回类型
        self.assertIsInstance(result_events, list)
        self.assertIsInstance(result_edges, list)
        self.assertTrue(all(isinstance(event, EventItem) for event in result_events))
        self.assertTrue(all(isinstance(edge, CausalEdge) for edge in result_edges))


class TestGraphRendererInterface(unittest.TestCase):
    """测试AbstractGraphRenderer接口"""
    
    def test_graph_renderer_interface(self):
        """测试图形渲染器接口"""
        renderer = MockGraphRenderer()
        events = [
            EventItem(event_id="event-001", description="事件1", chapter_id="第一章"),
            EventItem(event_id="event-002", description="事件2", chapter_id="第一章")
        ]
        edges = [
            CausalEdge(
                from_id="event-001",
                to_id="event-002",
                strength="高",
                reason="描述"
            )
        ]
        
        mermaid_str = renderer.render(events, edges)
        
        # 验证模拟方法被调用
        renderer.mock_render.assert_called_once_with(events, edges)
        # 验证返回类型
        self.assertIsInstance(mermaid_str, str)
        # 简单验证返回的Mermaid字符串格式
        self.assertTrue("graph TD" in mermaid_str)
        self.assertTrue("event-001-->event-002" in mermaid_str)


if __name__ == '__main__':
    unittest.main()
