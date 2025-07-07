import argparse
import os
import sys

# TODO: Translate - Add project root directory to路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from event_extraction.controller.extractor_controller import extract_events_from_chapter


def main():
    """EVENT_EXTRACTION 模块的主入口"""
    parser = argparse.ArgumentParser(description="从章节中抽取事件")
    parser.add_argument("--input", "-i", required=True, help="输入章节JSON文件或目录")
    parser.add_argument("--output", "-o", required=True, help="输出事件JSON文件或目录")
    parser.add_argument("--batch", "-b", action="store_true", help="批处理模式")
    
    args = parser.parse_args()
    
    if args.batch:
        # TODO: Translate - 批Process模式
        if not os.path.isdir(args.input):
            print(f"错误: 输入路径 {args.input} 不是一个目录")
            return
        
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        
        # TODO: Translate - Get所有JSON文件
        import glob
        chapter_files = glob.glob(os.path.join(args.input, "*.json"))
        
        for chapter_file in chapter_files:
            filename = os.path.basename(chapter_file)
            output_file = os.path.join(args.output, filename)
            extract_events_from_chapter(chapter_file, output_file)
    else:
        # Single file mode
        extract_events_from_chapter(args.input, args.output)


if __name__ == "__main__":
    main()
