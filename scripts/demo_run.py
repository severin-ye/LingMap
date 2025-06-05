#!/usr/bin/env python3
"""
示例运行脚本，用于测试《凡人修仙传》因果图谱生成系统的完整流程
"""

import os
import sys
from pathlib import Path

# 获取项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from api_gateway.main import process_text, setup_env
import argparse


def main():
    """
    运行示例流程
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="《凡人修仙传》因果图谱生成系统示例运行")
    parser.add_argument("--provider", "-p", choices=["openai", "deepseek"], default="deepseek",
                      help="LLM API提供商 (默认: deepseek)")
    args = parser.parse_args()
    
    # 设置环境变量
    setup_env()
    
    # 获取测试文本路径
    novel_dir = os.path.join(project_root, "novel")
    test_file = os.path.join(novel_dir, "test.txt")
    
    # 输出目录
    output_dir = os.path.join(project_root, "output")
    
    print(f"=== 《凡人修仙传》因果图谱生成系统示例运行 ===")
    print(f"测试文件: {test_file}")
    print(f"输出目录: {output_dir}")
    print(f"API提供商: {args.provider}")
    print("=" * 50)
    
    # 如果没有测试文件，输出错误信息
    if not os.path.exists(test_file):
        print(f"错误: 测试文件 {test_file} 不存在")
        print(f"请将小说文本文件放在 {novel_dir} 目录下，并命名为 'test.txt'")
        return
    
    # 处理文本
    process_text(test_file, output_dir, provider=args.provider)
    
    # 输出完成信息
    print("\n=== 示例运行完成 ===")
    print(f"请查看 {output_dir} 目录下的输出文件")
    
    # 检查是否生成了 Mermaid 文件
    mermaid_files = list(Path(output_dir).glob("*.mmd"))
    if mermaid_files:
        print("\n图谱文件已生成:")
        for mmd_file in mermaid_files:
            print(f"- {mmd_file}")
        print("\n您可以在 Mermaid Live Editor (https://mermaid.live/) 查看生成的图谱")


if __name__ == "__main__":
    main()
