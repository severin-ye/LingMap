#!/usr/bin/env python3
"""
因果链接提示词测试脚本

专门测试因果链接服务的提示词生成和解析
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
from causal_linking.domain.base_linker import BaseLinker
from common.utils.json_loader import JsonLoader
from common.utils.path_utils import get_config_path

# 创建日志记录器
logger = EnhancedLogger("causal_prompt_test", log_level="DEBUG")

def main():
    """运行因果链接提示词测试"""
    print("="*80)
    print("因果链接提示词测试")
    print("="*80)
    
    # 1. 创建测试事件
    print("\n1. 创建测试事件...")
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
    
    # 2. 获取CausalLinker并生成提示词
    print("\n2. 生成提示词...")
    linker = provide_linker()
    
    # 调用其私有方法format_prompt通过反射
    import inspect
    format_prompt_method = inspect.getmembers(linker, predicate=lambda x: callable(x) and x.__name__ == 'format_prompt')
    if format_prompt_method:
        prompt = format_prompt_method[0][1](event1, event2)
    else:
        print("无法找到format_prompt方法")
        prompt = {"system": "未找到提示词", "instruction": "未找到提示词"}
    
    # 3. 打印生成的提示词
    print("\n系统提示词:")
    print(prompt['system'])
    
    print("\n用户提示词:")
    print(prompt['instruction'])
    
    # 4. 手动创建模拟响应
    print("\n4. 模拟解析响应...")
    mock_response = {
        "has_causal_relation": True,
        "direction": "event1->event2",
        "strength": "高",
        "reason": "在修真小说中，体质的显著增强通常会为修炼者提供更好的基础，从而有助于突破修炼境界。韩立在洗灵池中炼体导致体质增强，这为他突破至练气期第三层提供了必要的条件和动力。"
    }
    
    # 获取真实的CausalLinker实例
    causal_linker = provide_linker()
    
    # 解析响应
    edge = causal_linker.parse_response(mock_response, event1.event_id, event2.event_id)
    
    if edge:
        print(f"\n解析结果: {edge.from_id} -> {edge.to_id}, 强度: {edge.strength}")
        print(f"原因: {edge.reason}")
    else:
        print("\n解析失败: 未能从响应中提取因果关系")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()
