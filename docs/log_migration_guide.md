
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
