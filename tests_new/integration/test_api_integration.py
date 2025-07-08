#!/usr/bin/env python3
"""
统一的API集成测试模块

合并了原有的多个API测试文件的功能：
- test_api_integration.py
- test_api_integration_improved.py
- test_api_integration_scripts.py
- test_api_integration_new.py
- test_api_integration_fixed.py

提供完整的DeepSeek API测试功能，包括：
- 基本连接测试
- JSON响应测试
- 各种API调用功能测试
- 超时控制和错误处理
- 模拟模式支持
"""

import os
import sys
import json
import time
import signal
import threading
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
import pytest

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

# 配置参数
MOCK_MODE = os.environ.get("MOCK_API", "false").lower() == "true"
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"
API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "30"))

class TimeoutException(Exception):
    """超时异常"""
    pass

class APITestRunner:
    """API测试运行器类"""
    
    def __init__(self):
        self.client = None
        self.test_results = []
        
    def setup(self):
        """初始化测试环境"""
        try:
            if MOCK_MODE:
                logger.info("运行在模拟模式下")
                self.client = None  # 模拟模式下不需要真实客户端
                return True
            else:
                self.client = LLMClient()
                logger.info("初始化LLM客户端成功")
                return True
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            self.client = None
            return False
    
    def timeout_handler(self, signum, frame):
        """信号超时处理函数"""
        raise TimeoutException("API调用超时 (信号触发)")
    
    def with_timeout(self, func, *args, **kwargs):
        """添加超时控制的函数装饰器"""
        if MOCK_MODE:
            # 模拟模式下返回模拟数据
            return self._get_mock_response(func.__name__)
        
        # 设置信号处理器
        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(API_TIMEOUT)
        
        try:
            result = func(*args, **kwargs)
            signal.alarm(0)  # 取消超时
            return result
        except TimeoutException:
            logger.error(f"函数 {func.__name__} 执行超时")
            raise
        except Exception as e:
            signal.alarm(0)  # 取消超时
            logger.error(f"函数 {func.__name__} 执行出错: {e}")
            raise
    
    def _get_mock_response(self, func_name: str) -> Dict[str, Any]:
        """获取模拟响应数据"""
        mock_responses = {
            "test_basic_connection": {
                "status": "success",
                "message": "模拟连接成功",
                "response_time": 0.1
            },
            "test_json_response": {
                "status": "success",
                "data": {
                    "events": [
                        {
                            "event_id": "mock_001",
                            "description": "模拟事件描述",
                            "timestamp": "2023-01-01"
                        }
                    ]
                },
                "response_time": 0.2
            },
            "test_event_extraction": {
                "status": "success",
                "extracted_events": [
                    {
                        "event_id": "extracted_001",
                        "type": "action",
                        "description": "模拟提取的事件",
                        "participants": ["张三", "李四"],
                        "timestamp": "明朝初年"
                    }
                ],
                "response_time": 0.5
            }
        }
        return mock_responses.get(func_name, {"status": "mock", "message": "默认模拟响应"})
    
    def test_basic_connection(self) -> Dict[str, Any]:
        """测试基本API连接"""
        logger.info("开始测试基本API连接")
        
        def _test():
            if MOCK_MODE:
                return self._get_mock_response("test_basic_connection")
            
            if not self.client:
                raise Exception("LLM客户端未初始化")
            
            start_time = time.time()
            
            # 简单的API调用测试
            system_prompt = "你是一个测试助手，请简单回应用户的消息。"
            user_prompt = "测试连接"
            result = self.client.call_llm(system_prompt, user_prompt)
            response = result.get("content", "")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response and len(response.strip()) > 0:
                return {
                    "status": "success",
                    "message": "API连接正常",
                    "response_time": response_time,
                    "response_length": len(response)
                }
            else:
                return {
                    "status": "failed",
                    "message": "API返回空响应",
                    "response_time": response_time
                }
        
        try:
            result = self.with_timeout(_test)
            self.test_results.append(("basic_connection", True, result))
            logger.info(f"基本连接测试成功: {result}")
            return result
        except Exception as e:
            error_result = {"status": "error", "message": str(e)}
            self.test_results.append(("basic_connection", False, error_result))
            logger.error(f"基本连接测试失败: {e}")
            return error_result
    
    def test_json_response(self) -> Dict[str, Any]:
        """测试JSON响应格式"""
        logger.info("开始测试JSON响应格式")
        
        def _test():
            if MOCK_MODE:
                return self._get_mock_response("test_json_response")
            
            if not self.client:
                raise Exception("LLM客户端未初始化")
            
            start_time = time.time()
            
            # 要求返回JSON格式的提示
            system_prompt = "你是一个事件提取专家，请严格按照用户要求的JSON格式返回结果。"
            user_prompt = '''
            请从以下文本中提取事件信息，并以JSON格式返回：
            
            文本："张三在明朝初年参加了科举考试，后来成为了县令。"
            
            请返回格式如下的JSON：
            {
                "events": [
                    {
                        "event_id": "001",
                        "description": "事件描述",
                        "participants": ["参与者"],
                        "timestamp": "时间"
                    }
                ]
            }
            '''
            
            result = self.client.call_llm(system_prompt, user_prompt)
            response = result.get("content", "")
            end_time = time.time()
            response_time = end_time - start_time
            
            # 尝试解析JSON
            try:
                json_data = json.loads(response)
                return {
                    "status": "success",
                    "message": "JSON响应解析成功",
                    "response_time": response_time,
                    "data": json_data
                }
            except json.JSONDecodeError as e:
                return {
                    "status": "failed",
                    "message": f"JSON解析失败: {e}",
                    "response_time": response_time,
                    "raw_response": response[:200] + "..." if len(response) > 200 else response
                }
        
        try:
            result = self.with_timeout(_test)
            self.test_results.append(("json_response", True, result))
            logger.info(f"JSON响应测试成功: {result}")
            return result
        except Exception as e:
            error_result = {"status": "error", "message": str(e)}
            self.test_results.append(("json_response", False, error_result))
            logger.error(f"JSON响应测试失败: {e}")
            return error_result
    
    def test_event_extraction(self) -> Dict[str, Any]:
        """测试事件抽取功能"""
        logger.info("开始测试事件抽取功能")
        
        def _test():
            if MOCK_MODE:
                return self._get_mock_response("test_event_extraction")
            
            if not self.client:
                raise Exception("LLM客户端未初始化")
            
            start_time = time.time()
            
            # 事件抽取测试文本
            test_text = """
            明太祖朱元璋在至正十六年（1356年）攻克集庆（今南京），
            改集庆为应天府。至正二十八年（1368年）正月，朱元璋在应天府称帝，
            建立明朝，年号洪武。同年八月，明军攻克大都（今北京），
            元朝在中原地区的统治结束。
            """
            
            system_prompt = "你是一个历史事件提取专家，请严格按照用户要求的JSON格式返回结果。"
            user_prompt = f'''
            请从以下历史文本中提取重要事件，并以JSON格式返回：
            
            文本：{test_text}
            
            提取要求：
            1. 识别重要的历史事件
            2. 确定事件的时间、地点、参与者
            3. 按时间顺序排列
            
            返回格式：
            {{
                "extracted_events": [
                    {{
                        "event_id": "事件ID",
                        "type": "事件类型",
                        "description": "事件描述",
                        "participants": ["参与者列表"],
                        "location": "地点",
                        "timestamp": "时间"
                    }}
                ]
            }}
            '''
            
            result = self.client.call_llm(system_prompt, user_prompt)
            response = result.get("content", "")
            end_time = time.time()
            response_time = end_time - start_time
            
            # 尝试解析和验证JSON
            try:
                json_data = json.loads(response)
                extracted_events = json_data.get("extracted_events", [])
                
                if len(extracted_events) > 0:
                    return {
                        "status": "success",
                        "message": f"成功提取 {len(extracted_events)} 个事件",
                        "response_time": response_time,
                        "extracted_events": extracted_events
                    }
                else:
                    return {
                        "status": "failed",
                        "message": "未提取到任何事件",
                        "response_time": response_time,
                        "raw_response": response[:200] + "..." if len(response) > 200 else response
                    }
            except json.JSONDecodeError as e:
                return {
                    "status": "failed",
                    "message": f"JSON解析失败: {e}",
                    "response_time": response_time,
                    "raw_response": response[:200] + "..." if len(response) > 200 else response
                }
        
        try:
            result = self.with_timeout(_test)
            self.test_results.append(("event_extraction", True, result))
            logger.info(f"事件抽取测试成功: {result}")
            return result
        except Exception as e:
            error_result = {"status": "error", "message": str(e)}
            self.test_results.append(("event_extraction", False, error_result))
            logger.error(f"事件抽取测试失败: {e}")
            return error_result
    
    def test_stress_test(self, num_requests: int = 5) -> Dict[str, Any]:
        """压力测试"""
        logger.info(f"开始压力测试 ({num_requests} 次请求)")
        
        if MOCK_MODE:
            # 模拟压力测试
            return {
                "status": "success",
                "message": f"模拟压力测试完成 ({num_requests} 次请求)",
                "total_requests": num_requests,
                "successful_requests": num_requests,
                "failed_requests": 0,
                "average_response_time": 0.1
            }
        
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        for i in range(num_requests):
            try:
                if not self.client:
                    raise Exception("LLM客户端未初始化")
                    
                start_time = time.time()
                
                system_prompt = "你是一个测试助手，请简单回应用户的消息。"
                user_prompt = f"压力测试请求 #{i+1}"
                result = self.client.call_llm(system_prompt, user_prompt)
                response = result.get("content", "")
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                if response and len(response.strip()) > 0:
                    successful_requests += 1
                else:
                    failed_requests += 1
                
                logger.debug(f"请求 {i+1}/{num_requests} 完成，响应时间: {response_time:.2f}s")
                
                # 请求间隔
                time.sleep(1)
                
            except Exception as e:
                failed_requests += 1
                logger.error(f"请求 {i+1} 失败: {e}")
        
        average_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        result = {
            "status": "success" if successful_requests > 0 else "failed",
            "message": f"压力测试完成",
            "total_requests": num_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "average_response_time": average_response_time,
            "response_times": response_times
        }
        
        self.test_results.append(("stress_test", successful_requests > 0, result))
        logger.info(f"压力测试完成: {result}")
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("开始运行所有API集成测试")
        
        if not self.setup():
            return {"status": "error", "message": "测试环境初始化失败"}
        
        all_results = {}
        
        # 运行所有测试
        test_methods = [
            ("基本连接测试", self.test_basic_connection),
            ("JSON响应测试", self.test_json_response),
            ("事件抽取测试", self.test_event_extraction),
            ("压力测试", lambda: self.test_stress_test(3))  # 简化的压力测试
        ]
        
        for test_name, test_method in test_methods:
            logger.info(f"执行: {test_name}")
            try:
                result = test_method()
                all_results[test_name] = result
                
                if result.get("status") == "success":
                    logger.info(f"✓ {test_name} - 成功")
                else:
                    logger.warning(f"✗ {test_name} - 失败: {result.get('message', '未知错误')}")
                    
            except Exception as e:
                error_msg = f"测试执行异常: {e}"
                all_results[test_name] = {"status": "error", "message": error_msg}
                logger.error(f"✗ {test_name} - 异常: {error_msg}")
        
        # 汇总结果
        successful_tests = sum(1 for result in all_results.values() if result.get("status") == "success")
        total_tests = len(all_results)
        
        summary = {
            "status": "success" if successful_tests == total_tests else "partial_success",
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "test_results": all_results,
            "summary_message": f"测试完成: {successful_tests}/{total_tests} 成功"
        }
        
        logger.info(f"所有测试完成: {summary['summary_message']}")
        return summary
    
    def get_test_summary(self) -> str:
        """获取测试摘要"""
        if not self.test_results:
            return "暂无测试结果"
        
        total = len(self.test_results)
        passed = sum(1 for _, success, _ in self.test_results if success)
        
        summary_lines = [
            f"\n测试摘要:",
            f"总计: {total} 个测试",
            f"成功: {passed} 个",
            f"失败: {total - passed} 个",
            f"成功率: {(passed/total)*100:.1f}%"
        ]
        
        return "\n".join(summary_lines)


# pytest测试类
class TestAPIIntegration:
    """pytest测试类"""
    
    @pytest.fixture
    def test_runner(self):
        """测试运行器fixture"""
        runner = APITestRunner()
        yield runner
    
    def test_basic_connection(self, test_runner):
        """测试基本API连接"""
        result = test_runner.test_basic_connection()
        assert result["status"] in ["success", "mock"], f"连接测试失败: {result.get('message', '')}"
    
    def test_json_response(self, test_runner):
        """测试JSON响应"""
        result = test_runner.test_json_response()
        assert result["status"] in ["success", "mock"], f"JSON测试失败: {result.get('message', '')}"
    
    def test_event_extraction(self, test_runner):
        """测试事件抽取"""
        result = test_runner.test_event_extraction()
        assert result["status"] in ["success", "mock"], f"事件抽取测试失败: {result.get('message', '')}"


def main():
    """主函数 - 用于直接执行测试"""
    print("="*80)
    print("API集成测试")
    print("="*80)
    
    runner = APITestRunner()
    results = runner.run_all_tests()
    
    print("\n" + "="*80)
    print("测试结果汇总:")
    print("="*80)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    print(runner.get_test_summary())
    
    # 返回退出代码
    if results.get("status") in ["success"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
