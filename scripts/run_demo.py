#!/usr/bin/env python3
"""
完整演示脚本，用于一键演示《凡人修仙传》因果图谱生成系统的全部功能
"""

import os
import sys
import argparse
import time
from pathlib import Path

# TODO: Translate - Get项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# TODO: Translate - Import相关模块
from api_gateway.main import setup_env, process_text
from scripts.check_env import check_python_version, check_dependencies, check_api_key


def run_complete_demo():
    """运行完整演示"""
    # TODO: Translate - 解析命令行参数
    parser = argparse.ArgumentParser(description="《凡人修仙传》因果图谱生成系统完整演示")
    parser.add_argument("--provider", "-p", choices=["openai", "deepseek"], default="deepseek",
                      help="LLM API提供商 (默认: deepseek)")
    parser.add_argument("--input", "-i", default="test.txt",
                      help="输入文件名，位于novel目录下 (默认: test.txt)")
    parser.add_argument("--output", "-o", default=None,
                      help="输出目录名 (默认: output_YYYY-MM-DD_HH-MM-SS)")
    args = parser.parse_args()
    
    # Setenvironment variables
    setup_env()
    
    print("\n" + "=" * 60)
    print(f"《凡人修仙传》因果图谱生成系统 - 完整演示")
    print("=" * 60)
    
    # TODO: Translate - 步骤1: Check环境
    print("\n【步骤1】检查环境...")
    python_ok = check_python_version()
    deps_ok = check_dependencies()
    api_ok = check_api_key()
    
    if not (python_ok and deps_ok and api_ok):
        print("\n环境检查未通过，请解决上述问题后再试。")
        return 1
    
    # TODO: Translate - 步骤2: 准备输入Output路径
    print("\n【步骤2】准备输入输出路径...")
    
    # TODO: Translate - 输入文件
    novel_dir = os.path.join(project_root, "novel")
    input_file = os.path.join(novel_dir, args.input)
    
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 {input_file} 不存在")
        return 1
    
    # TODO: Translate - Output目录
    if args.output:
        output_dir = os.path.join(project_root, args.output)
    else:
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join(project_root, f"output_{timestamp}")
    
    # TODO: Translate - CreateOutput目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"输入文件: {input_file}")
    print(f"输出目录: {output_dir}")
    print(f"API提供商: {args.provider}")
    
    # TODO: Translate - 步骤3: Process文本
    print("\n【步骤3】开始处理文本...")
    try:
        process_text(input_file, output_dir, provider=args.provider)
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        return 1
    
    # TODO: Translate - 步骤4: VerifyOutput
    print("\n【步骤4】验证输出文件...")
    
    # TODO: Translate - CheckGenerate的Mermaid文件
    mermaid_files = list(Path(output_dir).glob("*.mmd"))
    if mermaid_files:
        print("\n成功生成以下图谱文件:")
        for mmd_file in mermaid_files:
            print(f"- {mmd_file.name}")
            
        print("\n您可以在以下网站查看生成的图谱:")
        print("- Mermaid Live Editor: https://mermaid.live/")
        print("- 或使用VS Code的Mermaid插件")
    else:
        print("警告: 未找到生成的图谱文件")
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(run_complete_demo())
