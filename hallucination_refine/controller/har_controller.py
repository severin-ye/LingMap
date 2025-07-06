import argparse
import os
import json
from typing import List

from common.models.event import EventItem
from common.utils.json_loader import JsonLoader
from hallucination_refine.di.provider import provide_refiner


def refine_events(events_path: str, output_path: str, context_path: str = "") -> List[EventItem]:
    """
 forevent列表performhallucinationdetectionandrepair
    
    Args:
 events_path: eventJSONfile路径
 output_path: OutputJSONfile路径
 context_path: contextfile路径（optional）
        
    Returns:
 refinededevent列表
    """
    # LoadEvent
    with open(events_path, 'r', encoding='utf-8') as f:
        events_data = json.load(f)
        
    events = [EventItem.from_dict(event_data) for event_data in events_data]
    
 # Loadcontext（IfProvide）
    context = ""
    if context_path and os.path.exists(context_path):
        with open(context_path, 'r', encoding='utf-8') as f:
            context = f.read()
    
    # getrefiner
    refiner = provide_refiner()
    
 # refinedEvent
 print(f"for {len(events)} 个eventperformhallucinationdetectionandrepair...")
    refined_events = refiner.refine(events, context)
 print(f"refined完成，共 {len(refined_events)} 个event")
    
    # SaveResult
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    refined_events_dict = [event.to_dict() for event in refined_events]
    JsonLoader.save_json(refined_events_dict, output_path)
 print(f"refinededeventalready保存到: {output_path}")
    
    return refined_events


def main():
 """HALLUCINATION_REFINE moduleExecute入口"""
 parser = argparse.ArgumentParser(description="foreventperformhallucinationdetectionandrepair")
 parser.add_argument("--input", "-i", required=True, help="InputeventJSONfile")
 parser.add_argument("--output", "-o", required=True, help="OutputrefinededeventJSONfile")
 parser.add_argument("--context", "-c", help="supportrefinedcontextfile（optional）")
    
    args = parser.parse_args()
    
    refine_events(args.input, args.output, args.context)


if __name__ == "__main__":
    main()
