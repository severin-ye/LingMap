#!/usr/bin/env python3
"""
第六阶段测试运行器

运行所有第六阶段的测试，包括：
1. API网关和CLI接口测试
2. 端到端集成测试
3. 错误处理和异常情况测试
4. 性能和扩展性测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# 导入测试模块
from tests.stage_6.test_api_gateway_cli import run_tests as run_api_cli_tests
from tests.stage_6.test_end_to_end_integration import run_tests as run_integration_tests


def main():
    """运行第六阶段所有测试"""
    print("🚀 开始运行第六阶段测试：集成与统一调用接口")
    print("=" * 100)
    
    all_success = True
    
    # 运行API网关和CLI接口测试
    print("\n📋 1. API网关和CLI接口测试")
    print("-" * 50)
    try:
        success1 = run_api_cli_tests()
        if not success1:
            all_success = False
            print("❌ API网关和CLI接口测试失败")
        else:
            print("✅ API网关和CLI接口测试通过")
    except Exception as e:
        print(f"❌ API网关和CLI接口测试执行异常: {e}")
        all_success = False
    
    # 运行端到端集成测试
    print("\n🔗 2. 端到端集成测试")
    print("-" * 50)
    try:
        success2 = run_integration_tests()
        if not success2:
            all_success = False
            print("❌ 端到端集成测试失败")
        else:
            print("✅ 端到端集成测试通过")
    except Exception as e:
        print(f"❌ 端到端集成测试执行异常: {e}")
        all_success = False
    
    # 输出最终结果
    print("\n" + "=" * 100)
    print("第六阶段测试最终结果")
    print("=" * 100)
    
    if all_success:
        print("🎉 所有第六阶段测试均通过！")
        print("\n✅ 测试通过的模块:")
        print("   • API网关统一入口功能")
        print("   • CLI命令行接口")
        print("   • 端到端流程集成")
        print("   • 环境设置和检查")
        print("   • 错误处理机制")
        print("   • 性能和扩展性")
        
        print("\n🎯 第六阶段验证完成:")
        print("   • 统一调用接口工作正常")
        print("   • CLI参数解析正确")
        print("   • 完整流程可端到端运行")
        print("   • 系统具备生产就绪能力")
        
    else:
        print("❌ 部分第六阶段测试失败")
        print("请检查上述测试输出，修复相关问题后重新运行测试")
    
    return all_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
