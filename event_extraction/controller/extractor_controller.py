import argparse
import os
import json
from typing import List

from common.models.chapter import Chapter
from common.models.event import EventItem
from common.utils.json_loader import JsonLoader
from common.utils.unified_id_processor import UnifiedIdProcessor
from event_extraction.di.provider import provide_extractor


def extract_events_from_chapter(chapter_path: str, output_path: str) -> List[EventItem]:
    """
    # [CN] 从章节JSON文件中抽取事件并保存结果
    # [EN] Extract events from chapter JSON file and save results
    
    Args:
        # [CN] chapter_path: 章节JSON文件路径
        # [EN] chapter_path: Chapter JSON file path
        # [CN] output_path: 输出JSON文件路径
        # [EN] output_path: Output JSON file path
        
    Returns:
        # [CN] 抽取的事件列表
        # [EN] List of extracted events
    """
    # [CN] 加载章节
    # [EN] Load chapter
    chapter = JsonLoader.load_chapter_json(chapter_path)
    
    # [CN] 获取抽取器
    # [EN] Get extractor
    extractor = provide_extractor()
    
    # [CN] 抽取事件
    # [EN] Extract events
    print(f"# [CN] 从章节 {chapter.chapter_id} 抽取事件...")
    print(f"# [EN] Extracting events from chapter {chapter.chapter_id}...")
    events = extractor.extract(chapter)
    print(f"# [CN] 成功抽取 {len(events)} 个事件")
    print(f"# [EN] Successfully extracted {len(events)} events")
    
    # [CN] 注意：事件ID唯一性已在抽取服务中处理，这里不再重复处理
    # [EN] Note: Event ID uniqueness is already handled in extraction service, no need to process again here
    # [CN] 检查事件ID是否唯一（仅作验证）
    # [EN] Check if event IDs are unique (for verification only)
    event_ids = [e.event_id for e in events]
    unique_ids = set(event_ids)
    if len(event_ids) != len(unique_ids):
        print(f"# [CN] 警告：抽取的事件中存在重复ID，原有 {len(events)} 个事件，唯一ID仅有 {len(unique_ids)} 个")
        print(f"# [EN] Warning: Duplicate IDs found in extracted events, original {len(events)} events, only {len(unique_ids)} unique IDs")
    
    # [CN] 保存结果
    # [EN] Save results
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    events_dict = [event.to_dict() for event in events]
    JsonLoader.save_json(events_dict, output_path)
    print(f"# [CN] 事件已保存到: {output_path}")
    print(f"# [EN] Events saved to: {output_path}")
    
    return events


def main():
    """
    # [CN] EVENT_EXTRACTION 模块执行入口
    # [EN] EVENT_EXTRACTION module execution entry point
    """
    parser = argparse.ArgumentParser(description="# [CN] 从章节中抽取事件 # [EN] Extract events from chapters")
    parser.add_argument("--input", "-i", required=True, help="# [CN] 输入章节JSON文件或目录 # [EN] Input chapter JSON file or directory")
    parser.add_argument("--output", "-o", required=True, help="输出事件JSON文件或目录")
    parser.add_argument("--batch", "-b", action="store_true", help="批处理模式")
    
    args = parser.parse_args()
    
    if args.batch:
        # 批处理模式
        if not os.path.isdir(args.input):
            print(f"错误: 输入路径 {args.input} 不是一个目录")
            return
        
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        
        # 获取所有JSON文件
        import glob
        chapter_files = glob.glob(os.path.join(args.input, "*.json"))
        
        total_events = []
        for chapter_file in chapter_files:
            filename = os.path.basename(chapter_file)
            output_file = os.path.join(args.output, filename)
            events = extract_events_from_chapter(chapter_file, output_file)
            total_events.extend(events)
        
        # 检查跨章节事件ID是否唯一（仅作验证）
        event_ids = [e.event_id for e in total_events]
        unique_ids = set(event_ids)
        if len(event_ids) != len(unique_ids):
            print(f"警告：跨章节合并后存在重复ID，原有 {len(total_events)} 个事件，唯一ID仅有 {len(unique_ids)} 个")
            
        # 在合并输出之前，确保事件ID的唯一性（这是多章节合并处理，较为特殊）
        # 仅在这个跨章节合并场景才需要额外处理
        original_count = len(total_events)
        total_events = UnifiedIdProcessor.ensure_unique_event_ids(total_events)
        if len(total_events) != original_count:
            print(f"合并去重处理：从 {original_count} 个事件减少到 {len(total_events)} 个唯一事件")
        else:
            print(f"所有跨章节事件ID均唯一，共 {len(total_events)} 个事件")
        
        # 保存所有事件到一个合并的文件
        all_events_path = os.path.join(args.output, "all_events.json")
        all_events_dict = [event.to_dict() for event in total_events]
        JsonLoader.save_json(all_events_dict, all_events_path)
        print(f"所有事件已合并保存到: {all_events_path}")
    else:
        # 单文件模式
        extract_events_from_chapter(args.input, args.output)


if __name__ == "__main__":
    main()
