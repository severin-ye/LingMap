import os
import re
from typing import List, Dict, Optional

from common.models.chapter import Chapter
from common.utils.text_splitter import TextSplitter


class ChapterLoader:
    """Load novel chapters from text files and process into standard format"""
    
    def __init__(self, segment_size: int = 800):
        """
        Initialize chapter loader
        
        Args:
            segment_size: Segment size, target character count per segment
        """
        self.segment_size = segment_size
    
    @staticmethod
    def extract_chapter_info(text: str) -> Optional[Dict[str, str]]:
        """
        Extract chapter information (chapter number and title) from text
        
        Args:
            text: Chapter text
            
        Returns:
            Dictionary containing chapter ID and title, returns None if unable to extract
        """
        # Match chapter titles like 【Chapter 15 Spirit Gathering Pill】 or Chapter 1 Enter Seven Mystery Gate
        pattern = r'[【]?第([^章]+)章\s*([^】\n]+)[】]?'
        match = re.search(pattern, text[:200])  # Only search at the beginning
        
        if match:
            chapter_id = f"第{match.group(1)}章"
            title = match.group(2).strip()
            return {"chapter_id": chapter_id, "title": title}
        
        return None
    
    def load_from_txt(self, file_path: str) -> Optional[Chapter]:
        """
        Load chapter content from TXT file
        
        Args:
            file_path: TXT file path
            
        Returns:
            Chapter object, returns None if loading fails
        """
        if not os.path.exists(file_path):
            import logging
            logging.error(f"File does not exist: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract chapter information
            chapter_info = self.extract_chapter_info(content)
            if not chapter_info:
                chapter_id = os.path.basename(file_path).replace('.txt', '')
                title = f"Unnamed_chapter_{chapter_id}"
            else:
                chapter_id = chapter_info["chapter_id"]
                title = chapter_info["title"]
            
            # Segment the text
            segments = TextSplitter.split_chapter(content, self.segment_size)
            
            # Add chapter_id prefix to each segment
            for i, seg in enumerate(segments):
                seg["seg_id"] = f"{chapter_id}-{seg['seg_id']}"
                
            return Chapter(
                chapter_id=chapter_id,
                title=title,
                content=content,
                segments=segments
            )
        
        except Exception as e:
            print(f"Failed to load chapter: {str(e)}")
            return None
    
    def load_multiple_txt(self, directory: str, pattern: str = "*.txt") -> List[Chapter]:
        """
        Batch load TXT files
        
        Args:
            directory: Directory path
            pattern: File matching pattern
            
        Returns:
            List of chapter objects
        """
        import glob
        
        chapters = []
        file_paths = glob.glob(os.path.join(directory, pattern))
        
        for file_path in sorted(file_paths):
            chapter = self.load_from_txt(file_path)
            if chapter:
                chapters.append(chapter)
        
        return chapters
