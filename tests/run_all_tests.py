#!/usr/bin/env python3
"""
运行所有测试脚本

这个脚本用于运行所有迁移到tests目录中的测试，按类别组织执行测试。
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import argparse

# TODO: Translate - Add project root directory to路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# TODO: Translate - 定义终端颜色
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def get_test_files(test_dir):
    """获取指定目录中的所有测试文件，优先选择改进版测试文件"""
    result = []
    if not os.path.exists(test_dir):
        return result
    
    # TODO: Translate - 收集目录中的所有Test文件
    regular_tests = []
    improved_tests = []
    
    for file in os.listdir(test_dir):
        if file.startswith('test_') and file.endswith('.py'):
            if 'improved' in file:
                improved_tests.append(os.path.join(test_dir, file))
            else:
                regular_tests.append(os.path.join(test_dir, file))
    
    # TODO: Translate - 对于每个常规Test文件，Check是否存在改进版
    for test in regular_tests:
        base_name = os.path.basename(test)
        name_without_ext = os.path.splitext(base_name)[0]
        
        # TODO: Translate - Check是否有对应的改进版Test (test_xxx_improved.py)
        improved_version = os.path.join(test_dir, f"{name_without_ext}_improved.py")
        if os.path.exists(improved_version):
            # TODO: Translate - 存在改进版，Use改进版替代原版
            result.append(improved_version)
        else:
            # TODO: Translate - 不存在改进版，Use原版
            result.append(test)
    
    # TODO: Translate - 添加没有对应原始版本的改进版Test
    for improved_test in improved_tests:
        improved_name = os.path.basename(improved_test)
        potential_original = improved_name.replace('_improved', '')
        
        if not os.path.exists(os.path.join(test_dir, potential_original)):
            result.append(improved_test)
    
    return result

def run_test(test_file, verbose=False):
    """运行单个测试文件"""
    is_improved = "improved" in os.path.basename(test_file)
    file_label = os.path.basename(test_file)
    
    # TODO: Translate - 对于APITest，如果Use的是改进版，添加特殊标记
    if "api" in test_file and is_improved:
        print(f"{Colors.CYAN}运行测试: {file_label} {Colors.GREEN}[增强版]{Colors.END}")
    else:
        print(f"{Colors.CYAN}运行测试: {file_label}{Colors.END}")
    
    start_time = time.time()
    
    # TODO: Translate - 为APITestSet额外的environment variables
    env = os.environ.copy()
    if "api" in test_file:
        # TODO: Translate - 默认UseMOCK_API模式以避免实际API调用
        if "MOCK_API" not in env:
            env["MOCK_API"] = "true"
            print(f"{Colors.YELLOW}自动启用API模拟模式 (MOCK_API=true){Colors.END}")
    
    try:
        # TODO: Translate - RunTest文件
        process = subprocess.Popen(
            [sys.executable, test_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env
        )
        stdout, stderr = process.communicate()
        
        elapsed_time = time.time() - start_time
        
        # TODO: Translate - Output结果
        if process.returncode == 0:
            print(f"{Colors.GREEN}✓ 测试通过 {file_label} ({elapsed_time:.2f}秒){Colors.END}")
            if verbose:
                print(f"{Colors.BLUE}输出:{Colors.END}")
                print(stdout)
            return True
        else:
            print(f"{Colors.RED}✗ 测试失败 {file_label} ({elapsed_time:.2f}秒){Colors.END}")
            print(f"{Colors.RED}错误信息:{Colors.END}")
            if stderr:
                print(stderr)
            else:
                print(stdout)
            return False
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"{Colors.RED}✗ 测试运行出错 {file_label} ({elapsed_time:.2f}秒): {str(e)}{Colors.END}")
        return False

def run_test_category(category_dir, category_name, verbose=False):
    """运行一个类别的所有测试"""
    print(f"\n{Colors.HEADER}=== 运行{category_name}测试 ==={Colors.END}")
    
    test_files = get_test_files(category_dir)
    if not test_files:
        print(f"{Colors.YELLOW}没有找到{category_name}测试文件{Colors.END}")
        return 0, 0
    
    passed_count = 0
    failed_count = 0
    
    for test_file in test_files:
        success = run_test(test_file, verbose)
        if success:
            passed_count += 1
        else:
            failed_count += 1
            
    return passed_count, failed_count

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行测试脚本")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细输出")
    parser.add_argument("-c", "--category", type=str, help="仅运行指定类别的测试 (api, causal_linking, event_extraction, integration, utils)")
    parser.add_argument("--no-mock", action="store_true", help="不使用模拟模式进行API测试（实际调用API）")
    parser.add_argument("--timeout", type=int, default=30, help="API调用超时时间（秒），默认30秒")
    args = parser.parse_args()
    
    # TODO: Translate - Setenvironment variables，控制APITest行为
    if not args.no_mock:
        os.environ["MOCK_API"] = "true"
    else:
        os.environ["MOCK_API"] = "false"
        print(f"{Colors.YELLOW}警告: API测试将实际调用API (--no-mock){Colors.END}")
        
    os.environ["API_TIMEOUT"] = str(args.timeout)
    
    # TODO: Translate - Test类别Configure
    test_categories = {
        "api": ("API测试", os.path.join(current_dir, "api_tests")),
        "causal_linking": ("因果链接测试", os.path.join(current_dir, "causal_linking_tests")),
        "event_extraction": ("事件抽取测试", os.path.join(current_dir, "event_extraction_tests")),
        "integration": ("集成测试", os.path.join(current_dir, "integration_tests")),
        "utils": ("工具测试", os.path.join(current_dir, "utils_tests")),
    }
    
    start_time = time.time()
    test_report = []
    total_passed = 0
    total_failed = 0
    
    print(f"{Colors.BOLD}{Colors.HEADER}开始运行测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    # TODO: Translate - 如果指定了类别，只Run该类别的Test
    if args.category:
        if args.category not in test_categories:
            print(f"{Colors.RED}错误：未知测试类别 '{args.category}'。可用类别: {', '.join(test_categories.keys())}{Colors.END}")
            return 1
        
        category_name, category_dir = test_categories[args.category]
        passed, failed = run_test_category(category_dir, category_name, args.verbose)
        total_passed += passed
        total_failed += failed
        test_report.append((args.category, passed, failed))
    else:
        # TODO: Translate - Run所有类别的Test
        for category, (name, directory) in test_categories.items():
            passed, failed = run_test_category(directory, name, args.verbose)
            total_passed += passed
            total_failed += failed
            test_report.append((category, passed, failed))
    
    # TODO: Translate - OutputTest总结
    total_time = time.time() - start_time
    total_tests = total_passed + total_failed
    
    print(f"\n{Colors.HEADER}=== 测试报告总结 ==={Colors.END}")
    for category, passed, failed in test_report:
        if passed + failed > 0:
            print(f"{category}: {Colors.GREEN}通过 {passed}{Colors.END}, {Colors.RED if failed else Colors.GREEN}失败 {failed}{Colors.END}")
    
    print(f"\n总测试结果: {Colors.GREEN if total_failed == 0 else Colors.RED}通过 {total_passed}/{total_tests} ({total_passed/total_tests*100 if total_tests else 0:.1f}%){Colors.END}")
    print(f"总耗时: {total_time:.2f} 秒")
    print(f"{Colors.BOLD}{Colors.HEADER}测试完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
