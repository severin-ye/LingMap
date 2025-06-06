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
   - 使用美化输出格式显示测试对象的输出
   - 支持详细模式显示每个测试用例的执行结果和耗时

使用方法：
1. 运行所有测试: python tests/run_all_tests.py
2. 运行特定阶段测试: python tests/run_all_tests.py -s {阶段号}
3. 显示详细输出: python tests/run_all_tests.py -v
"""

import os
import sys
import argparse
import importlib.util
import time

# 将项目根目录添加到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 定义终端颜色
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def import_test_module(stage_num):
    """
    导入指定阶段的测试模块
    
    Args:
        stage_num: 阶段编号（1-7）
        
    Returns:
        导入的模块或None
    """
    stage_dir = f"stage_{stage_num}"
    run_tests_path = os.path.join(current_dir, stage_dir, "run_tests.py")
    
    if not os.path.exists(run_tests_path):
        print(f"{Colors.RED}错误：阶段 {stage_num} 的测试脚本不存在！{Colors.END}")
        return None
    
    # 构建模块名
    module_name = f"tests.{stage_dir}.run_tests"
    
    # 导入模块
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        print(f"{Colors.RED}错误：导入阶段 {stage_num} 测试模块失败：{e}{Colors.END}")
        return None


def run_stage_tests(stage_num, verbose=False):
    """
    运行指定阶段的测试
    
    Args:
        stage_num: 阶段编号（1-7）
        verbose: 是否显示详细输出
    
    Returns:
        bool: 测试是否全部通过
    """
    print(f"{Colors.CYAN}准备运行阶段 {stage_num} 测试...{Colors.END}")
    
    # 尝试导入测试模块
    test_module = import_test_module(stage_num)
    if not test_module:
        return False
    
    # 使用模块中的测试运行函数
    try:
        start_time = time.time()
        print(f"{Colors.CYAN}开始运行阶段 {stage_num} 测试...{Colors.END}")
        
        # 调用模块中的测试运行函数
        if hasattr(test_module, f"run_stage{stage_num}_tests"):
            run_func = getattr(test_module, f"run_stage{stage_num}_tests")
            success = run_func(verbose)
        else:
            # 回退到通过命令行运行
            cmd = [sys.executable, "-m", f"tests.stage_{stage_num}.run_tests"]
            if verbose:
                cmd.append('-v')
            result = os.system(' '.join(cmd))
            success = result == 0
            
        end_time = time.time()
        
        # 显示测试耗时
        print(f"\n阶段 {stage_num} 测试耗时: {Colors.YELLOW}{end_time - start_time:.2f}秒{Colors.END}")
        
        return success
    except Exception as e:
        print(f"{Colors.RED}错误：运行阶段 {stage_num} 测试时出现异常：{e}{Colors.END}")
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
    
    # 当前有阶段1和阶段2的测试
    stages = [1, 2]
    
    # 记录总体测试开始时间
    overall_start_time = time.time()
    
    for stage in stages:
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"运行阶段 {stage} 测试")
        print(f"{'='*60}{Colors.END}")
        
        success = run_stage_tests(stage, verbose)
        if not success:
            all_success = False
    
    # 显示总测试耗时
    overall_end_time = time.time()
    print(f"\n{Colors.BOLD}总测试耗时: {Colors.YELLOW}{overall_end_time - overall_start_time:.2f}秒{Colors.END}")
    
    return all_success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="《凡人修仙传》因果事件图谱生成系统测试")
    parser.add_argument("-s", "--stage", type=int, choices=range(1, 8), help="指定要运行的测试阶段（1-7）")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细测试输出")
    args = parser.parse_args()
    
    print(f"\n{Colors.BOLD}《凡人修仙传》因果事件图谱生成系统 - 测试运行{Colors.END}")
    print(f"{Colors.CYAN}提示：可直接运行 'python -m tests.run_all_tests' 执行所有测试{Colors.END}")
    
    if args.stage:
        success = run_stage_tests(args.stage, args.verbose)
    else:
        success = run_all_tests(args.verbose)
    
    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}所有测试通过！✅{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}测试失败！❌{Colors.END}")
        sys.exit(1)
