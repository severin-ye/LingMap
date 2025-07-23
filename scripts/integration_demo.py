#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化集成应用脚本
演示如何将优化工具集成到现有的因果链接系统中
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from causal_linking.service.optimized_pair_analyzer import OptimizedPairAnalyzer

def create_sample_events() -> List[EventItem]:
    """创建示例事件数据"""
    events = [
        EventItem(
            event_id="E1-1",
            description="韩立在七玄门外门修炼长春功",
            characters=["韩立"],
            location="七玄门",
            chapter_id="第1章"
        ),
        EventItem(
            event_id="E1-2", 
            description="韩立服用小绿瓶中的绿液",
            characters=["韩立"],
            treasures=["小绿瓶", "绿液"],
            chapter_id="第1章"
        ),
        EventItem(
            event_id="E1-3",
            description="韩立的修炼速度大幅提升",
            characters=["韩立"],
            result="修炼速度提升",
            chapter_id="第1章"
        ),
        EventItem(
            event_id="E2-1",
            description="韩立突破到练气期第三层",
            characters=["韩立"],
            result="突破练气期第三层",
            chapter_id="第2章"
        ),
        EventItem(
            event_id="E2-2",
            description="韩立在藏书阁发现了进阶功法",
            characters=["韩立"],
            treasures=["进阶功法"],
            location="藏书阁",
            chapter_id="第2章"
        ),
        EventItem(
            event_id="E2-3",
            description="韩立开始修炼新功法",
            characters=["韩立"],
            chapter_id="第2章"
        ),
        EventItem(
            event_id="E3-1",
            description="韩立的实力再次提升",
            characters=["韩立"],
            result="实力提升",
            chapter_id="第3章"
        ),
        EventItem(
            event_id="E3-2",
            description="韩立被师兄注意到修炼异常",
            characters=["韩立"],
            chapter_id="第3章"
        )
    ]
    return events

def demonstrate_original_vs_optimized():
    """演示原始方法与优化方法的对比"""
    print("=" * 60)
    print("因果链接优化效果演示")
    print("=" * 60)
    
    # 准备测试数据
    events = create_sample_events()
    print(f"准备了 {len(events)} 个测试事件")
    
    # 生成事件对（简化版：相邻事件对）
    event_pairs = []
    for i in range(len(events) - 1):
        event_pairs.append((events[i], events[i + 1]))
    
    print(f"生成了 {len(event_pairs)} 个事件对进行分析")
    
    # 1. 模拟原始方法（单线程，无缓存）
    print("\n1. 原始方法测试...")
    original_start = time.time()
    
    # 模拟原始处理（这里我们直接模拟结果）
    original_edges = []
    for event1, event2 in event_pairs:
        time.sleep(0.1)  # 模拟LLM调用延迟
        # 简单的规则：如果两个事件涉及同一角色，就认为可能有因果关系
        if (event1.characters and event2.characters and 
            any(char in event2.characters for char in event1.characters)):
            edge = CausalEdge(
                from_id=event1.event_id,
                to_id=event2.event_id,
                strength="中",
                reason="涉及相同角色，可能存在因果关系"
            )
            original_edges.append(edge)
    
    original_time = time.time() - original_start
    
    print(f"原始方法结果:")
    print(f"  - 处理时间: {original_time:.2f} 秒")
    print(f"  - 发现因果关系: {len(original_edges)} 条")
    print(f"  - 平均每对时间: {original_time/len(event_pairs):.3f} 秒")
    
    # 2. 优化方法测试
    print("\n2. 优化方法测试...")
    
    # 初始化优化版分析器
    analyzer = OptimizedPairAnalyzer(
        enable_cache=True,
        enable_performance_tracking=True,
        max_workers=3
    )
    
    optimized_start = time.time()
    optimized_edges = analyzer.analyze_batch_optimized(event_pairs)
    optimized_time = time.time() - optimized_start
    
    print(f"优化方法结果:")
    print(f"  - 处理时间: {optimized_time:.2f} 秒")
    print(f"  - 发现因果关系: {len(optimized_edges)} 条")
    print(f"  - 平均每对时间: {optimized_time/len(event_pairs):.3f} 秒")
    
    # 3. 性能对比
    print("\n3. 性能对比分析...")
    time_improvement = max(0, (original_time - optimized_time) / original_time * 100)
    
    print(f"性能提升:")
    print(f"  - 时间节省: {original_time - optimized_time:.2f} 秒")
    print(f"  - 性能提升: {time_improvement:.1f}%")
    print(f"  - 速度倍数: {original_time / max(optimized_time, 0.001):.1f}x")
    
    # 4. 缓存效果测试
    print("\n4. 缓存效果测试...")
    
    # 重复相同的分析以测试缓存
    cache_start = time.time()
    cached_edges = analyzer.analyze_batch_optimized(event_pairs)  # 同样的事件对
    cache_time = time.time() - cache_start
    
    cache_improvement = max(0, (optimized_time - cache_time) / optimized_time * 100)
    
    print(f"缓存效果:")
    print(f"  - 首次分析: {optimized_time:.2f} 秒")
    print(f"  - 缓存分析: {cache_time:.2f} 秒")
    print(f"  - 缓存提升: {cache_improvement:.1f}%")
    
    # 5. 详细统计
    print("\n5. 详细性能统计...")
    stats = analyzer.get_performance_stats()
    
    print(f"优化器统计:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  - {key}: {value:.3f}")
        else:
            print(f"  - {key}: {value}")
    
    # 6. 结果验证
    print("\n6. 结果分析...")
    
    if optimized_edges:
        print("发现的因果关系:")
        for i, edge in enumerate(optimized_edges[:5]):  # 只显示前5个
            print(f"  {i+1}. {edge.from_id} -> {edge.to_id} (强度: {edge.strength})")
            if edge.reason:
                print(f"     理由: {edge.reason}")
    
    # 7. 保存详细报告
    print("\n7. 保存性能报告...")
    report_file = analyzer.save_performance_report()
    
    # 8. 生成集成建议
    print("\n8. 集成建议...")
    generate_integration_recommendations(stats, time_improvement)
    
    return {
        "original_time": original_time,
        "optimized_time": optimized_time,
        "cache_time": cache_time,
        "improvement_percent": time_improvement,
        "cache_improvement_percent": cache_improvement,
        "optimized_edges": len(optimized_edges),
        "stats": stats,
        "report_file": report_file
    }

def generate_integration_recommendations(stats: Dict[str, Any], improvement: float):
    """生成集成建议"""
    recommendations = {
        "immediate_actions": [],
        "configuration_suggestions": {},
        "monitoring_recommendations": [],
        "next_steps": []
    }
    
    # 基于性能数据生成建议
    if improvement > 50:
        recommendations["immediate_actions"].append(
            "✅ 立即部署：性能提升超过50%，建议立即将优化版本集成到生产环境"
        )
    elif improvement > 20:
        recommendations["immediate_actions"].append(
            "🔄 逐步迁移：性能有显著提升，建议先在测试环境验证后部署"
        )
    else:
        recommendations["immediate_actions"].append(
            "⚠️ 需要调优：性能提升有限，建议先优化配置参数"
        )
    
    # 配置建议
    cache_hit_rate = stats.get("cache_hit_rate_percent", 0)
    if cache_hit_rate < 30:
        recommendations["configuration_suggestions"]["cache_size"] = f"当前缓存命中率 {cache_hit_rate:.1f}%，建议增加缓存大小"
    
    if stats.get("success_rate_percent", 100) < 95:
        recommendations["configuration_suggestions"]["error_handling"] = "成功率较低，建议加强错误处理和重试机制"
    
    # 监控建议
    recommendations["monitoring_recommendations"] = [
        "监控缓存命中率，目标 > 60%",
        "监控平均响应时间，目标 < 0.5秒/对",
        "监控内存使用情况，避免内存泄漏",
        "监控API调用成功率，目标 > 95%"
    ]
    
    # 下一步行动
    recommendations["next_steps"] = [
        "1. 在更大数据集上进行压力测试",
        "2. 调整批处理大小和线程数以优化性能",
        "3. 实现持久化缓存以支持重启后的性能",
        "4. 集成到现有的 unified_linker_service.py",
        "5. 添加性能监控仪表板"
    ]
    
    # 打印建议
    print("📋 集成建议:")
    print("\n立即行动:")
    for action in recommendations["immediate_actions"]:
        print(f"  {action}")
    
    if recommendations["configuration_suggestions"]:
        print("\n配置建议:")
        for key, suggestion in recommendations["configuration_suggestions"].items():
            print(f"  - {key}: {suggestion}")
    
    print("\n监控建议:")
    for rec in recommendations["monitoring_recommendations"]:
        print(f"  - {rec}")
    
    print("\n下一步:")
    for step in recommendations["next_steps"]:
        print(f"  {step}")
    
    # 保存建议到文件
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"integration_recommendations_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False)
    
    print(f"\n集成建议已保存到: {filename}")

def demonstrate_real_integration():
    """演示真实的集成场景"""
    print("\n" + "=" * 60)
    print("真实集成场景演示")
    print("=" * 60)
    
    # 1. 检查现有配置文件
    config_files = [
        "common/config/config.json",
        "common/config/parallel_config.json", 
        "common/config/prompt_causal_linking.json"
    ]
    
    print("1. 检查现有配置...")
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"  ✅ 找到配置文件: {config_file}")
        else:
            print(f"  ❌ 缺少配置文件: {config_file}")
    
    # 2. 集成到现有服务
    print("\n2. 集成方案...")
    print("  方案1: 直接替换 PairAnalyzer")
    print("    - 修改 unified_linker_service.py 导入 OptimizedPairAnalyzer")
    print("    - 保持接口兼容性，无需修改其他代码")
    
    print("  方案2: 渐进式集成")
    print("    - 添加配置开关控制是否使用优化版本")
    print("    - 在生产环境中对比两个版本的性能")
    
    print("  方案3: 混合模式")
    print("    - 小批量数据使用原版本")
    print("    - 大批量数据使用优化版本")
    
    # 3. 生成集成代码示例
    print("\n3. 生成集成代码示例...")
    generate_integration_code_example()

def generate_integration_code_example():
    """生成集成代码示例"""
    integration_code = '''
# 在 unified_linker_service.py 中的集成示例

from causal_linking.service.pair_analyzer import PairAnalyzer
from causal_linking.service.optimized_pair_analyzer import OptimizedPairAnalyzer

class UnifiedLinkerService:
    def __init__(self, config):
        self.config = config
        
        # 根据配置选择分析器
        use_optimized = config.get("use_optimized_analyzer", True)
        
        if use_optimized:
            self.pair_analyzer = OptimizedPairAnalyzer(
                model=config.get("model", "gpt-4o"),
                enable_cache=config.get("enable_cache", True),
                enable_performance_tracking=config.get("enable_monitoring", True),
                max_workers=config.get("max_workers", 3)
            )
            print("使用优化版因果分析器")
        else:
            self.pair_analyzer = PairAnalyzer(
                model=config.get("model", "gpt-4o"),
                max_workers=config.get("max_workers", 3)
            )
            print("使用原版因果分析器")
    
    def analyze_events(self, events):
        # 生成事件对
        event_pairs = self.generate_event_pairs(events)
        
        # 分析因果关系（接口保持一致）
        edges = self.pair_analyzer.analyze_batch(event_pairs)
        
        # 如果使用优化版本，获取性能统计
        if hasattr(self.pair_analyzer, 'get_performance_stats'):
            stats = self.pair_analyzer.get_performance_stats()
            print(f"性能统计: {stats}")
        
        return edges
'''
    
    # 保存示例代码
    with open("integration_example.py", "w", encoding="utf-8") as f:
        f.write(integration_code)
    
    print("集成代码示例已保存到: integration_example.py")

if __name__ == "__main__":
    try:
        # 运行完整演示
        results = demonstrate_original_vs_optimized()
        
        # 演示集成场景
        demonstrate_real_integration()
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
        
        print(f"主要成果:")
        print(f"  - 性能提升: {results['improvement_percent']:.1f}%")
        print(f"  - 缓存提升: {results['cache_improvement_percent']:.1f}%")
        print(f"  - 发现因果关系: {results['optimized_edges']} 条")
        print(f"  - 性能报告: {results['report_file']}")
        
        print(f"\n建议下一步:")
        print(f"  1. 查看生成的集成建议和代码示例")
        print(f"  2. 在测试环境中验证集成效果")
        print(f"  3. 逐步部署到生产环境")
        print(f"  4. 持续监控和优化性能")
        
    except Exception as e:
        print(f"演示运行失败: {e}")
        import traceback
        traceback.print_exc()
