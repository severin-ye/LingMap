import argparse
import os
import sys
import logging
import multiprocessing
from typing import List, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 将项目根目录添加到路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from common.utils.path_utils import get_project_root, get_config_path, get_novel_path, get_output_path

from text_ingestion.chapter_loader import ChapterLoader
from common.models.chapter import Chapter
from common.utils.json_loader import JsonLoader
from event_extraction.di.provider import provide_extractor
from hallucination_refine.di.provider import provide_refiner
from causal_linking.di.provider import provide_linker
from graph_builder.service.mermaid_renderer import MermaidRenderer

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api_gateway")


def setup_env():
    """设置环境变量"""
    # 检查是否存在.env文件，并尝试加载
    env_file = os.path.join(project_root, ".env")
    if os.path.exists(env_file):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logger.info("已加载 .env 文件")
            
            # 设置API密钥 - 确保大写变量名可用
            if "deepseek_api_key" in os.environ:
                os.environ["DEEPSEEK_API_KEY"] = os.environ["deepseek_api_key"]
                logger.info("已设置 DeepSeek API 密钥")
            
            if "openai_api_key" in os.environ:
                os.environ["OPENAI_API_KEY"] = os.environ["openai_api_key"]
                logger.info("已设置 OpenAI API 密钥")
                
        except ImportError:
            logger.warning("未找到 python-dotenv 库，无法加载 .env 文件")
    else:
        logger.warning("未找到 .env 文件")


def process_text(text_path: str, output_dir: str, temp_dir: str = "", provider: str = "openai"):
    """
    处理小说文本，生成因果图谱
    
    Args:
        text_path: 小说文本文件路径
        output_dir: 输出目录
        temp_dir: 临时文件目录
        provider: LLM API提供商，"openai"或"deepseek"
    """
    # 设置LLM提供商环境变量
    os.environ["LLM_PROVIDER"] = provider
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 创建临时目录
    if temp_dir is None:
        temp_dir = os.path.join(output_dir, "temp")
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    print("=== 步骤1: 加载和分割章节 ===")
    # 加载章节
    loader = ChapterLoader(segment_size=800)
    print(f"从 {text_path} 加载章节...")
    chapter = loader.load_from_txt(text_path)
    
    if not chapter:
        print("加载章节失败")
        return
    
    # 保存章节JSON
    chapter_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}.json")
    JsonLoader.save_json(chapter.to_dict(), chapter_json_path)
    print(f"章节已保存到: {chapter_json_path}")
    
    print("\n=== 步骤2: 提取事件 ===")
    # 提取事件
    extractor = provide_extractor()
    print(f"从章节 {chapter.chapter_id} 提取事件...")
    events = extractor.extract(chapter)
    print(f"成功提取 {len(events)} 个事件")
    
    # 保存事件JSON
    events_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}_events.json")
    events_dict = [event.to_dict() for event in events]
    JsonLoader.save_json(events_dict, events_json_path)
    print(f"事件已保存到: {events_json_path}")
    
    print("\n=== 步骤3: 修复幻觉 ===")
    # 修复幻觉
    refiner = provide_refiner()
    print(f"对 {len(events)} 个事件进行幻觉检测和修复...")
    refined_events = refiner.refine(events, context=chapter.content)
    print(f"精修完成，共 {len(refined_events)} 个事件")
    
    # 保存精修后的事件JSON
    refined_events_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}_refined_events.json")
    refined_events_dict = [event.to_dict() for event in refined_events]
    JsonLoader.save_json(refined_events_dict, refined_events_json_path)
    print(f"精修后的事件已保存到: {refined_events_json_path}")
    
    print("\n=== 步骤4: 分析因果关系 ===")
    # 分析因果关系
    linker = provide_linker()
    print(f"分析 {len(refined_events)} 个事件之间的因果关系...")
    edges = linker.link_events(refined_events)
    print(f"发现 {len(edges)} 个因果关系")
    
    # 构建DAG
    print("构建有向无环图（DAG）...")
    events, dag_edges = linker.build_dag(refined_events, edges)
    print(f"DAG构建完成，保留 {len(dag_edges)} 条边")
    
    # 保存因果关系JSON
    causal_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}_causal.json")
    causal_data = {
        "nodes": [event.to_dict() for event in events],
        "edges": [edge.to_dict() for edge in dag_edges]
    }
    JsonLoader.save_json(causal_data, causal_json_path)
    print(f"因果关系已保存到: {causal_json_path}")
    
    print("\n=== 步骤5: 生成Mermaid图谱 ===")
    # 生成Mermaid图谱
    renderer = MermaidRenderer()
    options = {
        "show_legend": True,
        "show_edge_labels": True,
        "custom_edge_style": True
    }
    
    mermaid_text = renderer.render(events, dag_edges, options)
    
    # 保存Mermaid文件
    mermaid_path = os.path.join(output_dir, f"{chapter.chapter_id}_graph.mmd")
    with open(mermaid_path, 'w', encoding='utf-8') as f:
        f.write(mermaid_text)
    print(f"Mermaid图谱已保存到: {mermaid_path}")
    
    print("\n=== 处理完成 ===")
    print(f"处理结果已保存到目录: {output_dir}")


def process_directory(input_dir: str, output_dir: str, provider: str = "openai", parallel: bool = True):
    """
    处理目录中的所有文本文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        provider: LLM API提供商，"openai"或"deepseek"
        parallel: 是否并行处理文件
    """
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 获取所有TXT文件
    import glob
    txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
    
    if not parallel:
        # 顺序处理
        for txt_file in txt_files:
            file_name = os.path.basename(txt_file)
            file_output_dir = os.path.join(output_dir, file_name.replace(".txt", ""))
            
            print(f"\n处理文件: {file_name}")
            process_text(txt_file, file_output_dir, provider=provider)
    else:
        # 并行处理
        print(f"启用并行处理 {len(txt_files)} 个文件...")
        
        # 确定合适的线程数
        cpu_count = multiprocessing.cpu_count()
        # 使用系统CPU核心数的一半，至少2个，最多8个
        max_workers = max(2, min(8, cpu_count // 2))
        print(f"使用 {max_workers} 个工作线程进行并行处理")
        
        def process_file_task(txt_file):
            try:
                file_name = os.path.basename(txt_file)
                file_output_dir = os.path.join(output_dir, file_name.replace(".txt", ""))
                
                print(f"开始处理文件: {file_name}")
                process_text(txt_file, file_output_dir, provider=provider)
                print(f"成功完成文件: {file_name}")
                return (True, file_name, None)
            except Exception as e:
                print(f"处理文件 {os.path.basename(txt_file)} 时出错: {str(e)}")
                return (False, os.path.basename(txt_file), str(e))
        
        # 使用线程池并行处理文件
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {executor.submit(process_file_task, txt_file): txt_file for txt_file in txt_files}
            
            # 收集结果
            for future in as_completed(future_to_file):
                txt_file = future_to_file[future]
                try:
                    success, file_name, error = future.result()
                    results.append((success, file_name, error))
                except Exception as e:
                    results.append((False, os.path.basename(txt_file), str(e)))
        
        # 汇总结果
        success_count = sum(1 for success, _, _ in results if success)
        failed_count = len(results) - success_count
        
        print("\n===处理结果汇总===")
        print(f"成功处理: {success_count} 个文件")
        print(f"处理失败: {failed_count} 个文件")
        
        if failed_count > 0:
            print("\n失败的文件:")
            for success, file_name, error in results:
                if not success:
                    print(f"- {file_name}: {error}")


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description="《凡人修仙传》因果图谱生成系统")
    parser.add_argument("--input", "-i", required=True, help="输入小说文本文件或目录")
    parser.add_argument("--output", "-o", required=True, help="输出目录")
    parser.add_argument("--batch", "-b", action="store_true", help="批处理模式（处理目录中的所有文件）")
    parser.add_argument("--provider", "-p", choices=["openai", "deepseek"], default="deepseek",
                        help="LLM API提供商 (默认: deepseek)")
    parser.add_argument("--no-parallel", action="store_true", help="禁用并行处理")
    
    args = parser.parse_args()
    
    # 设置环境变量
    setup_env()
    
    # 设置LLM提供商
    os.environ["LLM_PROVIDER"] = args.provider
    logger.info(f"使用LLM提供商: {args.provider}")
    
    if args.batch:
        # 批处理模式
        if not os.path.isdir(args.input):
            logger.error(f"错误: 输入路径 {args.input} 不是一个目录")
            return
        
        process_directory(args.input, args.output, provider=args.provider, parallel=not args.no_parallel)
    else:
        # 单文件模式
        if not os.path.isfile(args.input):
            logger.error(f"错误: 输入路径 {args.input} 不是一个文件")
            return
        
        process_text(args.input, args.output, provider=args.provider)


if __name__ == "__main__":
    main()
