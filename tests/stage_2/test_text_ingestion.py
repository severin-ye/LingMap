#!/usr/bin/env python3
"""
文本摄入模块测试

本文件包含对文本摄入模块的测试用例，主要测试：
1. ChapterLoader 是否能正确加载小说文本
2. 文本分割功能是否正常工作
3. 章节信息提取是否准确
"""

import unittest
import os
import tempfile
import shutil
from text_ingestion.chapter_loader import ChapterLoader
from common.models.chapter import Chapter


class TestChapterLoader(unittest.TestCase):
    """测试 ChapterLoader 类的功能"""
    
    def setUp(self):
        """测试前的准备工作，创建临时文本文件"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, "test_novel.txt")
        
        # 创建测试用的小说文本
        test_content = """# 第一章 山村少年

韩立，一个山村少年，自小喜欢炼药。
他天资普通，但勤奋好学。

# 第二章 炼药学徒

韩立成为了七玄门的学徒，开始了修仙之路。
他遇到了南宫婉，一个美丽的女修士。
"""
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 实例化章节加载器
        self.loader = ChapterLoader(segment_size=50)
    
    def tearDown(self):
        """测试后的清理工作"""
        shutil.rmtree(self.temp_dir)
    
    def test_load_from_txt(self):
        """测试从文本文件加载章节"""
        chapter = self.loader.load_from_txt(self.test_file_path)
        
        self.assertIsInstance(chapter, Chapter)
        self.assertEqual(chapter.chapter_id, "第一章")  # 根据文本内容提取的章节ID
        self.assertEqual(chapter.title, "山村少年")  # 根据文本内容提取的章节标题
        self.assertEqual(len(chapter.segments), 2)  # 实际上我们的文本只会被分成2段
    
    def test_chapter_segmentation(self):
        """测试章节分段功能"""
        chapter = self.loader.load_from_txt(self.test_file_path)
        
        # 检查分段是否包含正确的内容
        self.assertIn("山村少年", chapter.segments[0]["text"])
        self.assertIn("韩立", chapter.segments[0]["text"])
        # 修改期望内容在正确的段落中
        self.assertIn("七玄门", chapter.segments[1]["text"])
        self.assertIn("南宫婉", chapter.segments[1]["text"])
    
    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        non_existent_path = os.path.join(self.temp_dir, "non_existent.txt")
        chapter = self.loader.load_from_txt(non_existent_path)
        
        self.assertIsNone(chapter)


if __name__ == "__main__":
    unittest.main()
