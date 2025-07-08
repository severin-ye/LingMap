#!/usr/bin/env python3
"""
统一的事件抽取集成测试脚本

合并自 test_event_extraction.py 和 test_event_extraction_scripts.py，
用于测试事件抽取服务的完整功能，包括文本加载、事件抽取和结果验证。
"""

import os
import sys
import json
from pathlib import Path
import pytest

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from common.models.chapter import Chapter
from common.utils.path_utils import get_novel_path
from common.utils.enhanced_logger import EnhancedLogger
from event_extraction.di.provider import provide_extractor
from event_extraction.service.enhanced_extractor_service import EnhancedEventExtractor

logger = EnhancedLogger("event_extraction_test", log_level="DEBUG")

def load_test_chapter():
    """加载测试章节数据"""
    test_novel_path = get_novel_path("test.txt")
    if os.path.exists(test_novel_path):
        with open(test_novel_path, 'r', encoding='utf-8') as f:
            content = f.read()
        title = "测试章节"
        chapter_id = "test"
    else:
        chapter_path = get_novel_path("1.txt")
        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read()
        title = "第一章"
        chapter_id = "1"
    return Chapter(chapter_id=chapter_id, title=title, content=content)

def extract_events(chapter: Chapter):
    """调用事件抽取服务"""
    extractor = provide_extractor()
    result = extractor.extract(chapter)
    return result

def test_event_extraction_integration():
    """集成测试：事件抽取主流程"""
    chapter = load_test_chapter()
    events = extract_events(chapter)
    assert events is not None, "事件抽取结果为空"
    assert isinstance(events, list), "事件抽取结果应为列表"
    assert len(events) > 0, "未抽取到任何事件"
    logger.info(f"抽取到 {len(events)} 个事件")

if __name__ == "__main__":
    chapter = load_test_chapter()
    events = extract_events(chapter)
    print(f"抽取到 {len(events)} 个事件")
    for i, event in enumerate(events[:3]):  # 只显示前3个事件
        print(f"事件 {i+1}: {event.description[:100]}...")
