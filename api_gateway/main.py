import argparse
import os
import sys
import logging
import multiprocessing
from typing import List, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# [CN] 将项目根目录添加到路径中
# [EN] Add the project root directory to the path
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

# [CN] 设置日志
# [EN] Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api_gateway")


def setup_env():
    """
    # [CN] 设置环境变量
    # [EN] Set environment variables
    """
    # [CN] 检查是否存在.env文件，并尝试加载
    # [EN] Check if .env file exists and try to load it
    env_file = os.path.join(project_root, ".env")
    if os.path.exists(env_file):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logger.info("已加载 .env 文件")  # [CN] 已加载 .env 文件 [EN] .env file loaded
            # [CN] 设置API密钥 - 确保大写变量名可用
            # [EN] Set API keys - ensure uppercase variable names are available
            if "deepseek_api_key" in os.environ:
                os.environ["DEEPSEEK_API_KEY"] = os.environ["deepseek_api_key"]
                logger.info("已设置 DeepSeek API 密钥")  # [CN] 已设置 DeepSeek API 密钥 [EN] DeepSeek API key set
            if "openai_api_key" in os.environ:
                os.environ["OPENAI_API_KEY"] = os.environ["openai_api_key"]
                logger.info("已设置 OpenAI API 密钥")  # [CN] 已设置 OpenAI API 密钥 [EN] OpenAI API key set
        except ImportError:
            logger.warning("未找到 python-dotenv 库，无法加载 .env 文件")  # [CN] 未找到 python-dotenv 库，无法加载 .env 文件 [EN] python-dotenv not found, cannot load .env file
    else:
        logger.warning("未找到 .env 文件")  # [CN] 未找到 .env 文件 [EN] .env file not found


def process_text(text_path: str, output_dir: str, temp_dir: str = "", provider: str = "openai"):
    """
    # [CN] 处理小说文本，生成因果图谱
    # [EN] Process novel text and generate causal graph
    
    Args:
        text_path: # [CN] 小说文本文件路径 [EN] Path to novel text file
        output_dir: # [CN] 输出目录 [EN] Output directory
        temp_dir: # [CN] 临时文件目录 [EN] Temporary file directory
        provider: # [CN] LLM API提供商，"openai"或"deepseek" [EN] LLM API provider, "openai" or "deepseek"
    """
    # [CN] 设置LLM提供商环境变量
    # [EN] Set LLM provider environment variable
    os.environ["LLM_PROVIDER"] = provider
    # [CN] 创建输出目录
    # [EN] Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # [CN] 创建临时目录
    # [EN] Create temporary directory
    if temp_dir is None:
        temp_dir = os.path.join(output_dir, "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    print("=== 步骤1: 加载和分割章节 ===")  # [CN] === 步骤1: 加载和分割章节 === [EN] === Step 1: Load and split chapters ===
    # [CN] 加载章节
    # [EN] Load chapters
    loader = ChapterLoader(segment_size=800)
    print(f"从 {text_path} 加载章节...")  # [CN] 从 {text_path} 加载章节... [EN] Loading chapters from {text_path} ...
    chapter = loader.load_from_txt(text_path)
    if not chapter:
        print("加载章节失败")  # [CN] 加载章节失败 [EN] Failed to load chapters
        return
    # [CN] 保存章节JSON
    # [EN] Save chapter JSON
    chapter_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}.json")
    JsonLoader.save_json(chapter.to_dict(), chapter_json_path)
    print(f"章节已保存到: {chapter_json_path}")  # [CN] 章节已保存到: {chapter_json_path} [EN] Chapter saved to: {chapter_json_path}
    print("\n=== 步骤2: 提取事件 ===")  # [CN] === 步骤2: 提取事件 === [EN] === Step 2: Extract events ===
    # [CN] 提取事件
    # [EN] Extract events
    extractor = provide_extractor()
    print(f"从章节 {chapter.chapter_id} 提取事件...")  # [CN] 从章节 {chapter.chapter_id} 提取事件... [EN] Extracting events from chapter {chapter.chapter_id} ...
    events = extractor.extract(chapter)
    print(f"成功提取 {len(events)} 个事件")  # [CN] 成功提取 {len(events)} 个事件 [EN] Successfully extracted {len(events)} events
    # [CN] 保存事件JSON
    # [EN] Save events JSON
    events_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}_events.json")
    events_dict = [event.to_dict() for event in events]
    JsonLoader.save_json(events_dict, events_json_path)
    print(f"事件已保存到: {events_json_path}")  # [CN] 事件已保存到: {events_json_path} [EN] Events saved to: {events_json_path}
    print("\n=== 步骤3: 修复幻觉 ===")  # [CN] === 步骤3: 修复幻觉 === [EN] === Step 3: Refine hallucinations ===
    # [CN] 修复幻觉
    # [EN] Refine hallucinations
    refiner = provide_refiner()
    print(f"对 {len(events)} 个事件进行幻觉检测和修复...")  # [CN] 对 {len(events)} 个事件进行幻觉检测和修复... [EN] Detecting and refining hallucinations for {len(events)} events ...
    refined_events = refiner.refine(events, context=chapter.content)
    print(f"精修完成，共 {len(refined_events)} 个事件")  # [CN] 精修完成，共 {len(refined_events)} 个事件 [EN] Refinement complete, total {len(refined_events)} events
    # [CN] 保存精修后的事件JSON
    # [EN] Save refined events JSON
    refined_events_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}_refined_events.json")
    refined_events_dict = [event.to_dict() for event in refined_events]
    JsonLoader.save_json(refined_events_dict, refined_events_json_path)
    print(f"精修后的事件已保存到: {refined_events_json_path}")  # [CN] 精修后的事件已保存到: {refined_events_json_path} [EN] Refined events saved to: {refined_events_json_path}
    print("\n=== 步骤4: 分析因果关系 ===")  # [CN] === 步骤4: 分析因果关系 === [EN] === Step 4: Analyze causal relationships ===
    # [CN] 分析因果关系
    # [EN] Analyze causal relationships
    linker = provide_linker()
    print(f"分析 {len(refined_events)} 个事件之间的因果关系...")  # [CN] 分析 {len(refined_events)} 个事件之间的因果关系... [EN] Analyzing causal relationships among {len(refined_events)} events ...
    edges = linker.link_events(refined_events)
    print(f"发现 {len(edges)} 个因果关系")  # [CN] 发现 {len(edges)} 个因果关系 [EN] Found {len(edges)} causal relationships
    # [CN] 构建DAG
    # [EN] Build DAG
    print("构建有向无环图（DAG）...")  # [CN] 构建有向无环图（DAG）... [EN] Building Directed Acyclic Graph (DAG) ...
    events, dag_edges = linker.build_dag(refined_events, edges)
    print(f"DAG构建完成，保留 {len(dag_edges)} 条边")  # [CN] DAG构建完成，保留 {len(dag_edges)} 条边 [EN] DAG built, {len(dag_edges)} edges retained
    # [CN] 保存因果关系JSON
    # [EN] Save causal relationships JSON
    causal_json_path = os.path.join(temp_dir, f"{chapter.chapter_id}_causal.json")
    causal_data = {
        "nodes": [event.to_dict() for event in events],
        "edges": [edge.to_dict() for edge in dag_edges]
    }
    JsonLoader.save_json(causal_data, causal_json_path)
    print(f"因果关系已保存到: {causal_json_path}")  # [CN] 因果关系已保存到: {causal_json_path} [EN] Causal relationships saved to: {causal_json_path}
    print("\n=== 步骤5: 生成Mermaid图谱 ===")  # [CN] === 步骤5: 生成Mermaid图谱 === [EN] === Step 5: Generate Mermaid graph ===
    # [CN] 生成Mermaid图谱
    # [EN] Generate Mermaid graph
    renderer = MermaidRenderer()
    options = {
        "show_legend": True,
        "show_edge_labels": True,
        "custom_edge_style": True
    }
    mermaid_text = renderer.render(events, dag_edges, options)
    # [CN] 保存Mermaid文件
    # [EN] Save Mermaid file
    mermaid_path = os.path.join(output_dir, f"{chapter.chapter_id}_graph.mmd")
    with open(mermaid_path, 'w', encoding='utf-8') as f:
        f.write(mermaid_text)
    print(f"Mermaid图谱已保存到: {mermaid_path}")  # [CN] Mermaid图谱已保存到: {mermaid_path} [EN] Mermaid graph saved to: {mermaid_path}
    print("\n=== 处理完成 ===")  # [CN] === 处理完成 === [EN] === Processing complete ===
    print(f"处理结果已保存到目录: {output_dir}")  # [CN] 处理结果已保存到目录: {output_dir} [EN] Results saved to directory: {output_dir}


def process_directory(input_dir: str, output_dir: str, provider: str = "openai", parallel: bool = True):
    """
    # [CN] 处理目录中的所有文本文件
    # [EN] Process all text files in the directory
    
    Args:
        input_dir: # [CN] 输入目录 [EN] Input directory
        output_dir: # [CN] 输出目录 [EN] Output directory
        provider: # [CN] LLM API提供商，"openai"或"deepseek" [EN] LLM API provider, "openai" or "deepseek"
        parallel: # [CN] 是否并行处理文件 [EN] Whether to process files in parallel
    """
    # [CN] 创建输出目录
    # [EN] Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # [CN] 获取所有TXT文件
    # [EN] Get all TXT files
    import glob
    txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
    if not parallel:
        # [CN] 顺序处理
        # [EN] Sequential processing
        for txt_file in txt_files:
            file_name = os.path.basename(txt_file)
            file_output_dir = os.path.join(output_dir, file_name.replace(".txt", ""))
            print(f"\n处理文件: {file_name}")  # [CN] 处理文件: {file_name} [EN] Processing file: {file_name}
            process_text(txt_file, file_output_dir, provider=provider)
    else:
        # [CN] 并行处理
        # [EN] Parallel processing
        print(f"启用并行处理 {len(txt_files)} 个文件...")  # [CN] 启用并行处理 {len(txt_files)} 个文件... [EN] Enabling parallel processing for {len(txt_files)} files ...
        # [CN] 确定合适的线程数
        # [EN] Determine appropriate number of threads
        cpu_count = multiprocessing.cpu_count()
        # [CN] 使用系统CPU核心数的一半，至少2个，最多8个
        # [EN] Use half of system CPU cores, at least 2, at most 8
        max_workers = max(2, min(8, cpu_count // 2))
        print(f"使用 {max_workers} 个工作线程进行并行处理")  # [CN] 使用 {max_workers} 个工作线程进行并行处理 [EN] Using {max_workers} worker threads for parallel processing
        def process_file_task(txt_file):
            try:
                file_name = os.path.basename(txt_file)
                file_output_dir = os.path.join(output_dir, file_name.replace(".txt", ""))
                print(f"开始处理文件: {file_name}")  # [CN] 开始处理文件: {file_name} [EN] Start processing file: {file_name}
                process_text(txt_file, file_output_dir, provider=provider)
                print(f"成功完成文件: {file_name}")  # [CN] 成功完成文件: {file_name} [EN] Successfully completed file: {file_name}
                return (True, file_name, None)
            except Exception as e:
                print(f"处理文件 {os.path.basename(txt_file)} 时出错: {str(e)}")  # [CN] 处理文件 {os.path.basename(txt_file)} 时出错: {str(e)} [EN] Error processing file {os.path.basename(txt_file)}: {str(e)}
                return (False, os.path.basename(txt_file), str(e))
        # [CN] 使用线程池并行处理文件
        # [EN] Use thread pool to process files in parallel
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # [CN] 提交所有任务
            # [EN] Submit all tasks
            future_to_file = {executor.submit(process_file_task, txt_file): txt_file for txt_file in txt_files}
            # [CN] 收集结果
            # [EN] Collect results
            for future in as_completed(future_to_file):
                txt_file = future_to_file[future]
                try:
                    success, file_name, error = future.result()
                    results.append((success, file_name, error))
                except Exception as e:
                    results.append((False, os.path.basename(txt_file), str(e)))
        # [CN] 汇总结果
        # [EN] Summarize results
        success_count = sum(1 for success, _, _ in results if success)
        failed_count = len(results) - success_count
        print("\n===处理结果汇总===")  # [CN] ===处理结果汇总=== [EN] ===Summary of Results===
        print(f"成功处理: {success_count} 个文件")  # [CN] 成功处理: {success_count} 个文件 [EN] Successfully processed: {success_count} files
        print(f"处理失败: {failed_count} 个文件")  # [CN] 处理失败: {failed_count} 个文件 [EN] Failed to process: {failed_count} files
        if failed_count > 0:
            print("\n失败的文件:")  # [CN] 失败的文件: [EN] Failed files:
            for success, file_name, error in results:
                if not success:
                    print(f"- {file_name}: {error}")


def main():
    """
    # [CN] 主入口函数
    # [EN] Main entry function
    """
    parser = argparse.ArgumentParser(description="《凡人修仙传》因果图谱生成系统")  # [CN] 《凡人修仙传》因果图谱生成系统 [EN] 'A Record of a Mortal's Journey to Immortality' Causal Graph Generation System
    parser.add_argument("--input", "-i", required=True, help="输入小说文本文件或目录")  # [CN] 输入小说文本文件或目录 [EN] Input novel text file or directory
    parser.add_argument("--output", "-o", required=True, help="输出目录")  # [CN] 输出目录 [EN] Output directory
    parser.add_argument("--batch", "-b", action="store_true", help="批处理模式（处理目录中的所有文件）")  # [CN] 批处理模式（处理目录中的所有文件） [EN] Batch mode (process all files in directory)
    parser.add_argument("--provider", "-p", choices=["openai", "deepseek"], default="deepseek",
                        help="LLM API提供商 (默认: deepseek)")  # [CN] LLM API提供商 (默认: deepseek) [EN] LLM API provider (default: deepseek)
    parser.add_argument("--no-parallel", action="store_true", help="禁用并行处理")  # [CN] 禁用并行处理 [EN] Disable parallel processing
    args = parser.parse_args()
    # [CN] 设置环境变量
    # [EN] Set environment variables
    setup_env()
    # [CN] 设置LLM提供商
    # [EN] Set LLM provider
    os.environ["LLM_PROVIDER"] = args.provider
    logger.info(f"使用LLM提供商: {args.provider}")  # [CN] 使用LLM提供商: {args.provider} [EN] Using LLM provider: {args.provider}
    if args.batch:
        # [CN] 批处理模式
        # [EN] Batch mode
        if not os.path.isdir(args.input):
            logger.error(f"错误: 输入路径 {args.input} 不是一个目录")  # [CN] 错误: 输入路径 {args.input} 不是一个目录 [EN] Error: input path {args.input} is not a directory
            return
        process_directory(args.input, args.output, provider=args.provider, parallel=not args.no_parallel)
    else:
        # [CN] 单文件模式
        # [EN] Single file mode
        if not os.path.isfile(args.input):
            logger.error(f"错误: 输入路径 {args.input} 不是一个文件")  # [CN] 错误: 输入路径 {args.input} 不是一个文件 [EN] Error: input path {args.input} is not a file
            return
        process_text(args.input, args.output, provider=args.provider)


if __name__ == "__main__":
    main()
