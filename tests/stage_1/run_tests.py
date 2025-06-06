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

# 将项目根目录添加到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# 导入美化测试输出的运行器
from tests.utils.pretty_test_runner import PrettyTestRunner

# 导入阶段一测试
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

# 添加钩子，确保所有测试类的测试方法都会输出一些内容
import unittest
import functools

# 保存原始的setUp方法
original_setUp = unittest.TestCase.setUp

# 定义一个新的setUp方法，添加输出
def setup_with_output(self):
    original_setUp(self)
    print(f"\n测试对象: {self.__class__.__name__}.{self._testMethodName} 开始执行")
    print(f"-------------------------------------------")

# 替换原始方法
unittest.TestCase.setUp = setup_with_output


def run_stage1_tests(verbose=False):
    """
    运行阶段一的所有测试
    
    Args:
        verbose: 是否显示详细输出
    """
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加数据模型测试
    print("\n正在准备模型和工具类测试...")
    model_suite = unittest.TestSuite()
    model_suite.addTest(unittest.makeSuite(TestEventModel))
    model_suite.addTest(unittest.makeSuite(TestChapterModel))
    model_suite.addTest(unittest.makeSuite(TestCausalEdgeModel))
    model_suite.addTest(unittest.makeSuite(TestTreasureModel))
    model_suite.addTest(unittest.makeSuite(TestJsonLoader))
    model_suite.addTest(unittest.makeSuite(TestTextSplitter))
    
    # 添加接口测试
    print("正在准备接口测试...")
    interface_suite = unittest.TestSuite()
    interface_suite.addTest(unittest.makeSuite(TestExtractorInterface))
    interface_suite.addTest(unittest.makeSuite(TestRefinerInterface))
    interface_suite.addTest(unittest.makeSuite(TestLinkerInterface))
    interface_suite.addTest(unittest.makeSuite(TestGraphRendererInterface))
    
    # 合并测试套件
    suite.addTest(model_suite)
    suite.addTest(interface_suite)
    
    # 运行测试
    verbosity = 2 if verbose else 1
    
    # 使用美化的测试运行器
    print("\n模型和工具类测试:")
    print("-" * 60)
    runner = PrettyTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # 如果有详细模式，显示完整测试统计
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
print("测试开始")
