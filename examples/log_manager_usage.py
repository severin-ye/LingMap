#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理器使用示例
演示如何在LingMap项目中使用统一的日志管理器
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.utils.log_manager import get_log_manager, LogType


def example_system_logging():
    """系统日志使用示例"""
    print("📝 系统日志示例")
    log_manager = get_log_manager()
    logger = log_manager.get_logger("example_system", LogType.SYSTEM)
    
    logger.info("系统启动")
    logger.debug("加载配置文件")
    logger.warning("内存使用率较高: 85%")
    logger.error("连接数据库失败")
    
    print("  ✅ 系统日志已记录到文件")


def example_performance_logging():
    """性能日志使用示例"""
    print("\n⚡ 性能日志示例")
    log_manager = get_log_manager()
    
    # 模拟性能数据
    performance_data = {
        "module": "event_extraction",
        "operation": "extract_events",
        "input_size": 1000,
        "processing_time": 2.35,
        "memory_usage_mb": 125.6,
        "events_extracted": 45,
        "success_rate": 97.8,
        "cache_hits": 12,
        "api_calls": 8,
        "optimization_notes": [
            "缓存命中率较高",
            "API调用次数已优化",
            "内存使用在预期范围内"
        ]
    }
    
    report_file = log_manager.save_performance_report(
        performance_data,
        custom_filename="event_extraction_performance"
    )
    
    print(f"  ✅ 性能报告已保存: {report_file}")


def example_test_logging():
    """测试日志使用示例"""
    print("\n🧪 测试日志示例")
    log_manager = get_log_manager()
    logger = log_manager.get_logger("example_test", LogType.TEST)
    
    # 记录测试过程
    logger.info("开始执行测试套件: causal_linking_tests")
    logger.info("测试1: test_pair_analysis - PASS")
    logger.info("测试2: test_cache_mechanism - PASS")
    logger.warning("测试3: test_edge_cases - SKIP (依赖服务不可用)")
    logger.info("测试4: test_performance - PASS")
    
    # 保存测试结果
    test_results = {
        "test_suite": "causal_linking_integration",
        "start_time": "2025-09-01 19:05:00",
        "end_time": "2025-09-01 19:05:30",
        "total_tests": 4,
        "passed": 3,
        "failed": 0,
        "skipped": 1,
        "coverage_percent": 87.5,
        "test_details": [
            {
                "name": "test_pair_analysis",
                "status": "PASS",
                "duration": 0.123,
                "assertions": 5
            },
            {
                "name": "test_cache_mechanism", 
                "status": "PASS",
                "duration": 0.089,
                "assertions": 3
            },
            {
                "name": "test_edge_cases",
                "status": "SKIP",
                "reason": "依赖服务不可用"
            },
            {
                "name": "test_performance",
                "status": "PASS", 
                "duration": 0.256,
                "assertions": 8,
                "performance_notes": "性能符合预期"
            }
        ]
    }
    
    result_file = log_manager.save_test_results(
        test_results,
        "causal_linking_integration"
    )
    
    print(f"  ✅ 测试结果已保存: {result_file}")


def example_error_logging():
    """错误日志使用示例"""
    print("\n❌ 错误日志示例")
    log_manager = get_log_manager()
    
    try:
        # 模拟一个实际的错误场景
        def problematic_function():
            data = {"events": []}
            # 故意访问不存在的键
            return data["non_existent_key"]
        
        problematic_function()
        
    except KeyError as e:
        # 使用日志管理器记录错误
        log_manager.log_error(
            e,
            context={
                "module": "event_processing",
                "function": "problematic_function",
                "operation": "data_access",
                "input_data": {"events": []},
                "user_action": "processing_events",
                "environment": "development"
            },
            save_to_file=True
        )
        
        print("  ✅ 错误已记录并保存到文件")


def example_optimization_report():
    """优化报告示例"""
    print("\n🚀 优化报告示例")
    log_manager = get_log_manager()
    
    optimization_data = {
        "optimization_target": "事件提取模块",
        "baseline_performance": {
            "processing_time": 5.2,
            "memory_usage_mb": 256,
            "success_rate": 89.5
        },
        "optimized_performance": {
            "processing_time": 2.1,
            "memory_usage_mb": 180,
            "success_rate": 97.2
        },
        "improvements": {
            "speed_improvement": "59.6%",
            "memory_reduction": "29.7%", 
            "accuracy_improvement": "8.6%"
        },
        "optimization_techniques": [
            "缓存机制优化",
            "批处理实现",
            "内存池管理",
            "算法优化"
        ],
        "next_steps": [
            "监控生产环境性能",
            "继续优化边缘情况",
            "扩展到其他模块"
        ]
    }
    
    json_file, txt_file = log_manager.save_optimization_report(
        optimization_data,
        include_summary=True,
        custom_filename="event_extraction_optimization"
    )
    
    print(f"  ✅ 优化报告已保存: {json_file}")
    print(f"  ✅ 优化摘要已保存: {txt_file}")


def show_log_statistics():
    """显示日志统计信息"""
    print("\n📊 日志统计信息")
    log_manager = get_log_manager()
    stats = log_manager.get_log_stats()
    
    print(f"  📁 日志目录: {stats['logs_directory']}")
    print(f"  📄 总文件数: {stats['total_files']}")
    print(f"  💾 总大小: {stats['total_size_mb']} MB")
    print(f"  🗂️ 文件类型分布:")
    for file_type, count in stats['file_types'].items():
        print(f"     {file_type}: {count} 个文件")


def main():
    """主演示函数"""
    print("🎯 LingMap 统一日志管理器使用示例")
    print("=" * 60)
    
    # 演示各种日志类型
    example_system_logging()
    example_performance_logging()
    example_test_logging()
    example_error_logging()
    example_optimization_report()
    
    # 显示统计信息
    show_log_statistics()
    
    print("\n✅ 演示完成!")
    print("\n📋 要点总结:")
    print("  • 所有日志文件统一保存在 logs/ 目录")
    print("  • 支持多种日志类型: SYSTEM, TEST, PERFORMANCE, API, ERROR")
    print("  • 自动添加时间戳和元数据")
    print("  • 提供便捷的报告保存功能")
    print("  • 支持错误跟踪和上下文记录")
    print("  • 内置日志文件管理和统计")
    
    print("\n🔧 使用建议:")
    print("  1. 在模块开始时获取logger: logger = get_log_manager().get_logger('module_name')")
    print("  2. 使用适当的日志级别: INFO, DEBUG, WARNING, ERROR")
    print("  3. 保存重要数据时使用专门的报告函数")
    print("  4. 在异常处理中使用 log_error() 记录详细上下文")
    print("  5. 定期检查 logs/ 目录的文件大小和数量")


if __name__ == "__main__":
    main()
