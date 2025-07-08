import argparse
import os
import sys

# [CN] 将项目根目录添加到路径中
# [EN] Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from event_extraction.controller.extractor_controller import extract_events_from_chapter


def main():
    """
    # [CN] EVENT_EXTRACTION 模块的主入口
    # [EN] Main entry point for EVENT_EXTRACTION module
    """
    parser = argparse.ArgumentParser(description="# [CN] 从章节中抽取事件 # [EN] Extract events from chapters")
    parser.add_argument("--input", "-i", required=True, help="# [CN] 输入章节JSON文件或目录 # [EN] Input chapter JSON file or directory")
    parser.add_argument("--output", "-o", required=True, help="# [CN] 输出事件JSON文件或目录 # [EN] Output events JSON file or directory")
    parser.add_argument("--batch", "-b", action="store_true", help="# [CN] 批处理模式 # [EN] Batch processing mode")
    
    args = parser.parse_args()
    
    if args.batch:
        # [CN] 批处理模式
        # [EN] Batch processing mode
        if not os.path.isdir(args.input):
            print(f"# [CN] 错误: 输入路径 {args.input} 不是一个目录")
            print(f"# [EN] Error: Input path {args.input} is not a directory")
            return
        
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        
        # [CN] 获取所有JSON文件
        # [EN] Get all JSON files
        import glob
        chapter_files = glob.glob(os.path.join(args.input, "*.json"))
        
        for chapter_file in chapter_files:
            filename = os.path.basename(chapter_file)
            output_file = os.path.join(args.output, filename)
            extract_events_from_chapter(chapter_file, output_file)
    else:
        # [CN] 单文件模式
        # [EN] Single file mode
        extract_events_from_chapter(args.input, args.output)


if __name__ == "__main__":
    main()
