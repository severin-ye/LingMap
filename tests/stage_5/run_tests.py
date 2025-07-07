#!/usr/bin/env python3
"""
《凡人修仙传》因果事件图谱生成系统 - 阶段五测试

本脚本用于运行第五阶段的测试，包括：
1. 图谱构建模块测试
2. Mermaid 渲染器功能测试
3. 颜色映射工具测试

使用方法：
    python -m tests.stage_5.run_tests
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

from tests.stage_5.test_mermaid_renderer import TestMermaidRenderer
from tests.stage_5.test_color_map import TestColorMap
from tests.stage_5.test_graph_controller import TestGraphController


def run_stage5_tests(verbose=False):
    """运行第五阶段的所有测试"""
    
    print("============================================================")
    print("《凡人修仙传》因果事件图谱生成系统 - 阶段五测试")
    print("============================================================")
    print("测试内容：图谱构建与可视化输出模块")
    print()
    
    # TODO: Translate - 准备Test套件
    print("正在准备图谱构建模块测试...")
    print("正在准备Mermaid渲染器测试（含孤立节点连接功能）...")
    print("正在准备颜色映射工具测试...")
    print()
    
    # TODO: Translate - CreateTest套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # TODO: Translate - 添加Mermaid渲染器Test
    suite.addTests(loader.loadTestsFromTestCase(TestMermaidRenderer))
    
    # TODO: Translate - 添加颜色映射工具Test
    suite.addTests(loader.loadTestsFromTestCase(TestColorMap))
    
    # TODO: Translate - 添加图谱控制器Test
    suite.addTests(loader.loadTestsFromTestCase(TestGraphController))
    
    # RunTest
    print("阶段五测试:")
    print("-" * 60)
    
    start_time = time.time()
    
    # TODO: Translate - CreateTestRun器
    verbosity = 2 if verbose else 1
    
    # TODO: Translate - 如果不是详细模式，捕获Output
    if not verbose:
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=verbosity,
            failfast=False
        )
    else:
        runner = unittest.TextTestRunner(
            verbosity=verbosity,
            failfast=False
        )
    
    # RunTest
    result = runner.run(suite)
    
    # TODO: Translate - Get并显示Output
    if not verbose and hasattr(result, 'stream'):
        test_output = stream.getvalue()
        print(test_output)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"阶段五测试耗时: {duration:.2f}秒")
    print()
    
    # TODO: Translate - 显示Test结果统计
    if result.wasSuccessful():
        print("所有测试通过！✅")
        return True
    else:
        print("部分测试失败或出错！❌")
        if result.failures:
            print(f"失败: {len(result.failures)}")
        if result.errors:
            print(f"错误: {len(result.errors)}")
        return False


if __name__ == "__main__":
    # TODO: Translate - 支持通过命令行参数控制Output详细程度
    import argparse
    parser = argparse.ArgumentParser(description="运行阶段五测试")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细测试输出")
    args = parser.parse_args()
    
    success = run_stage5_tests(args.verbose)
    sys.exit(0 if success else 1)
