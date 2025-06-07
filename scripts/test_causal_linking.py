#!/usr/bin/env python3
"""
因果链接测试脚本

专门测试因果链接服务与DeepSeek API的集成
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from common.models.event import EventItem
from common.utils.enhanced_logger import EnhancedLogger
from causal_linking.di.provider import provide_linker

# 创建日志记录器
logger = EnhancedLogger("causal_linking_test", log_level="DEBUG")

def main():
    """运行因果链接测试"""
    print("="*80)
    print("因果链接服务 - DeepSeek API集成测试")
    print("="*80)
    
    # 获取因果链接器
    print("1. 初始化因果链接器...")
    linker = provide_linker()
    
    # 打印配置信息
    print(f"   - 提供商: {linker.provider}")
    print(f"   - 模型: {linker.model}")
    print(f"   - API密钥前缀: {linker.api_key[:10]}...")
    
    # 创建测试事件
    print("\n2. 创建测试事件...")
    event1 = EventItem(
        event_id="event_1",
        description="韩立在洗灵池中炼体",
        characters=["韩立"],
        treasures=["洗灵池"],
        time="",
        location="七玄门",
        result="韩立的体质得到了显著增强"
    )
    
    event2 = EventItem(
        event_id="event_2", 
        description="韩立突破至练气期第三层",
        characters=["韩立"],
        treasures=[],
        time="",
        location="七玄门",
        result="韩立的修为提升至练气期第三层"
    )
    
    # 测试因果分析
    print("\n3. 分析事件因果关系...")
    events = [event1, event2]
    
    # 添加调试日志
    print("\n调试日志:")
    print("- 测试直接调用analyze_causal_relation方法")
    edge = linker.analyze_causal_relation(event1, event2)
    if edge:
        print(f"  - 直接调用返回: {edge.from_id} -> {edge.to_id}, 强度: {edge.strength}")
        print(f"    原因: {edge.reason}")
    else:
        print("  - 直接调用未返回因果关系")
    
    causal_links = linker.link_events(events)
    
    # 输出结果
    print("\n4. 测试结果:")
    if causal_links:
        print(f"   - 发现 {len(causal_links)} 个因果关系")
        for link in causal_links:
            print(f"   - {link.from_id} -> {link.to_id}, 强度: {link.strength}")
            print(f"     原因: {link.reason}")
    else:
        print("   - 未发现因果关系")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()
