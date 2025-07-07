#!/usr/bin/env python3
"""
测试颜色映射工具

测试 ColorMap 类的方法和功能，确保能正确根据事件内容分配颜色
"""

import unittest
import os
import sys

# TODO: Translate - Add project root directory to Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from graph_builder.utils.color_map import ColorMap


class TestColorMap(unittest.TestCase):
    """测试颜色映射工具功能"""
    
    def test_default_colors(self):
        """测试默认颜色定义"""
        # TODO: Translate - Verify所有必要的默认颜色都已定义
        self.assertIn("default", ColorMap.DEFAULT_COLORS)
        self.assertIn("character", ColorMap.DEFAULT_COLORS)
        self.assertIn("treasure", ColorMap.DEFAULT_COLORS)
        self.assertIn("conflict", ColorMap.DEFAULT_COLORS)
        self.assertIn("cultivation", ColorMap.DEFAULT_COLORS)
        
        # TODO: Translate - Verify颜色格式
        for color_name, color_value in ColorMap.DEFAULT_COLORS.items():
            self.assertTrue(color_value.startswith("# TODO: Translate - "), f"颜色值{color_value}应以#开头")
            self.assertEqual(len(color_value), 7, f"颜色值{color_value}长度应为7 (# RRGGBB)")
    
    def test_get_node_color_character(self):
        """测试获取角色事件节点颜色"""
        # TODO: Translate - 角色相关event
        color = ColorMap.get_node_color("韩立前往集市", [], ["韩立"])
        self.assertEqual(color["fill"], ColorMap.DEFAULT_COLORS["character"])
    
    def test_get_node_color_treasure(self):
        """测试获取宝物事件节点颜色"""
        # TODO: Translate - 宝物相关event
        color = ColorMap.get_node_color("获得宝物", ["灵药", "丹药"], [])
        self.assertEqual(color["fill"], ColorMap.DEFAULT_COLORS["treasure"])
    
    def test_get_node_color_conflict(self):
        """测试获取冲突事件节点颜色"""
        # TODO: Translate - 冲突相关event
        color = ColorMap.get_node_color("韩立与敌人战斗", [], ["韩立", "敌人"])
        self.assertEqual(color["fill"], ColorMap.DEFAULT_COLORS["conflict"])
        
        # TODO: Translate - 另一个冲突关键词
        color = ColorMap.get_node_color("韩立被追杀", [], ["韩立"])
        self.assertEqual(color["fill"], ColorMap.DEFAULT_COLORS["conflict"])
    
    def test_get_node_color_cultivation(self):
        """测试获取修炼事件节点颜色"""
        # TODO: Translate - 修炼相关event
        color = ColorMap.get_node_color("韩立修炼功法", [], ["韩立"])
        self.assertEqual(color["fill"], ColorMap.DEFAULT_COLORS["cultivation"])
        
        # TODO: Translate - 另一个修炼关键词
        color = ColorMap.get_node_color("韩立突破境界", [], ["韩立"])
        self.assertEqual(color["fill"], ColorMap.DEFAULT_COLORS["cultivation"])
    
    def test_get_node_color_default(self):
        """测试获取默认节点颜色"""
        # TODO: Translate - 无特殊类型event
        color = ColorMap.get_node_color("一般事件", [], [])
        self.assertEqual(color["fill"], ColorMap.DEFAULT_COLORS["default"])
    
    def test_get_node_color_priority(self):
        """测试颜色分配的优先级"""
        # TODO: Translate - 冲突优先于宝物和角色
        color = ColorMap.get_node_color("韩立为宝物战斗", ["宝物"], ["韩立"])
        self.assertEqual(color["fill"], ColorMap.DEFAULT_COLORS["conflict"])
        
        # TODO: Translate - 宝物优先于角色
        color = ColorMap.get_node_color("韩立获得宝物", ["宝物"], ["韩立"])
        self.assertEqual(color["fill"], ColorMap.DEFAULT_COLORS["treasure"])
        
        # TODO: Translate - 修炼优先于角色
        color = ColorMap.get_node_color("韩立修炼法术", [], ["韩立"])
        self.assertEqual(color["fill"], ColorMap.DEFAULT_COLORS["cultivation"])
    
    def test_get_edge_style_high(self):
        """测试获取高强度边样式"""
        style = ColorMap.get_edge_style("高")
        self.assertEqual(style["style"], "normal")
        self.assertEqual(style["stroke_width"], "2px")
        # TODO: Translate - Verify颜色格式
        self.assertTrue(style["stroke"].startswith("#"))
    
    def test_get_edge_style_medium(self):
        """测试获取中强度边样式"""
        style = ColorMap.get_edge_style("中")
        self.assertEqual(style["style"], "normal")
        self.assertEqual(style["stroke_width"], "1.5px")
        # TODO: Translate - Verify颜色格式
        self.assertTrue(style["stroke"].startswith("#"))
    
    def test_get_edge_style_low(self):
        """测试获取低强度边样式"""
        style = ColorMap.get_edge_style("低")
        self.assertEqual(style["style"], "dashed")
        self.assertEqual(style["stroke_width"], "1px")
        # TODO: Translate - Verify颜色格式
        self.assertTrue(style["stroke"].startswith("#"))
    
    def test_get_edge_style_unknown(self):
        """测试获取未知强度边样式"""
        # TODO: Translate - 未知强度应默认为低强度
        style = ColorMap.get_edge_style("未知")
        self.assertEqual(style["style"], "dashed")  # TODO: Translate - 应该与低强度相同
        self.assertEqual(style["stroke_width"], "1px")
        # TODO: Translate - Verify颜色格式
        self.assertTrue(style["stroke"].startswith("#"))
