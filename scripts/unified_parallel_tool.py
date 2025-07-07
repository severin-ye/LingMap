#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并行处理测试和报告工具

集成功能：
1. 并行配置测试
2. 性能基准测试
3. 并行配置报告生成
"""

import os
import sys
import time
import json
import argparse
import logging
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# TODO: Translate - Add project root directory to系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from common.utils.parallel_config import ParallelConfig
from common.utils.config_writer import ConfigWriter
from common.utils.thread_monitor import ThreadUsageMonitor
from common.utils.json_loader import JsonLoader


class ParallelToolMode(Enum):
    """并行工具运行模式"""
    TEST = "test"         # TODO: Translate - Test模式：VerifyConfigure
    BENCHMARK = "bench"   # TODO: Translate - 基准Test模式：比较性能
    REPORT = "report"     # TODO: Translate - 报告模式：GenerateConfigure报告
    ALL = "all"           # TODO: Translate - 全部Run


def setup_logging(log_filename=None):
    """
    设置日志记录
    
    Args:
        log_filename: 日志文件名，如果为None则按日期生成
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    if log_filename is None:
        log_filename = f"parallel_tool_{datetime.now().strftime('%Y%m%d')}.log"
    
    log_file = log_dir / log_filename
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )
    
    return logging.getLogger("parallel_tool")


def format_duration(seconds):
    """
    格式化时间为可读形式
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.2f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}小时"


def run_module_test(module_name, test_func, *args, **kwargs):
    """
    运行模块测试
    
    Args:
        module_name: 模块名称
        test_func: 测试函数
        args: 位置参数
        kwargs: 关键字参数
        
    Returns:
        测试结果和执行时间
    """
    print(f"\n测试模块: {module_name}")
    start_time = time.time()
    try:
        result = test_func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"✅ {module_name} 测试成功，耗时: {format_duration(duration)}")
        return result, duration
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ {module_name} 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None, duration


#--------------------------------------------------------------------
# TODO: Translate - ConfigureTest相关功能
#--------------------------------------------------------------------
def test_parallel_config_consistency(logger=None):
    """
    测试并行配置一致性
    
    Args:
        logger: 日志记录器
    """
    if logger is None:
        logger = logging.getLogger()

    # InitializeParallelConfig
    ParallelConfig.initialize()
    
    # TODO: Translate - 记录Configure信息
    logger.info("====== 并行配置测试 ======")
    logger.info(f"并行处理启用状态: {ParallelConfig.is_enabled()}")
    logger.info(f"全局最大线程数: {ParallelConfig._config['max_workers']}")
    
    # TODO: Translate - 记录各模块Configure
    logger.info("模块特定配置:")
    for module, workers in ParallelConfig._config["default_workers"].items():
        logger.info(f"  - {module}: {workers}")
    
    # TODO: Translate - Test各模块实例
    logger.info("\n测试各模块实例化:")
    
    try:
        # eventExtract
        logger.info("创建事件抽取器...")
        from event_extraction.di.provider import provide_extractor
        extractor = provide_extractor()
        
        # hallucinationrefine
        logger.info("创建幻觉修复器...")
        from hallucination_refine.di.provider import provide_refiner
        refiner = provide_refiner()
        
        # causallinking
        logger.info("创建因果链接器...")
        from causal_linking.di.provider import provide_linker
        linker = provide_linker()
        
        # TODO: Translate - 图形Build
        logger.info("创建图形渲染器...")
        from graph_builder.service.mermaid_renderer import MermaidRenderer
        renderer = MermaidRenderer()
        
        logger.info("所有模块初始化完成")
        return True
    except Exception as e:
        logger.error(f"模块初始化失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_config_updates(logger=None):
    """
    测试配置更新
    
    Args:
        logger: 日志记录器
    
    Returns:
        是否测试成功
    """
    if logger is None:
        logger = logging.getLogger()
    
    try:
        logger.info("\n====== 配置更新测试 ======")
        
        # TODO: Translate - 记录原始Configure
        original_max = ParallelConfig._config["max_workers"]
        original_graph = ParallelConfig._config["default_workers"]["graph_builder"]
        logger.info(f"原始线程配置: 全局={original_max}, 图形构建={original_graph}")
        
        # TODO: Translate - 更新Configure
        test_updates = {
            "max_workers": original_max + 2,
            "default_workers": {
                "graph_builder": original_graph + 1
            }
        }
        logger.info(f"更新配置: {test_updates}")
        
        # TODO: Translate - 应用更新
        ConfigWriter.update_parallel_config(test_updates)
        
        # TODO: Translate - Verify更新后的Configure
        logger.info(f"更新后配置: 全局={ParallelConfig._config['max_workers']}, " +
                   f"图形构建={ParallelConfig._config['default_workers']['graph_builder']}")
        
        # TODO: Translate - 恢复原始Configure
        restore_updates = {
            "max_workers": original_max,
            "default_workers": {
                "graph_builder": original_graph
            }
        }
        logger.info(f"恢复原始配置: {restore_updates}")
        ConfigWriter.update_parallel_config(restore_updates)
        
        # TODO: Translate - 确认恢复Successfully
        logger.info(f"恢复后配置: 全局={ParallelConfig._config['max_workers']}, " +
                   f"图形构建={ParallelConfig._config['default_workers']['graph_builder']}")
        return True
    except Exception as e:
        logger.error(f"配置更新测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


#--------------------------------------------------------------------
# TODO: Translate - 报告Generate相关功能
#--------------------------------------------------------------------
def generate_parallel_report():
    """
    生成并行配置报告
    
    Returns:
        报告文件路径
    """
    # InitializeparallelConfigure
    ParallelConfig.initialize()
    
    # TODO: Translate - Initializethread监控
    thread_monitor = ThreadUsageMonitor.get_instance()
    
    # TODO: Translate - Create报告目录
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    report_file = report_dir / f"parallel_config_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    # TODO: Translate - 收集Configure信息
    config_info = {
        "enabled": ParallelConfig.is_enabled(),
        "max_workers": ParallelConfig._config["max_workers"],
        "adaptive": ParallelConfig._config["adaptive"],
        "default_workers": ParallelConfig._config["default_workers"]
    }
    
    # TODO: Translate - GenerateparallelConfigure报告
    logging.info("生成并行配置报告...")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# TODO: Translate - 系统parallelProcessConfigure报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # TODO: Translate - 基本Configure
        f.write("# TODO: Translate - 基本Configure\n\n")
        f.write(f"- 并行处理状态: {'启用' if config_info['enabled'] else '禁用'}\n")
        f.write(f"- 全局最大线程数: {config_info['max_workers']}\n")
        
        # TODO: Translate - 自适应Configure
        f.write("\n# TODO: Translate - 自适应threadConfigure\n\n")
        adaptive = config_info['adaptive']
        f.write(f"- 自适应模式: {'启用' if adaptive['enabled'] else '禁用'}\n")
        if adaptive['enabled']:
            f.write(f"- IO密集型任务系数: {adaptive['io_bound_factor']}\n")
            f.write(f"- CPU密集型任务系数: {adaptive['cpu_bound_factor']}\n")
            
            io_threads = int(config_info['max_workers'] * adaptive['io_bound_factor'])
            cpu_threads = int(config_info['max_workers'] * adaptive['cpu_bound_factor'])
            
            f.write(f"- IO密集型任务线程数: {io_threads}\n")
            f.write(f"- CPU密集型任务线程数: {cpu_threads}\n")
        
        # TODO: Translate - 模块特定Configure
        f.write("\n# TODO: Translate - 模块特定Configure\n\n")
        f.write("| 模块 | 配置线程数 |\n")
        f.write("|------|----------|\n")
        
        for module, workers in config_info['default_workers'].items():
            f.write(f"| {module} | {workers} |\n")
        
        # TODO: Translate - Initialize各模块并记录threadUse
        f.write("\n# TODO: Translate - 实际threadUse情况\n\n")
        f.write("现在开始测试各模块实际使用的线程数...\n\n")
        
        # eventExtract
        logging.info("测试事件抽取模块...")
        f.write("# TODO: Translate - eventExtract模块\n\n")
        try:
            from event_extraction.di.provider import provide_extractor
            extractor = provide_extractor()
            f.write("✅ 事件抽取模块初始化成功\n\n")
        except Exception as e:
            f.write(f"❌ 事件抽取模块初始化失败: {e}\n\n")
        
        # hallucinationrefine
        logging.info("测试幻觉修复模块...")
        f.write("\n# TODO: Translate - hallucinationrefine模块\n\n")
        try:
            from hallucination_refine.di.provider import provide_refiner
            refiner = provide_refiner()
            f.write("✅ 幻觉修复模块初始化成功\n\n")
        except Exception as e:
            f.write(f"❌ 幻觉修复模块初始化失败: {e}\n\n")
        
        # causallinking
        logging.info("测试因果链接模块...")
        f.write("\n# TODO: Translate - causallinking模块\n\n")
        try:
            from causal_linking.di.provider import provide_linker
            linker = provide_linker()
            f.write("✅ 因果链接模块初始化成功\n\n")
        except Exception as e:
            f.write(f"❌ 因果链接模块初始化失败: {e}\n\n")
        
        # TODO: Translate - 图形Build
        logging.info("测试图形构建模块...")
        f.write("\n# TODO: Translate - 图形Build模块\n\n")
        try:
            from graph_builder.service.mermaid_renderer import MermaidRenderer
            renderer = MermaidRenderer()
            f.write("✅ 图形构建模块初始化成功\n\n")
        except Exception as e:
            f.write(f"❌ 图形构建模块初始化失败: {e}\n\n")
        
        # TODO: Translate - Get并记录thread监控信息
        usage_info = thread_monitor.thread_usage
        
        f.write("\n# TODO: Translate - threadUse摘要\n\n")
        f.write("| 模块 | 配置线程数 | 实际使用线程数 | 任务类型 |\n")
        f.write("|------|------------|--------------|--------|\n")
        
        for module, workers in config_info['default_workers'].items():
            actual_workers = usage_info.get(module, {}).get("thread_count", "未知")
            task_type = usage_info.get(module, {}).get("task_type", "未知")
            f.write(f"| {module} | {workers} | {actual_workers} | {task_type} |\n")
        
        # TODO: Translate - 结论和建议
        f.write("\n# TODO: Translate - 结论和建议\n\n")
        
        # TODO: Translate - Check是否有模块未Use集中Configure
        unconfigured_modules = set(usage_info.keys()) - set(config_info['default_workers'].keys())
        if unconfigured_modules:
            f.write("⚠️ 以下模块未使用中央配置:\n\n")
            for module in unconfigured_modules:
                f.write(f"- {module}\n")
            f.write("\n建议将这些模块添加到中央配置中。\n\n")
        
        # TODO: Translate - CheckConfigure与Use是否一致
        inconsistent_modules = []
        for module, info in usage_info.items():
            if module in config_info['default_workers']:
                expected = config_info['default_workers'][module]
                actual = info.get("thread_count", 0)
                if expected != actual and ParallelConfig.is_enabled():
                    inconsistent_modules.append((module, expected, actual))
                    
        if inconsistent_modules:
            f.write("⚠️ 以下模块的线程使用与配置不一致:\n\n")
            for module, expected, actual in inconsistent_modules:
                f.write(f"- {module}: 期望 {expected}，实际 {actual}\n")
            f.write("\n建议检查这些模块的并行实现是否正确使用了ParallelConfig。\n\n")
        
        # TODO: Translate - 适应性建议
        f.write("# TODO: Translate - 优化建议\n\n")
        f.write("根据模块任务特性的不同，建议以下线程配置：\n\n")
        f.write("- IO密集型任务 (如API调用): 核心数 x 1.5\n")
        f.write("- CPU密集型任务 (如图形渲染): 核心数 x 0.8\n")
        f.write("- 混合型任务: 与核心数相当\n\n")
        
        f.write("当前系统中的分类：\n\n")
        f.write("- IO密集型：event_extraction, hallucination_refine\n")
        f.write("- CPU密集型：graph_builder\n")
        f.write("- 混合型：causal_linking\n")
    
    logging.info(f"报告已生成: {report_file}")
    print(f"📊 并行配置报告已生成: {report_file}")
    
    return report_file


#--------------------------------------------------------------------
# TODO: Translate - 基准Test相关功能
#--------------------------------------------------------------------
def test_event_extraction(chapter_file):
    """
    测试事件提取模块
    
    Args:
        chapter_file: 章节文件路径
        
    Returns:
        提取的事件
    """
    from text_ingestion.chapter_loader import ChapterLoader
    from event_extraction.di.provider import provide_extractor
    
    # Loadchapter
    loader = ChapterLoader(segment_size=800)
    chapter = loader.load_from_json(chapter_file)
    
    if not chapter:
        raise ValueError("Failed to load chapter")
    
    # Extractevent
    extractor = provide_extractor()
    print(f"从章节 {chapter.chapter_id} 提取事件...")
    events = extractor.extract(chapter)
    print(f"成功提取 {len(events)} 个事件")
    
    return events


def test_hallucination_refine(events, context):
    """
    测试幻觉修复模块
    
    Args:
        events: 事件列表
        context: 上下文信息
        
    Returns:
        Refined event
    """
    from hallucination_refine.di.provider import provide_refiner
    
    refiner = provide_refiner()
    print(f"对 {len(events)} 个事件进行幻觉检测和修复...")
    refined_events = refiner.refine(events, context=context)
    print(f"精修完成，共 {len(refined_events)} 个事件")
    
    return refined_events


def test_causal_linking(events):
    """
    测试因果分析模块
    
    Args:
        events: 事件列表
        
    Returns:
        事件和边的元组
    """
    from causal_linking.di.provider import provide_linker
    
    linker = provide_linker(use_optimized=True)
    print(f"分析 {len(events)} 个事件之间的因果关系...")
    edges = linker.link_events(events)
    print(f"发现 {len(edges)} 个因果关系")
    
    # BuildDAG
    print("构建有向无环图（DAG）...")
    events, dag_edges = linker.build_dag(events, edges)
    print(f"DAG构建完成，保留 {len(dag_edges)} 条边")
    
    return events, dag_edges


def test_graph_rendering(events, edges):
    """
    测试图形渲染模块
    
    Args:
        events: 事件列表
        edges: 边列表
        
    Returns:
        渲染的Mermaid文本
    """
    from graph_builder.service.mermaid_renderer import MermaidRenderer
    
    renderer = MermaidRenderer()
    options = {
        "show_legend": True,
        "show_edge_labels": True,
        "custom_edge_style": True
    }
    
    print(f"渲染 {len(events)} 个事件节点和 {len(edges)} 条边...")
    mermaid_text = renderer.render(events, edges, options)
    
    return mermaid_text


def run_benchmark(args):
    """
    运行性能基准测试
    
    Args:
        args: 命令行参数
        
    Returns:
        测试报告文件路径
    """
    # TODO: Translate - Set输入文件路径
    if args.input:
        chapter_file = args.input
    else:
        # TODO: Translate - 查找Test数据
        temp_dir = os.path.join(project_root, "temp")
        output_dirs = [d for d in os.listdir(os.path.join(project_root, "output")) 
                       if os.path.isdir(os.path.join(project_root, "output", d))]
        
        if output_dirs:
            # TODO: Translate - Use最新的Output目录
            latest_dir = sorted(output_dirs)[-1]
            temp_dir = os.path.join(project_root, "output", latest_dir, "temp")
            
        # TODO: Translate - 查找chapterJSON文件
        json_files = [f for f in os.listdir(temp_dir) 
                     if os.path.isfile(os.path.join(temp_dir, f))
                     and f.endswith('.json') and 'chapter' in f.lower()]
        
        if not json_files:
            # TODO: Translate - 尝试查找任意JSON文件
            json_files = [f for f in os.listdir(temp_dir) 
                         if os.path.isfile(os.path.join(temp_dir, f))
                         and f.endswith('.json')]
            
        if not json_files:
            raise FileNotFoundError("找不到测试用的章节JSON文件")
            
        # TODO: Translate - Use第一个找到的JSON文件
        chapter_file = os.path.join(temp_dir, json_files[0])
        
    print(f"使用测试数据: {chapter_file}")
    
    # TODO: Translate - Runparallel模式Test
    print("===== 并行模式测试 =====")
    
    # TODO: Translate - 确保parallel模式已启用
    ParallelConfig.initialize({"enabled": True})
    print(f"并行模式: 启用，最大线程数: {ParallelConfig._config['max_workers']}")
    
    # TODO: Translate - Save各Test阶段的Execute时间
    parallel_results = {}
    
    # TODO: Translate - eventExtract阶段
    events, duration = run_module_test("事件抽取", test_event_extraction, chapter_file)
    parallel_results["事件抽取"] = duration
    
    if not events:
        print("事件抽取失败，无法继续测试")
        return
    
    # TODO: Translate - Extractchapter上下文用于hallucination检测
    context = "测试上下文"
    try:
        with open(chapter_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and "content" in data:
                context = data["content"][:500] + "..." if len(data["content"]) > 500 else data["content"]
    except:
        print("提取上下文失败，使用默认上下文")
    
    # TODO: Translate - hallucinationrefine阶段
    refined_events, duration = run_module_test("幻觉修复", test_hallucination_refine, events, context)
    parallel_results["幻觉修复"] = duration
    
    if not refined_events:
        refined_events = events
    
    # TODO: Translate - causallinking阶段
    linking_result, duration = run_module_test("因果链接", test_causal_linking, refined_events)
    parallel_results["因果链接"] = duration
    
    if not linking_result:
        print("因果链接失败，无法继续测试")
        return
        
    events, edges = linking_result
    
    # TODO: Translate - 图谱渲染阶段
    mermaid_text, duration = run_module_test("图谱渲染", test_graph_rendering, events, edges)
    parallel_results["图谱渲染"] = duration
    
    # TODO: Translate - 如果不跳过顺序Test，则进行顺序模式Test
    sequential_results = {}
    if not args.skip_sequential:
        print("\n===== 顺序模式测试 =====")
        
        # TODO: Translate - 切换到顺序模式
        ParallelConfig.initialize({"enabled": False})
        print("顺序模式: 启用")
        
        # TODO: Translate - 同样的Test流程
        events, duration = run_module_test("事件抽取(顺序)", test_event_extraction, chapter_file)
        sequential_results["事件抽取"] = duration
        
        if not events:
            print("事件抽取失败，无法继续测试")
            return
        
        # TODO: Translate - hallucinationrefine阶段
        refined_events, duration = run_module_test("幻觉修复(顺序)", test_hallucination_refine, events, context)
        sequential_results["幻觉修复"] = duration
        
        if not refined_events:
            refined_events = events
        
        # TODO: Translate - causallinking阶段
        linking_result, duration = run_module_test("因果链接(顺序)", test_causal_linking, refined_events)
        sequential_results["因果链接"] = duration
        
        if not linking_result:
            print("因果链接失败，无法继续测试")
            return
            
        events, edges = linking_result
        
        # TODO: Translate - 图谱渲染阶段
        mermaid_text, duration = run_module_test("图谱渲染(顺序)", test_graph_rendering, events, edges)
        sequential_results["图谱渲染"] = duration
    
    # TODO: Translate - 重新启用parallel模式
    ParallelConfig.initialize({"enabled": True})
    
    # TODO: Translate - Generate报告
    report_content = generate_benchmark_report(parallel_results, sequential_results)
    
    # TODO: Translate - Create报告目录
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    # TODO: Translate - Write报告
    report_file = None
    if args.output:
        report_file = args.output
    else:
        report_file = report_dir / f"parallel_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n报告已保存至: {report_file}")
    return report_file


def generate_benchmark_report(parallel_results, sequential_results):
    """
    生成性能比较报告
    
    Args:
        parallel_results: 并行模式测试结果
        sequential_results: 顺序模式测试结果
        
    Returns:
        报告文本内容
    """
    report = []
    report.append("# TODO: Translate - parallelProcess性能基准Test报告")
    report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # TODO: Translate - 性能摘要
    report.append("# TODO: Translate - 性能摘要")
    total_parallel = sum(parallel_results.values())
    total_sequential = sum(sequential_results.values()) if sequential_results else 0
    
    report.append(f"- 并行处理总耗时: {format_duration(total_parallel)}")
    if sequential_results:
        speedup = (total_sequential / total_parallel) if total_parallel > 0 else 0
        report.append(f"- 顺序处理总耗时: {format_duration(total_sequential)}")
        report.append(f"- 加速比: {speedup:.2f}x")
        report.append(f"- 性能提升: {(speedup - 1) * 100:.2f}%")
    else:
        report.append("- 顺序处理测试已跳过")
    report.append("")
    
    # TODO: Translate - 模块性能比较
    if sequential_results:
        report.append("# TODO: Translate - 各模块性能比较")
        report.append("| 模块 | 并行处理耗时 | 顺序处理耗时 | 加速比 | 提升百分比 |")
        report.append("| --- | ------- | ------- | ----- | ------- |")
        
        for module in parallel_results.keys():
            par_time = parallel_results[module]
            seq_time = sequential_results.get(module, 0)
            if seq_time > 0 and par_time > 0:
                mod_speedup = seq_time / par_time
                improvement = (mod_speedup - 1) * 100
                report.append(f"| {module} | {format_duration(par_time)} | {format_duration(seq_time)} | {mod_speedup:.2f}x | {improvement:.2f}% |")
    else:
        report.append("# TODO: Translate - parallel模式Execute时间")
        report.append("| 模块 | 并行处理耗时 |")
        report.append("| --- | ------- |")
        for module, time in parallel_results.items():
            report.append(f"| {module} | {format_duration(time)} |")
    
    report.append("")
    report.append("# TestConfigure")
    report.append(f"- CPU核心数: {os.cpu_count()}")
    report.append(f"- 并行模式工作线程数:")
    report.append(f"  - 事件提取: {ParallelConfig.get_max_workers('io_bound')}")
    report.append(f"  - 幻觉修复: {ParallelConfig.get_max_workers('io_bound')}")
    report.append(f"  - 因果分析: {ParallelConfig.get_max_workers()}")
    report.append(f"  - 图谱渲染: {ParallelConfig.get_max_workers('cpu_bound')}")
    
    return '\n'.join(report)


def main():
    """程序主入口"""
    # TODO: Translate - 解析命令行参数
    parser = argparse.ArgumentParser(description="并行处理工具")
    parser.add_argument("mode", choices=["test", "bench", "report", "all"], default="all", 
                        nargs="?", help="运行模式：test-配置测试，bench-性能测试，report-生成报告，all-全部运行")
    parser.add_argument("--input", "-i", help="输入文件路径 (用于性能测试)")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--skip-sequential", action="store_true", help="跳过顺序处理测试")
    args = parser.parse_args()
    
    # TODO: Translate - Set日志
    logger = setup_logging()
    logger.info(f"运行并行处理工具，模式: {args.mode}")
    
    # TODO: Translate - 记录启动时间
    start_time = time.time()
    
    # TODO: Translate - 根据模式Run不同功能
    try:
        mode = ParallelToolMode(args.mode)
        
        if mode in [ParallelToolMode.TEST, ParallelToolMode.ALL]:
            logger.info("==== 运行并行配置测试 ====")
            test_result = test_parallel_config_consistency(logger)
            if test_result:
                config_result = test_config_updates(logger)
                if config_result:
                    print("✅ 配置测试成功")
                else:
                    print("❌ 配置更新测试失败")
            else:
                print("❌ 配置一致性测试失败")
                
        if mode in [ParallelToolMode.REPORT, ParallelToolMode.ALL]:
            logger.info("==== 生成并行配置报告 ====")
            report_file = generate_parallel_report()
            print(f"✅ 报告生成成功: {report_file}")
            
        if mode in [ParallelToolMode.BENCHMARK, ParallelToolMode.ALL]:
            logger.info("==== 运行性能基准测试 ====")
            benchmark_file = run_benchmark(args)
            print(f"✅ 基准测试完成: {benchmark_file}")
            
    except Exception as e:
        logger.error(f"运行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"❌ 运行失败: {e}")
        
    # TODO: Translate - 记录总Execute时间
    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"总执行时间: {format_duration(duration)}")
    print(f"总执行时间: {format_duration(duration)}")


if __name__ == "__main__":
    main()
