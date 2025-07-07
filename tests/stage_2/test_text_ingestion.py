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

# TODO: Translate - Add project root directory to Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from text_ingestion.chapter_loader import ChapterLoader
from common.models.chapter import Chapter


class TestChapterLoader(unittest.TestCase):
    """测试 ChapterLoader 类的功能"""
    
    def setUp(self):
        """测试前的准备工作，使用真实的小说数据"""
        # TODO: Translate - Get项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # TODO: Translate - Use真实的Test数据文件
        self.real_test_file = os.path.join(project_root, "novel", "test.txt")
        
        # TODO: Translate - Create临时目录用于Test不存在的文件
        self.temp_dir = tempfile.mkdtemp()
        
        # TODO: Translate - 实例化chapterLoad器，Use较大的segment_size来Process真实数据
        self.loader = ChapterLoader(segment_size=800)
    
    def tearDown(self):
        """测试后的清理工作"""
        shutil.rmtree(self.temp_dir)
    
    def test_load_from_txt(self):
        """测试从真实文本文件加载章节"""
        chapter = self.loader.load_from_txt(self.real_test_file)
        
        # VerifychapterLoadSuccessfully
        self.assertIsNotNone(chapter)
        self.assertIsInstance(chapter, Chapter)
        
        # TODO: Translate - 类型Check后的安全访问
        if chapter is not None:
            # TODO: Translate - Verify从真实数据中Extract的chapter信息
            self.assertEqual(chapter.chapter_id, "第一章")  # TODO: Translate - 从真实文本中Extract的chapterID
            self.assertEqual(chapter.title, "山边小村")      # TODO: Translate - 从真实文本中Extract的chapter标题
            
            # TODO: Translate - Verify内容不为空
            self.assertGreater(len(chapter.content), 0)
            
            # TODO: Translate - VerifySegment text功能正常工作
            self.assertGreater(len(chapter.segments), 0)
            
            # TODO: Translate - Verify每个Segment text都有必要的字段
            for segment in chapter.segments:
                self.assertIn("seg_id", segment)
                self.assertIn("text", segment)
                self.assertGreater(len(segment["text"]), 0)
    
    def test_chapter_segmentation(self):
        """测试章节分段功能，使用真实数据"""
        chapter = self.loader.load_from_txt(self.real_test_file)
        
        self.assertIsNotNone(chapter)
        
        # TODO: Translate - 类型Check后的安全访问
        if chapter is not None:
            # TODO: Translate - CheckSegment text是否包含真实文本中的关键内容
            all_segment_text = " ".join([seg["text"] for seg in chapter.segments])
            
            # TODO: Translate - Verify真实文本中的关键人物和地点
            self.assertIn("韩立", all_segment_text)
            self.assertIn("二愣子", all_segment_text)
            self.assertIn("七玄门", all_segment_text)
            
            # TODO: Translate - Verify每个Segment text的长度合理（不为空，不超过segment_size太多）
            for segment in chapter.segments:
                self.assertGreater(len(segment["text"]), 0)
                # TODO: Translate - 允许一定的超出范围，因为按段落分割可能会超出目标长度
                self.assertLess(len(segment["text"]), self.loader.segment_size * 2)
            
    def test_real_data_content_verification(self):
        """测试真实数据的内容验证"""
        chapter = self.loader.load_from_txt(self.real_test_file)
        
        self.assertIsNotNone(chapter)
        
        # TODO: Translate - 类型Check后的安全访问
        if chapter is not None:
            # TODO: Translate - Verify真实数据中的关键情节
            content = chapter.content
            self.assertIn("《凡人修仙传》", content)
            self.assertIn("忘语", content)
            self.assertIn("韩立", content)
            self.assertIn("七玄门", content)
            
            # TODO: Translate - Verifychapter结构
            self.assertTrue(chapter.title and len(chapter.title) > 0)
            self.assertTrue(chapter.chapter_id and len(chapter.chapter_id) > 0)
    
    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        non_existent_path = os.path.join(self.temp_dir, "non_existent.txt")
        chapter = self.loader.load_from_txt(non_existent_path)
        
        self.assertIsNone(chapter)


if __name__ == "__main__":
    unittest.main()
