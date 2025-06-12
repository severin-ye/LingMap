#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试候选事件对生成器的优化效果
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from common.models.event import EventItem
from causal_linking.di.provider import provide_linker
from causal_linking.service.candidate_generator import CandidateGenerator


def test_candidate_generation():
    """测试候选事件对生成效果"""
    print("=== 候选事件对生成优化测试 ===")
    
    # 加载事件数据
    try:
        event_file = os.path.join(project_root, 'debug/extracted_events.json')
        with open(event_file, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        events = [EventItem.from_dict(event_data) for event_data in events_data]
        print(f"成功加载 {len(events)} 个事件")
    except Exception as e:
        print(f"加载事件失败: {e}")
        return
    
    # 测试不同配置
    configs = [
        {
            "name": "高限制",
            "params": {
                "max_events_per_chapter": 10,
                "min_entity_support": 5,  # 高支持度
                "max_chapter_span": 5,   # 小跨度
                "max_candidate_pairs": 50,  # 少候选对
                "max_pairs_per_entity": 5   # 每实体少对
            }
        },
        {
            "name": "中限制",
            "params": {
                "max_events_per_chapter": 15,
                "min_entity_support": 3,   # 中支持度
                "max_chapter_span": 10,
                "max_candidate_pairs": 100,
                "max_pairs_per_entity": 10
            }
        },
        {
            "name": "低限制",
            "params": {
                "max_events_per_chapter": 20,
                "min_entity_support": 2,   # 低支持度
                "max_chapter_span": 15,
                "max_candidate_pairs": 300,
                "max_pairs_per_entity": 20  # 每实体多对
            }
        }
    ]
    
    # 输出结果到文件
    result_file = os.path.join(project_root, f'logs/candidate_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    with open(result_file, 'w', encoding='utf-8') as log:
        log.write(f"候选事件对优化测试结果 - {datetime.now()}\n")
        log.write(f"事件总数: {len(events)}\n\n")
        
        for config in configs:
            print(f"\n测试配置: {config['name']}")
            log.write(f"=== 配置: {config['name']} ===\n")
            
            # 创建候选生成器
            generator = CandidateGenerator(**config['params'])
            
            # 生成候选事件对
            try:
                candidate_pairs = generator.generate_candidates(events)
                
                # 输出结果
                result = (
                    f"配置: {config['name']}\n"
                    f"参数: {config['params']}\n"
                    f"生成候选事件对数量: {len(candidate_pairs)}\n"
                    f"相对于全配对 ({len(events) * (len(events) - 1) // 2}) 的比例: "
                    f"{len(candidate_pairs) / (len(events) * (len(events) - 1) // 2) * 100:.2f}%\n"
                )
                print(result)
                log.write(result + "\n")
                
            except Exception as e:
                error_msg = f"测试失败: {e}"
                print(error_msg)
                log.write(error_msg + "\n")
    
    print(f"测试结果已保存到: {result_file}")


if __name__ == "__main__":
    try:
        test_candidate_generation()
    except Exception as e:
        import traceback
        print(f"测试失败: {e}")
        traceback.print_exc()
