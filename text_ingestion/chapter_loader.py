import os
import re
from typing import List, Dict, Optional

from common.models.chapter import Chapter
from common.utils.text_splitter import TextSplitter


class ChapterLoader:
    """
    # [CN] 从文本文件加载小说章节并处理成标准格式
    # [EN] Load novel chapters from text files and process them into standard format
    """
    
    def __init__(self, segment_size: int = 800):
        """
        # [CN] 初始化章节加载器
        # [EN] Initialize chapter loader
        
        Args:
            segment_size: # [CN] 分段大小，每段的目标字符数 [EN] Segment size, target character count per segment
        """
        self.segment_size = segment_size
    
    @staticmethod
    def extract_chapter_info(text: str) -> Optional[Dict[str, str]]:
        """
        # [CN] 从文本中提取章节信息（章节号和标题）
        # [EN] Extract chapter information (chapter number and title) from text
        
        Args:
            text: # [CN] 章节文本 [EN] Chapter text
            
        Returns:
            # [CN] 包含章节ID和标题的字典，如果无法提取则返回None
            # [EN] Dictionary containing chapter ID and title, returns None if extraction fails
        """
        # [CN] 匹配章节标题，如【第十五章 聚灵丹】或 第一章 初入七玄门
        # [EN] Match chapter titles, e.g., 【第十五章 聚灵丹】or 第一章 初入七玄门
        pattern = r'[【]?第([^章]+)章\s*([^】\n]+)[】]?'
        match = re.search(pattern, text[:200])  # [CN] 只在开头部分查找 [EN] Search only in the beginning part
        
        if match:
            chapter_id = f"第{match.group(1)}章"
            title = match.group(2).strip()
            return {"chapter_id": chapter_id, "title": title}
        
        return None
    
    def load_from_txt(self, file_path: str) -> Optional[Chapter]:
        """
        # [CN] 从TXT文件加载章节内容
        # [EN] Load chapter content from TXT file
        
        Args:
            file_path: # [CN] TXT文件路径 [EN] TXT file path
            
        Returns:
            # [CN] 章节对象，如果加载失败则返回None
            # [EN] Chapter object, returns None if loading fails
        """
        if not os.path.exists(file_path):
            import logging
            logging.error(f"文件不存在: {file_path}")  # [CN] 文件不存在: {file_path} [EN] File does not exist: {file_path}
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # [CN] 提取章节信息
            # [EN] Extract chapter information
            chapter_info = self.extract_chapter_info(content)
            if not chapter_info:
                chapter_id = os.path.basename(file_path).replace('.txt', '')
                title = f"未命名章节_{chapter_id}"  # [CN] 未命名章节_{chapter_id} [EN] Unnamed_chapter_{chapter_id}
            else:
                chapter_id = chapter_info["chapter_id"]
                title = chapter_info["title"]
            
            # [CN] 分段
            # [EN] Segmentation
            segments = TextSplitter.split_chapter(content, self.segment_size)
            
            # [CN] 为每个segment添加chapter_id前缀
            # [EN] Add chapter_id prefix to each segment
            for i, seg in enumerate(segments):
                seg["seg_id"] = f"{chapter_id}-{seg['seg_id']}"
                
            return Chapter(
                chapter_id=chapter_id,
                title=title,
                content=content,
                segments=segments
            )
        
        except Exception as e:
            print(f"加载章节失败: {str(e)}")  # [CN] 加载章节失败: {str(e)} [EN] Failed to load chapter: {str(e)}
            return None
    
    def load_multiple_txt(self, directory: str, pattern: str = "*.txt") -> List[Chapter]:
        """
        # [CN] 批量加载TXT文件
        # [EN] Batch load TXT files
        
        Args:
            directory: # [CN] 目录路径 [EN] Directory path
            pattern: # [CN] 文件匹配模式 [EN] File matching pattern
            
        Returns:
            # [CN] 章节对象列表
            # [EN] List of chapter objects
        """
        import glob
        
        chapters = []
        file_paths = glob.glob(os.path.join(directory, pattern))
        
        for file_path in sorted(file_paths):
            chapter = self.load_from_txt(file_path)
            if chapter:
                chapters.append(chapter)
        
        return chapters
