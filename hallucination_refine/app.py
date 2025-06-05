import argparse
import os
import sys

# 将项目根目录添加到路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hallucination_refine.controller.har_controller import refine_events


def main():
    """HALLUCINATION_REFINE 模块的主入口"""
    parser = argparse.ArgumentParser(description="对事件进行幻觉检测和修复")
    parser.add_argument("--input", "-i", required=True, help="输入事件JSON文件")
    parser.add_argument("--output", "-o", required=True, help="输出精修后的事件JSON文件")
    parser.add_argument("--context", "-c", help="支持精修的上下文文件（可选）")
    
    args = parser.parse_args()
    
    refine_events(args.input, args.output, args.context)


if __name__ == "__main__":
    main()
