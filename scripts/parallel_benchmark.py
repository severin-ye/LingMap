#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并行处理性能基准测试脚本

比较启用和禁用并行处理时各模块的性能差异。
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# 将项目根目录添加到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from common.utils.parallel_config import ParallelConfig
from common.utils.json_loader import JsonLoader
from text_ingestion.chapter_loader import ChapterLoader
from event_extraction.di.provider import provide_extractor
from hallucination_refine.di.provider import provide_refiner
from causal_linking.di.provider import provide_linker
from graph_builder.service.mermaid_renderer import MermaidRenderer


def format_duration(seconds):
    """格式化时间为可读形式"""
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


def test_event_extraction(chapter_file):
    """测试事件提取模块"""
    # 加载章节
    loader = ChapterLoader(segment_size=800)
    chapter = loader.load_from_json(chapter_file)
    
    if not chapter:
        raise ValueError("加载章节失败")
    
    # 提取事件
    extractor = provide_extractor()
    print(f"从章节 {chapter.chapter_id} 提取事件...")
    events = extractor.extract(chapter)
    print(f"成功提取 {len(events)} 个事件")
    
    return events


def test_hallucination_refine(events, context):
    """测试幻觉修复模块"""
    refiner = provide_refiner()
    print(f"对 {len(events)} 个事件进行幻觉检测和修复...")
    refined_events = refiner.refine(events, context=context)
    print(f"精修完成，共 {len(refined_events)} 个事件")
    
    return refined_events


def test_causal_linking(events):
    """测试因果分析模块"""
    linker = provide_linker(use_optimized=True)
    print(f"分析 {len(events)} 个事件之间的因果关系...")
    edges = linker.link_events(events)
    print(f"发现 {len(edges)} 个因果关系")
    
    # 构建DAG
    print("构建有向无环图（DAG）...")
    events, dag_edges = linker.build_dag(events, edges)
    print(f"DAG构建完成，保留 {len(dag_edges)} 条边")
    
    return events, dag_edges


def test_graph_rendering(events, edges):
    """测试图形渲染模块"""
    renderer = MermaidRenderer()
    options = {
        "show_legend": True,
        "show_edge_labels": True,
        "custom_edge_style": True
    }
    
    print(f"渲染 {len(events)} 个事件节点和 {len(edges)} 条边...")
    mermaid_text = renderer.render(events, edges, options)
    
    return mermaid_text


def generate_report(parallel_results, sequential_results):
    """生成性能比较报告"""
    report = []
    report.append("# 并行处理性能基准测试报告")
    report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 性能摘要
    report.append("## 性能摘要")
    total_parallel = sum(parallel_results.values())
    total_sequential = sum(sequential_results.values())
    speedup = (total_sequential / total_parallel) if total_parallel > 0 else 0
    
    report.append(f"- 并行处理总耗时: {format_duration(total_parallel)}")
    report.append(f"- 顺序处理总耗时: {format_duration(total_sequential)}")
    report.append(f"- 加速比: {speedup:.2f}x")
    report.append(f"- 性能提升: {(speedup - 1) * 100:.2f}%")
    report.append("")
    
    # 模块性能比较
    report.append("## 各模块性能比较")
    report.append("| 模块 | 并行处理耗时 | 顺序处理耗时 | 加速比 | 提升百分比 |")
    report.append("| --- | ------- | ------- | ----- | ------- |")
    
    for module in parallel_results.keys():
        par_time = parallel_results[module]
        seq_time = sequential_results.get(module, 0)
        if seq_time > 0 and par_time > 0:
            mod_speedup = seq_time / par_time
            improvement = (mod_speedup - 1) * 100
            report.append(f"| {module} | {format_duration(par_time)} | {format_duration(seq_time)} | {mod_speedup:.2f}x | {improvement:.2f}% |")
    
    report.append("")
    report.append("## 测试配置")
    report.append(f"- CPU核心数: {os.cpu_count()}")
    report.append(f"- 并行模式工作线程数:")
    report.append(f"  - 事件提取: {ParallelConfig.get_max_workers('io_bound')}")
    report.append(f"  - 幻觉修复: {ParallelConfig.get_max_workers('io_bound')}")
    report.append(f"  - 因果分析: {ParallelConfig.get_max_workers()}")
    report.append(f"  - 图谱渲染: {ParallelConfig.get_max_workers('cpu_bound')}")
    
    return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description="并行处理性能基准测试")
    parser.add_argument("--input", "-i", default=None, help="输入章节JSON文件路径")
    parser.add_argument("--output", "-o", default=None, help="输出报告文件路径")
    parser.add_argument("--skip-sequential", action="store_true", help="跳过顺序处理测试")
    args = parser.parse_args()
    
    # 设置输入文件路径
    if args.input:
        chapter_file = args.input
    else:
        # 查找测试数据
        temp_dir = os.path.join(project_root, "temp")
        output_dirs = [d for d in os.listdir(os.path.join(project_root, "output")) 
                       if os.path.isdir(os.path.join(project_root, "output", d))]
        
        if output_dirs:
            # 使用最新的输出目录
            latest_dir = sorted(output_dirs)[-1]
            temp_dir = os.path.join(project_root, "output", latest_dir, "temp")
            
        # 查找章节JSON文件
        json_files = [f for f in os.listdir(temp_dir) 
                     if os.path.isfile(os.path.join(temp_dir, f)) 
                     and f.endswith('.json') and not f.endswith('_events.json')]
        
        if not json_files:
            print("❌ 未找到章节JSON文件")
            return
            
        chapter_file = os.path.join(temp_dir, json_files[0])
    
    print(f"使用章节文件: {chapter_file}")
    
    # 加载章节以获取内容作为上下文
    loader = ChapterLoader()
    chapter = loader.load_from_json(chapter_file)
    if not chapter:
        print("❌ 加载章节失败")
        return
        
    print(f"章节ID: {chapter.chapter_id}, 标题: {chapter.title}")
    print(f"章节内容长度: {len(chapter.content)} 字符")
    print(f"章节分段数: {len(chapter.segments)}")
    
    # 设置输出报告路径
    if args.output:
        report_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(project_root, "output", f"parallel_benchmark_{timestamp}.md")
    
    # 运行并行测试
    print("\n=== 开始并行处理测试 ===")
    ParallelConfig.initialize({"enabled": True})
    
    parallel_results = {}
    
    # 事件提取测试
    events, duration = run_module_test("事件提取", test_event_extraction, chapter_file)
    parallel_results["事件提取"] = duration
    
    if events:
        # 幻觉修复测试
        refined_events, duration = run_module_test(
            "幻觉修复", test_hallucination_refine, events, chapter.content)
        parallel_results["幻觉修复"] = duration
        
        if refined_events:
            # 因果分析测试
            events_edges, duration = run_module_test("因果分析", test_causal_linking, refined_events)
            parallel_results["因果分析"] = duration
            
            if events_edges:
                # 图形渲染测试
                _, duration = run_module_test(
                    "图谱渲染", test_graph_rendering, events_edges[0], events_edges[1])
                parallel_results["图谱渲染"] = duration
    
    sequential_results = {}
    
    # 运行顺序测试
    if not args.skip_sequential:
        print("\n=== 开始顺序处理测试 ===")
        ParallelConfig.initialize({"enabled": False})
        
        # 事件提取测试
        events, duration = run_module_test("事件提取", test_event_extraction, chapter_file)
        sequential_results["事件提取"] = duration
        
        if events:
            # 幻觉修复测试
            refined_events, duration = run_module_test(
                "幻觉修复", test_hallucination_refine, events, chapter.content)
            sequential_results["幻觉修复"] = duration
            
            if refined_events:
                # 因果分析测试
                events_edges, duration = run_module_test("因果分析", test_causal_linking, refined_events)
                sequential_results["因果分析"] = duration
                
                if events_edges:
                    # 图形渲染测试
                    _, duration = run_module_test(
                        "图谱渲染", test_graph_rendering, events_edges[0], events_edges[1])
                    sequential_results["图谱渲染"] = duration
    
    # 生成性能报告
    print("\n=== 生成性能报告 ===")
    report = generate_report(parallel_results, sequential_results)
    
    # 保存报告
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"\n性能报告已保存到: {report_file}")
    
    # 打印摘要
    print("\n=== 性能测试摘要 ===")
    total_parallel = sum(parallel_results.values())
    if sequential_results:
        total_sequential = sum(sequential_results.values())
        speedup = (total_sequential / total_parallel) if total_parallel > 0 else 0
        print(f"并行处理总耗时: {format_duration(total_parallel)}")
        print(f"顺序处理总耗时: {format_duration(total_sequential)}")
        print(f"加速比: {speedup:.2f}x")
        print(f"性能提升: {(speedup - 1) * 100:.2f}%")
    else:
        print(f"并行处理总耗时: {format_duration(total_parallel)}")
        print("顺序处理测试已跳过")


if __name__ == "__main__":
    main()
