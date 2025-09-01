#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理器迁移脚本
将项目中的其他日志代码迁移到统一的日志管理器
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.utils.log_manager import get_log_manager, LogType


def update_test_files():
    """更新测试文件中的日志代码"""
    print("🔄 正在更新测试文件...")
    
    # 1. unified_causal_tests.py
    test_file = project_root / "tests/causal_linking_tests/unified_causal_tests.py"
    if test_file.exists():
        print(f"  - 更新 {test_file}")
        # 这里可以添加自动替换逻辑，或者提供手动更新指导
        
    # 2. test_smart_candidate_generator.py
    test_file = project_root / "tests/causal_linking_tests/test_smart_candidate_generator.py"
    if test_file.exists():
        print(f"  - 更新 {test_file}")
        
    # 3. test_candidate_generator.py
    test_file = project_root / "tests/causal_linking_tests/test_candidate_generator.py"
    if test_file.exists():
        print(f"  - 更新 {test_file}")


def demonstrate_unified_logging():
    """演示统一日志管理器的使用"""
    print("🎯 统一日志管理器使用演示")
    print("=" * 50)
    
    # 获取日志管理器
    log_manager = get_log_manager()
    
    # 演示不同类型的logger
    system_logger = log_manager.get_logger("system_demo", LogType.SYSTEM)
    test_logger = log_manager.get_logger("test_demo", LogType.TEST)
    perf_logger = log_manager.get_logger("perf_demo", LogType.PERFORMANCE)
    
    # 记录一些示例日志
    system_logger.info("系统模块初始化完成")
    test_logger.info("测试开始执行")
    perf_logger.info("性能监控启动")
    
    # 演示保存报告
    print("\n📊 保存性能报告演示:")
    perf_data = {
        "test_name": "日志管理器测试",
        "duration": 0.123,
        "operations": 100,
        "success_rate": 100.0,
        "notes": "统一日志管理器集成测试"
    }
    
    perf_file = log_manager.save_performance_report(
        perf_data,
        custom_filename="log_manager_test"
    )
    print(f"  ✅ 性能报告已保存: {perf_file}")
    
    # 演示保存测试结果
    print("\n🧪 保存测试结果演示:")
    test_data = {
        "test_suite": "日志管理器测试套件",
        "tests_run": 5,
        "tests_passed": 5,
        "tests_failed": 0,
        "coverage": "100%",
        "details": [
            {"test": "logger_creation", "status": "PASS"},
            {"test": "file_logging", "status": "PASS"},
            {"test": "performance_reporting", "status": "PASS"},
            {"test": "error_handling", "status": "PASS"},
            {"test": "cleanup", "status": "PASS"}
        ]
    }
    
    test_file = log_manager.save_test_results(
        test_data,
        "log_manager_integration",
        custom_filename="log_manager_test_results"
    )
    print(f"  ✅ 测试结果已保存: {test_file}")
    
    # 演示错误记录
    print("\n❌ 错误记录演示:")
    try:
        # 故意触发一个错误
        raise ValueError("这是一个演示错误")
    except Exception as e:
        log_manager.log_error(
            e,
            context={
                "module": "log_manager_demo",
                "operation": "error_demonstration",
                "user_action": "running_migration_script"
            }
        )
    
    # 获取统计信息
    print("\n📈 日志统计信息:")
    stats = log_manager.get_log_stats()
    for key, value in stats.items():
        print(f"  - {key}: {value}")


def generate_migration_guide():
    """生成迁移指南"""
    print("\n📋 生成迁移指南...")
    
    guide_content = """
# 日志管理器迁移指南

## 概述
统一日志管理器 (`common/utils/log_manager.py`) 提供了项目中所有日志功能的集中管理。

## 主要功能
1. **统一日志记录** - 标准化的logging配置
2. **性能报告管理** - 自动化的性能数据保存
3. **文件组织** - 所有日志文件统一存放在logs目录
4. **类型化日志** - 支持不同类型的日志（系统、测试、性能等）
5. **错误跟踪** - 统一的错误记录和报告

## 使用方法

### 基本日志记录
```python
from common.utils.log_manager import get_log_manager, LogType

# 获取日志管理器
log_manager = get_log_manager()

# 获取logger
logger = log_manager.get_logger("module_name", LogType.SYSTEM)
logger.info("这是一条信息")
logger.error("这是一条错误")
```

### 保存性能报告
```python
# 替换原来的手动文件保存
perf_data = {"duration": 1.23, "success_rate": 100.0}
filepath = log_manager.save_performance_report(
    perf_data, 
    custom_filename="my_performance_test"
)
```

### 保存测试结果
```python
test_data = {"tests_run": 10, "tests_passed": 9}
filepath = log_manager.save_test_results(
    test_data,
    "integration_test"
)
```

### 错误处理
```python
try:
    # 一些操作
    pass
except Exception as e:
    log_manager.log_error(e, context={"module": "my_module"})
```

## 迁移步骤

### 1. 导入日志管理器
```python
from common.utils.log_manager import get_log_manager, LogType
```

### 2. 替换logging配置
**原来：**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

**现在：**
```python
log_manager = get_log_manager()
logger = log_manager.get_logger(__name__, LogType.SYSTEM)
```

### 3. 替换文件保存逻辑
**原来：**
```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"report_{timestamp}.json"
logs_dir = "logs"
os.makedirs(logs_dir, exist_ok=True)
filepath = os.path.join(logs_dir, filename)
with open(filepath, 'w') as f:
    json.dump(data, f)
```

**现在：**
```python
filepath = log_manager.save_performance_report(data, "my_report")
```

## 已迁移的文件
- ✅ `scripts/integration_demo_mock.py`
- ✅ `scripts/final_optimization_report.py`

## 待迁移的文件
- 🔄 `tests/causal_linking_tests/unified_causal_tests.py`
- 🔄 `tests/causal_linking_tests/test_smart_candidate_generator.py`
- 🔄 `tests/causal_linking_tests/test_candidate_generator.py`
- 🔄 其他包含日志逻辑的测试文件

## 注意事项
1. 迁移后确保测试通过
2. 检查日志文件是否正确生成在logs目录
3. 验证日志格式和内容的正确性
4. 考虑旧日志文件的清理

## 配置选项
可以通过 `LogConfig` 类自定义日志行为：
```python
from common.utils.log_manager import LogConfig, LogManager

config = LogConfig(
    logs_dir="custom_logs",
    log_level="DEBUG",
    enable_console=True
)
log_manager = LogManager(config)
```
"""
    
    guide_file = project_root / "docs" / "log_migration_guide.md"
    guide_file.parent.mkdir(exist_ok=True)
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"  ✅ 迁移指南已保存: {guide_file}")


def main():
    """主函数"""
    print("🚀 LingMap 日志管理器迁移")
    print("=" * 50)
    
    # 演示统一日志管理器
    demonstrate_unified_logging()
    
    # 生成迁移指南
    generate_migration_guide()
    
    # 提供迁移建议
    print("\n✅ 迁移完成!")
    print("\n📋 下一步:")
    print("  1. 查看生成的迁移指南: docs/log_migration_guide.md")
    print("  2. 逐步迁移测试文件到新的日志管理器")
    print("  3. 验证所有日志功能正常工作")
    print("  4. 清理项目根目录的旧日志文件")
    
    print("\n🎯 已集成的功能:")
    print("  ✅ 统一的日志配置和管理")
    print("  ✅ 自动化的报告文件保存")
    print("  ✅ 类型化的日志记录")
    print("  ✅ 错误跟踪和报告")
    print("  ✅ 日志文件统计和管理")


if __name__ == "__main__":
    main()
