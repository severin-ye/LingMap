#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的因果链接流程
"""

import os
import sys
import json
import time
from datetime import datetime

# TODO: Translate - Add project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from common.models.event import EventItem
from causal_linking.di.provider import provide_linker


def test_causal_linking():
    """测试优化后的因果链接流程"""
    print("=== 优化后因果链接测试 ===")
    start_time = time.time()
    
    # TODO: Translate - SetTest参数
    os.environ["MAX_EVENTS_PER_CHAPTER"] = "15"
    os.environ["MIN_ENTITY_SUPPORT"] = "3"
    os.environ["MAX_CANDIDATE_PAIRS"] = "100"
    
    # TODO: Translate - Loadevent数据
    try:
        event_file = os.path.join(project_root, 'debug/extracted_events.json')
        with open(event_file, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        events = [EventItem.from_dict(event_data) for event_data in events_data]
        print(f"成功加载 {len(events)} 个事件")
    except Exception as e:
        print(f"加载事件失败: {e}")
        return
    
    # TODO: Translate - Createcausallinking器
    try:
        linker = provide_linker(use_optimized=True)
        print("成功创建因果链接器")
    except Exception as e:
        print(f"创建链接器失败: {e}")
        return
    
    # Executecausallinking
    try:
        print("开始执行因果链接...")
        edges = linker.link_events(events)
        print(f"发现 {len(edges)} 个因果关系")
    except Exception as e:
        print(f"因果链接失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # TODO: Translate - Build有向无环图
    try:
        print("构建有向无环图...")
        events, dag_edges = linker.build_dag(events, edges)
        print(f"DAG构建完成，保留 {len(dag_edges)} 条边")
    except Exception as e:
        print(f"构建DAG失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # TODO: Translate - 计算总Execute时间
    elapsed = time.time() - start_time
    print(f"总耗时: {elapsed:.2f} 秒")
    
    # SaveOutput
    try:
        output_dir = os.path.join(project_root, 'output', f'optimized_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        os.makedirs(output_dir, exist_ok=True)
        
        # TODO: Translate - Savecausal关系
        output_file = os.path.join(output_dir, 'causal_relations.json')
        output_data = {
            "nodes": [event.to_dict() for event in events],
            "edges": [edge.to_dict() for edge in dag_edges]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print(f"结果已保存到: {output_file}")
        
        # TODO: Translate - SaveTest信息
        info_file = os.path.join(output_dir, 'test_info.txt')
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"优化后因果链接测试结果 - {datetime.now()}\n")
            f.write(f"事件总数: {len(events)}\n")
            f.write(f"发现因果关系数: {len(edges)}\n")
            f.write(f"DAG边数: {len(dag_edges)}\n")
            f.write(f"总耗时: {elapsed:.2f} 秒\n")
        
        print(f"测试信息已保存到: {info_file}")
    except Exception as e:
        print(f"保存结果失败: {e}")


if __name__ == "__main__":
    try:
        test_causal_linking()
    except Exception as e:
        import traceback
        print(f"测试执行失败: {e}")
        traceback.print_exc()
