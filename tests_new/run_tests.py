#!/usr/bin/env python3
"""
统一测试运行器

用于运行新测试目录结构中的所有测试，替代原有的多个测试运行脚本。
支持不同的测试级别和模式。
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any
import json

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from common.utils.enhanced_logger import EnhancedLogger

logger = EnhancedLogger("test_runner", log_level="INFO")

class TestRunner:
    """统一测试运行器"""
    
    def __init__(self):
        self.tests_dir = current_dir
        self.results = []
    
    def run_pytest(self, test_path: str, extra_args: List[str] = None) -> Dict[str, Any]:
        """运行pytest并返回结果"""
        cmd = ["python", "-m", "pytest", test_path, "-v", "--tb=short"]
        if extra_args is not None:
            cmd.extend(extra_args)
        
        logger.info(f"运行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.tests_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            return {
                "test_path": test_path,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            logger.error(f"测试超时: {test_path}")
            return {
                "test_path": test_path,
                "returncode": -1,
                "stdout": "",
                "stderr": "测试超时",
                "success": False
            }
        except Exception as e:
            logger.error(f"运行测试失败: {e}")
            return {
                "test_path": test_path,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """运行单元测试"""
        logger.info("开始运行单元测试...")
        return self.run_pytest("unit/")
    
    def run_integration_tests(self, mock_mode: bool = False) -> Dict[str, Any]:
        """运行集成测试"""
        logger.info("开始运行集成测试...")
        extra_args = []
        if mock_mode:
            # 设置模拟模式环境变量
            os.environ["MOCK_API"] = "true"
            logger.info("启用模拟模式")
        return self.run_pytest("integration/", extra_args)
    
    def run_e2e_tests(self, mock_mode: bool = False) -> Dict[str, Any]:
        """运行端到端测试"""
        logger.info("开始运行端到端测试...")
        extra_args = []
        if mock_mode:
            os.environ["MOCK_API"] = "true"
            logger.info("启用模拟模式")
        return self.run_pytest("e2e/", extra_args)
    
    def run_utils_tests(self) -> Dict[str, Any]:
        """运行工具测试"""
        logger.info("开始运行工具测试...")
        return self.run_pytest("utils/")
    
    def run_specific_test(self, test_file: str, mock_mode: bool = False) -> Dict[str, Any]:
        """运行特定的测试文件"""
        logger.info(f"运行特定测试: {test_file}")
        if mock_mode:
            os.environ["MOCK_API"] = "true"
        return self.run_pytest(test_file)
    
    def run_all_tests(self, mock_mode: bool = False, quick_mode: bool = False) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("开始运行所有测试...")
        
        if mock_mode:
            os.environ["MOCK_API"] = "true"
            logger.info("启用模拟模式")
        
        all_results = []
        total_tests = 0
        passed_tests = 0
        
        # 定义测试套件
        test_suites = [
            ("单元测试", self.run_unit_tests),
            ("工具测试", self.run_utils_tests),
        ]
        
        # 只在非快速模式下运行集成和E2E测试
        if not quick_mode:
            test_suites.extend([
                ("集成测试", lambda: self.run_integration_tests(mock_mode)),
                ("端到端测试", lambda: self.run_e2e_tests(mock_mode))
            ])
        
        for suite_name, test_func in test_suites:
            logger.info(f"\n{'='*60}")
            logger.info(f"运行 {suite_name}")
            logger.info(f"{'='*60}")
            
            result = test_func()
            all_results.append({
                "suite": suite_name,
                "result": result
            })
            
            if result["success"]:
                logger.info(f"✓ {suite_name} 通过")
                passed_tests += 1
            else:
                logger.error(f"✗ {suite_name} 失败")
                if result["stderr"]:
                    logger.error(f"错误信息: {result['stderr'][:500]}...")
            
            total_tests += 1
        
        # 汇总结果
        summary = {
            "total_suites": total_tests,
            "passed_suites": passed_tests,
            "failed_suites": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "results": all_results,
            "mock_mode": mock_mode,
            "quick_mode": quick_mode
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """打印测试汇总"""
        logger.info("\n" + "="*80)
        logger.info("测试汇总报告")
        logger.info("="*80)
        
        print(f"总测试套件: {summary['total_suites']}")
        print(f"通过套件: {summary['passed_suites']}")
        print(f"失败套件: {summary['failed_suites']}")
        print(f"成功率: {summary['success_rate']:.1f}%")
        
        if summary.get('mock_mode'):
            print("模式: 模拟模式")
        if summary.get('quick_mode'):
            print("模式: 快速模式")
        
        print("\n详细结果:")
        for item in summary['results']:
            suite = item['suite']
            result = item['result']
            status = "✓ 通过" if result['success'] else "✗ 失败"
            print(f"  {suite}: {status}")
        
        logger.info("="*80)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="统一测试运行器")
    parser.add_argument("--type", choices=["unit", "integration", "e2e", "utils", "all"], 
                       default="all", help="测试类型")
    parser.add_argument("--mock", action="store_true", help="启用模拟模式")
    parser.add_argument("--quick", action="store_true", help="快速模式(只运行单元测试和工具测试)")
    parser.add_argument("--file", help="运行特定的测试文件")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.logger.setLevel("DEBUG")
    
    runner = TestRunner()
    
    try:
        if args.file:
            # 运行特定文件
            result = runner.run_specific_test(args.file, args.mock)
            success = result["success"]
            if result["stdout"]:
                print(result["stdout"])
            if result["stderr"]:
                print(result["stderr"], file=sys.stderr)
        
        elif args.type == "unit":
            result = runner.run_unit_tests()
            success = result["success"]
            if result["stdout"]:
                print(result["stdout"])
        
        elif args.type == "integration":
            result = runner.run_integration_tests(args.mock)
            success = result["success"]
            if result["stdout"]:
                print(result["stdout"])
        
        elif args.type == "e2e":
            result = runner.run_e2e_tests(args.mock)
            success = result["success"]
            if result["stdout"]:
                print(result["stdout"])
        
        elif args.type == "utils":
            result = runner.run_utils_tests()
            success = result["success"]
            if result["stdout"]:
                print(result["stdout"])
        
        else:  # all
            summary = runner.run_all_tests(args.mock, args.quick)
            runner.print_summary(summary)
            success = summary["failed_suites"] == 0
        
        # 返回适当的退出代码
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试运行器出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
