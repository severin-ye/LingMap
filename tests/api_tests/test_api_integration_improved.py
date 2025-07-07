#!/usr/bin/env python3
"""
增强版API集成测试脚本

测试DeepSeek API的基本连接、JSON响应和各种API调用功能
- 添加多种超时控制机制
- 提供更丰富的错误诊断信息
- 完全支持模拟模式进行离线测试
"""

import os
import sys
import json
import time
import signal
import threading
from pathlib import Path
import traceback

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

# TODO: Translate - 调试模式：打印更多详细信息
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"

# TODO: Translate - 超时Set（秒）
API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "30"))

class TimeoutException(Exception):
    """超时异常"""
    pass

def timeout_handler(signum, frame):
    """信号超时处理函数"""
    raise TimeoutException("API调用超时 (信号触发)")

class ThreadingTimeout:
    """线程超时控制器，作为信号超时机制的备选"""
    def __init__(self, seconds):
        self.seconds = seconds
        self.timeout_happened = False
        
    def __enter__(self):
        self.timer = threading.Timer(self.seconds, self._timeout)
        self.timer.daemon = True
        self.timer.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.timer.cancel()
        
    def _timeout(self):
        self.timeout_happened = True

def with_timeout(func, *args, **kwargs):
    """添加多重超时控制的函数装饰器
    
    同时使用信号和线程两种超时机制，确保在各种环境下都能正常工作
    """
    # TODO: Translate - Set信号Process器（如果平台支持）
    try:
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(API_TIMEOUT)
        has_alarm = True
    except (AttributeError, ValueError):
        # TODO: Translate - 某些平台不支持SIGALRM
        has_alarm = False
    
    # TODO: Translate - Usethread作为备选超时机制
    with ThreadingTimeout(API_TIMEOUT) as timeout_ctx:
        try:
            # TODO: Translate - Execute目标函数
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            # TODO: Translate - Checkthread超时
            if timeout_ctx.timeout_happened:
                return {"success": False, "error": f"API调用超时 (线程触发，{API_TIMEOUT}秒)"}
                
            # TODO: Translate - 一切正常，Return结果
            return result
        except TimeoutException as e:
            logger.warning(f"API调用超时: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            error_msg = str(e)
            logger.error(f"API调用异常: {error_msg}")
            if DEBUG_MODE:
                logger.debug(f"异常详情:\n{traceback.format_exc()}")
            return {"success": False, "error": error_msg}
        finally:
            # TODO: Translate - 清理超时Set
            if has_alarm:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

def mock_api_response(system_prompt, user_prompt):
    """生成模拟API响应，用于测试模式"""
    logger.info("使用模拟API响应模式")
    time.sleep(0.5)  # TODO: Translate - 模拟少量的网络延迟
    
    if "JSON" in system_prompt.upper() or "json" in user_prompt.lower():
        mock_result = {
            "success": True,
            "content": '{"name": "韩立", "origin": "七玄门", "cultivation_type": "修仙", "main_characteristics": ["坚毅", "谨慎", "善良"]}',
            "json_content": {
                "name": "韩立",
                "origin": "七玄门",
                "cultivation_type": "修仙",
                "main_characteristics": ["坚毅", "谨慎", "善良"]
            },
            "model": "mock-model"
        }
    else:
        mock_result = {
            "success": True,
            "content": "《凡人修仙传》是忘语所著的一部东方玄幻小说，讲述了一个普通少年韩立从凡人家庭出身，偶获奇遇踏入仙途的故事。修仙路上，韩立凭借自己的聪慧毅力和坚韧不拔的精神，一路披荆斩棘，最终修炼成仙。",
            "model": "mock-model"
        }
    
    # TODO: Translate - 模拟网络延迟
    if "causal" in system_prompt.lower() or "因果" in system_prompt:
        time.sleep(0.5)  # TODO: Translate - 复杂查询需要更长时间
        mock_result["json_content"] = {
            "has_causal_relation": True,
            "direction": "event1->event2",
            "strength": "高",
            "reason": "韩立在洗灵池中炼体增强了体质，这直接促使他突破至练气期第三层，两者存在明显的因果关系。"
        }
    
    return mock_result

def test_basic_api_connection():
    """测试基本API连接"""
    logger.info("="*80)
    logger.info("1. 基本API连接测试")
    logger.info("="*80)
    
    # GetAPI key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key and not MOCK_MODE:
        logger.error("未找到DeepSeek API密钥")
        return False
    
    if MOCK_MODE:
        logger.warning("测试运行在模拟模式，不会实际调用API")
        response = mock_api_response(
            "你是一个有用的AI助手。", 
            "请简单介绍一下《凡人修仙传》这部小说。"
        )
    else:
        logger.info(f"找到API密钥: {api_key[:5]}...")
        
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
            logger.info("\n测试简单文本调用...")
            system = "你是一个有用的AI助手。"
            user = "请简单介绍一下《凡人修仙传》这部小说。"
            
            start_time = time.time()
            response = with_timeout(client.call_llm, system, user)
            elapsed = time.time() - start_time
            logger.info(f"API调用耗时: {elapsed:.2f}秒")
        except Exception as e:
            logger.error(f"API调用异常: {str(e)}")
            if DEBUG_MODE:
                logger.debug(f"异常详情:\n{traceback.format_exc()}")
            return False
    
    logger.info(f"响应成功: {response['success']}")
    
    if response['success']:
        content = response['content']
        logger.info(f"响应长度: {len(content)} 字符")
        logger.info("响应内容预览:")
        logger.info(content[:200] + "..." if len(content) > 200 else content)
        return True
    else:
        logger.error(f"错误信息: {response.get('error', '未知错误')}")
        return False

def test_json_response():
    """测试JSON格式响应"""
    logger.info("\n" + "="*80)
    logger.info("2. JSON响应测试")
    logger.info("="*80)
    
    if MOCK_MODE:
        logger.warning("测试运行在模拟模式，使用模拟数据")
        response = mock_api_response(
            "你是一个专门分析小说内容的AI助手。请以JSON格式回复。",
            "请分析《凡人修仙传》主角韩立的基本信息"
        )
    else:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            logger.error("未找到DeepSeek API密钥")
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
            logger.info(f"API调用耗时: {elapsed:.2f}秒")
        except Exception as e:
            logger.error(f"API调用异常: {str(e)}")
            if DEBUG_MODE:
                logger.debug(f"异常详情:\n{traceback.format_exc()}")
            return False
    
    logger.info(f"响应成功: {response['success']}")
    
    if response['success'] and 'json_content' in response:
        json_content = response['json_content']
        logger.info("\nJSON内容:")
        logger.info(json.dumps(json_content, ensure_ascii=False, indent=2))
        
        # TODO: Translate - VerifyJSON结构
        required_fields = ["name", "origin", "cultivation_type", "main_characteristics"]
        missing_fields = [field for field in required_fields if field not in json_content]
        
        if missing_fields:
            logger.warning(f"缺少字段: {missing_fields}")
            return False
        else:
            logger.info("JSON结构完整")
            return True
    else:
        logger.error(f"错误信息: {response.get('error', '未知错误')}")
        if 'content' in response:
            logger.warning("原始响应内容:")
            logger.warning(response['content'])
        return False

def test_causal_analysis_api():
    """测试因果分析API调用"""
    logger.info("\n" + "="*80)
    logger.info("3. 因果分析API测试")
    logger.info("="*80)
    
    # TODO: Translate - 如果是模拟模式，Return模拟数据
    if MOCK_MODE:
        logger.warning("测试运行在模拟模式，使用模拟数据")
        response = mock_api_response(
            "你是一个专门分析《凡人修仙传》中事件因果关系的AI助手。请以JSON格式回复。",
            "请分析以下两个事件之间是否存在因果关系"
        )
    else:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            logger.error("未找到DeepSeek API密钥")
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
            logger.info(f"API调用耗时: {elapsed:.2f}秒")
        except Exception as e:
            logger.error(f"API调用异常: {str(e)}")
            if DEBUG_MODE:
                logger.debug(f"异常详情:\n{traceback.format_exc()}")
            return False
    
    logger.info(f"响应成功: {response['success']}")
    
    if response['success'] and 'json_content' in response:
        json_content = response['json_content']
        logger.info("\n因果分析结果:")
        logger.info(json.dumps(json_content, ensure_ascii=False, indent=2))
        
        # TODO: Translate - Verifycausal分析结果
        has_causal = json_content.get("has_causal_relation", False)
        if has_causal:
            direction = json_content.get("direction", "")
            strength = json_content.get("strength", "")
            reason = json_content.get("reason", "")
            
            logger.info(f"\n发现因果关系: {direction}")
            logger.info(f"  强度: {strength}")
            logger.info(f"  理由: {reason}")
            return True
        else:
            logger.info("\n未发现因果关系")
            return True
    else:
        logger.error(f"错误信息: {response.get('error', '未知错误')}")
        return False

def main():
    """运行API集成测试"""
    print("DeepSeek API集成测试套件")
    print("="*80)
    
    # TODO: Translate - Check是否启用了模拟模式和调试模式
    if MOCK_MODE:
        print("⚠️  警告: 测试运行在模拟模式，不会实际调用API")
        
    if DEBUG_MODE:
        print("ℹ️  信息: 调试模式已启用，将显示更详细的错误信息")
        
    print(f"ℹ️  API超时设置: {API_TIMEOUT}秒")
    
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
            if DEBUG_MODE:
                print(f"异常详情:\n{traceback.format_exc()}")
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
        print("\n故障排除提示:")
        print("1. 检查API密钥是否正确设置")
        print("2. 确保网络连接正常")
        print("3. 尝试增加API_TIMEOUT环境变量值")
        print("4. 使用MOCK_API=true在模拟模式下测试")
        print("5. 启用DEBUG_MODE=true获取更多错误信息")
    
    # TODO: Translate - Return0表示Successfully，非0表示Failed
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
