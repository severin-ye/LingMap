#!/usr/bin/env python3
"""
阶段二测试：测试运行器

本文件用于统一运行阶段二（文本摄入和事件抽取）的所有测试。
阶段二是《凡人修仙传》因果事件图谱生成系统的输入处理阶段，
主要测试系统的文本摄入和事件抽取模块是否正确实现。

功能说明：
1. 自动收集并组织阶段二的所有测试用例
   - 收集文本摄入测试：ChapterLoader
   - 收集事件抽取测试：EventExtractor, LLMClient
   
2. 提供统一的测试执行入口
   - 支持命令行参数控制测试详细程度
   - 提供清晰的测试结果输出
   - 返回测试成功/失败状态

使用方法：
1. 直接运行: python tests/stage_2/run_tests.py
2. 显示详细输出: python tests/stage_2/run_tests.py -v
"""

import unittest
import sys
import os
import argparse
import time

# TODO: Translate - Add project root directory to路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# TODO: Translate - Import阶段二Test
from tests.stage_2.test_text_ingestion import TestChapterLoader
from tests.stage_2.test_event_extraction import TestEventExtractor


def run_stage2_tests(verbose=False) -> bool:
    """
    运行阶段二测试
    
    Args:
        verbose: 是否显示详细输出
    
    Returns:
        测试是否全部通过
    """
    # TODO: Translate - CreateTest套件
    suite = unittest.TestSuite()
    
    # TODO: Translate - 添加文本摄入Test
    print("\n正在准备文本摄入模块测试...")
    text_suite = unittest.TestSuite()
    text_suite.addTest(unittest.makeSuite(TestChapterLoader))
    
    # TODO: Translate - 添加eventExtractTest
    print("正在准备事件抽取模块测试...")
    event_suite = unittest.TestSuite()
    event_suite.addTest(unittest.makeSuite(TestEventExtractor))
    
    # TODO: Translate - 合并Test套件
    suite.addTest(text_suite)
    suite.addTest(event_suite)
    
    # RunTest
    verbosity = 2 if verbose else 1
    
    # TODO: Translate - Use标准的TestRun器
    print("\n阶段二测试:")
    print("-" * 60)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # TODO: Translate - 如果有详细模式，显示完整Test统计
    if verbose:
        print("\n详细测试统计:")
        print(f"运行的测试数: {result.testsRun}")
        print(f"失败的测试数: {len(result.failures)}")
        print(f"错误的测试数: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行阶段二测试：文本摄入和事件抽取")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细测试输出")
    args = parser.parse_args()
    
    print("=" * 60)
    print("《凡人修仙传》因果事件图谱生成系统 - 阶段二测试")
    print("=" * 60)
    print("测试内容：文本摄入和事件抽取模块")
    
    start_time = time.time()
    success = run_stage2_tests(args.verbose)
    end_time = time.time()
    
    print(f"\n阶段二测试耗时: {end_time - start_time:.2f}秒")
    
    if success:
        print("\n所有测试通过！✅")
        sys.exit(0)
    else:
        print("\n测试失败！❌")
        sys.exit(1)
