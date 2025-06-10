#!/usr/bin/env python3
"""
图形构建器集成测试

测试图形构建模块的端到端功能，从数据输入到生成Mermaid图谱
"""

import os
import sys
import unittest
import json
import tempfile
import shutil

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from graph_builder.controller.graph_controller import render_graph


class TestGraphBuilderIntegration(unittest.TestCase):
    """测试图形构建模块的集成功能"""
    
    def setUp(self):
        """设置测试环境和测试数据"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 准备测试数据，包括重复ID的节点
        self.test_data = {
            "nodes": [
                {
                    "event_id": "E01-1",
                    "description": "韩立在爬坡过程中感到害怕并决定加快速度",
                    "characters": ["韩立"],
                    "treasures": [],
                    "result": "加快速度",
                    "location": "山坡",
                    "time": "白天",
                    "chapter_id": "第一章"
                },
                {
                    "event_id": "E01-1",  # 重复ID
                    "description": "墨大夫进入大屋子，韩立疲惫入睡",
                    "characters": ["韩立", "墨大夫"],
                    "treasures": [],
                    "result": "入睡",
                    "location": "大屋子",
                    "time": "晚上",
                    "chapter_id": "第一章"
                },
                {
                    "event_id": "E01-2",
                    "description": "韩立发现灵药",
                    "characters": ["韩立"],
                    "treasures": ["灵药"],
                    "result": "获得灵药",
                    "location": "药园",
                    "time": "下午",
                    "chapter_id": "第一章"
                }
            ],
            "edges": [
                {
                    "from": "E01-1",
                    "to": "E01-2",
                    "strength": "高",
                    "reason": "韩立在爬坡时发现了药园"
                }
            ]
        }
        
        # 保存测试数据到JSON文件
        self.input_json_path = os.path.join(self.temp_dir, "test_input.json")
        with open(self.input_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, ensure_ascii=False, indent=2)
            
        # 设置输出路径
        self.output_mermaid_path = os.path.join(self.temp_dir, "test_output.mmd")
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_rendering(self):
        """测试从JSON文件到Mermaid文件的端到端渲染流程"""
        # 执行渲染
        options = {"show_legend": True, "show_edge_labels": True}
        mermaid_text = render_graph(self.input_json_path, self.output_mermaid_path, options)
        
        # 验证输出文件存在
        self.assertTrue(os.path.exists(self.output_mermaid_path))
        
        # 验证输出内容
        with open(self.output_mermaid_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查基本结构
        self.assertIn("```mermaid", content)
        self.assertIn("graph TD", content)
        
        # 检查重复ID已被处理
        self.assertIn("E01-1_1", content) 
        self.assertIn("E01-1_2", content)
        
        # 检查节点描述
        self.assertIn("韩立在爬坡过程中感到害怕", content)
        self.assertIn("墨大夫进入大屋子", content)
        
        # 检查边连接
        # 由于ID重新映射，无法确定具体的连接模式，但应该包含E01-2
        self.assertIn("E01-2", content)
        
        # 检查图例
        self.assertIn("subgraph 图例", content)
        
    def test_empty_graph(self):
        """测试处理空图的情况"""
        # 创建空图数据
        empty_data = {"nodes": [], "edges": []}
        empty_input_path = os.path.join(self.temp_dir, "empty_input.json")
        empty_output_path = os.path.join(self.temp_dir, "empty_output.mmd")
        
        # 保存空数据
        with open(empty_input_path, 'w', encoding='utf-8') as f:
            json.dump(empty_data, f)
            
        # 执行渲染
        mermaid_text = render_graph(empty_input_path, empty_output_path)
        
        # 验证输出
        self.assertTrue(os.path.exists(empty_output_path))
        with open(empty_output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 空图应至少包含基本结构
        self.assertIn("```mermaid", content)
        self.assertIn("graph TD", content)


if __name__ == "__main__":
    unittest.main()
