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


def run_stage1_tests(verbose=False):
    """
    运行阶段一的所有测试
    
    Args:
        verbose: 是否显示详细输出
    """
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加数据模型测试
    suite.addTest(unittest.makeSuite(TestEventModel))
    suite.addTest(unittest.makeSuite(TestChapterModel))
    suite.addTest(unittest.makeSuite(TestCausalEdgeModel))
    suite.addTest(unittest.makeSuite(TestTreasureModel))
    suite.addTest(unittest.makeSuite(TestJsonLoader))
    suite.addTest(unittest.makeSuite(TestTextSplitter))
    
    # 添加接口测试
    suite.addTest(unittest.makeSuite(TestExtractorInterface))
    suite.addTest(unittest.makeSuite(TestRefinerInterface))
    suite.addTest(unittest.makeSuite(TestLinkerInterface))
    suite.addTest(unittest.makeSuite(TestGraphRendererInterface))
    
    # 运行测试
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    print("\n模型测试:")
    print("-" * 40)
    result = runner.run(suite)
    
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
