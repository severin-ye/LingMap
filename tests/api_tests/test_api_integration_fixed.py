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

# 是否使用模拟模式（不实际调用API）
MOCK_MODE = os.environ.get("MOCK_API", "false").lower() == "true"

# 超时设置（秒）
API_TIMEOUT = 30

class TimeoutException(Exception):
    """超时异常"""
    pass

def timeout_handler(signum, frame):
    """超时处理函数"""
    raise TimeoutException("API调用超时")

def with_timeout(func, *args, **kwargs):
    """添加超时控制的函数装饰器"""
    # 设置信号处理器
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(API_TIMEOUT)
    
    try:
        result = func(*args, **kwargs)
        signal.alarm(0)  # 取消超时
        return result
    except TimeoutException:
        raise
    finally:
        signal.alarm(0)  # 确保取消超时

def mock_api_response(system, user):
    """模拟API响应"""
    time.sleep(0.1)  # 模拟网络延迟
    
    if "JSON" in system or "json" in user:
        return {
            "success": True,
            "content": '{"name": "韩立", "origin": "凡人", "cultivation_type": "炼气士", "main_characteristics": ["谨慎", "坚韧", "有天赋"]}',
            "json_content": {
                "name": "韩立",
                "origin": "凡人",
                "cultivation_type": "炼气士",
                "main_characteristics": ["谨慎", "坚韧", "有天赋"]
            }
        }
    else:
        return {
            "success": True,
            "content": "《凡人修仙传》是一部经典的仙侠修真小说，主角韩立从凡人开始修仙之路..."
        }

def test_basic_api_connection():
    """测试基本API连接"""
    print("="*80)
    print("1. 基本API连接测试")
    print("="*80)
    
    # 获取API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key and not MOCK_MODE:
        print("❌ 错误: 未找到DeepSeek API密钥")
        assert False, "未找到DeepSeek API密钥"
    
    if MOCK_MODE:
        print("⚠️  测试运行在模拟模式，不会实际调用API")
        response = mock_api_response(
            "你是一个有用的AI助手。", 
            "请简单介绍一下《凡人修仙传》这部小说。"
        )
    else:
        print(f"✓ 找到API密钥: {api_key[:5] if api_key else 'N/A'}...")
        
        try:
            # 初始化客户端
            client = LLMClient(
                api_key=api_key,
                model="deepseek-chat",
                provider="deepseek",
                temperature=0.0,
                timeout=API_TIMEOUT  # 设置超时时间
            )
            
            # 测试简单调用
            print("\n测试简单文本调用...")
            system = "你是一个有用的AI助手。"
            user = "请简单介绍一下《凡人修仙传》这部小说。"
            
            start_time = time.time()
            response = with_timeout(client.call_llm, system, user)
            elapsed = time.time() - start_time
            print(f"API调用耗时: {elapsed:.2f}秒")
        except Exception as e:
            print(f"❌ API调用异常: {str(e)}")
            assert False, f"API调用异常: {str(e)}"
    
    print(f"响应成功: {response['success']}")
    
    if response['success']:
        content = response['content']
        print(f"响应长度: {len(content)} 字符")
        print("响应内容预览:")
        print(content[:200] + "..." if len(content) > 200 else content)
        assert True  # 测试成功
    else:
        print(f"错误信息: {response.get('error', '未知错误')}")
        assert False, f"API调用失败: {response.get('error', '未知错误')}"

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
            assert False, "未找到DeepSeek API密钥"
            
        try:
            client = LLMClient(
                api_key=api_key,
                model="deepseek-chat",
                provider="deepseek",
                timeout=API_TIMEOUT
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
            
            start_time = time.time()
            response = with_timeout(client.call_with_json_response, system, user)
            elapsed = time.time() - start_time
            print(f"API调用耗时: {elapsed:.2f}秒")
        except Exception as e:
            print(f"❌ API调用异常: {str(e)}")
            assert False, f"API调用异常: {str(e)}"
    
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
            assert False, f"JSON结构不完整，缺少字段: {missing_fields}"
        else:
            print("✓ JSON结构完整")
            assert True
    else:
        print(f"错误信息: {response.get('error', '未知错误')}")
        if 'content' in response:
            print("原始响应内容:")
            print(response['content'])
        assert False, f"JSON响应失败: {response.get('error', '未知错误')}"

def test_causal_analysis_api():
    """测试因果分析API调用"""
    print("\n" + "="*80)
    print("3. 因果分析API测试")
    print("="*80)
    
    # 如果是模拟模式，返回模拟数据
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
            assert False, "未找到DeepSeek API密钥"
        
        try:
            client = LLMClient(
                api_key=api_key,
                model="deepseek-chat",
                provider="deepseek",
                timeout=API_TIMEOUT
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
            
            start_time = time.time()
            response = with_timeout(client.call_with_json_response, system, user)
            elapsed = time.time() - start_time
            print(f"API调用耗时: {elapsed:.2f}秒")
        except Exception as e:
            print(f"❌ API调用异常: {str(e)}")
            assert False, f"API调用异常: {str(e)}"
    
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
            assert True
        else:
            print("\n- 未发现因果关系")
            assert True
    else:
        print(f"错误信息: {response.get('error', '未知错误')}")
        assert False, f"因果分析失败: {response.get('error', '未知错误')}"
