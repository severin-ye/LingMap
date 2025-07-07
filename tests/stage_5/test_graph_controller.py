#!/usr/bin/env python3
"""
测试图谱控制器

测试 GraphController 模块的功能，确保能正确加载数据并生成图谱
"""

import unittest
import os
import sys
import json
import tempfile
import shutil

# TODO: Translate - Add project root directory to Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from graph_builder.controller.graph_controller import render_graph


class TestGraphController(unittest.TestCase):
    """测试图谱控制器功能"""
    
    def setUp(self):
        """设置测试环境"""
        # TODO: Translate - Create临时目录
        self.temp_dir = tempfile.mkdtemp()
        
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
            )
        ]
        
        # TODO: Translate - CreateTestcausal边
        self.test_edges = [
            CausalEdge(
                from_id="E1",
                to_id="E2",
                strength="高",
                reason="韩立上山采集时发现了药园"
            )
        ]
        
        # TODO: Translate - Create输入JSON文件
        self.input_file = os.path.join(self.temp_dir, "test_input.json")
        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump({
                "nodes": [event.to_dict() for event in self.test_events],
                "edges": [edge.to_dict() for edge in self.test_edges]
            }, f, ensure_ascii=False, indent=2)
        
        # TODO: Translate - 定义Output文件路径
        self.output_file = os.path.join(self.temp_dir, "test_output.mmd")
    
    def tearDown(self):
        """清理测试环境"""
        # TODO: Translate - 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_render_graph(self):
        """测试图谱渲染功能"""
        # TODO: Translate - 渲染图谱
        mermaid_text = render_graph(self.input_file, self.output_file)
        
        # TODO: Translate - Verify渲染结果
        self.assertIn("```mermaid", mermaid_text)
        self.assertIn("graph TD", mermaid_text)
        self.assertIn("E1", mermaid_text)
        self.assertIn("E2", mermaid_text)
        self.assertIn("E1 -->", mermaid_text)
        self.assertIn("```", mermaid_text)
        
        # TODO: Translate - VerifyOutput文件已Create
        self.assertTrue(os.path.exists(self.output_file))
        
        # TODO: Translate - VerifyOutput文件内容
        with open(self.output_file, 'r', encoding='utf-8') as f:
            file_content = f.read()
            self.assertEqual(file_content, mermaid_text)
    
    def test_render_with_options(self):
        """测试带选项的图谱渲染"""
        # TODO: Translate - 定义渲染选项
        options = {
            "show_legend": True,
            "show_edge_labels": True,
            "custom_edge_style": True
        }
        
        # TODO: Translate - 渲染图谱
        mermaid_text = render_graph(self.input_file, self.output_file, options)
        
        # TODO: Translate - Verify选项是否生效
        self.assertIn("subgraph 图例", mermaid_text)  # TODO: Translate - 显示图例
        self.assertIn("|", mermaid_text)  # TODO: Translate - 显示边标签
        self.assertIn("linkStyle", mermaid_text)  # TODO: Translate - 自定义边样式
    
    def test_render_missing_input(self):
        """测试输入文件不存在的情况"""
        invalid_input = os.path.join(self.temp_dir, "nonexistent.json")
        
        # TODO: Translate - Verify渲染不存在的文件会引发异常
        with self.assertRaises(FileNotFoundError):
            render_graph(invalid_input, self.output_file)
    
    def test_render_invalid_json(self):
        """测试输入无效JSON的情况"""
        # TODO: Translate - Create无效JSON文件
        invalid_json = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_json, 'w', encoding='utf-8') as f:
            f.write("This is not valid JSON")
        
        # TODO: Translate - VerifyProcess无效JSON会引发异常
        with self.assertRaises(json.JSONDecodeError):
            render_graph(invalid_json, self.output_file)
    
    def test_create_output_directory(self):
        """测试创建输出目录功能"""
        # TODO: Translate - 在不存在的子目录中定义Output文件
        nested_output = os.path.join(self.temp_dir, "subdir", "output.mmd")
        
        # TODO: Translate - 渲染图谱，应自动Create子目录
        render_graph(self.input_file, nested_output)
        
        # TODO: Translate - VerifyOutput文件已Create
        self.assertTrue(os.path.exists(nested_output))
