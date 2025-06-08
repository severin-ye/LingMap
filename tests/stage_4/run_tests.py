#!/usr/bin/env python3
"""
阶段4测试运行脚本 - 因果路径构建模块(CPC)

此脚本用于运行阶段4的所有测试，包括：
1. 因果链接识别与构建
2. 图过滤与DAG构建算法
3. 环路检测与处理
"""

import sys
import os
import unittest
import pytest

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    print("======== 运行阶段4测试：因果路径构建模块(CPC) ========")
    
    # 方式1: 使用unittest运行
    # test_loader = unittest.TestLoader()
    # test_suite = test_loader.discover(current_dir, pattern="test_*.py")
    # test_runner = unittest.TextTestRunner(verbosity=2)
    # test_runner.run(test_suite)
    
    # 方式2: 使用pytest运行(推荐)
    pytest.main(["-v", current_dir])
