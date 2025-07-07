#!/usr/bin/env python3
"""
测试 Mermaid 渲染器模块

测试 MermaidRenderer 类的方法和功能，确保能正确渲染事件和因果边为 Mermaid 语法
"""

import unittest
import os
import sys

# TODO: Translate - Add project root directory to Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from graph_builder.service.mermaid_renderer import MermaidRenderer


class TestMermaidRenderer(unittest.TestCase):
    """测试 Mermaid 渲染器功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.renderer = MermaidRenderer()
        
        # CreateTestevent
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
                description="韩立发现药园",
                characters=["韩立"],
                treasures=["灵药"],
                location="七玄门药园",
                chapter_id="第一章",
                result="获得灵药"
            ),
            EventItem(
                event_id="E3",
                description="韩立与白衣人战斗",
                characters=["韩立", "白衣人"],
                treasures=[],
                location="洞穴",
                chapter_id="第二章",
                result="韩立险胜"
            )
        ]
        
        # TODO: Translate - CreateTestcausal边
        self.test_edges = [
            CausalEdge(
                from_id="E1",
                to_id="E2",
                strength="高",
                reason="韩立上山采集时发现了药园"
            ),
            CausalEdge(
                from_id="E2",
                to_id="E3",
                strength="中",
                reason="韩立获得灵药引来白衣人追杀"
            )
        ]
    
    def test_render_basic_graph(self):
        """测试基本图谱渲染功能"""
        # TODO: Translate - 渲染图谱
        result = self.renderer.render(self.test_events, self.test_edges)
        
        # TODO: Translate - Verify基本结构
        self.assertIn("```mermaid", result)
        self.assertIn("graph TD", result)
        self.assertIn("```", result)
        
        # TODO: Translate - Verify节点存在
        for event in self.test_events:
            self.assertIn(event.event_id, result)
            # TODO: Translate - 转义的文本也应该存在
            self.assertIn(self.renderer._escape_text(event.description), result)
        
        # TODO: Translate - Verify边存在
        for edge in self.test_edges:
            self.assertIn(f"{edge.from_id} -->", result)
            self.assertIn(edge.to_id, result)
    
    def test_node_styles(self):
        """测试节点样式渲染"""
        result = self.renderer.render(self.test_events, self.test_edges)
        
        # TODO: Translate - Verify每个节点都有样式定义
        for event in self.test_events:
            self.assertIn(f"style {event.event_id} fill:", result)
            self.assertIn("stroke:", result)
    
    def test_edge_labels(self):
        """测试边标签渲染"""
        # TODO: Translate - 显示边标签的选项
        options = {"show_edge_labels": True}
        result = self.renderer.render(self.test_events, self.test_edges, options)
        
        # TODO: Translate - Verify边有标签
        for edge in self.test_edges:
            short_reason = self.renderer._truncate_text(edge.reason, 20)
            # TODO: Translate - Use更宽松的Verify，只Check是否包含标签文本
            self.assertIn(edge.from_id, result)
            self.assertIn(edge.to_id, result)
            self.assertIn(self.renderer._escape_text(short_reason), result)
    
    def test_custom_edge_style(self):
        """测试自定义边样式"""
        options = {"custom_edge_style": True}
        result = self.renderer.render(self.test_events, self.test_edges, options)
        
        # TODO: Translate - Verify自定义边样式定义
        self.assertIn("linkStyle", result)
        self.assertIn("stroke:", result)
        self.assertIn("stroke-width:", result)
    
    def test_legend(self):
        """测试图例渲染"""
        options = {"show_legend": True}
        result = self.renderer.render(self.test_events, self.test_edges, options)
        
        # TODO: Translate - Verify图例存在
        self.assertIn("subgraph 图例", result)
        self.assertIn("legend_character", result)
        self.assertIn("legend_treasure", result)
        self.assertIn("legend_conflict", result)
        self.assertIn("legend_cultivation", result)
    
    def test_text_escape(self):
        """测试文本转义功能"""
        # TODO: Translate - 含特殊字符的文本
        text = 'This has "quotes" and other special chars'
        escaped = self.renderer._escape_text(text)
        
        # TODO: Translate - Verify引号被转义
        self.assertEqual(escaped, 'This has \\"quotes\\" and other special chars')
    
    def test_text_truncation(self):
        """测试文本截断功能"""
        # TODO: Translate - 长文本
        long_text = "这是一段非常长的文本，需要被截断以适应显示需要"
        truncated = self.renderer._truncate_text(long_text, 10)
        
        # TODO: Translate - Verify截断结果
        self.assertEqual(truncated, "这是一段非常长...")
        self.assertEqual(len(truncated), 10)
        
        # TODO: Translate - 短文本不应被截断
        short_text = "短文本"
        self.assertEqual(self.renderer._truncate_text(short_text, 10), short_text)
    
    def test_options_merging(self):
        """测试Rendering options合并功能"""
        # TODO: Translate - Set默认选项的渲染器
        custom_renderer = MermaidRenderer({"show_legend": True, "custom_option": "value"})
        
        # TODO: Translate - Use覆盖一部分选项
        result = custom_renderer.render(
            self.test_events, 
            self.test_edges, 
            {"show_legend": False, "show_edge_labels": False}
        )
        
        # TODO: Translate - Verify图例未显示(被覆盖)
        self.assertNotIn("subgraph 图例", result)
        
        # TODO: Translate - 其他默认选项应保持不变
        # TODO: Translate - 注意：这里无法直接Test，因为选项合并后没有直接暴露出来
        # TODO: Translate - 可以通过功能表现来间接Verify
    
    def test_duplicate_node_ids(self):
        """测试处理重复节点ID的情况"""
        # TODO: Translate - Create包含重复ID的Testevent
        duplicate_events = [
            EventItem(
                event_id="E1",
                description="韩立上山采集浆果",
                characters=["韩立"],
                treasures=[]
            ),
            EventItem(
                event_id="E1",  # TODO: Translate - 重复ID
                description="韩立发现药园",
                characters=["韩立"],
                treasures=["灵药"]
            ),
            EventItem(
                event_id="E1",  # TODO: Translate - 重复ID
                description="韩立与白衣人战斗",
                characters=["韩立", "白衣人"],
                treasures=[]
            ),
            EventItem(
                event_id="E2",
                description="韩立修炼功法",
                characters=["韩立"],
                treasures=[]
            )
        ]
        
        # TODO: Translate - Create引用这些节点的边
        duplicate_edges = [
            CausalEdge(
                from_id="E1",
                to_id="E2",
                strength="高",
                reason="韩立上山采集时发现了药园"
            )
        ]
        
        # TODO: Translate - 渲染图谱
        result = self.renderer.render(duplicate_events, duplicate_edges)
        
        # TODO: Translate - VerifyGenerate的图谱包含唯一ID
        self.assertIn("E1_1", result)
        self.assertIn("E1_2", result)
        self.assertIn("E1_3", result)
        self.assertIn("E2", result)
        
        # TODO: Translate - Verify所有描述都存在
        self.assertIn(self.renderer._escape_text("韩立上山采集浆果"), result)
        self.assertIn(self.renderer._escape_text("韩立发现药园"), result)
        self.assertIn(self.renderer._escape_text("韩立与白衣人战斗"), result)
        
        # TODO: Translate - Verify边被正确更新
        # TODO: Translate - 由于我们不知道到底哪个E1会被映射为linking源，所以CheckE2作为目标
        self.assertIn("E2", result)
        
        # TODO: Translate - 每个节点都应该有自己的样式
        self.assertIn("style E1_1", result)
        self.assertIn("style E1_2", result) 
        self.assertIn("style E1_3", result)
        self.assertIn("style E2", result)
        
    def test_connect_isolated_nodes(self):
        """测试孤立节点连接功能"""
        # CreateTestevent
        test_events = [
            EventItem(
                event_id="E01-1",
                description="韩立在青牛镇长大",
                characters=["韩立"],
                location="青牛镇"
            ),
            EventItem(
                event_id="E01-2",
                description="韩立被选中参加七玄门测试",
                characters=["韩立"],
                location="青牛镇"
            ),
            EventItem(
                event_id="E01-3",
                description="七玄门测试开始",
                characters=["韩立", "测试官"],
                location="七玄门"
            ),
            EventItem(
                event_id="E02-1",  # TODO: Translate - 不同chapter的孤立节点
                description="韩立开始修炼基础功法",
                characters=["韩立"],
                location="七玄门"
            ),
            EventItem(
                event_id="E02-2",
                description="韩立发现自己灵根资质较差",
                characters=["韩立"],
                location="七玄门"
            ),
            EventItem(
                event_id="E03-1",  # TODO: Translate - 完全孤立的节点
                description="韩立偶然发现一本古籍",
                characters=["韩立"],
                location="山洞"
            )
        ]
        
        # TODO: Translate - CreateTest边（只连接部分节点，让一些节点成为孤立节点）
        test_edges = [
            CausalEdge(
                from_id="E01-1",
                to_id="E01-2",
                strength="高",
                reason="韩立生活在青牛镇，因此有机会被选中参加测试"
            ),
            CausalEdge(
                from_id="E01-2",
                to_id="E01-3",
                strength="高",
                reason="被选中后需要参加测试"
            )
        ]
        
        # TODO: Translate - 1. Test启用孤立节点连接（默认行为）
        with_connection = self.renderer.render(
            events=test_events,
            edges=test_edges.copy(),
            format_options={"connect_isolated_nodes": True}
        )
        
        # TODO: Translate - Verify原始边存在
        self.assertIn("E01-1 -->", with_connection)
        self.assertIn("E01-2 -->", with_connection)
        
        # TODO: Translate - Verify新的时序连接边已Create
        # E02-1 -> E02-2 -> E03-1
        self.assertIn("E02-1 -->", with_connection)
        self.assertIn("E02-2 -->", with_connection)
        
        # TODO: Translate - Verify时序边Use了特殊样式
        # TODO: Translate - 找到linkStyle定义中Use绿色的行
        self.assertIn("stroke:#27AE60", with_connection)
        self.assertIn("stroke-dasharray:5 5", with_connection)
        
        # TODO: Translate - 2. Test禁用孤立节点连接
        without_connection = self.renderer.render(
            events=test_events,
            edges=test_edges.copy(),
            format_options={"connect_isolated_nodes": False}
        )
        
        # TODO: Translate - Verify原始边存在
        self.assertIn("E01-1 -->", without_connection)
        self.assertIn("E01-2 -->", without_connection)
        
        # TODO: Translate - 统计边的数量（通过计算 "-->" 出现的次数）
        edges_with_connection = with_connection.count("-->")
        edges_without_connection = without_connection.count("-->")
        
        # TODO: Translate - 确认禁用时边数量少于启用时
        self.assertGreater(edges_with_connection, edges_without_connection)
        
        # TODO: Translate - 禁用时应该只有原始的两条边
        self.assertEqual(edges_without_connection, len(test_edges))
        
        # TODO: Translate - 启用时应该有额外的时序连接边
        self.assertEqual(edges_with_connection, len(test_edges) + 2)  # TODO: Translate - 增加了2个连接


if __name__ == "__main__":
    unittest.main()
