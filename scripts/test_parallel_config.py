#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并行配置测试脚本

测试各模块使用的线程数是否与配置文件一致。
"""

import os
import sys
import logging
from pathlib import Path

# 将项目根目录添加到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from common.utils.parallel_config import ParallelConfig
from common.utils.config_writer import ConfigWriter
from event_extraction.di.provider import provide_extractor
from hallucination_refine.di.provider import provide_refiner
from causal_linking.di.provider import provide_linker
from graph_builder.service.mermaid_renderer import MermaidRenderer


def setup_logging():
    """设置日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join("logs", "parallel_test.log"))
        ]
    )


def test_parallel_config_consistency():
    """测试并行配置一致性"""
    # 初始化ParallelConfig
    ParallelConfig.initialize()
    
    # 记录配置信息
    logging.info("====== 并行配置测试 ======")
    logging.info(f"并行处理启用状态: {ParallelConfig.is_enabled()}")
    logging.info(f"全局最大线程数: {ParallelConfig._config['max_workers']}")
    
    # 记录各模块配置
    logging.info("模块特定配置:")
    for module, workers in ParallelConfig._config["default_workers"].items():
        logging.info(f"  - {module}: {workers}")
    
    # 测试各模块实例
    logging.info("\n测试各模块实例化:")
    
    # 事件抽取
    logging.info("创建事件抽取器...")
    extractor = provide_extractor()
    
    # 幻觉修复
    logging.info("创建幻觉修复器...")
    refiner = provide_refiner()
    
    # 因果链接
    logging.info("创建因果链接器...")
    linker = provide_linker()
    
    # 图形构建
    logging.info("创建图形渲染器...")
    renderer = MermaidRenderer()
    
    logging.info("所有模块初始化完成")
    

def test_config_updates():
    """测试配置更新"""
    logging.info("\n====== 配置更新测试 ======")
    
    # 记录原始配置
    original_max = ParallelConfig._config["max_workers"]
    original_graph = ParallelConfig._config["default_workers"]["graph_builder"]
    logging.info(f"原始线程配置: 全局={original_max}, 图形构建={original_graph}")
    
    # 更新配置
    test_updates = {
        "max_workers": original_max + 2,
        "default_workers": {
            "graph_builder": original_graph + 1
        }
    }
    logging.info(f"更新配置: {test_updates}")
    
    # 应用更新
    ConfigWriter.update_parallel_config(test_updates)
    
    # 验证更新后的配置
    logging.info(f"更新后配置: 全局={ParallelConfig._config['max_workers']}, " +
                f"图形构建={ParallelConfig._config['default_workers']['graph_builder']}")
    
    # 恢复原始配置
    restore_updates = {
        "max_workers": original_max,
        "default_workers": {
            "graph_builder": original_graph
        }
    }
    logging.info(f"恢复原始配置: {restore_updates}")
    ConfigWriter.update_parallel_config(restore_updates)
    
    # 确认恢复成功
    logging.info(f"恢复后配置: 全局={ParallelConfig._config['max_workers']}, " +
                f"图形构建={ParallelConfig._config['default_workers']['graph_builder']}")


if __name__ == "__main__":
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 设置日志
    setup_logging()
    
    # 运行测试
    test_parallel_config_consistency()
    test_config_updates()
    
    logging.info("测试完成")
