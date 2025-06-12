#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化的候选事件对生成算法
"""

import os
import sys
import json
import time
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from common.models.event import EventItem
from causal_linking.service.candidate_generator import CandidateGenerator


def test_candidate_generation():
    """测试优化后的候选事件对生成算法"""
    print("=== 智能连接生成优化测试 ===")
    
    # 加载测试事件数据
    try:
        event_file = os.path.join(project_root, 'debug/extracted_events.json')
        with open(event_file, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        events = [EventItem.from_dict(event_data) for event_data in events_data]
        print(f"成功加载 {len(events)} 个事件")
    except Exception as e:
        print(f"加载事件失败: {e}")
        return
    
    # 计算全配对的总数，用于比较
    total_events = len(events)
    all_possible_pairs = (total_events * (total_events - 1)) // 2
    print(f"全组合配对数量: {all_possible_pairs} 对")
    
    # 使用不同的配置测试
    configurations = [
        {
            "name": "平衡模式",
            "params": {
                "max_events_per_chapter": 50,
                "min_entity_support": 3,
                "max_chapter_span": 10,
                "max_candidate_pairs": 150,
                "max_pairs_per_entity": 15,
                "connection_density": 0.2
            }
        },
        {
            "name": "高密度模式",
            "params": {
                "max_events_per_chapter": 100,
                "min_entity_support": 2,
                "max_chapter_span": 15,
                "max_candidate_pairs": 300,
                "max_pairs_per_entity": 25,
                "connection_density": 0.4
            }
        },
        {
            "name": "低密度模式",
            "params": {
                "max_events_per_chapter": 30,
                "min_entity_support": 5,
                "max_chapter_span": 5,
                "max_candidate_pairs": 80,
                "max_pairs_per_entity": 8,
                "connection_density": 0.1
            }
        }
    ]
    
    results = []
    
    for config in configurations:
        print(f"\n测试配置: {config['name']}")
        generator = CandidateGenerator(**config['params'])
        
        start_time = time.time()
        candidate_pairs = generator.generate_candidates(events)
        elapsed = time.time() - start_time
        
        # 计算相对于全配对的比例
        percentage = (len(candidate_pairs) / all_possible_pairs) * 100 if all_possible_pairs > 0 else 0
        
        result = {
            "config_name": config['name'],
            "params": config['params'],
            "pairs_count": len(candidate_pairs),
            "percentage": percentage,
            "elapsed_time": elapsed
        }
        results.append(result)
        
        print(f"配置: {config['name']}")
        print(f"参数: {config['params']}")
        print(f"生成候选事件对数量: {len(candidate_pairs)}")
        print(f"相对于全配对 ({all_possible_pairs}) 的比例: {percentage:.2f}%")
        print(f"耗时: {elapsed:.2f} 秒")
    
    # 保存测试结果到日志
    log_file = os.path.join(project_root, 'logs', f'candidate_smart_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"智能连接生成优化测试 - {datetime.now()}\n")
        f.write(f"事件总数: {len(events)}\n")
        f.write(f"全组合配对数量: {all_possible_pairs}\n\n")
        
        for result in results:
            f.write(f"配置: {result['config_name']}\n")
            f.write(f"参数: {result['params']}\n")
            f.write(f"生成候选事件对数量: {result['pairs_count']}\n")
            f.write(f"相对于全配对的比例: {result['percentage']:.2f}%\n")
            f.write(f"耗时: {result['elapsed_time']:.2f} 秒\n\n")
    
    print(f"\n测试结果已保存到: {log_file}")


if __name__ == "__main__":
    try:
        test_candidate_generation()
    except Exception as e:
        import traceback
        print(f"测试执行失败: {e}")
        traceback.print_exc()
