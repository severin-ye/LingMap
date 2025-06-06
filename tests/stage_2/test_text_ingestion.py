#!/usr/bin/env python3
"""
文本摄入模块测试

本文件包含对文本摄入模块的测试用例，主要测试：
1. ChapterLoader 是否能正确加载小说文本
2. 文本分割功能是否正常工作
3. 章节信息提取是否准确
"""

import sys
import os
import unittest
import tempfile
import shutil

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from text_ingestion.chapter_loader import ChapterLoader
from common.models.chapter import Chapter


class TestChapterLoader(unittest.TestCase):
    """测试 ChapterLoader 类的功能"""
    
    def setUp(self):
        """测试前的准备工作，使用真实的小说数据"""
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # 使用真实的测试数据文件
        self.real_test_file = os.path.join(project_root, "novel", "test.txt")
        
        # 创建临时目录用于测试不存在的文件
        self.temp_dir = tempfile.mkdtemp()
        
        # 实例化章节加载器，使用较大的segment_size来处理真实数据
        self.loader = ChapterLoader(segment_size=800)
    
    def tearDown(self):
        """测试后的清理工作"""
        shutil.rmtree(self.temp_dir)
    
    def test_load_from_txt(self):
        """测试从真实文本文件加载章节"""
        chapter = self.loader.load_from_txt(self.real_test_file)
        
        # 验证章节加载成功
        self.assertIsNotNone(chapter)
        self.assertIsInstance(chapter, Chapter)
        
        # 类型检查后的安全访问
        if chapter is not None:
            # 验证从真实数据中提取的章节信息
            self.assertEqual(chapter.chapter_id, "第一章")  # 从真实文本中提取的章节ID
            self.assertEqual(chapter.title, "山边小村")      # 从真实文本中提取的章节标题
            
            # 验证内容不为空
            self.assertGreater(len(chapter.content), 0)
            
            # 验证分段功能正常工作
            self.assertGreater(len(chapter.segments), 0)
            
            # 验证每个分段都有必要的字段
            for segment in chapter.segments:
                self.assertIn("seg_id", segment)
                self.assertIn("text", segment)
                self.assertGreater(len(segment["text"]), 0)
    
    def test_chapter_segmentation(self):
        """测试章节分段功能，使用真实数据"""
        chapter = self.loader.load_from_txt(self.real_test_file)
        
        self.assertIsNotNone(chapter)
        
        # 类型检查后的安全访问
        if chapter is not None:
            # 检查分段是否包含真实文本中的关键内容
            all_segment_text = " ".join([seg["text"] for seg in chapter.segments])
            
            # 验证真实文本中的关键人物和地点
            self.assertIn("韩立", all_segment_text)
            self.assertIn("二愣子", all_segment_text)
            self.assertIn("七玄门", all_segment_text)
            
            # 验证每个分段的长度合理（不为空，不超过segment_size太多）
            for segment in chapter.segments:
                self.assertGreater(len(segment["text"]), 0)
                # 允许一定的超出范围，因为按段落分割可能会超出目标长度
                self.assertLess(len(segment["text"]), self.loader.segment_size * 2)
            
    def test_real_data_content_verification(self):
        """测试真实数据的内容验证"""
        chapter = self.loader.load_from_txt(self.real_test_file)
        
        self.assertIsNotNone(chapter)
        
        # 类型检查后的安全访问
        if chapter is not None:
            # 验证真实数据中的关键情节
            content = chapter.content
            self.assertIn("《凡人修仙传》", content)
            self.assertIn("忘语", content)
            self.assertIn("韩立", content)
            self.assertIn("七玄门", content)
            
            # 验证章节结构
            self.assertTrue(chapter.title and len(chapter.title) > 0)
            self.assertTrue(chapter.chapter_id and len(chapter.chapter_id) > 0)
    
    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        non_existent_path = os.path.join(self.temp_dir, "non_existent.txt")
        chapter = self.loader.load_from_txt(non_existent_path)
        
        self.assertIsNone(chapter)


if __name__ == "__main__":
    unittest.main()
