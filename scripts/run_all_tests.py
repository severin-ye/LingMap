#!/usr/bin/env python3
"""
主测试脚本

运行所有模块的测试，提供统一的测试入口点
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

def run_test_script(script_name, description):
    """运行单个测试脚本"""
    print("="*100)
    print(f"运行测试: {description}")
    print("="*100)
    
    script_path = current_dir / script_name
    
    if not script_path.exists():
        print(f"❌ 测试脚本不存在: {script_path}")
        return False
    
    try:
        # 运行测试脚本
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        success = result.returncode == 0
        
        if success:
            print(f"✓ 测试 '{description}' 完成")
        else:
            print(f"❌ 测试 '{description}' 失败 (返回码: {result.returncode})")
        
        return success
        
    except subprocess.TimeoutExpired:
        print(f"❌ 测试 '{description}' 超时")
        return False
    except Exception as e:
        print(f"❌ 运行测试 '{description}' 时发生异常: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("🚀 开始运行完整测试套件")
    print("="*100)
    
    # 定义测试脚本和描述
    test_suites = [
        ("test_system_config.py", "系统配置和环境测试"),
        ("test_api_integration.py", "API集成测试"),
        ("test_event_extraction.py", "事件抽取模块测试"),
        ("test_causal_module.py", "因果链接模块测试")
    ]
    
    results = []
    
    for script_name, description in test_suites:
        try:
            success = run_test_script(script_name, description)
            results.append((description, success))
        except KeyboardInterrupt:
            print("\n❌ 用户中断测试")
            break
        except Exception as e:
            print(f"❌ 运行测试套件时发生异常: {str(e)}")
            results.append((description, False))
    
    # 输出总体测试结果
    print("\n" + "="*100)
    print("🏁 测试套件总结")
    print("="*100)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for description, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{description}: {status}")
    
    print(f"\n📊 总体结果: {passed}/{total} 测试套件通过")
    
    if passed == total:
        print("🎉 所有测试套件通过！系统集成成功！")
        print("\n🔧 下一步建议:")
        print("  1. 运行完整的端到端测试")
        print("  2. 测试实际的小说章节处理")
        print("  3. 验证图谱生成功能")
    elif passed > 0:
        print("⚠️  部分测试套件通过，请修复失败的测试")
        print("\n🔧 修复建议:")
        failed_tests = [desc for desc, result in results if not result]
        for test in failed_tests:
            print(f"  - 检查 {test} 的配置和依赖")
    else:
        print("❌ 所有测试套件失败，请检查基础配置")
        print("\n🔧 基础修复建议:")
        print("  1. 检查环境变量配置(.env文件)")
        print("  2. 验证DeepSeek API密钥")
        print("  3. 确认所有依赖包已安装")
        print("  4. 检查项目文件结构")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
