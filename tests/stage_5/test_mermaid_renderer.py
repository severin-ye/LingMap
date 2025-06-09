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
            short_reason = self.renderer._truncate_text(edge.reason, 20)
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
