import argparse
import os
import json
from typing import List

from common.models.event import EventItem
from common.utils.json_loader import JsonLoader
from hallucination_refine.di.provider import provide_refiner


def refine_events(events_path: str, output_path: str, context_path: str = "") -> List[EventItem]:
    """
    # [CN] 对事件列表进行幻觉检测和修复
    # [EN] Perform hallucination detection and refinement on event list
    
    Args:
        # [CN] events_path: 事件JSON文件路径
        # [EN] events_path: Path to events JSON file
        # [CN] output_path: 输出JSON文件路径
        # [EN] output_path: Path to output JSON file
        # [CN] context_path: 上下文文件路径（可选）
        # [EN] context_path: Context file path (optional)
        
    Returns:
        # [CN] 精修后的事件列表
        # [EN] Refined event list
    """
    # [CN] 加载事件
    # [EN] Load events
    with open(events_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)
        
    events = [EventItem.from_dict(event_data) for event_data in events_data]
    
    # [CN] 加载上下文（如果提供）
    # [EN] Load context (if provided)
    context = ""
    if context_path and os.path.exists(context_path):
        with open(context_path, 'r', encoding='utf-8') as f:
            context = f.read()
    
    # [CN] 获取精修器
    # [EN] Get refiner
    refiner = provide_refiner()
    
    # [CN] 精修事件
    # [EN] Refine events
    # [CN] 对 {len(events)} 个事件进行幻觉检测和修复...
    # [EN] Performing hallucination detection and refinement on {len(events)} events...
    print(f"# [CN] 对 {len(events)} 个事件进行幻觉检测和修复...")
    print(f"# [EN] Performing hallucination detection and refinement on {len(events)} events...")
    refined_events = refiner.refine(events, context)
    # [CN] 精修完成，共 {len(refined_events)} 个事件
    # [EN] Refinement completed, total {len(refined_events)} events
    print(f"# [CN] 精修完成，共 {len(refined_events)} 个事件")
    print(f"# [EN] Refinement completed, total {len(refined_events)} events")
    
    # [CN] 保存结果
    # [EN] Save results
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    refined_events_dict = [event.to_dict() for event in refined_events]
    JsonLoader.save_json(refined_events_dict, output_path)
    # [CN] 精修后的事件已保存到
    # [EN] Refined events saved to
    print(f"# [CN] 精修后的事件已保存到: {output_path}")
    print(f"# [EN] Refined events saved to: {output_path}")
    
    return refined_events


def main():
    """HALLUCINATION_REFINE 模块执行入口"""
    parser = argparse.ArgumentParser(description="对事件进行幻觉检测和修复")
    parser.add_argument("--input", "-i", required=True, help="输入事件JSON文件")
    parser.add_argument("--output", "-o", required=True, help="输出精修后的事件JSON文件")
    parser.add_argument("--context", "-c", help="支持精修的上下文文件（可选）")
    
    args = parser.parse_args()
    
    refine_events(args.input, args.output, args.context)


if __name__ == "__main__":
    main()
