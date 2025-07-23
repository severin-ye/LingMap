#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化效果演示脚本
展示性能优化前后的对比效果
"""

import time
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def simulate_original_processing(texts: List[str]) -> Dict[str, Any]:
    """模拟原始处理方式（未优化）"""
    logger.info("开始原始处理方式...")
    start_time = time.time()
    
    all_events = []
    causal_links = []
    
    # 逐个处理文本（无批处理，无缓存）
    for i, text in enumerate(texts):
        logger.info(f"处理文本 {i+1}/{len(texts)}")
        
        # 模拟事件提取（较慢）
        time.sleep(0.3)  # 模拟API调用延迟
        events = extract_events_original(text)
        all_events.extend(events)
        
        # 模拟因果关系分析（较慢）
        if len(all_events) >= 2:
            time.sleep(0.2)  # 模拟分析延迟
            link = analyze_causal_original(all_events[-2], all_events[-1])
            if link:
                causal_links.append(link)
    
    processing_time = time.time() - start_time
    
    return {
        "method": "original",
        "texts_count": len(texts),
        "events_count": len(all_events),
        "links_count": len(causal_links),
        "processing_time": processing_time,
        "events": all_events,
        "causal_links": causal_links
    }

def extract_events_original(text: str) -> List[Dict[str, Any]]:
    """原始事件提取方法"""
    events = []
    keywords = ["修炼", "突破", "丹药", "法宝", "灵气", "战斗", "师父", "弟子"]
    
    for keyword in keywords:
        if keyword in text:
            events.append({
                "type": "event",
                "content": f"发现{keyword}相关事件",
                "text": text,
                "keyword": keyword,
                "method": "original"
            })
    
    return events

def analyze_causal_original(event1: Dict, event2: Dict) -> Dict[str, Any]:
    """原始因果关系分析"""
    causal_indicators = ["因为", "所以", "导致", "结果", "由于"]
    
    text1 = event1.get("text", "")
    text2 = event2.get("text", "")
    
    for indicator in causal_indicators:
        if indicator in text1 or indicator in text2:
            return {
                "type": "causal_link",
                "source_event": event1,
                "target_event": event2,
                "confidence": 0.6,
                "indicator": indicator,
                "method": "original"
            }
    
    return None

def run_optimization_demo():
    """运行优化演示"""
    # 准备测试数据
    test_texts = [
        "张三在修炼室中专心突破筑基期，灵气在体内涌动，最终成功晋级。",
        "李四因为服用了珍贵的筑基丹，所以实力大增，战力显著提升。",
        "王五在危险的秘境中冒险探索，结果发现了一件珍贵的法宝。",
        "赵六与师兄进行友好切磋，因此学会了威力强大的新法术。",
        "钱七在古老的藏书阁中研读典籍，由于勤奋努力而领悟了高深心法。",
        "孙八在修炼过程中遇到瓶颈，所以向师父请教，最终突破了障碍。",
        "周九因为掌握了新的炼丹技巧，结果成功炼制出了极品丹药。",
        "吴十在战斗中使用法宝，导致对手败北，赢得了宝贵的胜利。"
    ]
    
    print("=" * 60)
    print("凡人修仙传 - 优化效果演示")
    print("=" * 60)
    
    # 1. 原始方法测试
    print("\n1. 原始处理方法测试...")
    original_result = simulate_original_processing(test_texts)
    
    print(f"原始方法结果:")
    print(f"  - 处理文本数: {original_result['texts_count']}")
    print(f"  - 提取事件数: {original_result['events_count']}")
    print(f"  - 因果链接数: {original_result['links_count']}")
    print(f"  - 处理时间: {original_result['processing_time']:.2f} 秒")
    
    # 2. 优化方法测试
    print("\n2. 优化方法测试...")
    try:
        import sys
        from pathlib import Path
        
        # 添加项目根目录到路径
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from common.utils.practical_optimizer import OptimizationIntegrator
        
        integrator = OptimizationIntegrator()
        optimized_result = integrator.optimize_complete_pipeline(test_texts)
        
        print(f"优化方法结果:")
        print(f"  - 处理文本数: {len(optimized_result['input_texts'])}")
        print(f"  - 提取事件数: {len(optimized_result['all_events'])}")
        print(f"  - 因果链接数: {len(optimized_result['causal_links'])}")
        print(f"  - 处理时间: {optimized_result['processing_time']:.2f} 秒")
        
        # 3. 性能对比
        print("\n3. 性能对比分析...")
        time_improvement = (original_result['processing_time'] - optimized_result['processing_time']) / original_result['processing_time'] * 100
        
        print(f"性能提升:")
        print(f"  - 时间节省: {original_result['processing_time'] - optimized_result['processing_time']:.2f} 秒")
        print(f"  - 性能提升: {time_improvement:.1f}%")
        
        # 4. 缓存效果测试
        print("\n4. 缓存效果测试...")
        benchmark_result = integrator.benchmark_performance(test_texts[:5])  # 使用部分数据
        
        print(f"缓存效果:")
        print(f"  - 首次运行: {benchmark_result['first_run_time']:.2f} 秒")
        print(f"  - 缓存运行: {benchmark_result['second_run_time']:.2f} 秒")
        print(f"  - 缓存提升: {benchmark_result['cache_improvement_percent']:.1f}%")
        
        # 5. 保存详细报告
        print("\n5. 生成性能报告...")
        report_file = integrator.save_performance_report()
        
        # 6. 优化建议总结
        print("\n6. 优化效果总结:")
        optimization_stats = optimized_result['optimization_stats']
        print(f"  - 处理项目数: {optimization_stats['processed_items']}")
        print(f"  - 缓存命中数: {optimization_stats['cache_hits']}")
        print(f"  - 缓存命中率: {optimization_stats['cache_hit_rate_percent']:.1f}%")
        print(f"  - 批处理大小: {optimization_stats['batch_size']}")
        print(f"  - 预估时间节省: {optimization_stats['estimated_time_saved']:.2f} 秒")
        
        # 7. 具体优化建议
        print("\n7. 具体优化建议:")
        print("  ✅ 已实现:")
        print("    - 批处理优化: 减少API调用开销")
        print("    - 智能缓存: 避免重复计算")
        print("    - 性能监控: 实时跟踪处理效果")
        print("    - 错误处理: 提高系统稳定性")
        
        print("  🚀 可进一步优化:")
        print("    - 并行处理: 利用多线程/多进程")
        print("    - 数据库缓存: 持久化缓存数据")
        print("    - API优化: 连接池和重试机制")
        print("    - 内存优化: 大数据流式处理")
        
        return {
            "original": original_result,
            "optimized": optimized_result,
            "benchmark": benchmark_result,
            "report_file": report_file
        }
        
    except ImportError as e:
        print(f"导入优化模块失败: {e}")
        print("请确保优化模块正确安装")
        return None

def generate_optimization_roadmap():
    """生成优化路线图"""
    roadmap = {
        "immediate_optimizations": {
            "priority": "High",
            "timeframe": "1-2 weeks",
            "items": [
                {
                    "name": "集成批处理",
                    "description": "将批处理集成到现有的事件提取和因果链接模块",
                    "expected_improvement": "20-30%",
                    "files_to_modify": [
                        "causal_linking/service/unified_linker_service.py",
                        "event_extraction/service/event_extractor.py"
                    ]
                },
                {
                    "name": "添加智能缓存",
                    "description": "在关键计算点添加缓存机制",
                    "expected_improvement": "30-50%",
                    "files_to_modify": [
                        "causal_linking/service/pair_analyzer.py",
                        "common/utils/cache_manager.py"
                    ]
                }
            ]
        },
        "medium_term_optimizations": {
            "priority": "Medium",
            "timeframe": "2-4 weeks",
            "items": [
                {
                    "name": "API连接优化",
                    "description": "实现连接池和批量API调用",
                    "expected_improvement": "15-25%",
                    "files_to_modify": [
                        "common/utils/api_client.py",
                        "api_gateway/main.py"
                    ]
                },
                {
                    "name": "并行处理",
                    "description": "利用多线程处理独立任务",
                    "expected_improvement": "40-60%",
                    "files_to_modify": [
                        "common/utils/parallel_processor.py",
                        "scripts/unified_parallel_tool.py"
                    ]
                }
            ]
        },
        "long_term_optimizations": {
            "priority": "Low",
            "timeframe": "1-2 months",
            "items": [
                {
                    "name": "数据库优化",
                    "description": "优化数据存储和检索",
                    "expected_improvement": "10-20%",
                    "files_to_modify": [
                        "common/utils/database_optimizer.py",
                        "graph_builder/service/graph_service.py"
                    ]
                },
                {
                    "name": "架构重构",
                    "description": "微服务架构优化",
                    "expected_improvement": "20-40%",
                    "files_to_modify": [
                        "api_gateway/",
                        "common/interfaces/"
                    ]
                }
            ]
        }
    }
    
    # 保存路线图
    with open("optimization_roadmap.json", "w", encoding="utf-8") as f:
        json.dump(roadmap, f, indent=2, ensure_ascii=False)
    
    print("\n8. 优化路线图已生成 (optimization_roadmap.json)")
    print("   包含短期、中期、长期优化建议和实施计划")
    
    return roadmap

if __name__ == "__main__":
    # 运行演示
    try:
        results = run_optimization_demo()
        
        if results:
            # 生成优化路线图
            roadmap = generate_optimization_roadmap()
            
            print("\n" + "=" * 60)
            print("演示完成！")
            print("=" * 60)
            print(f"性能报告: {results['report_file']}")
            print("优化路线图: optimization_roadmap.json")
            print("\n建议下一步:")
            print("1. 查看性能报告了解详细数据")
            print("2. 根据路线图实施优化方案")
            print("3. 监控优化效果并持续改进")
        
    except Exception as e:
        logger.error(f"演示运行失败: {e}")
        import traceback
        traceback.print_exc()
