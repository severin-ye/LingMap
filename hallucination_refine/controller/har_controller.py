import argparse
import os
import json
from typing import List

from common.models.event import EventItem
from common.utils.json_loader import JsonLoader
from hallucination_refine.di.provider import provide_refiner


def refine_events(events_path: str, output_path: str, context_path: str = None) -> List[EventItem]:
    """
    对事件列表进行幻觉检测和修复
    
    Args:
        events_path: 事件JSON文件路径
        output_path: 输出JSON文件路径
        context_path: 上下文文件路径（可选）
        
    Returns:
        精修后的事件列表
    """
    # 加载事件
    with open(events_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)
        
    events = [EventItem.from_dict(event_data) for event_data in events_data]
    
    # 加载上下文（如果提供）
    context = None
    if context_path and os.path.exists(context_path):
        with open(context_path, 'r', encoding='utf-8') as f:
            context = f.read()
    
    # 获取精修器
    refiner = provide_refiner()
    
    # 精修事件
    print(f"对 {len(events)} 个事件进行幻觉检测和修复...")
    refined_events = refiner.refine(events, context)
    print(f"精修完成，共 {len(refined_events)} 个事件")
    
    # 保存结果
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    refined_events_dict = [event.to_dict() for event in refined_events]
    JsonLoader.save_json(refined_events_dict, output_path)
    print(f"精修后的事件已保存到: {output_path}")
    
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
