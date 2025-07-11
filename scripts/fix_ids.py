#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ID修复工具

使用统一ID处理器修复事件、图谱节点中的重复ID问题。
"""

import os
import sys
import argparse
from pathlib import Path

# 将项目根目录添加到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from common.utils.unified_id_processor import UnifiedIdProcessor


def main():
    """程序主入口"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="ID修复工具")
    parser.add_argument("--input", "-i", required=True, help="输入文件路径")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--type", "-t", choices=["event", "node"], default="event", 
                        help="ID类型：event-事件ID，node-节点ID")
    args = parser.parse_args()
    
    try:
        print(f"处理文件: {args.input}")
        
        # 确保输入文件存在
        if not os.path.exists(args.input):
            print(f"错误: 文件不存在: {args.input}")
            return 1
        
        # 设置输出路径
        output_path = args.output
        if not output_path:
            # 如果未指定输出路径，则基于输入路径生成
            input_path = Path(args.input)
            output_path = str(input_path.parent / f"{input_path.stem}_fixed{input_path.suffix}")
        
        # 使用统一ID处理器修复ID
        UnifiedIdProcessor.fix_duplicate_event_ids(args.input, output_path)
        print(f"已修复ID并保存到: {output_path}")
        return 0
        
    except Exception as e:
        print(f"处理失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
