import argparse
import os
import sys

# [CN] 将项目根目录添加到路径中
# [EN] Add the project root directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from causal_linking.controller.linker_controller import link_events


def main():
    """
    # [CN] CAUSAL_LINKING 模块的主入口
    # [EN] Main entry point for CAUSAL_LINKING module
    """
    parser = argparse.ArgumentParser(description="# [CN] 分析事件之间的因果关系 # [EN] Analyze causal relationships between events")
    parser.add_argument("--input", "-i", required=True, help="# [CN] 输入事件JSON文件 # [EN] Input event JSON file")
    parser.add_argument("--output", "-o", required=True, help="# [CN] 输出因果关系JSON文件 # [EN] Output causal relationship JSON file")
    
    args = parser.parse_args()
    
    link_events(args.input, args.output)


if __name__ == "__main__":
    main()
