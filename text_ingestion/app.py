import argparse
import json
import os

from text_ingestion.chapter_loader import ChapterLoader
from common.utils.json_loader import JsonLoader


def main():
    """TEXT_INGESTION 模块执行入口"""
    parser = argparse.ArgumentParser(description="加载小说文本并转换为章节JSON")
    parser.add_argument("--input", "-i", required=True, help="输入TXT文件或目录")
    parser.add_argument("--output", "-o", required=True, help="输出JSON文件或目录")
    parser.add_argument("--segment_size", "-s", type=int, default=800, help="分段大小")
    parser.add_argument("--batch", "-b", action="store_true", help="批处理模式")
    
    args = parser.parse_args()
    
    loader = ChapterLoader(segment_size=args.segment_size)
    
    if args.batch:
        # 批处理模式
        if not os.path.isdir(args.input):
            print(f"错误: 输入路径 {args.input} 不是一个目录")
            return
        
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        
        chapters = loader.load_multiple_txt(args.input)
        print(f"成功加载 {len(chapters)} 个章节")
        
        for chapter in chapters:
            output_file = os.path.join(args.output, f"{chapter.chapter_id}.json")
            JsonLoader.save_json(chapter.to_dict(), output_file)
            print(f"保存章节: {output_file}")
    else:
        # 单文件模式
        if not os.path.isfile(args.input):
            print(f"错误: 输入路径 {args.input} 不是一个文件")
            return
        
        chapter = loader.load_from_txt(args.input)
        if chapter:
            JsonLoader.save_json(chapter.to_dict(), args.output)
            print(f"保存章节: {args.output}")
            # 打印一些统计信息
            print(f"章节ID: {chapter.chapter_id}")
            print(f"章节标题: {chapter.title}")
            print(f"分段数量: {len(chapter.segments)}")
        else:
            print("加载章节失败")


if __name__ == "__main__":
    main()
