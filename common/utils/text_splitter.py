from typing import List, Dict
import re


class TextSplitter:
    """文本分段工具，将章节文本切分为多个段落"""
    
    @staticmethod
    def split_by_paragraphs(text: str) -> List[str]:
        """
        按段落分割文本（以空行为分隔）
        
        Args:
            text: 输入文本
            
        Returns:
            段落列表
        """
        paragraphs = [p.strip() for p in text.split('\n\n')]
        return [p for p in paragraphs if p]  # 过滤空段落
    
    @staticmethod
    def split_by_sentences(text: str) -> List[str]:
        """
        按句子分割文本（以句号、叹号、问号为分隔）
        
        Args:
            text: 输入文本
            
        Returns:
            句子列表
        """
        # 中文分句正则
        pattern = r'([^。！？]+[。！？])'
        sentences = re.findall(pattern, text)
        # 处理末尾可能没有标点的句子
        if text and not text.endswith(('。', '！', '？')):
            last_sentence = text.split('。')[-1].split('！')[-1].split('？')[-1].strip()
            if last_sentence:
                sentences.append(last_sentence)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def split_chapter(chapter_text: str, seg_size: int = 500) -> List[Dict]:
        """
        将章节内容分割为适合LLM处理的片段
        
        Args:
            chapter_text: 章节文本
            seg_size: 目标片段长度
            
        Returns:
            分段后的章节片段列表，每个片段为字典 {"seg_id": "xx-1", "text": "..."}
        """
        paragraphs = TextSplitter.split_by_paragraphs(chapter_text)
        
        segments = []
        current_segment = []
        current_length = 0
        seg_index = 1
        
        for para in paragraphs:
            para_length = len(para)
            
            # 如果当前段落加上已有内容会超出目标长度且当前段不为空，则保存当前段并开始新段
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
        
        # 处理剩余内容
        if current_segment:
            segment_text = '\n\n'.join(current_segment)
            segments.append({
                "seg_id": f"{seg_index}",
                "text": segment_text
            })
        
        return segments
