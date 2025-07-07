#!/usr/bin/env python3
"""
修复API测试卡住问题的工具脚本

该脚本提供了以下功能：
1. 重置API测试环境
2. 配置模拟模式测试
3. 增加API超时时间
4. 运行改进版的API测试
"""

import os
import sys
import argparse
from pathlib import Path

# TODO: Translate - Add project root directory to系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

def setup_parser():
    """设置命令行参数解析器"""
    parser = argparse.ArgumentParser(description="API测试修复工具")
    parser.add_argument("--mock", "-m", action="store_true", 
                        help="使用模拟模式（不进行实际API调用）")
    parser.add_argument("--timeout", "-t", type=int, default=30,
                        help="设置API调用超时时间（秒），默认30秒")
    parser.add_argument("--debug", "-d", action="store_true",
                        help="启用调试模式，显示更详细的错误信息")
    parser.add_argument("--use-improved", "-i", action="store_true",
                        help="使用改进版测试脚本，推荐选择")
    parser.add_argument("--compare", "-c", action="store_true",
                        help="运行原始和改进版脚本进行对比")
    return parser

def run_test_script(script_path, mock=False, timeout=30, debug=False):
    """运行测试脚本
    
    Args:
        script_path: 测试脚本路径
        mock: 是否使用模拟模式
        timeout: API超时时间
        debug: 是否启用调试模式
    """
    # Setenvironment variables
    env = os.environ.copy()
    
    # TODO: Translate - Configure模拟模式
    if mock:
        env["MOCK_API"] = "true"
        print(f"🔄 将以模拟模式运行: {script_path}")
    else:
        env["MOCK_API"] = "false"
        
    # TODO: Translate - Configure超时
    env["API_TIMEOUT"] = str(timeout)
    print(f"🕒 API超时设置为: {timeout}秒")
    
    # TODO: Translate - Configure调试模式
    if debug:
        env["DEBUG_MODE"] = "true"
        print("🐞 调试模式已启用")
    else:
        env["DEBUG_MODE"] = "false"
        
    # TODO: Translate - 确保脚本有Execute权限
    if not os.access(script_path, os.X_OK):
        print(f"🔧 正在设置脚本执行权限: {script_path}")
        os.chmod(script_path, 0o755)
        
    # TODO: Translate - Run脚本
    print(f"\n{'='*60}")
    print(f"运行测试脚本: {os.path.basename(script_path)}")
    print(f"{'='*60}")
    
    result = os.system(f"{sys.executable} {script_path}")
    
    print(f"\n脚本退出代码: {result}")
    return result

def main():
    """主函数"""
    parser = setup_parser()
    args = parser.parse_args()
    
    # TODO: Translate - 定义脚本路径
    original_script = os.path.join(current_dir, "test_api_integration.py")
    improved_script = os.path.join(current_dir, "test_api_integration_improved.py")
    
    # TODO: Translate - 确保改进版脚本有Execute权限
    if os.path.exists(improved_script) and not os.access(improved_script, os.X_OK):
        os.chmod(improved_script, 0o755)
    
    # TODO: Translate - 显示Execute信息
    print("API测试修复工具")
    print("="*60)
    
    if args.compare:
        # TODO: Translate - 先Run原始脚本
        print("\n🔄 正在运行原始测试脚本...")
        orig_result = run_test_script(original_script, args.mock, args.timeout, args.debug)
        
        # TODO: Translate - 然后Run改进版脚本
        print("\n🔄 正在运行改进版测试脚本...")
        imp_result = run_test_script(improved_script, args.mock, args.timeout, args.debug)
        
        # TODO: Translate - Output比较结果
        print("\n"+"="*60)
        print("脚本对比结果")
        print("="*60)
        print(f"原始脚本: {'通过 ✓' if orig_result == 0 else '失败 ✗'}")
        print(f"改进脚本: {'通过 ✓' if imp_result == 0 else '失败 ✗'}")
        
        # TODO: Translate - Output建议
        if orig_result != 0 and imp_result == 0:
            print("\n🎯 建议: 改进版脚本解决了问题，推荐使用改进版脚本")
        elif orig_result != 0 and imp_result != 0:
            print("\n⚠️ 注意: 两个脚本都存在问题，建议检查网络连接和API密钥")
        elif orig_result == 0 and imp_result == 0:
            print("\n✅ 两个脚本都可以正常工作")
            
    elif args.use_improved:
        # TODO: Translate - Use改进版脚本
        if not os.path.exists(improved_script):
            print(f"❌ 错误: 改进版脚本不存在: {improved_script}")
            return 1
            
        print("🚀 使用改进版API测试脚本...")
        run_test_script(improved_script, args.mock, args.timeout, args.debug)
    else:
        # TODO: Translate - Use原始脚本
        print("🔄 使用原始API测试脚本...")
        run_test_script(original_script, args.mock, args.timeout, args.debug)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
