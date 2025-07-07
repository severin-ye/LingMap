#!/usr/bin/env python3
"""
API集成测试脚本

测试DeepSeek API的基本连接、JSON响应和各种API调用功能
"""

import os
import sys
import json
import time
import signal
from pathlib import Path

# TODO: Translate - Add project root directory to系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Loadenvironment variables
from dotenv import load_dotenv
load_dotenv()

from event_extraction.repository.llm_client import LLMClient
from common.utils.enhanced_logger import EnhancedLogger

# TODO: Translate - Create日志记录器
logger = EnhancedLogger("api_integration_test", log_level="DEBUG")

# TODO: Translate - 是否Use模拟模式（不实际调用API）
MOCK_MODE = os.environ.get("MOCK_API", "false").lower() == "true"

# TODO: Translate - 超时Set（秒）
API_TIMEOUT = 30

class TimeoutException(Exception):
    """超时异常"""
    pass

def timeout_handler(signum, frame):
    """超时处理函数"""
    raise TimeoutException("API调用超时")

def with_timeout(func, *args, **kwargs):
    """添加超时控制的函数装饰器"""
    # TODO: Translate - Set信号Process器
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(API_TIMEOUT)
    
    try:
        result = func(*args, **kwargs)
        signal.alarm(0)  # TODO: Translate - 取消闹钟
        return result
    except TimeoutException as e:
        print(f"⚠️  {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        signal.alarm(0)  # TODO: Translate - 确保闹钟被取消

def mock_api_response(system_prompt, user_prompt):
    """生成模拟API响应，用于测试模式"""
    print("⚠️  使用模拟API响应模式")
    if "JSON" in system_prompt.upper():
        return {
            "success": True,
            "content": '{"name": "韩立", "origin": "七玄门", "cultivation_type": "修仙", "main_characteristics": ["坚毅", "谨慎", "善良"]}',
            "json_content": {
                "name": "韩立",
                "origin": "七玄门",
                "cultivation_type": "修仙",
                "main_characteristics": ["坚毅", "谨慎", "善良"]
            }
        }
    else:
        return {
            "success": True,
            "content": "《凡人修仙传》是忘语所著的一部东方玄幻小说，讲述了一个普通少年韩立从凡人家庭出身，偶获奇遇踏入仙途的故事。修仙路上，韩立凭借自己的聪慧毅力和坚韧不拔的精神，一路披荆斩棘，最终修炼成仙。"
        }

def test_basic_api_connection():
    """测试基本API连接"""
    print("="*80)
    print("1. 基本API连接测试")
    print("="*80)
    
    # GetAPI key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key and not MOCK_MODE:
        print("❌ 错误: 未找到DeepSeek API密钥")
        return False
    
    if MOCK_MODE:
        print("⚠️  测试运行在模拟模式，不会实际调用API")
        response = mock_api_response(
            "你是一个有用的AI助手。", 
            "请简单介绍一下《凡人修仙传》这部小说。"
        )
    else:
        print(f"✓ 找到API密钥: {api_key[:5]}...")
        
        try:
            # Initializeclient
            client = LLMClient(
                api_key=api_key,
                model="deepseek-chat",
                provider="deepseek",
                temperature=0.0,
                timeout=API_TIMEOUT  # TODO: Translate - Set超时时间
            )
            
            # TODO: Translate - Test简单调用
            print("\n测试简单文本调用...")
            system = "你是一个有用的AI助手。"
            user = "请简单介绍一下《凡人修仙传》这部小说。"
            
            start_time = time.time()
            response = with_timeout(client.call_llm, system, user)
            elapsed = time.time() - start_time
            print(f"API调用耗时: {elapsed:.2f}秒")
        except Exception as e:
            print(f"❌ API调用异常: {str(e)}")
            return False
    
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
    
    if MOCK_MODE:
        print("⚠️  测试运行在模拟模式，使用模拟数据")
        response = mock_api_response(
            "你是一个专门分析小说内容的AI助手。请以JSON格式回复。",
            "请分析《凡人修仙传》主角韩立的基本信息"
        )
    else:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            print("❌ 错误: 未找到DeepSeek API密钥")
            return False
            
        try:
            client = LLMClient(
                api_key=api_key,
                model="deepseek-chat",
                provider="deepseek",
                timeout=API_TIMEOUT
            )
            
            # TODO: Translate - TestJSON响应
            system = "你是一个专门分析小说内容的AI助手。请以JSON格式回复。"
            user = """请分析《凡人修仙传》主角韩立的基本信息，以JSON格式回复：
    {
      "name": "角色姓名",
      "origin": "出身背景",
      "cultivation_type": "修炼类型",
      "main_characteristics": ["特点1", "特点2", "特点3"]
    }"""
            
            start_time = time.time()
            response = with_timeout(client.call_with_json_response, system, user)
            elapsed = time.time() - start_time
            print(f"API调用耗时: {elapsed:.2f}秒")
        except Exception as e:
            print(f"❌ API调用异常: {str(e)}")
            return False
    
    print(f"响应成功: {response['success']}")
    
    if response['success'] and 'json_content' in response:
        json_content = response['json_content']
        print("\nJSON内容:")
        print(json.dumps(json_content, ensure_ascii=False, indent=2))
        
        # TODO: Translate - VerifyJSON结构
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
    
    # TODO: Translate - 如果是模拟模式，Return模拟数据
    if MOCK_MODE:
        print("⚠️  测试运行在模拟模式，使用模拟数据")
        response = {
            "success": True,
            "json_content": {
                "has_causal_relation": True,
                "direction": "event1->event2",
                "strength": "高",
                "reason": "韩立在洗灵池中炼体增强了体质，这直接促使他突破至练气期第三层，两者存在明显的因果关系。"
            }
        }
    else:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            print("❌ 错误: 未找到DeepSeek API密钥")
            return False
        
        try:
            client = LLMClient(
                api_key=api_key,
                model="deepseek-chat",
                provider="deepseek",
                timeout=API_TIMEOUT
            )
            
            # TODO: Translate - Testcausal分析
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
            
            start_time = time.time()
            response = with_timeout(client.call_with_json_response, system, user)
            elapsed = time.time() - start_time
            print(f"API调用耗时: {elapsed:.2f}秒")
        except Exception as e:
            print(f"❌ API调用异常: {str(e)}")
            return False
    
    print(f"响应成功: {response['success']}")
    
    if response['success'] and 'json_content' in response:
        json_content = response['json_content']
        print("\n因果分析结果:")
        print(json.dumps(json_content, ensure_ascii=False, indent=2))
        
        # TODO: Translate - Verifycausal分析结果
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
    
    # TODO: Translate - Check是否启用了模拟模式
    if MOCK_MODE:
        print("⚠️  警告: 测试运行在模拟模式，不会实际调用API")
    
    tests = [
        ("基本API连接", test_basic_api_connection),
        ("JSON响应格式", test_json_response),
        ("因果分析API", test_causal_analysis_api)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n开始测试: {test_name}")
            test_start = time.time()
            result = test_func()
            test_duration = time.time() - test_start
            
            results.append((test_name, result, test_duration))
            print(f"测试 '{test_name}' {'通过 ✓' if result else '失败 ✗'} (耗时: {test_duration:.2f}秒)")
        except KeyboardInterrupt:
            print("\n⚠️  测试被用户中断")
            results.append((test_name, False, 0))
            break
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 发生异常: {str(e)}")
            results.append((test_name, False, 0))
    
    # TODO: Translate - OutputTest总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for test_name, result, duration in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status} (耗时: {duration:.2f}秒)")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有API集成测试通过！")
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接")
    
    # TODO: Translate - Return0表示Successfully，非0表示Failed
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
