#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
因果链接测试统一脚本

将所有与因果链接相关的测试集成到一个文件中，提供以下测试功能：
1. 标准候选生成器测试
2. 智能候选生成器测试
3. 优化的因果链接流程测试
4. 实体权重调整测试
5. 链接器综合测试

使用方式:
    python unified_causal_tests.py --test all              # TODO: Translate - Run所有Test
    python unified_causal_tests.py --test candidate        # TODO: Translate - Run候选Generate器Test
    python unified_causal_tests.py --test smart-candidate  # TODO: Translate - Run智能候选Generate器Test
    python unified_causal_tests.py --test linking          # TODO: Translate - Run优化的causallinkingTest
    python unified_causal_tests.py --test entity-weights   # TODO: Translate - Run实体权重Test
    python unified_causal_tests.py --test linker           # TODO: Translate - Runlinking器综合Test
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime

# TODO: Translate - Add project root directory toPython路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# TODO: Translate - Import相关模块
from common.models.event import EventItem
from causal_linking.di.provider import provide_linker
from causal_linking.service.candidate_generator import CandidateGenerator

# TODO: Translate - Set日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(project_root, 'logs', f"unified_causal_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        )
    ]
)
logger = logging.getLogger(__name__)


def load_test_events(event_file_path=None):
    """加载测试事件数据"""
    if not event_file_path:
        event_file_path = os.path.join(project_root, 'debug/extracted_events.json')
    
    try:
        with open(event_file_path, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        events = [EventItem.from_dict(event_data) for event_data in events_data]
        logger.info(f"成功加载 {len(events)} 个事件")
        return events
    except Exception as e:
        logger.error(f"加载事件失败: {e}")
        return []


def test_candidate_generator():
    """测试候选事件对生成器"""
    logger.info("=== 候选事件对生成器测试 ===")
    
    # TODO: Translate - Loadevent数据
    events = load_test_events()
    if not events:
        return
    
    # SetTestConfigure
    test_configs = [
        {"name": "默认配置", "params": {"min_entity_support": 3, "entity_weight": 1.0, "time_weight": 1.0}},
        {"name": "较高实体支持", "params": {"min_entity_support": 5, "entity_weight": 1.0, "time_weight": 1.0}},
        {"name": "较低实体支持", "params": {"min_entity_support": 2, "entity_weight": 1.0, "time_weight": 1.0}},
        {"name": "高实体权重", "params": {"min_entity_support": 3, "entity_weight": 2.0, "time_weight": 0.5}},
        {"name": "高时间权重", "params": {"min_entity_support": 3, "entity_weight": 0.5, "time_weight": 2.0}}
    ]
    
    # TODO: Translate - Create结果目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = os.path.join(project_root, 'output', f'candidate_test_{timestamp}')
    os.makedirs(result_dir, exist_ok=True)
    result_file = os.path.join(result_dir, 'candidate_generator_results.txt')
    
    # RunTest
    logger.info(f"开始测试各种配置下的候选生成器性能...")
    
    with open(result_file, 'w', encoding='utf-8') as log:
        log.write(f"候选事件对生成器测试 - {datetime.now()}\n")
        log.write(f"事件总数: {len(events)}\n")
        log.write(f"全组合配对数: {len(events) * (len(events) - 1) // 2}\n\n")
        
        for config in test_configs:
            try:
                logger.info(f"测试配置: {config['name']}")
                
                # TODO: Translate - CreateGenerate器并Run
                generator = CandidateGenerator(**config['params'])
                candidate_pairs = generator.generate_candidate_pairs(events)
                
                # TODO: Translate - 记录结果
                result = (
                    f"配置: {config['name']}\n"
                    f"参数: {config['params']}\n"
                    f"生成候选事件对数量: {len(candidate_pairs)}\n"
                    f"相对于全配对 ({len(events) * (len(events) - 1) // 2}) 的比例: "
                    f"{len(candidate_pairs) / (len(events) * (len(events) - 1) // 2) * 100:.2f}%\n"
                )
                logger.info(result)
                log.write(result + "\n")
                
            except Exception as e:
                error_msg = f"测试失败: {e}"
                logger.error(error_msg)
                log.write(error_msg + "\n")
    
    logger.info(f"测试结果已保存到: {result_file}")


def test_smart_candidate_generator():
    """测试智能候选事件对生成器"""
    logger.info("=== 智能候选事件对生成器测试 ===")
    
    # TODO: Translate - Loadevent数据
    events = load_test_events()
    if not events:
        return
    
    # SetTestConfigure
    test_configs = [
        {
            "name": "基础配置",
            "params": {
                "min_entity_support": 3,
                "entity_weight": 1.0,
                "time_weight": 1.0,
                "smart_filter": True
            }
        },
        {
            "name": "实体聚焦",
            "params": {
                "min_entity_support": 3,
                "entity_weight": 2.0,
                "time_weight": 0.5,
                "smart_filter": True
            }
        },
        {
            "name": "时间优先",
            "params": {
                "min_entity_support": 2,
                "entity_weight": 0.5,
                "time_weight": 1.5,
                "smart_filter": True
            }
        },
        {
            "name": "平衡配置",
            "params": {
                "min_entity_support": 2,
                "entity_weight": 1.0,
                "time_weight": 1.0,
                "smart_filter": True,
                "max_distance": 10
            }
        },
        {
            "name": "非智能对照组",
            "params": {
                "min_entity_support": 3,
                "entity_weight": 1.0,
                "time_weight": 1.0,
                "smart_filter": False
            }
        }
    ]
    
    # TODO: Translate - Create结果目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = os.path.join(project_root, 'output', f'smart_candidate_test_{timestamp}')
    os.makedirs(result_dir, exist_ok=True)
    log_file = os.path.join(result_dir, 'smart_candidate_results.txt')
    
    # TODO: Translate - RunTest并收集结果
    all_possible_pairs = len(events) * (len(events) - 1) // 2
    results = []
    
    for config in test_configs:
        logger.info(f"测试配置: {config['name']}")
        
        try:
            # TODO: Translate - CreateGenerate器
            start_time = time.time()
            generator = CandidateGenerator(**config["params"])
            
            # TODO: Translate - Generate候选对
            candidate_pairs = generator.generate_candidate_pairs(events)
            elapsed_time = time.time() - start_time
            
            # TODO: Translate - 收集结果
            result = {
                "config_name": config["name"],
                "params": config["params"],
                "pairs_count": len(candidate_pairs),
                "percentage": len(candidate_pairs) / all_possible_pairs * 100,
                "elapsed_time": elapsed_time
            }
            
            results.append(result)
            logger.info(
                f"配置 '{config['name']}' 生成 {len(candidate_pairs)} 个候选对 "
                f"({result['percentage']:.2f}% 全组合), 耗时: {elapsed_time:.2f}秒"
            )
            
        except Exception as e:
            logger.error(f"配置 '{config['name']}' 测试失败: {e}")
    
    # TODO: Translate - Save结果
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"智能候选事件对生成器测试 - {datetime.now()}\n")
        f.write(f"事件总数: {len(events)}\n")
        f.write(f"全组合配对数量: {all_possible_pairs}\n\n")
        
        for result in results:
            f.write(f"配置: {result['config_name']}\n")
            f.write(f"参数: {result['params']}\n")
            f.write(f"生成候选事件对数量: {result['pairs_count']}\n")
            f.write(f"相对于全配对的比例: {result['percentage']:.2f}%\n")
            f.write(f"耗时: {result['elapsed_time']:.2f} 秒\n\n")
    
    logger.info(f"测试结果已保存到: {log_file}")


def test_causal_linking():
    """测试优化后的因果链接流程"""
    logger.info("=== 优化后因果链接测试 ===")
    start_time = time.time()
    
    # TODO: Translate - SetTest参数
    os.environ["MAX_EVENTS_PER_CHAPTER"] = "15"
    os.environ["MIN_ENTITY_SUPPORT"] = "3"
    os.environ["MAX_CANDIDATE_PAIRS"] = "100"
    
    # TODO: Translate - Loadevent数据
    events = load_test_events()
    if not events:
        return
    
    # TODO: Translate - Createcausallinking器
    try:
        linker = provide_linker(use_optimized=True)
        logger.info("成功创建因果链接器")
    except Exception as e:
        logger.error(f"创建链接器失败: {e}")
        return
    
    # Executecausallinking
    try:
        logger.info("开始执行因果链接...")
        edges = linker.link_events(events)
        logger.info(f"发现 {len(edges)} 个因果关系")
    except Exception as e:
        logger.error(f"因果链接失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # TODO: Translate - Build有向无环图
    try:
        logger.info("构建有向无环图...")
        events, dag_edges = linker.build_dag(events, edges)
        logger.info(f"DAG构建完成，保留 {len(dag_edges)} 条边")
    except Exception as e:
        logger.error(f"构建DAG失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # TODO: Translate - 计算总Execute时间
    elapsed = time.time() - start_time
    logger.info(f"总耗时: {elapsed:.2f} 秒")
    
    # SaveOutput
    try:
        output_dir = os.path.join(project_root, 'output', f'optimized_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        os.makedirs(output_dir, exist_ok=True)
        
        # TODO: Translate - Savecausal关系
        output_file = os.path.join(output_dir, 'causal_relations.json')
        output_data = {
            "nodes": [event.to_dict() for event in events],
            "edges": [edge.to_dict() for edge in dag_edges]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"结果已保存到: {output_file}")
        
        # TODO: Translate - SaveTest信息
        info_file = os.path.join(output_dir, 'test_info.txt')
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"优化后因果链接测试结果 - {datetime.now()}\n")
            f.write(f"事件总数: {len(events)}\n")
            f.write(f"发现因果关系数: {len(edges)}\n")
            f.write(f"DAG边数: {len(dag_edges)}\n")
            f.write(f"总耗时: {elapsed:.2f} 秒\n")
        
        logger.info(f"测试信息已保存到: {info_file}")
    except Exception as e:
        logger.error(f"保存结果失败: {e}")


def test_entity_weights():
    """测试实体频率权重调整功能"""
    logger.info("=== 实体频率权重调整测试 ===")
    
    # TODO: Translate - Loadevent数据
    events = load_test_events()
    if not events:
        return
    
    # TestConfigure
    entity_weight_configs = [0.5, 1.0, 1.5, 2.0, 2.5]
    reverse_weight_configs = [True, False]
    
    # TODO: Translate - Create结果目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = os.path.join(project_root, 'output', f'entity_weights_test_{timestamp}')
    os.makedirs(result_dir, exist_ok=True)
    result_file = os.path.join(result_dir, 'entity_weights_results.txt')
    
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(f"实体频率权重调整测试 - {datetime.now()}\n")
        f.write(f"事件总数: {len(events)}\n\n")
        
        for reverse in reverse_weight_configs:
            f.write(f"{'反向权重' if reverse else '正向权重'} 测试:\n")
            f.write("-" * 50 + "\n")
            
            for weight in entity_weight_configs:
                try:
                    logger.info(f"测试 {'反向' if reverse else '正向'}权重，权重值: {weight}")
                    
                    # TODO: Translate - ConfigureGenerate器
                    generator = CandidateGenerator(
                        min_entity_support=2,
                        entity_weight=weight,
                        time_weight=1.0,
                        reverse_entity_weight=reverse
                    )
                    
                    # TODO: Translate - Generate候选对
                    start_time = time.time()
                    candidate_pairs = generator.generate_candidate_pairs(events)
                    elapsed_time = time.time() - start_time
                    
                    # TODO: Translate - 分析实体分布
                    entity_counts = {}
                    for pair in candidate_pairs:
                        for entity in pair.shared_entities:
                            if entity not in entity_counts:
                                entity_counts[entity] = 0
                            entity_counts[entity] += 1
                    
                    # TODO: Translate - 统计分布情况
                    top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                    
                    # TODO: Translate - 记录结果
                    f.write(f"权重值: {weight}\n")
                    f.write(f"候选对数量: {len(candidate_pairs)}\n")
                    f.write(f"处理时间: {elapsed_time:.2f}秒\n")
                    f.write(f"Top 10实体分布:\n")
                    for entity, count in top_entities:
                        f.write(f"  {entity}: {count}次\n")
                    f.write("\n")
                    
                    logger.info(
                        f"{'反向' if reverse else '正向'}权重 {weight}: "
                        f"生成 {len(candidate_pairs)} 个候选对，耗时: {elapsed_time:.2f}秒"
                    )
                    
                except Exception as e:
                    error_msg = f"测试失败 (权重={weight}, 反向={reverse}): {e}"
                    logger.error(error_msg)
                    f.write(f"{error_msg}\n\n")
    
    logger.info(f"测试结果已保存到: {result_file}")


def test_linker_comprehensive():
    """链接器综合测试"""
    logger.info("=== 链接器综合测试 ===")
    
    # LoadTestevent
    events = load_test_events()
    if not events:
        return
    
    # TODO: Translate - CreateOutput目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(project_root, 'output', f'linker_test_{timestamp}')
    os.makedirs(output_dir, exist_ok=True)
    
    # TODO: Translate - Test不同的linking器Configure
    configs = [
        {"name": "优化版 (默认)", "params": {"use_optimized": True}},
        {"name": "基础版", "params": {"use_optimized": False}},
        {"name": "优化版 (高实体权重)", "params": {"use_optimized": True, "entity_weight": 2.0, "time_weight": 0.8}},
        {"name": "优化版 (高时间权重)", "params": {"use_optimized": True, "entity_weight": 0.8, "time_weight": 2.0}},
    ]
    
    # TODO: Translate - 比较结果
    results = []
    for config in configs:
        logger.info(f"测试配置: {config['name']}")
        
        try:
            # TODO: Translate - Createlinking器
            start_time = time.time()
            linker = provide_linker(**config['params'])
            
            # Executelinking
            edges = linker.link_events(events)
            
            # BuildDAG
            _, dag_edges = linker.build_dag(events, edges)
            elapsed_time = time.time() - start_time
            
            # TODO: Translate - 记录结果
            result = {
                "config_name": config["name"],
                "params": config["params"],
                "total_edges": len(edges),
                "dag_edges": len(dag_edges),
                "elapsed_time": elapsed_time
            }
            results.append(result)
            
            # TODO: Translate - Output结果
            logger.info(
                f"配置 '{config['name']}' - 发现 {len(edges)} 条边，"
                f"DAG保留 {len(dag_edges)} 条边，耗时: {elapsed_time:.2f}秒"
            )
            
            # TODO: Translate - Save此Configure的图谱结果
            result_file = os.path.join(output_dir, f"result_{config['name'].replace(' ', '_')}.json")
            result_data = {
                "nodes": [event.to_dict() for event in events],
                "edges": [edge.to_dict() for edge in dag_edges]
            }
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"配置 '{config['name']}' 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    # TODO: Translate - Save比较结果
    compare_file = os.path.join(output_dir, "comparison_results.txt")
    with open(compare_file, 'w', encoding='utf-8') as f:
        f.write(f"链接器综合测试结果比较 - {datetime.now()}\n")
        f.write(f"事件总数: {len(events)}\n\n")
        
        for result in results:
            f.write(f"配置: {result['config_name']}\n")
            f.write(f"参数: {result['params']}\n")
            f.write(f"发现边数: {result['total_edges']}\n")
            f.write(f"DAG边数: {result['dag_edges']}\n")
            f.write(f"耗时: {result['elapsed_time']:.2f} 秒\n\n")
    
    logger.info(f"比较结果已保存到: {compare_file}")
    logger.info(f"所有测试结果已保存到: {output_dir}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="因果链接测试统一脚本")
    parser.add_argument(
        "--test", 
        choices=["all", "candidate", "smart-candidate", "linking", "entity-weights", "linker"],
        default="all",
        help="要运行的测试类型"
    )
    
    args = parser.parse_args()
    
    logger.info(f"=== 开始因果链接统一测试 ({args.test}) ===")
    
    if args.test == "all" or args.test == "candidate":
        test_candidate_generator()
    
    if args.test == "all" or args.test == "smart-candidate":
        test_smart_candidate_generator()
    
    if args.test == "all" or args.test == "linking":
        test_causal_linking()
    
    if args.test == "all" or args.test == "entity-weights":
        test_entity_weights()
    
    if args.test == "all" or args.test == "linker":
        test_linker_comprehensive()
    
    logger.info("=== 测试完成 ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        import traceback
        traceback.print_exc()
