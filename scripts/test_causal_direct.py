#!/usr/bin/env python3
"""
因果链接DeepSeek API集成测试

专门测试因果链接服务与DeepSeek API的集成，使用更明确的测试案例
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
from common.models.event import EventItem
from common.utils.enhanced_logger import EnhancedLogger
from causal_linking.di.provider import provide_linker

# 创建日志记录器
logger = EnhancedLogger("causal_linking_test", log_level="DEBUG")

def main():
    """运行因果链接DeepSeek API集成测试"""
    print("="*80)
    print("因果链接 - DeepSeek API集成测试 (直接调用)")
    print("="*80)
    
    # 获取API密钥和模型
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    model = "deepseek-chat"
    
    print(f"使用模型: {model}")
    print(f"API密钥前缀: {api_key[:10]}...")
    
    # 创建测试事件
    print("\n1. 创建测试事件...")
    event1_dict = {
        "event_id": "event_1",
        "description": "韩立在洗灵池中炼体",
        "characters": ["韩立"],
        "treasures": ["洗灵池"],
        "location": "七玄门",
        "result": "韩立的体质得到了显著增强"
    }
    
    event2_dict = {
        "event_id": "event_2",
        "description": "韩立突破至练气期第三层",
        "characters": ["韩立"],
        "treasures": [],
        "location": "七玄门",
        "result": "韩立的修为提升至练气期第三层"
    }
    
    # 读取提示词模板
    with open('/home/severin/CodeLib_linux/KNU_Class/Digital_Huma/Fianl_HW/common/config/prompt_causal_linking.json', 'r', encoding='utf-8') as f:
        prompt_template = json.load(f)
    
    # 2. 手动构建提示词
    print("\n2. 构建提示词...")
    system_prompt = prompt_template.get('system', '')
    instruction = prompt_template.get('instruction', '').format(
        event1=json.dumps(event1_dict, ensure_ascii=False),
        event2=json.dumps(event2_dict, ensure_ascii=False)
    )
    
    print("\n系统提示词:")
    print(system_prompt)
    
    print("\n用户提示词:")
    print(instruction)
    
    # 3. 直接调用API
    print("\n3. 调用DeepSeek API...")
    client = LLMClient(
        api_key=api_key,
        model=model,
        provider="deepseek"
    )
    
    response = client.call_with_json_response(system_prompt, instruction)
    
    # 4. 解析响应
    print("\n4. API响应结果:")
    print(f"响应成功: {response['success']}")
    
    if response['success'] and 'json_content' in response:
        json_content = response['json_content']
        print("\nJSON内容:")
        print(json.dumps(json_content, ensure_ascii=False, indent=2))
        
        # 5. 手动解析结果
        print("\n5. 解析因果关系:")
        has_causal = json_content.get("has_causal_relation", False)
        
        if has_causal:
            direction = json_content.get("direction", "")
            strength = json_content.get("strength", "中")
            reason = json_content.get("reason", "")
            
            if direction == "event1->event2":
                from_id = "event_1"
                to_id = "event_2"
            elif direction == "event2->event1":
                from_id = "event_2"
                to_id = "event_1"
            else:
                print(f"无法解析因果方向: {direction}")
                return
                
            print(f"发现因果关系: {from_id} -> {to_id}, 强度: {strength}")
            print(f"原因: {reason}")
        else:
            print("未发现因果关系")
    else:
        print(f"API调用失败或响应格式错误: {response.get('error', '未知错误')}")
        print("\n原始响应内容:")
        print(response.get('content', '无内容'))
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()
