#!/usr/bin/env python3
"""
API集成测试脚本

测试DeepSeek API的基本连接、JSON响应和各种API调用功能
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from event_extraction.repository.llm_client import LLMClient
from common.utils.enhanced_logger import EnhancedLogger

# 创建日志记录器
logger = EnhancedLogger("api_integration_test", log_level="DEBUG")

def test_basic_api_connection():
    """测试基本API连接"""
    print("="*80)
    print("1. 基本API连接测试")
    print("="*80)
    
    # 获取API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 错误: 未找到DeepSeek API密钥")
        return False
    
    print(f"✓ 找到API密钥: {api_key[:10]}...")
    
    # 初始化客户端
    client = LLMClient(
        api_key=api_key,
        model="deepseek-chat",
        provider="deepseek",
        temperature=0.0
    )
    
    # 测试简单调用
    print("\n测试简单文本调用...")
    system = "你是一个有用的AI助手。"
    user = "请简单介绍一下《凡人修仙传》这部小说。"
    
    response = client.call_llm(system, user)
    print(f"响应成功: {response['success']}")
    
    if response['success']:
        content = response['content']
        print(f"响应长度: {len(content)} 字符")
        print("响应内容预览:")
        print(content[:200] + "..." if len(content) > 200 else content)
        return True
    else:
        print(f"错误信息: {response.get('error', '未知错误')}")
        return False

def test_json_response():
    """测试JSON格式响应"""
    print("\n" + "="*80)
    print("2. JSON响应测试")
    print("="*80)
    
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    client = LLMClient(
        api_key=api_key,
        model="deepseek-chat",
        provider="deepseek"
    )
    
    # 测试JSON响应
    system = "你是一个专门分析小说内容的AI助手。请以JSON格式回复。"
    user = """请分析《凡人修仙传》主角韩立的基本信息，以JSON格式回复：
{
  "name": "角色姓名",
  "origin": "出身背景",
  "cultivation_type": "修炼类型",
  "main_characteristics": ["特点1", "特点2", "特点3"]
}"""
    
    response = client.call_with_json_response(system, user)
    print(f"响应成功: {response['success']}")
    
    if response['success'] and 'json_content' in response:
        json_content = response['json_content']
        print("\nJSON内容:")
        print(json.dumps(json_content, ensure_ascii=False, indent=2))
        
        # 验证JSON结构
        required_fields = ["name", "origin", "cultivation_type", "main_characteristics"]
        missing_fields = [field for field in required_fields if field not in json_content]
        
        if missing_fields:
            print(f"⚠️  缺少字段: {missing_fields}")
            return False
        else:
            print("✓ JSON结构完整")
            return True
    else:
        print(f"错误信息: {response.get('error', '未知错误')}")
        if 'content' in response:
            print("原始响应内容:")
            print(response['content'])
        return False

def test_causal_analysis_api():
    """测试因果分析API调用"""
    print("\n" + "="*80)
    print("3. 因果分析API测试")
    print("="*80)
    
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    client = LLMClient(
        api_key=api_key,
        model="deepseek-chat",
        provider="deepseek"
    )
    
    # 测试因果分析
    system = "你是一个专门分析《凡人修仙传》中事件因果关系的AI助手。请以JSON格式回复。"
    user = """请分析以下两个事件之间是否存在因果关系:

事件1: {"event_id": "event_1", "description": "韩立在洗灵池中炼体", "characters": ["韩立"], "treasures": ["洗灵池"], "location": "七玄门", "result": "韩立的体质得到了显著增强"}

事件2: {"event_id": "event_2", "description": "韩立突破至练气期第三层", "characters": ["韩立"], "treasures": [], "location": "七玄门", "result": "韩立的修为提升至练气期第三层"}

请以JSON格式回复：
{
  "has_causal_relation": true或false,
  "direction": "event1->event2"或"event2->event1",
  "strength": "高"、"中"或"低",
  "reason": "简要解释因果关系的理由"
}"""
    
    response = client.call_with_json_response(system, user)
    print(f"响应成功: {response['success']}")
    
    if response['success'] and 'json_content' in response:
        json_content = response['json_content']
        print("\n因果分析结果:")
        print(json.dumps(json_content, ensure_ascii=False, indent=2))
        
        # 验证因果分析结果
        has_causal = json_content.get("has_causal_relation", False)
        if has_causal:
            direction = json_content.get("direction", "")
            strength = json_content.get("strength", "")
            reason = json_content.get("reason", "")
            
            print(f"\n✓ 发现因果关系: {direction}")
            print(f"  强度: {strength}")
            print(f"  理由: {reason}")
            return True
        else:
            print("\n- 未发现因果关系")
            return True
    else:
        print(f"错误信息: {response.get('error', '未知错误')}")
        return False

def main():
    """运行API集成测试"""
    print("DeepSeek API集成测试套件")
    print("="*80)
    
    tests = [
        ("基本API连接", test_basic_api_connection),
        ("JSON响应格式", test_json_response),
        ("因果分析API", test_causal_analysis_api)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 发生异常: {str(e)}")
            results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有API集成测试通过！")
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接")

if __name__ == "__main__":
    main()
