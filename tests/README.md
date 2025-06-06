# 《凡人修仙传》因果事件图谱生成系统测试

本目录包含针对《凡人修仙传》因果事件图谱生成系统的各阶段测试。

## 测试结构

测试按照系统开发阶段组织：

- **阶段一**：抽象接口与通用模型测试 (`stage_1/`)
  - `test_models.py`: 测试数据模型 (EventItem, Chapter, CausalEdge, Treasure) 和工具类
  - `test_interfaces.py`: 测试抽象接口 (AbstractExtractor, AbstractRefiner, AbstractLinker, AbstractGraphRenderer)

- **测试工具**：
  - `utils/pretty_test_runner.py`: 美化测试输出格式的自定义测试运行器，捕获并展示测试对象的输出

## 运行测试

### 运行所有测试

```bash
python tests/run_all_tests.py
```

### 运行特定阶段的测试

```bash
python tests/run_all_tests.py -s 1  # 运行阶段一测试
```

### 显示详细测试输出

添加 `-v` 参数可以显示详细的测试输出，包括每个测试类中的测试方法输出：

```bash
python tests/run_all_tests.py -v
python tests/run_all_tests.py -s 1 -v
```

使用详细模式时，测试运行器会：
- 显示每个测试的执行状态（通过、失败或错误）
- 捕获并显示测试方法中的标准输出和错误输出
- 显示测试执行的耗时
- 用彩色文本提高输出的可读性

### 直接运行阶段测试

也可以直接运行各阶段的测试脚本：

```bash
python tests/stage_1/run_tests.py
```
