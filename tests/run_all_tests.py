#!/usr/bin/env python3
"""
测试运行主脚本：用于运行所有阶段的测试

本文件是《凡人修仙传》因果事件图谱生成系统的测试主控脚本，
用于协调和执行系统各个阶段的测试，提供统一的测试入口和报告机制。

功能说明：
1. 测试执行控制：
   - 支持运行单个阶段的测试或所有阶段的测试
   - 提供命令行参数控制测试的详细程度和范围
   - 统一收集和报告测试结果
   
2. 测试阶段管理：
   - 阶段一：抽象接口与通用模型测试 (stage_1)
   - 后续阶段：根据系统开发进度逐步添加
   
3. 报告生成：
   - 提供测试通过/失败状态的总体报告
   - 支持详细模式显示每个测试用例的执行结果

使用方法：
1. 运行所有测试: python tests/run_all_tests.py
2. 运行特定阶段测试: python tests/run_all_tests.py -s {阶段号}
3. 显示详细输出: python tests/run_all_tests.py -v
"""

import os
import sys
import argparse
import importlib.util

# 将项目根目录添加到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)


def run_stage_tests(stage_num, verbose=False):
    """
    运行指定阶段的测试
    
    Args:
        stage_num: 阶段编号（1-7）
        verbose: 是否显示详细输出
    
    Returns:
        bool: 测试是否全部通过
    """
    stage_dir = f"stage_{stage_num}"
    run_tests_path = os.path.join(current_dir, stage_dir, "run_tests.py")
    
    if not os.path.exists(run_tests_path):
        print(f"错误：阶段 {stage_num} 的测试脚本不存在！")
        return False
    
    # 直接调用测试脚本
    cmd = [sys.executable, run_tests_path]
    if verbose:
        cmd.append('-v')
    
    try:
        result = os.system(' '.join(cmd))
        return result == 0
    except Exception as e:
        print(f"错误：运行阶段 {stage_num} 测试时出现异常：{e}")
        return False


def run_all_tests(verbose=False):
    """
    运行所有阶段的测试
    
    Args:
        verbose: 是否显示详细输出
    
    Returns:
        bool: 所有测试是否全部通过
    """
    all_success = True
    
    # 当前只有阶段1的测试
    stages = [1]
    
    for stage in stages:
        print(f"\n{'='*60}")
        print(f"运行阶段 {stage} 测试")
        print(f"{'='*60}")
        
        success = run_stage_tests(stage, verbose)
        if not success:
            all_success = False
    
    return all_success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="《凡人修仙传》因果事件图谱生成系统测试")
    parser.add_argument("-s", "--stage", type=int, choices=range(1, 8), help="指定要运行的测试阶段（1-7）")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细测试输出")
    args = parser.parse_args()
    
    print("\n《凡人修仙传》因果事件图谱生成系统 - 测试运行")
    
    if args.stage:
        success = run_stage_tests(args.stage, args.verbose)
    else:
        success = run_all_tests(args.verbose)
    
    if success:
        print("\n所有测试通过！✅")
        sys.exit(0)
    else:
        print("\n测试失败！❌")
        sys.exit(1)
