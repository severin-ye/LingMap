#!/usr/bin/env python3
"""
并行配置总结生成器

生成系统各模块并行配置和实际线程使用情况的详细报告。
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# 将项目根目录添加到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from common.utils.parallel_config import ParallelConfig
from common.utils.thread_monitor import ThreadUsageMonitor
from event_extraction.di.provider import provide_extractor
from hallucination_refine.di.provider import provide_refiner
from causal_linking.di.provider import provide_linker
from graph_builder.service.mermaid_renderer import MermaidRenderer


def setup_logging():
    """设置日志记录"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"parallel_config_report_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )


def generate_report():
    """生成并行配置报告"""
    # 初始化并行配置
    ParallelConfig.initialize()
    
    # 初始化线程监控
    thread_monitor = ThreadUsageMonitor.get_instance()
    
    # 创建报告目录
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    report_file = report_dir / f"parallel_config_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    # 收集配置信息
    config_info = {
        "enabled": ParallelConfig.is_enabled(),
        "max_workers": ParallelConfig._config["max_workers"],
        "adaptive": ParallelConfig._config["adaptive"],
        "default_workers": ParallelConfig._config["default_workers"]
    }
    
    # 生成并行配置报告
    logging.info("生成并行配置报告...")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 系统并行处理配置报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 基本配置
        f.write("## 基本配置\n\n")
        f.write(f"- 并行处理状态: {'启用' if config_info['enabled'] else '禁用'}\n")
        f.write(f"- 全局最大线程数: {config_info['max_workers']}\n")
        
        # 自适应配置
        f.write("\n## 自适应线程配置\n\n")
        adaptive = config_info['adaptive']
        f.write(f"- 自适应模式: {'启用' if adaptive['enabled'] else '禁用'}\n")
        if adaptive['enabled']:
            f.write(f"- IO密集型任务系数: {adaptive['io_bound_factor']}\n")
            f.write(f"- CPU密集型任务系数: {adaptive['cpu_bound_factor']}\n")
            
            io_threads = int(config_info['max_workers'] * adaptive['io_bound_factor'])
            cpu_threads = int(config_info['max_workers'] * adaptive['cpu_bound_factor'])
            
            f.write(f"- IO密集型任务线程数: {io_threads}\n")
            f.write(f"- CPU密集型任务线程数: {cpu_threads}\n")
        
        # 模块特定配置
        f.write("\n## 模块特定配置\n\n")
        f.write("| 模块 | 配置线程数 |\n")
        f.write("|------|----------|\n")
        
        for module, workers in config_info['default_workers'].items():
            f.write(f"| {module} | {workers} |\n")
        
        # 初始化各模块并记录线程使用
        f.write("\n## 实际线程使用情况\n\n")
        f.write("现在开始测试各模块实际使用的线程数...\n\n")
        
        # 事件抽取
        logging.info("测试事件抽取模块...")
        f.write("### 事件抽取模块\n\n")
        extractor = provide_extractor()
        
        # 幻觉修复
        logging.info("测试幻觉修复模块...")
        f.write("\n### 幻觉修复模块\n\n")
        refiner = provide_refiner()
        
        # 因果链接
        logging.info("测试因果链接模块...")
        f.write("\n### 因果链接模块\n\n")
        linker = provide_linker()
        
        # 图形构建
        logging.info("测试图形构建模块...")
        f.write("\n### 图形构建模块\n\n")
        renderer = MermaidRenderer()
        
        # 获取并记录线程监控信息
        usage_info = thread_monitor.thread_usage
        
        f.write("\n## 线程使用摘要\n\n")
        f.write("| 模块 | 配置线程数 | 实际使用线程数 | 任务类型 |\n")
        f.write("|------|------------|--------------|--------|\n")
        
        for module, workers in config_info['default_workers'].items():
            actual_workers = usage_info.get(module, {}).get("thread_count", "未知")
            task_type = usage_info.get(module, {}).get("task_type", "未知")
            f.write(f"| {module} | {workers} | {actual_workers} | {task_type} |\n")
        
        # 结论和建议
        f.write("\n## 结论和建议\n\n")
        
        # 检查是否有模块未使用集中配置
        unconfigured_modules = set(usage_info.keys()) - set(config_info['default_workers'].keys())
        if unconfigured_modules:
            f.write("⚠️ 以下模块未使用中央配置:\n\n")
            for module in unconfigured_modules:
                f.write(f"- {module}\n")
            f.write("\n建议将这些模块添加到中央配置中。\n\n")
        
        # 检查配置与使用是否一致
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
        
        # 适应性建议
        f.write("### 优化建议\n\n")
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
    

if __name__ == "__main__":
    setup_logging()
    generate_report()
