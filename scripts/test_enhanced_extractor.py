#!/usr/bin/env python3
"""
增强型事件抽取测试脚本

用于测试增强型事件抽取器的功能和诊断问题
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到sys.path
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from common.models.chapter import Chapter
from common.utils.path_utils import get_novel_path, get_project_root
from event_extraction.service.enhanced_extractor_service import EnhancedEventExtractor

def load_test_chapter():
    """加载测试章节数据"""
    print("加载测试章节...")
    
    # 尝试加载测试文件
    test_novel_path = get_novel_path("test.txt")
    if os.path.exists(test_novel_path):
        with open(test_novel_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✓ 从测试文件加载了 {len(content)} 个字符")
    else:
        # 如果测试文件不存在，使用第1章
        chapter_path = get_novel_path("1.txt")
        if not os.path.exists(chapter_path):
            print(f"❌ 未找到任何小说文件")
            return None
            
        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read(2000)  # 只读取前2000个字符用于测试
            
        print(f"✓ 从章节1加载了 {len(content)} 个字符")
    
    # 创建Chapter对象
    chapter = Chapter(
        chapter_id="第一章",
        title="第一章",
        content=content,
        segments=None  # 让抽取器自动分段
    )
    
    return chapter

def test_enhanced_extractor():
    """测试增强型事件抽取器"""
    print("="*60)
    print("增强型事件抽取器测试")
    print("="*60)
    
    # 创建调试目录
    debug_dir = project_root / "debug"
    debug_dir.mkdir(exist_ok=True)
    
    # 从环境变量获取API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        # 尝试从.env文件加载
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("DEEPSEEK_API_KEY")
        except ImportError:
            pass
            
    if not api_key:
        print("❌ 未找到DEEPSEEK_API_KEY环境变量，请确保.env文件中包含此密钥")
        return
    
    print(f"✓ 找到API密钥: {api_key[:5]}...{api_key[-3:]}")
    
    # 加载测试章节
    chapter = load_test_chapter()
    if not chapter:
        return
    
    # 创建增强型事件抽取器
    extractor = EnhancedEventExtractor(
        model="deepseek-chat",  # 使用DeepSeek模型进行测试
        api_key=api_key,
        provider="deepseek",
        max_workers=2,  # 减少并发以便于调试
        debug_mode=True
    )
    
    print("\n开始事件抽取...")
    events = extractor.extract(chapter)
    
    if events:
        print(f"\n✓ 成功抽取 {len(events)} 个事件:")
        for i, event in enumerate(events, 1):
            print(f"  事件 {i}:")
            print(f"    ID: {event.event_id}")
            print(f"    描述: {event.description}")
            print(f"    角色: {', '.join(event.characters) if event.characters else '无'}")
            print(f"    宝物: {', '.join(event.treasures) if event.treasures else '无'}")
            print()
            
        # 保存事件到文件
        events_file = debug_dir / "extracted_events.json"
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump([event.to_dict() for event in events], f, ensure_ascii=False, indent=2)
            
        print(f"事件已保存到 {events_file}")
    else:
        print("\n❌ 未能抽取任何事件，请检查debug目录中的详细日志")

if __name__ == "__main__":
    test_enhanced_extractor()
