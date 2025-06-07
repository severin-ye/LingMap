#!/usr/bin/env python3
"""
专门测试DeepSeek API调用的辅助脚本
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

from event_extraction.repository.llm_client import LLMClient

def main():
    """测试DeepSeek API直接调用"""
    print("="*80)
    print("DeepSeek API直接调用测试")
    print("="*80)
    
    # 获取API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("错误: 未找到DeepSeek API密钥")
        return
    
    # 初始化客户端
    client = LLMClient(
        api_key=api_key,
        model="deepseek-chat",
        provider="deepseek"
    )
    
    # 测试简单调用
    print("\n1. 测试简单调用...")
    system = "你是一个有用的AI助手。"
    user = "告诉我韩立是谁？他在《凡人修仙传》中的角色是什么？"
    
    response = client.call_llm(system, user)
    print(f"\n响应成功: {response['success']}")
    if response['success']:
        print("\n响应内容:")
        print(response['content'][:500] + "..." if len(response['content']) > 500 else response['content'])
    else:
        print(f"\n错误信息: {response.get('error', '未知错误')}")
    
    # 测试JSON响应
    print("\n2. 测试JSON响应...")
    system = "你是一个专门分析事件因果关系的AI助手。请以JSON格式回复。"
    user = """请分析以下两个事件之间是否存在因果关系:
    
事件1: 韩立在洗灵池中炼体，体质得到显著增强
事件2: 韩立突破至练气期第三层

请以JSON格式回复，包含以下字段:
{
  "has_causal_relation": true或false,
  "direction": "event1->event2"或"event2->event1",
  "strength": "高"、"中"或"低",
  "reason": "简要解释因果关系的理由"
}"""
    
    response = client.call_with_json_response(system, user)
    print(f"\n响应成功: {response['success']}")
    if response['success']:
        print("\nJSON内容:")
        json_content = response.get('json_content', {})
        print(json.dumps(json_content, ensure_ascii=False, indent=2))
    else:
        print(f"\n错误信息: {response.get('error', '未知错误')}")
        print("\n原始响应内容:")
        print(response.get('content', '无内容'))
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()
