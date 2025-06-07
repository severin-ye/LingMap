#!/usr/bin/env python3
"""
API客户端测试脚本

用于测试LLM API调用是否正常工作，以及响应的解析是否正确
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到sys.path
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from event_extraction.repository.llm_client import LLMClient
from common.utils.path_utils import get_config_path, get_novel_path
from common.utils.json_loader import JsonLoader
from common.utils.enhanced_logger import EnhancedLogger

# 创建专用的日志记录器
logger = EnhancedLogger("api_test", log_level="DEBUG")

def test_api_connection():
    """测试API连接和基础调用"""
    print("="*60)
    print("API连接测试")
    print("="*60)
    
    # 从环境变量获取API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        # 尝试从.env文件加载
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("DEEPSEEK_API_KEY")
        except ImportError:
            pass
    
    if not api_key:
        print("❌ 未找到DEEPSEEK_API_KEY环境变量")
        return False
    
    print(f"✓ 找到API密钥: {api_key[:5]}...{api_key[-3:]}")
    
    # 创建LLM客户端
    client = LLMClient(
        api_key=api_key,
        model="deepseek-chat",  # 使用DeepSeek模型
        temperature=0.0,
        provider="deepseek"
    )
    
    # 测试简单响应
    test_system = "你是一个帮助分析文本的AI助手。"
    test_user = "请问今天的天气怎么样？请用JSON格式回复，包含weather_condition字段。"
    
    print("\n测试基本API调用...")
    response = client.call_with_json_response(test_system, test_user)
    
    if response["success"]:
        print(f"✓ API调用成功: {json.dumps(response.get('json_content'), ensure_ascii=False, indent=2)}")
    else:
        print(f"❌ API调用失败: {response.get('error')}")
        return False
    
    return True

def test_event_extraction_prompt():
    """测试事件抽取提示词"""
    print("\n"+"="*60)
    print("事件抽取提示词测试")
    print("="*60)
    
    # 加载提示词模板
    prompt_path = get_config_path("prompt_event_extraction.json")
    template = JsonLoader.load_json(prompt_path)
    
    if not template:
        print("❌ 加载提示词模板失败")
        return False
    
    print(f"✓ 成功加载提示词模板: {prompt_path}")
    
    # 检查必要字段
    required_fields = ["system", "instruction", "output_format"]
    for field in required_fields:
        if field not in template:
            print(f"❌ 提示词模板缺少必要字段: {field}")
            return False
    
    # 加载小说测试片段
    test_novel_path = get_novel_path("test.txt")
    if not os.path.exists(test_novel_path):
        # 如果测试文件不存在，使用第1章的前1000字符作为测试
        chapter1_path = get_novel_path("1.txt")
        if os.path.exists(chapter1_path):
            with open(chapter1_path, 'r', encoding='utf-8') as f:
                test_text = f.read(1000)  # 只读取前1000个字符用于测试
                
            # 创建测试文件
            with open(test_novel_path, 'w', encoding='utf-8') as f:
                f.write(test_text)
        else:
            print(f"❌ 未找到任何小说文件")
            return False
    
    # 读取测试文本
    with open(test_novel_path, 'r', encoding='utf-8') as f:
        test_text = f.read()
        
    print(f"✓ 加载测试文本: {len(test_text)} 字符")
    
    # 从环境变量获取API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        # 尝试从.env文件加载
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("DEEPSEEK_API_KEY")
        except ImportError:
            pass
            
    if not api_key:
        print("❌ 未找到DEEPSEEK_API_KEY环境变量")
        return False
    
    # 创建LLM客户端
    client = LLMClient(
        api_key=api_key,
        model="deepseek-chat",  # 使用DeepSeek模型
        temperature=0.0,
        provider="deepseek"
    )
    
    # 格式化提示词
    system_prompt = template["system"]
    user_prompt = template["instruction"].format(text=test_text)
    
    # 请求中添加详细的格式描述
    format_desc = template.get("output_format", "")
    if format_desc:
        user_prompt += f"\n\n输出格式: {format_desc}"
    
    print("\n发送事件抽取请求...")
    logger.debug("发送事件抽取API请求", 
                system_prompt=system_prompt, 
                user_prompt=user_prompt[:100] + "...",
                text_length=len(test_text))
                
    # 调用API
    response = client.call_with_json_response(system_prompt, user_prompt)
    
    if response["success"] and "json_content" in response:
        events_data = response["json_content"]
        print(f"✓ API调用成功，获取到事件数据")
        
        # 检查响应格式
        events = None
        if isinstance(events_data, list):
            events = events_data
        elif isinstance(events_data, dict) and "events" in events_data:
            events = events_data["events"]
            
        if events is not None and len(events) > 0:
            print(f"✓ 成功提取 {len(events)} 个事件")
            for i, event in enumerate(events[:2], 1):  # 只显示前两个事件
                print(f"  事件 {i}:")
                print(f"    描述: {event.get('description', 'N/A')}")
                print(f"    类型: {event.get('event_type', 'N/A')}")
        else:
            print(f"❌ 未能提取任何事件或格式不正确")
            print(f"响应内容: {json.dumps(events_data, ensure_ascii=False, indent=2)}")
    else:
        print(f"❌ API调用失败: {response.get('error', '未知错误')}")
        return False
        
    # 保存完整响应以供后续分析
    debug_dir = project_root / "debug"
    debug_dir.mkdir(exist_ok=True)
    
    with open(debug_dir / "api_response.json", 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=2)
        
    print(f"\n完整API响应已保存到 {debug_dir / 'api_response.json'}")
    
    return True

def main():
    # 创建调试目录
    debug_dir = project_root / "debug"
    debug_dir.mkdir(exist_ok=True)
    
    # 测试API连接
    if not test_api_connection():
        print("\n❌ API基础连接测试失败，请检查API密钥和网络连接")
        return
        
    # 测试事件抽取提示词
    if not test_event_extraction_prompt():
        print("\n❌ 事件抽取提示词测试失败，请检查提示词模板和API响应")
        return
        
    print("\n✓ 所有测试完成")

if __name__ == "__main__":
    main()
