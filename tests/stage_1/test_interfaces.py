#!/usr/bin/env python3
"""
# [CN] 阶段一测试：抽象接口定义测试
# [EN] Stage 1 Test: Abstract Interface Definition Testing

# [CN] 本文件包含针对《凡人修仙传》因果事件图谱系统基础接口的单元测试。
# [CN] 测试采用模拟类（Mock）实现各个接口，验证接口定义的正确性和功能的完整性。
# [EN] This file contains unit tests for the basic interfaces of the "A Record of Mortal's Journey to Immortality" causal event graph system.
# [EN] Tests use mock class implementations for each interface to verify the correctness of interface definitions and completeness of functionality.

# [CN] 测试内容：
# [EN] Test Content:
# [CN] 1. AbstractExtractor 抽象提取器接口：
# [EN] 1. AbstractExtractor abstract extractor interface:
#    # [CN] - test_extractor_interface: 测试事件提取接口的功能实现
#    # [EN] - test_extractor_interface: Test the functional implementation of event extraction interface
#    # [CN] - 验证接口能够从章节内容中提取事件信息
#    # [EN] - Verify that the interface can extract event information from chapter content
#    # [CN] - 确认返回的事件数据结构符合 EventItem 模型
#    # [EN] - Confirm that returned event data structure conforms to EventItem model

# [CN] 2. AbstractRefiner 抽象优化器接口：
# [EN] 2. AbstractRefiner abstract refiner interface:
#    # [CN] - test_refiner_interface: 测试事件优化接口的功能实现
#    # [EN] - test_refiner_interface: Test the functional implementation of event refinement interface
#    # [CN] - 验证接口能够优化和过滤事件列表
#    # [EN] - Verify that the interface can optimize and filter event lists
#    # [CN] - 确认返回的优化后事件仍符合 EventItem 模型要求
#    # [EN] - Confirm that returned optimized events still conform to EventItem model requirements

# [CN] 3. AbstractLinker 抽象链接器接口：
# [EN] 3. AbstractLinker abstract linker interface:
#    # [CN] - test_linker_interface: 测试事件链接功能实现
#    # [EN] - test_linker_interface: Test event linking functionality implementation
#    # [CN] - 验证接口能够在事件之间建立因果关系
#    # [EN] - Verify that the interface can establish causal relationships between events
#    # [CN] - 确认返回的边数据结构符合 CausalEdge 模型
#    # [EN] - Confirm that returned edge data structure conforms to CausalEdge model
   
#    # [CN] - test_build_dag_interface: 测试构建有向无环图(DAG)功能
#    # [EN] - test_build_dag_interface: Test directed acyclic graph (DAG) construction functionality
#    # [CN] - 验证接口能够处理事件和边，构建有效的图结构
#    # [EN] - Verify that the interface can process events and edges to build valid graph structures
#    # [CN] - 确认返回的数据结构符合预期格式
#    # [EN] - Confirm that returned data structures conform to expected formats

# [CN] 4. AbstractGraphRenderer 抽象图渲染器接口：
# [EN] 4. AbstractGraphRenderer abstract graph renderer interface:
#    # [CN] - test_graph_renderer_interface: 测试图形渲染接口的功能实现
#    # [EN] - test_graph_renderer_interface: Test the functional implementation of graph rendering interface
#    # [CN] - 验证接口能够将事件和边渲染为有效的图表表示（如Mermaid格式）
#    # [EN] - Verify that the interface can render events and edges into valid chart representations (such as Mermaid format)
#    # [CN] - 确认返回的字符串格式符合渲染要求
#    # [EN] - Confirm that returned string format meets rendering requirements
"""

import unittest
import os
import sys
from typing import List, Dict, Any, Tuple
from unittest.mock import MagicMock

# [CN] 将项目根目录添加到路径
# [EN] Add project root directory to path
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
    """
    # [CN] AbstractExtractor接口的模拟实现
    # [EN] Mock implementation of AbstractExtractor interface
    """
    
    def __init__(self):
        """
        # [CN] 初始化
        # [EN] Initialize
        """
        self.mock_extract = MagicMock()
        # [CN] 加载小说数据
        # [EN] Load novel data
        novel_path = os.path.join(project_root, "novel", "test.txt")
        with open(novel_path, 'r', encoding='utf-8') as f:
            novel_text = f.read()
        self.novel_text = novel_text
        
    def extract(self, chapter: Chapter) -> List[EventItem]:
        """
        # [CN] 模拟提取事件：使用小说真实内容
        # [EN] Mock event extraction: using real novel content
        """
        self.mock_extract(chapter)
        # [CN] 返回基于小说内容的测试事件
        # [EN] Return test events based on novel content
        return [
            EventItem(
                event_id="event-001",
                chapter_id=chapter.chapter_id,
                description="韩立和同伴一起进山拣干柴和采集浆果",
                characters=["韩立"],
                location="莫家村附近的山上",
                time="幼年"
            ),
            EventItem(
                event_id="event-002",
                chapter_id=chapter.chapter_id,
                description="韩立回家时发现三叔来访，这会改变他一生的命运",
                characters=["韩立", "三叔", "韩父", "韩母"],
                location="莫家村",
                time="幼年"
            )
        ]


class MockRefiner(AbstractRefiner):
    """
    # [CN] AbstractRefiner接口的模拟实现
    # [EN] Mock implementation of AbstractRefiner interface
    """
    
    def __init__(self):
        """
        # [CN] 初始化
        # [EN] Initialize
        """
        self.mock_refine = MagicMock()
        
    def refine(self, events: List[EventItem], chapter: Chapter) -> List[EventItem]:
        """
        # [CN] 模拟优化事件
        # [EN] Mock event optimization
        """
        self.mock_refine(events, chapter)
        # [CN] 简单返回输入的事件
        # [EN] Simply return input events
        return events


class MockLinker(AbstractLinker):
    """
    # [CN] AbstractLinker接口的模拟实现
    # [EN] Mock implementation of AbstractLinker interface
    """
    
    def __init__(self):
        """
        # [CN] 初始化
        # [EN] Initialize
        """
        self.mock_link_events = MagicMock()
        self.mock_build_dag = MagicMock()
        
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        """
        # [CN] 模拟链接事件：使用小说中的真实因果关系
        # [EN] Mock event linking: using real causal relationships from the novel
        """
        self.mock_link_events(events)
        # [CN] 返回基于小说内容的因果关系
        # [EN] Return causal relationships based on novel content
        if len(events) >= 2:
            return [
                CausalEdge(
                    from_id=events[0].event_id,
                    to_id=events[1].event_id,
                    strength="高",
                    reason="韩立上山采集浆果，归来后遇到三叔，导致他的命运发生转折"
                )
            ]
        return []
        
    def build_dag(self, events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        # [CN] 模拟构建DAG
        # [EN] Mock DAG construction
        """
        self.mock_build_dag(events, edges)
        # [CN] 简单返回输入
        # [EN] Simply return input
        return events, edges


class MockGraphRenderer(AbstractGraphRenderer):
    """
    # [CN] AbstractGraphRenderer接口的模拟实现
    # [EN] Mock implementation of AbstractGraphRenderer interface
    """
    
    def __init__(self):
        """
        # [CN] 初始化
        # [EN] Initialize
        """
        self.mock_render = MagicMock()
        
    def render(self, events: List[EventItem], edges: List[CausalEdge]) -> str:
        """
        # [CN] 模拟渲染图谱
        # [EN] Mock graph rendering
        """
        self.mock_render(events, edges)
        # 返回简单的Mermaid字符串
        return "graph TD;\n  event-001-->event-002;"


class TestExtractorInterface(unittest.TestCase):
    """测试AbstractExtractor接口"""
    
    def setUp(self):
        """测试前准备，加载真实小说数据"""
        novel_path = os.path.join(project_root, "novel", "test.txt")
        with open(novel_path, 'r', encoding='utf-8') as f:
            novel_text = f.read()
            
        # 提取第一章内容
        chapter_start = novel_text.find("第一章")
        chapter_end = novel_text.find("第二章")
        if chapter_end == -1:  # 如果找不到第二章，则使用全文
            self.chapter_text = novel_text[chapter_start:]
        else:
            self.chapter_text = novel_text[chapter_start:chapter_end]
        
        # 提取章节标题
        title_start = self.chapter_text.find("第一章")
        title_end = self.chapter_text.find("\n", title_start)
        self.chapter_title = self.chapter_text[title_start:title_end].strip()
    
    def test_extractor_interface(self):
        """测试提取器接口：使用小说真实内容"""
        extractor = MockExtractor()
        chapter = Chapter(
            chapter_id="第一章",
            title=self.chapter_title,
            content=self.chapter_text
        )
        
        events = extractor.extract(chapter)
        
        # 验证模拟方法被调用
        extractor.mock_extract.assert_called_once_with(chapter)
        # 验证返回类型
        self.assertIsInstance(events, list)
        self.assertTrue(all(isinstance(event, EventItem) for event in events))
        # 验证事件内容与小说有关
        self.assertIn("韩立", events[0].description)


class TestRefinerInterface(unittest.TestCase):
    """测试AbstractRefiner接口"""
    
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
    
    def test_refiner_interface(self):
        """测试优化器接口：使用小说真实内容"""
        refiner = MockRefiner()
        events = [
            EventItem(
                event_id="event-001",
                chapter_id="第一章",
                description="韩立背着半人高的木柴，怀里还揣着满满一布袋浆果",
                characters=["韩立"],
                location="莫家村附近的山上",
                time="幼年"
            ),
            EventItem(
                event_id="event-002",
                chapter_id="第一章",
                description="韩立发现三叔来访，三叔是附近小城酒楼的大掌柜",
                characters=["韩立", "三叔"],
                location="莫家村",
                time="幼年"
            )
        ]
        chapter = Chapter(
            chapter_id="第一章",
            title=self.chapter_title,
            content=self.chapter_text
        )
        
        refined_events = refiner.refine(events, chapter)
        
        # 验证模拟方法被调用
        refiner.mock_refine.assert_called_once()
        # 验证返回类型
        self.assertIsInstance(refined_events, list)
        self.assertTrue(all(isinstance(event, EventItem) for event in refined_events))
        # 验证事件内容仍然保留
        self.assertEqual(len(refined_events), 2)
        self.assertIn("韩立", refined_events[0].description)


class TestLinkerInterface(unittest.TestCase):
    """测试AbstractLinker接口"""
    
    def test_linker_interface(self):
        """测试链接器接口：使用小说真实场景"""
        linker = MockLinker()
        events = [
            EventItem(
                event_id="event-001",
                description="韩立上山采集木柴和浆果",
                characters=["韩立"],
                location="莫家村附近的山上",
                time="幼年",
                chapter_id="第一章"
            ),
            EventItem(
                event_id="event-002",
                description="韩立回家后遇到三叔，三叔的到来将改变他的命运",
                characters=["韩立", "三叔"],
                location="莫家村",
                time="幼年",
                chapter_id="第一章"
            )
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
            self.assertTrue("韩立" in edges[0].reason if edges[0].reason else False)
            
    def test_build_dag_interface(self):
        """测试构建DAG接口：使用小说真实场景"""
        linker = MockLinker()
        events = [
            EventItem(
                event_id="event-001",
                description="韩立被三叔带去参加七玄门的考验",
                characters=["韩立", "三叔"],
                location="青牛镇",
                time="幼年",
                chapter_id="第一章"
            ),
            EventItem(
                event_id="event-002",
                description="韩立见到墨大夫，获得三阶丹药参加测试",
                characters=["韩立", "墨大夫"],
                location="莫家村",
                time="幼年",
                chapter_id="第一章"
            ),
            EventItem(
                event_id="event-003",
                description="韩立通过七玄门测试，得到铁皮指功修炼口诀",
                characters=["韩立", "墨大夫"],
                location="青牛镇",
                time="幼年",
                chapter_id="第一章"
            )
        ]
        edges = [
            CausalEdge(
                from_id="event-001",
                to_id="event-002",
                strength="高",
                reason="韩立需要参加七玄门考核，所以去找墨大夫寻求帮助"
            ),
            CausalEdge(
                from_id="event-002",
                to_id="event-003",
                strength="高",
                reason="墨大夫赠送韩立三阶丹药，帮助他通过了七玄门测试"
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
        # 验证结果内容
        self.assertEqual(len(result_events), 3)
        self.assertEqual(len(result_edges), 2)


class TestGraphRendererInterface(unittest.TestCase):
    """测试AbstractGraphRenderer接口"""
    
    def test_graph_renderer_interface(self):
        """测试图形渲染器接口：使用小说真实场景"""
        renderer = MockGraphRenderer()
        events = [
            EventItem(
                event_id="event-001",
                description="韩立被三叔带去参加七玄门的考验",
                characters=["韩立", "三叔"],
                location="青牛镇",
                chapter_id="第一章"
            ),
            EventItem(
                event_id="event-002",
                description="韩立见到墨大夫，获得三阶丹药参加测试",
                characters=["韩立", "墨大夫"],
                location="莫家村",
                chapter_id="第一章"
            ),
            EventItem(
                event_id="event-003",
                description="韩立通过七玄门测试，得到铁皮指功修炼口诀",
                characters=["韩立", "墨大夫"],
                location="青牛镇",
                chapter_id="第一章"
            )
        ]
        edges = [
            CausalEdge(
                from_id="event-001",
                to_id="event-002",
                strength="高",
                reason="韩立需要参加七玄门考核，所以去找墨大夫寻求帮助"
            ),
            CausalEdge(
                from_id="event-002",
                to_id="event-003",
                strength="高",
                reason="墨大夫赠送韩立三阶丹药，帮助他通过了七玄门测试"
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
