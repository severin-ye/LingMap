from typing import List, Dict
import re


class TextSplitter:
    """Text segmentation tool for splitting chapter text into multiple paragraphs"""
    
    @staticmethod
    def split_by_paragraphs(text: str) -> List[str]:
        """
        Split text by paragraphs (separated by empty lines)
        
        Args:
            text: Input text
            
        Returns:
            List of paragraphs
        """
        paragraphs = [p.strip() for p in text.split('\n\n')]
        return [p for p in paragraphs if p]  # Filter empty paragraphs
    
    @staticmethod
    def split_by_sentences(text: str) -> List[str]:
        """
        Split text by sentences (separated by periods, exclamation marks, question marks)
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Chinese sentence splitting regex
        pattern = r'([^。！？]+[。！？])'
        sentences = re.findall(pattern, text)
        # Process sentences that may not end with punctuation
        if text and not text.endswith(('。', '！', '？')):
            last_sentence = text.split('。')[-1].split('！')[-1].split('？')[-1].strip()
            if last_sentence:
                sentences.append(last_sentence)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def split_chapter(chapter_text: str, seg_size: int = 500) -> List[Dict]:
        """
        Split chapter content into segments suitable for LLM processing
        
        Args:
            chapter_text: Chapter text
            seg_size: Target segment length
            
        Returns:
            List of segmented chapter fragments, each segment is a dictionary {"seg_id": "xx-1", "text": "..."}
        """
        paragraphs = TextSplitter.split_by_paragraphs(chapter_text)
        
        segments = []
        current_segment = []
        current_length = 0
        seg_index = 1
        
        for para in paragraphs:
            para_length = len(para)
            
            # If current paragraph plus existing content would exceed target length and current segment is not empty, save current segment and start new segment
            if current_length + para_length > seg_size and current_segment:
                segment_text = '\n\n'.join(current_segment)
                segments.append({
                    "seg_id": f"{seg_index}",
                    "text": segment_text
                })
                current_segment = [para]
                current_length = para_length
                seg_index += 1
            else:
                current_segment.append(para)
                current_length += para_length
        
        # Process remaining content
        if current_segment:
            segment_text = '\n\n'.join(current_segment)
            segments.append({
                "seg_id": f"{seg_index}",
                "text": segment_text
            })
        
        return segments
