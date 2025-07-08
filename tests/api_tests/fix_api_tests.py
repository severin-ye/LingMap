#!/usr/bin/env python3
"""
# [CN] 修复API测试卡住问题的工具脚本
# [EN] Tool script to fix API test hanging issues

# [CN] 该脚本提供了以下功能：
# [EN] This script provides the following features:
# [CN] 1. 重置API测试环境
# [EN] 1. Reset API test environment
# [CN] 2. 配置模拟模式测试
# [EN] 2. Configure mock mode testing
# [CN] 3. 增加API超时时间
# [EN] 3. Increase API timeout duration
# [CN] 4. 运行改进版的API测试
# [EN] 4. Run improved API tests
"""

import os
import sys
import argparse
from pathlib import Path

# [CN] 添加项目根目录到系统路径
# [EN] Add project root directory to system path
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

def setup_parser():
    """
    # [CN] 设置命令行参数解析器
    # [EN] Set up command line argument parser
    """
    # [CN] API测试修复工具
    # [EN] API test fix tool
    parser = argparse.ArgumentParser(description="# [CN] API测试修复工具 # [EN] API test fix tool")
    parser.add_argument("--mock", "-m", action="store_true", 
                        # [CN] 使用模拟模式（不进行实际API调用）
                        # [EN] Use mock mode (no actual API calls)
                        help="# [CN] 使用模拟模式（不进行实际API调用） # [EN] Use mock mode (no actual API calls)")
    parser.add_argument("--timeout", "-t", type=int, default=30,
                        # [CN] 设置API调用超时时间（秒），默认30秒
                        # [EN] Set API call timeout (seconds), default 30 seconds
                        help="# [CN] 设置API调用超时时间（秒），默认30秒 # [EN] Set API call timeout (seconds), default 30 seconds")
    parser.add_argument("--debug", "-d", action="store_true",
                        # [CN] 启用调试模式，显示更详细的错误信息
                        # [EN] Enable debug mode, show more detailed error information
                        help="# [CN] 启用调试模式，显示更详细的错误信息 # [EN] Enable debug mode, show more detailed error information")
    parser.add_argument("--use-improved", "-i", action="store_true",
                        # [CN] 使用改进版测试脚本，推荐选择
                        # [EN] Use improved test script, recommended choice
                        help="# [CN] 使用改进版测试脚本，推荐选择 # [EN] Use improved test script, recommended choice")
    parser.add_argument("--compare", "-c", action="store_true",
                        # [CN] 运行原始和改进版脚本进行对比
                        # [EN] Run original and improved scripts for comparison
                        help="# [CN] 运行原始和改进版脚本进行对比 # [EN] Run original and improved scripts for comparison")
    return parser

def run_test_script(script_path, mock=False, timeout=30, debug=False):
    """
    # [CN] 运行测试脚本
    # [EN] Run test script
    
    Args:
        # [CN] script_path: 测试脚本路径
        # [EN] script_path: Test script path
        # [CN] mock: 是否使用模拟模式
        # [EN] mock: Whether to use mock mode
        # [CN] timeout: API超时时间
        # [EN] timeout: API timeout duration
        # [CN] debug: 是否启用调试模式
        # [EN] debug: Whether to enable debug mode
    """
    # [CN] 设置环境变量
    # [EN] Set environment variables
    env = os.environ.copy()
    
    # [CN] 配置模拟模式
    # [EN] Configure mock mode
    if mock:
        env["MOCK_API"] = "true"
        # [CN] 将以模拟模式运行
        # [EN] Will run in mock mode
        print(f"# [CN] 🔄 将以模拟模式运行: {script_path}")
        print(f"# [EN] 🔄 Will run in mock mode: {script_path}")
    else:
        env["MOCK_API"] = "false"
        
    # [CN] 配置超时
    # [EN] Configure timeout
    env["API_TIMEOUT"] = str(timeout)
    # [CN] API超时设置为: {timeout}秒
    # [EN] API timeout set to: {timeout} seconds
    print(f"# [CN] 🕒 API超时设置为: {timeout}秒")
    print(f"# [EN] 🕒 API timeout set to: {timeout} seconds")
    
    # [CN] 配置调试模式
    # [EN] Configure debug mode
    if debug:
        env["DEBUG_MODE"] = "true"
        # [CN] 调试模式已启用
        # [EN] Debug mode enabled
        print("# [CN] 🐞 调试模式已启用")
        print("# [EN] 🐞 Debug mode enabled")
    else:
        env["DEBUG_MODE"] = "false"
        
    # [CN] 确保脚本有执行权限
    # [EN] Ensure script has execution permissions
    if not os.access(script_path, os.X_OK):
        # [CN] 正在设置脚本执行权限
        # [EN] Setting script execution permissions
        print(f"# [CN] 🔧 正在设置脚本执行权限: {script_path}")
        print(f"# [EN] 🔧 Setting script execution permissions: {script_path}")
        os.chmod(script_path, 0o755)
        
    # [CN] 运行脚本
    # [EN] Run script
    print(f"\n{'='*60}")
    # [CN] 运行测试脚本
    # [EN] Running test script
    print(f"# [CN] 运行测试脚本: {os.path.basename(script_path)}")
    print(f"# [EN] Running test script: {os.path.basename(script_path)}")
    print(f"{'='*60}")
    
    result = os.system(f"{sys.executable} {script_path}")
    
    # [CN] 脚本退出代码
    # [EN] Script exit code
    print(f"# [CN] 脚本退出代码: {result}")
    print(f"# [EN] Script exit code: {result}")
    return result

def main():
    """
    # [CN] 主函数
    # [EN] Main function
    """
    parser = setup_parser()
    args = parser.parse_args()
    
    # [CN] 定义脚本路径
    # [EN] Define script paths
    original_script = os.path.join(current_dir, "test_api_integration.py")
    improved_script = os.path.join(current_dir, "test_api_integration_improved.py")
    
    # [CN] 确保改进版脚本有执行权限
    # [EN] Ensure improved script has execution permissions
    if os.path.exists(improved_script) and not os.access(improved_script, os.X_OK):
        os.chmod(improved_script, 0o755)
    
    # [CN] 显示执行信息
    # [EN] Display execution information
    # [CN] API测试修复工具
    # [EN] API test fix tool
    print("# [CN] API测试修复工具")
    print("# [EN] API test fix tool")
    print("="*60)
    
    if args.compare:
        # [CN] 先运行原始脚本
        # [EN] First run original script
        print("# [CN] 🔄 正在运行原始测试脚本...")
        print("# [EN] 🔄 Running original test script...")
        orig_result = run_test_script(original_script, args.mock, args.timeout, args.debug)
        
        # [CN] 然后运行改进版脚本
        # [EN] Then run improved script
        print("# [CN] 🔄 正在运行改进版测试脚本...")
        print("# [EN] 🔄 Running improved test script...")
        imp_result = run_test_script(improved_script, args.mock, args.timeout, args.debug)
        
        # [CN] 输出比较结果
        # [EN] Output comparison results
        print("\n"+"="*60)
        # [CN] 脚本对比结果
        # [EN] Script comparison results
        print("# [CN] 脚本对比结果")
        print("# [EN] Script comparison results")
        print("="*60)
        # [CN] 原始脚本: 通过 ✓ / 失败 ✗
        # [EN] Original script: Pass ✓ / Fail ✗
        print(f"# [CN] 原始脚本: {'通过 ✓' if orig_result == 0 else '失败 ✗'}")
        print(f"# [EN] Original script: {'Pass ✓' if orig_result == 0 else 'Fail ✗'}")
        # [CN] 改进脚本: 通过 ✓ / 失败 ✗
        # [EN] Improved script: Pass ✓ / Fail ✗
        print(f"# [CN] 改进脚本: {'通过 ✓' if imp_result == 0 else '失败 ✗'}")
        print(f"# [EN] Improved script: {'Pass ✓' if imp_result == 0 else 'Fail ✗'}")
        
        # [CN] 输出建议
        # [EN] Output recommendations
        if orig_result != 0 and imp_result == 0:
            # [CN] 建议: 改进版脚本解决了问题，推荐使用改进版脚本
            # [EN] Recommendation: Improved script solved the problem, recommend using improved script
            print("# [CN] 🎯 建议: 改进版脚本解决了问题，推荐使用改进版脚本")
            print("# [EN] 🎯 Recommendation: Improved script solved the problem, recommend using improved script")
        elif orig_result != 0 and imp_result != 0:
            # [CN] 注意: 两个脚本都存在问题，建议检查网络连接和API密钥
            # [EN] Note: Both scripts have issues, recommend checking network connection and API key
            print("# [CN] ⚠️ 注意: 两个脚本都存在问题，建议检查网络连接和API密钥")
            print("# [EN] ⚠️ Note: Both scripts have issues, recommend checking network connection and API key")
        elif orig_result == 0 and imp_result == 0:
            # [CN] 两个脚本都可以正常工作
            # [EN] Both scripts work normally
            print("# [CN] ✅ 两个脚本都可以正常工作")
            print("# [EN] ✅ Both scripts work normally")
            
    elif args.use_improved:
        # [CN] 使用改进版脚本
        # [EN] Use improved script
        if not os.path.exists(improved_script):
            # [CN] 错误: 改进版脚本不存在
            # [EN] Error: Improved script does not exist
            print(f"# [CN] ❌ 错误: 改进版脚本不存在: {improved_script}")
            print(f"# [EN] ❌ Error: Improved script does not exist: {improved_script}")
            return 1
            
        # [CN] 使用改进版API测试脚本...
        # [EN] Using improved API test script...
        print("# [CN] 🚀 使用改进版API测试脚本...")
        print("# [EN] 🚀 Using improved API test script...")
        run_test_script(improved_script, args.mock, args.timeout, args.debug)
    else:
        # [CN] 使用原始脚本
        # [EN] Use original script
        # [CN] 使用原始API测试脚本...
        # [EN] Using original API test script...
        print("# [CN] 🔄 使用原始API测试脚本...")
        print("# [EN] 🔄 Using original API test script...")
        run_test_script(original_script, args.mock, args.timeout, args.debug)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
