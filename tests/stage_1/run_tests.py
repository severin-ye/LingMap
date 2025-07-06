#!/usr/bin/env python3
"""
阶段一测试：测试运行器

本文件用于统一运行阶段一（抽象接口与通用模型）的所有测试。
阶段一是《凡人修仙传》因果事件图谱生成系统的基础架构阶段，
主要测试系统的数据模型、工具类和接口定义是否正确实现。

功能说明：
1. 自动收集并组织阶段一的所有测试用例
   - 收集模型测试：EventItem、Chapter、CausalEdge、Treasure
   - 收集工具类测试：JsonLoader、TextSplitter
   - 收集接口测试：AbstractExtractor、AbstractRefiner、AbstractLinker、AbstractGraphRenderer
   
2. 提供统一的测试执行入口
   - 支持命令行参数控制测试详细程度
   - 提供清晰的测试结果输出
   - 捕获并美化显示测试对象的输出信息
   - 返回测试成功/失败状态

使用方法：
1. 直接运行: python tests/stage_1/run_tests.py
2. 显示详细输出: python tests/stage_1/run_tests.py -v
"""

import unittest
import sys
import os
import argparse

# Add project root directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Import beautified test output runner
# from tests.utils.pretty_test_runner import PrettyTestRunner

# Import stage 1 tests
from tests.stage_1.test_models import (
    TestEventModel,
    TestChapterModel,
    TestCausalEdgeModel,
    TestTreasureModel,
    TestJsonLoader,
    TestTextSplitter
)

from tests.stage_1.test_interfaces import (
    TestExtractorInterface,
    TestRefinerInterface,
    TestLinkerInterface,
    TestGraphRendererInterface
)

# Add hook to ensure all test class methods output something
import unittest
import functools

# Save original setUp method
original_setUp = unittest.TestCase.setUp

# Define a new setUp method to add output
def setup_with_output(self):
    original_setUp(self)
    print(f"\n测试对象: {self.__class__.__name__}.{self._testMethodName} 开始执行")
    print(f"-------------------------------------------")

# Replace original method
unittest.TestCase.setUp = setup_with_output


def run_stage1_tests(verbose=False):
    """
    运行阶段一的所有测试
    
    Args:
        verbose: 是否显示详细输出
    """
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add data model tests
    print("\n正在准备模型和工具类测试...")
    model_suite = unittest.TestSuite()
    model_suite.addTest(unittest.makeSuite(TestEventModel))
    model_suite.addTest(unittest.makeSuite(TestChapterModel))
    model_suite.addTest(unittest.makeSuite(TestCausalEdgeModel))
    model_suite.addTest(unittest.makeSuite(TestTreasureModel))
    model_suite.addTest(unittest.makeSuite(TestJsonLoader))
    model_suite.addTest(unittest.makeSuite(TestTextSplitter))
    
    # Add interface tests
    print("正在准备接口测试...")
    interface_suite = unittest.TestSuite()
    interface_suite.addTest(unittest.makeSuite(TestExtractorInterface))
    interface_suite.addTest(unittest.makeSuite(TestRefinerInterface))
    interface_suite.addTest(unittest.makeSuite(TestLinkerInterface))
    interface_suite.addTest(unittest.makeSuite(TestGraphRendererInterface))
    
    # Merge test suites
    suite.addTest(model_suite)
    suite.addTest(interface_suite)
    
    # Run tests
    verbosity = 2 if verbose else 1
    
    # Use standard test runner
    print("\n模型和工具类测试:")
    print("-" * 60)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # If in verbose mode, show full test statistics
    if verbose:
        print("\n详细测试统计:")
        print(f"运行的测试数: {result.testsRun}")
        print(f"失败的测试数: {len(result.failures)}")
        print(f"错误的测试数: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行阶段一测试：抽象接口与通用模型")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细测试输出")
    args = parser.parse_args()
    
    print("=" * 60)
    print("《凡人修仙传》因果事件图谱生成系统 - 阶段一测试")
    print("=" * 60)
    print("测试内容：数据模型、工具类和接口定义")
    
    success = run_stage1_tests(args.verbose)
    
    if success:
        print("\n所有测试通过！✅")
        sys.exit(0)
    else:
        print("\n测试失败！❌")
        sys.exit(1)
