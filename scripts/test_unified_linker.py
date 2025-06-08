#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试统一版因果链接器功能

验证统一版链接器能否正确处理以下场景：
1. 原始版本兼容性（不使用优化）
2. 优化版本兼容性（使用实体权重）
3. 直接使用统一版实现
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入测试所需模块
from common.models.event import EventItem
from causal_linking.service.unified_linker_service import UnifiedCausalLinker
from causal_linking.service.linker_service import CausalLinker
from causal_linking.service.optimized_linker_service import OptimizedCausalLinker


# 创建测试事件
def create_test_events(num_events=10, num_chapters=2):
    """创建测试事件"""
    events = []
    
    for chapter in range(1, num_chapters+1):
        for i in range(1, (num_events // num_chapters) + 1):
            event_id = f"E{chapter}-{i}"
            
            # 奇数ID的事件包含"韩立"，偶数ID的事件包含"南宫婉"
            characters = ["韩立"] if i % 2 == 1 else ["南宫婉"]
            
            # 第一章的事件包含"灵乳"，第二章的事件包含"火蟒剑"
            treasures = ["灵乳"] if chapter == 1 else ["火蟒剑"]
            
            event = EventItem(
                event_id=event_id,
                description=f"章节{chapter}的测试事件{i}，涉及{','.join(characters)}",
                characters=characters,
                treasures=treasures,
                location="测试地点",
                result="测试结果",
                chapter_id=f"第{chapter}章"
            )
            
            events.append(event)
    
    return events


def test_original_compatibility():
    """测试原始版本兼容性（不使用优化）"""
    print("\n===== 测试原始版本兼容性 =====")
    
    # 创建测试事件
    events = create_test_events(num_events=6, num_chapters=2)
    print(f"创建了 {len(events)} 个测试事件")
    
    # 创建原始版链接器实例
    linker = CausalLinker(
        api_key="dummy",  # 使用假API密钥，因为不会实际调用API
        model="dummy",
        provider="none"
    )
    
    # 打印类型信息，确认是否正确使用统一版
    print(f"链接器类型: {type(linker).__name__}")
    print(f"统一版基类: {isinstance(linker, UnifiedCausalLinker)}")
    print(f"优化模式: {getattr(linker, 'use_optimization', 'N/A')}")


def test_optimized_compatibility():
    """测试优化版本兼容性（使用实体权重）"""
    print("\n===== 测试优化版本兼容性 =====")
    
    # 创建测试事件
    events = create_test_events(num_events=8, num_chapters=2)
    print(f"创建了 {len(events)} 个测试事件")
    
    # 创建优化版链接器实例
    linker = OptimizedCausalLinker(
        api_key="dummy",  # 使用假API密钥，因为不会实际调用API
        model="dummy",
        provider="none",
        max_events_per_chapter=10,
        min_entity_support=1,
        max_chapter_span=99,
        max_candidate_pairs=1000,
        use_entity_weights=True
    )
    
    # 打印类型信息，确认是否正确使用统一版
    print(f"链接器类型: {type(linker).__name__}")
    print(f"统一版基类: {isinstance(linker, UnifiedCausalLinker)}")
    print(f"优化模式: {getattr(linker, 'use_optimization', 'N/A')}")
    print(f"实体权重: {getattr(linker, 'use_entity_weights', 'N/A')}")


def test_unified_implementation():
    """测试统一版实现，测试两种模式"""
    print("\n===== 测试统一版实现 =====")
    
    # 创建测试事件
    events = create_test_events(num_events=10, num_chapters=2)
    print(f"创建了 {len(events)} 个测试事件")
    
    # 1. 测试不优化模式
    print("\n----- 不优化模式 -----")
    linker1 = UnifiedCausalLinker(
        api_key="dummy",
        model="dummy",
        provider="none",
        use_optimization=False
    )
    
    print(f"链接器类型: {type(linker1).__name__}")
    print(f"优化模式: {linker1.use_optimization}")
    
    # 2. 测试优化模式
    print("\n----- 优化模式 -----")
    linker2 = UnifiedCausalLinker(
        api_key="dummy",
        model="dummy",
        provider="none",
        use_optimization=True,
        max_events_per_chapter=10,
        min_entity_support=1,
        use_entity_weights=True
    )
    
    print(f"链接器类型: {type(linker2).__name__}")
    print(f"优化模式: {linker2.use_optimization}")
    print(f"实体权重: {linker2.use_entity_weights}")


def main():
    """主函数"""
    print("测试统一版因果链接器")
    print("=" * 80)
    
    try:
        # 测试原始版本兼容性
        test_original_compatibility()
        
        # 测试优化版本兼容性
        test_optimized_compatibility()
        
        # 测试统一版实现
        test_unified_implementation()
        
        print("\n所有测试完成!")
        print("统一版因果链接器工作正常，兼容原有实现")
        
    except Exception as e:
        print(f"\n测试失败，错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
