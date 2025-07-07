#!/usr/bin/env python3
"""
阶段4测试运行脚本 - 因果路径构建模块(CPC)

此脚本用于运行阶段4的所有测试，包括：
1. 因果链接识别与构建
2. 图过滤与DAG构建算法
3. 环路检测与处理
4. 完整的因果路径构建流程

推荐运行 test_unified_cpc.py，这是整合了所有CPC功能测试的统一文件。
"""

import sys
import os
import unittest
import pytest

# TODO: Translate - Add project root directory to Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    print("======== 运行阶段4测试：因果路径构建模块(CPC) ========")
    
    # TODO: Translate - 方式1: UseunittestRun
    # test_loader = unittest.TestLoader()
    # test_suite = test_loader.discover(current_dir, pattern="test_*.py")
    # test_runner = unittest.TextTestRunner(verbosity=2)
    # test_runner.run(test_suite)
    
    # TODO: Translate - 方式2: UsepytestRun特定文件(推荐)
    # pytest.main(["-v", os.path.join(current_dir, "test_unified_cpc.py")])
    
    # TODO: Translate - 方式3: Run当前目录下所有Test
    pytest.main(["-v", current_dir])
