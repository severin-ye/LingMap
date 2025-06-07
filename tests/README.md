# 《凡人修仙传》因果事件图谱生成系统测试

本目录包含针对《凡人修仙传》因果事件图谱生成系统的各阶段测试。

## 测试结构

测试按照系统开发阶段组织：

- **阶段一**：抽象接口与通用模型测试 (`stage_1/`)
  - `test_models.py`: 测试数据模型 (EventItem, Chapter, CausalEdge, Treasure) 和工具类
  - `test_interfaces.py`: 测试抽象接口 (AbstractExtractor, AbstractRefiner, AbstractLinker, AbstractGraphRenderer)

- **阶段二**：文本摄入和事件抽取测试 (`stage_2/`)
  - `test_text_ingestion.py`: 测试文本加载和章节分割功能
  - `test_event_extraction.py`: 测试事件抽取模块和LLM调用

- **阶段三**：HAR幻觉修复和因果链构建测试 (`stage_3/`)
  - `test_hallucination_refine.py`: 测试HAR幻觉检测和修复功能
  - `test_causal_linking.py`: 测试因果关系识别和DAG构建功能

- **测试工具**：
  - `utils/pretty_test_runner.py`: 美化测试输出格式的自定义测试运行器，捕获并展示测试对象的输出

## 运行测试

### 运行所有测试

```bash
python -m tests.run_all_tests
```

### 运行特定阶段的测试

```bash
python -m tests.run_all_tests -s 1  # 运行阶段一测试
```

### 显示详细测试输出

添加 `-v` 参数可以显示详细的测试输出，包括每个测试类中的测试方法输出：

```bash
python -m tests.run_all_tests -v
python -m tests.run_all_tests -s 1 -v
```

使用详细模式时，测试运行器会：
- 显示每个测试的执行状态（通过、失败或错误）
- 捕获并显示测试方法中的标准输出和错误输出
- 显示测试执行的耗时
- 用彩色文本提高输出的可读性

### 直接运行阶段测试

也可以直接运行各阶段的测试脚本：

```bash
python -m tests.stage_1.run_tests
```

## Stage 3 Tests - HAR幻觉修复和因果链构建测试 ✅

**状态**: 已完成并通过

**测试内容**:
- HAR (Hallucination Refine) 幻觉修复模块
- Causal Linking 因果链接模块

### HAR幻觉修复模块测试

**文件**: `tests/stage_3/test_hallucination_refine.py`

测试覆盖:
- ✅ 单个事件幻觉检测和修复
- ✅ 批量事件并行修复
- ✅ LLM调用失败处理
- ✅ 无幻觉检测的情况
- ✅ 依赖注入提供器集成
- ✅ 响应解析功能
- ✅ 不完整响应处理

### 因果链接模块测试

**文件**: `tests/stage_3/test_causal_linking.py`

测试覆盖:
- ✅ 两事件间因果关系分析
- ✅ 批量事件因果链接
- ✅ DAG构建和环检测
- ✅ 图算法(可达性检测)
- ✅ LLM调用失败处理
- ✅ 无因果关系处理
- ✅ 依赖注入提供器集成
- ✅ 响应解析和验证
- ✅ 完整因果链构建流程

### 测试特点

1. **真实场景模拟**: 使用《凡人修仙传》中的真实角色和情节
2. **模拟LLM响应**: 完整模拟各种API响应场景
3. **错误处理覆盖**: 测试API失败、网络错误等异常情况
4. **并发处理测试**: 验证多线程批量处理功能
5. **集成测试**: 完整的端到端流程验证

### 运行方式

```bash
# 运行Stage 3所有测试
python tests/stage_3/run_tests.py

# 运行特定模块测试
python -m pytest tests/stage_3/test_hallucination_refine.py -v
python -m pytest tests/stage_3/test_causal_linking.py -v

# 运行所有阶段测试
python tests/run_all_tests.py
```

### 测试结果

- **总测试数**: 22
- **通过数**: 22
- **失败数**: 0
- **测试覆盖率**: 100%

---

## 🎉 项目测试总结

### 整体状态

- **Stage 1** ✅ 基础模型和接口测试 (18个测试)
- **Stage 2** ✅ 文本摄入和事件抽取测试 (7个测试)  
- **Stage 3** ✅ HAR幻觉修复和因果链接测试 (22个测试)

**总计**: 47个测试全部通过

### 系统测试流程

1. **模型验证** → 核心数据结构正确性
2. **接口测试** → 抽象接口规范验证
3. **文本处理** → 章节加载和文本分割
4. **事件抽取** → LLM驱动的事件提取
5. **幻觉修复** → 事件质量保证机制
6. **因果链接** → 事件间关系构建
7. **图谱生成** → 最终因果图谱输出

### 质量保证

- **单元测试**: 每个模块独立功能验证
- **集成测试**: 模块间协作验证
- **错误处理**: 异常情况覆盖
- **性能测试**: 并发处理验证
- **端到端测试**: 完整流程验证

---
