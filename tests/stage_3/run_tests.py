#!/usr/bin/env python3
"""
《凡人修仙传》因果事件图谱生成系统 - 阶段三测试

本脚本用于运行第三阶段的测试，包括：
1. HAR 幻觉修复模块测试
2. 因果链构建模块测试

使用方法：
    python -m tests.stage_3.run_tests
"""

import unittest
import sys
import os
import time
from io import StringIO

# TODO: Translate - Add project root directory to Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.stage_3.test_hallucination_refine import TestHallucinationRefiner, TestHARResponseParsing
# TODO: Translate - 注意：causallinkingTest已移至阶段 4
# TODO: Translate - 以前的Import内容: 
# from tests.stage_3.test_causal_linking import (
#     TestCausalLinker, 
#     TestCausalEdgeResponseParsing, 
#     TestCausalLinkingIntegration
# )


def run_stage_3_tests():
    """运行第三阶段的所有测试"""
    
    print("============================================================")
    print("《凡人修仙传》因果事件图谱生成系统 - 阶段三测试")
    print("============================================================")
    print("测试内容：HAR幻觉修复和因果链构建模块")
    print()
    
    # TODO: Translate - 准备Test套件
    print("正在准备HAR幻觉修复模块测试...")
    print("正在准备因果链构建模块测试...")
    print()
    
    # TODO: Translate - CreateTest套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # TODO: Translate - 添加HARhallucinationrefineTest
    suite.addTests(loader.loadTestsFromTestCase(TestHallucinationRefiner))
    suite.addTests(loader.loadTestsFromTestCase(TestHARResponseParsing))
    
    # TODO: Translate - 注意：causal链BuildTest已经移动到阶段4
    # TODO: Translate - 之前的代码:
    # suite.addTests(loader.loadTestsFromTestCase(TestCausalLinker))
    # suite.addTests(loader.loadTestsFromTestCase(TestCausalEdgeResponseParsing))
    # suite.addTests(loader.loadTestsFromTestCase(TestCausalLinkingIntegration))
    
    # RunTest
    print("阶段三测试:")
    print("-" * 60)
    
    start_time = time.time()
    
    # TODO: Translate - CreateTestRun器
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        failfast=False
    )
    
    # RunTest
    result = runner.run(suite)
    
    # TODO: Translate - Get并显示Output
    test_output = stream.getvalue()
    print(test_output)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"阶段三测试耗时: {duration:.2f}秒")
    print()
    
    # TODO: Translate - 显示Test结果统计
    if result.wasSuccessful():
        print("所有测试通过！✅")
    else:
        print("部分测试失败或出错！❌")
        if result.failures:
            print(f"失败: {len(result.failures)}")
        if result.errors:
            print(f"错误: {len(result.errors)}")
    
    return result


if __name__ == "__main__":
    result = run_stage_3_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
