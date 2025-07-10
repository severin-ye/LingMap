#!/usr/bin/env python3
"""
完整流程测试脚本

用于测试整个系统的工作流程，包括事件抽取、幻觉消除、因果链接和图谱生成
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from common.utils.path_utils import get_project_root, get_novel_path, get_output_path
from common.utils.enhanced_logger import EnhancedLogger
from common.models.chapter import Chapter

from text_ingestion.chapter_loader import ChapterLoader
from event_extraction.di.provider import provide_extractor
from hallucination_refine.di.provider import provide_refiner
from causal_linking.di.provider import provide_linker
from graph_builder.service.mermaid_renderer import MermaidRenderer

# 创建日志记录器
logger = EnhancedLogger("complete_test", log_level="DEBUG")

def main():
    """运行完整流程测试"""
    print("="*80)
    print("《凡人修仙传》因果事件图谱生成系统 - 完整流程测试")
    print("="*80)
    
    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = get_output_path(f"test_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"输出目录: {output_dir}")
    
    # 加载章节
    chapter_path = get_novel_path("test.txt")
    if not os.path.exists(chapter_path):
        print(f"错误: 未找到章节文件: {chapter_path}")
        return
    
    print("\n1. 加载章节数据...")
    loader = ChapterLoader()
    with open(chapter_path, 'r', encoding='utf-8') as f:
        content = f.read()
    chapter = Chapter(chapter_id="第一章", title="第一章", content=content)
    print(f"  ✓ 成功加载章节: {chapter.title}, {len(chapter.content)} 字符")
    
    # 事件抽取
    print("\n2. 提取事件...")
    extractor = provide_extractor()
    events = extractor.extract(chapter)
    
    if not events:
        print("  ❌ 事件抽取失败，未能提取任何事件")
        return
    
    print(f"  ✓ 成功抽取 {len(events)} 个事件")
    
    # 保存原始事件
    events_path = os.path.join(temp_dir, f"{chapter.chapter_id}_events.json")
    with open(events_path, 'w', encoding='utf-8') as f:
        json.dump([event.to_dict() for event in events], f, ensure_ascii=False, indent=2)
    
    print(f"  原始事件已保存到: {events_path}")
    
    # 幻觉消除
    print("\n3. 幻觉消除...")
    refiner = provide_refiner()
    refined_events = refiner.refine(events, chapter.content)
    
    # 保存精炼后的事件
    refined_events_path = os.path.join(temp_dir, f"{chapter.chapter_id}_refined_events.json")
    with open(refined_events_path, 'w', encoding='utf-8') as f:
        json.dump([event.to_dict() for event in refined_events], f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 幻觉消除完成，剩余 {len(refined_events)} 个事件")
    print(f"  精炼后的事件已保存到: {refined_events_path}")
    
    # 因果链接
    print("\n4. 生成因果链接...")
    linker = provide_linker()
    causal_links = linker.link_events(refined_events)
    
    # 保存因果链接
    causal_path = os.path.join(temp_dir, f"{chapter.chapter_id}_causal.json")
    with open(causal_path, 'w', encoding='utf-8') as f:
        json.dump([link.to_dict() for link in causal_links], f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 成功生成 {len(causal_links)} 个因果链接")
    print(f"  因果链接已保存到: {causal_path}")
    
    # 生成图谱
    print("\n5. 生成图谱...")
    renderer = MermaidRenderer()
    graph = renderer.render(refined_events, causal_links)
    
    # 保存图谱
    graph_path = os.path.join(output_dir, f"{chapter.chapter_id}_graph.mmd")
    with open(graph_path, 'w', encoding='utf-8') as f:
        f.write("```mermaid\n")
        f.write(graph)
        f.write("\n```")
    
    print(f"  ✓ 图谱已生成")
    print(f"  图谱已保存到: {graph_path}")
    
    print("\n完整流程测试完成！")
    print(f"所有输出文件位于: {output_dir}")

if __name__ == "__main__":
    main()
