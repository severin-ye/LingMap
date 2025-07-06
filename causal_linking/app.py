import argparse
import os
import sys

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from causal_linking.controller.linker_controller import link_events


def main():
    """CAUSAL_LINKING 模块的主入口"""
    parser = argparse.ArgumentParser(description="分析事件之间的因果关系")
    parser.add_argument("--input", "-i", required=True, help="输入事件JSON文件")
    parser.add_argument("--output", "-o", required=True, help="输出因果关系JSON文件")
    
    args = parser.parse_args()
    
    link_events(args.input, args.output)


if __name__ == "__main__":
    main()
