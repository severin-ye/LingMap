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

# Add project root directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Define terminal colors
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
    """获取指定目录中的所有测试文件"""
    result = []
    if not os.path.exists(test_dir):
        return result
        
    for file in os.listdir(test_dir):
        if file.startswith('test_') and file.endswith('.py'):
            result.append(os.path.join(test_dir, file))
    return result

def run_test(test_file, verbose=False):
    """运行单个测试文件"""
    print(f"{Colors.CYAN}运行测试: {os.path.basename(test_file)}{Colors.END}")
    
    start_time = time.time()
    
    try:
        # Run test file
        process = subprocess.Popen(
            [sys.executable, test_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        
        elapsed_time = time.time() - start_time
        
        # Output result
        if process.returncode == 0:
            print(f"{Colors.GREEN}✓ 测试通过 {os.path.basename(test_file)} ({elapsed_time:.2f}秒){Colors.END}")
            if verbose:
                print(f"{Colors.BLUE}输出:{Colors.END}")
                print(stdout)
            return True
        else:
            print(f"{Colors.RED}✗ 测试失败 {os.path.basename(test_file)} ({elapsed_time:.2f}秒){Colors.END}")
            print(f"{Colors.RED}错误信息:{Colors.END}")
            if stderr:
                print(stderr)
            else:
                print(stdout)
            return False
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"{Colors.RED}✗ 测试运行出错 {os.path.basename(test_file)} ({elapsed_time:.2f}秒): {str(e)}{Colors.END}")
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
    args = parser.parse_args()
    
    # Test category configuration
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
    
    # If a category is specified, only run tests for that category
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
        # Run tests for all categories
        for category, (name, directory) in test_categories.items():
            passed, failed = run_test_category(directory, name, args.verbose)
            total_passed += passed
            total_failed += failed
            test_report.append((category, passed, failed))
    
    # Output test summary
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
