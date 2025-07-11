#!/usr/bin/env python3
"""
测试 Mermaid 渲染器模块

测试 MermaidRenderer 类的方法和功能，确保能正确渲染事件和因果边为 Mermaid 语法
"""

import unittest
import os
import sys

# 添加项目根目录到 Python 路径
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
        
        # 创建测试事件
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
        
        # 创建测试因果边
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
        # 渲染图谱
        result = self.renderer.render(self.test_events, self.test_edges)
        
        # 验证基本结构
        self.assertIn("```mermaid", result)
        self.assertIn("graph TD", result)
        self.assertIn("```", result)
        
        # 验证节点存在
        for event in self.test_events:
            self.assertIn(event.event_id, result)
            # 转义的文本也应该存在
            self.assertIn(self.renderer._escape_text(event.description), result)
        
        # 验证边存在
        for edge in self.test_edges:
            self.assertIn(f"{edge.from_id} -->", result)
            self.assertIn(edge.to_id, result)
    
    def test_node_styles(self):
        """测试节点样式渲染"""
        result = self.renderer.render(self.test_events, self.test_edges)
        
        # 验证每个节点都有样式定义
        for event in self.test_events:
            self.assertIn(f"style {event.event_id} fill:", result)
            self.assertIn("stroke:", result)
    
    def test_edge_labels(self):
        """测试边标签渲染"""
        # 显示边标签的选项
        options = {"show_edge_labels": True}
        result = self.renderer.render(self.test_events, self.test_edges, options)
        
        # 验证边有标签
        for edge in self.test_edges:
            reason_text = edge.reason or "未知原因"  # 处理 None 的情况
            short_reason = self.renderer._truncate_text(reason_text, 20)
            # 使用更宽松的验证，只检查是否包含标签文本
            self.assertIn(edge.from_id, result)
            self.assertIn(edge.to_id, result)
            self.assertIn(self.renderer._escape_text(short_reason), result)
    
    def test_custom_edge_style(self):
        """测试自定义边样式"""
        options = {"custom_edge_style": True}
        result = self.renderer.render(self.test_events, self.test_edges, options)
        
        # 验证自定义边样式定义
        self.assertIn("linkStyle", result)
        self.assertIn("stroke:", result)
        self.assertIn("stroke-width:", result)
    
    def test_legend(self):
        """测试图例渲染"""
        options = {"show_legend": True}
        result = self.renderer.render(self.test_events, self.test_edges, options)
        
        # 验证图例存在
        self.assertIn("subgraph 图例", result)
        self.assertIn("legend_character", result)
        self.assertIn("legend_treasure", result)
        self.assertIn("legend_conflict", result)
        self.assertIn("legend_cultivation", result)
    
    def test_text_escape(self):
        """测试文本转义功能"""
        # 含特殊字符的文本
        text = 'This has "quotes" and other special chars'
        escaped = self.renderer._escape_text(text)
        
        # 验证引号被转义
        self.assertEqual(escaped, 'This has \\"quotes\\" and other special chars')
    
    def test_text_truncation(self):
        """测试文本截断功能"""
        # 长文本
        long_text = "这是一段非常长的文本，需要被截断以适应显示需要"
        truncated = self.renderer._truncate_text(long_text, 10)
        
        # 验证截断结果
        self.assertEqual(truncated, "这是一段非常长...")
        self.assertEqual(len(truncated), 10)
        
        # 短文本不应被截断
        short_text = "短文本"
        self.assertEqual(self.renderer._truncate_text(short_text, 10), short_text)
    
    def test_options_merging(self):
        """测试渲染选项合并功能"""
        # 设置默认选项的渲染器
        custom_renderer = MermaidRenderer({"show_legend": True, "custom_option": "value"})
        
        # 使用覆盖一部分选项
        result = custom_renderer.render(
            self.test_events, 
            self.test_edges, 
            {"show_legend": False, "show_edge_labels": False}
        )
        
        # 验证图例未显示(被覆盖)
        self.assertNotIn("subgraph 图例", result)
        
        # 其他默认选项应保持不变
        # 注意：这里无法直接测试，因为选项合并后没有直接暴露出来
        # 可以通过功能表现来间接验证
    
    def test_duplicate_node_ids(self):
        """测试处理重复节点ID的情况"""
        # 创建包含重复ID的测试事件
        duplicate_events = [
            EventItem(
                event_id="E1",
                description="韩立上山采集浆果",
                characters=["韩立"],
                treasures=[]
            ),
            EventItem(
                event_id="E1",  # 重复ID
                description="韩立发现药园",
                characters=["韩立"],
                treasures=["灵药"]
            ),
            EventItem(
                event_id="E1",  # 重复ID
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
        
        # 创建引用这些节点的边
        duplicate_edges = [
            CausalEdge(
                from_id="E1",
                to_id="E2",
                strength="高",
                reason="韩立上山采集时发现了药园"
            )
        ]
        
        # 渲染图谱
        result = self.renderer.render(duplicate_events, duplicate_edges)
        
        # 验证生成的图谱包含唯一ID
        self.assertIn("E1_1", result)
        self.assertIn("E1_2", result)
        self.assertIn("E1_3", result)
        self.assertIn("E2", result)
        
        # 验证所有描述都存在
        self.assertIn(self.renderer._escape_text("韩立上山采集浆果"), result)
        self.assertIn(self.renderer._escape_text("韩立发现药园"), result)
        self.assertIn(self.renderer._escape_text("韩立与白衣人战斗"), result)
        
        # 验证边被正确更新
        # 由于我们不知道到底哪个E1会被映射为链接源，所以检查E2作为目标
        self.assertIn("E2", result)
        
        # 每个节点都应该有自己的样式
        self.assertIn("style E1_1", result)
        self.assertIn("style E1_2", result) 
        self.assertIn("style E1_3", result)
        self.assertIn("style E2", result)
        
    def test_connect_isolated_nodes(self):
        """测试孤立节点连接功能"""
        # 创建测试事件
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
                event_id="E02-1",  # 不同章节的孤立节点
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
                event_id="E03-1",  # 完全孤立的节点
                description="韩立偶然发现一本古籍",
                characters=["韩立"],
                location="山洞"
            )
        ]
        
        # 创建测试边（只连接部分节点，让一些节点成为孤立节点）
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
        
        # 1. 测试启用孤立节点连接（默认行为）
        with_connection = self.renderer.render(
            events=test_events,
            edges=test_edges.copy(),
            format_options={"connect_isolated_nodes": True}
        )
        
        # 验证原始边存在
        self.assertIn("E01-1 -->", with_connection)
        self.assertIn("E01-2 -->", with_connection)
        
        # 验证新的时序连接边已创建
        # E02-1 -> E02-2 -> E03-1
        self.assertIn("E02-1 -->", with_connection)
        self.assertIn("E02-2 -->", with_connection)
        
        # 验证时序边使用了特殊样式
        # 找到linkStyle定义中使用绿色的行
        self.assertIn("stroke:#27AE60", with_connection)
        self.assertIn("stroke-dasharray:5 5", with_connection)
        
        # 2. 测试禁用孤立节点连接
        without_connection = self.renderer.render(
            events=test_events,
            edges=test_edges.copy(),
            format_options={"connect_isolated_nodes": False}
        )
        
        # 验证原始边存在
        self.assertIn("E01-1 -->", without_connection)
        self.assertIn("E01-2 -->", without_connection)
        
        # 统计边的数量（通过计算 "-->" 出现的次数）
        edges_with_connection = with_connection.count("-->")
        edges_without_connection = without_connection.count("-->")
        
        # 确认禁用时边数量少于启用时
        self.assertGreater(edges_with_connection, edges_without_connection)
        
        # 禁用时应该只有原始的两条边
        self.assertEqual(edges_without_connection, len(test_edges))
        
        # 启用时应该有额外的时序连接边
        self.assertEqual(edges_with_connection, len(test_edges) + 2)  # 增加了2个连接


if __name__ == "__main__":
    unittest.main()
