# 《凡人修仙传》因果事件图谱生成系统测试

本目录包含针对《凡人修仙传》因果事件图谱生成系统的各类测试。

## 测试结构

测试按照功能模块进行组织：

- **API测试** (`api_tests/`)
  - `test_api_integration.py`: 测试API连接、请求和响应功能

- **因果链接测试** (`causal_linking_tests/`)
  - `test_causal_linking_optimized.py`: 测试优化后的因果链接流程
  - `test_candidate_generator.py`: 测试候选事件对生成器
  - `test_smart_candidate_generator.py`: 测试优化的候选事件对生成算法
  - `test_linker.py`: 全面测试因果链接器功能

- **事件抽取测试** (`event_extraction_tests/`)
  - `test_event_extraction.py`: 测试事件抽取、处理和验证功能

- **集成测试** (`integration_tests/`)
  - `complete_test.py`: 测试从文本读取到图谱生成的完整流程

- **工具测试** (`utils_tests/`)
  - `check_env.py`: 测试环境变量、依赖和系统配置

## 老版本测试结构 (已弃用)

系统早期开发版本的测试按照系统开发阶段组织：

- **阶段一**：抽象接口与通用模型测试 (`stage_1/`)
- **阶段二**：文本摄入和事件抽取测试 (`stage_2/`)
- **阶段三**：HAR幻觉修复和因果链构建测试 (`stage_3/`)

- **测试工具**：
  - `utils/pretty_test_runner.py`: 美化测试输出格式的自定义测试运行器，捕获并展示测试对象的输出

## 运行测试

### 运行所有测试

```bash
python tests/run_all_tests.py
```

### 运行指定类别的测试

```bash
python tests/run_all_tests.py -c api              # 运行API测试
python tests/run_all_tests.py -c causal_linking   # 运行因果链接测试
python tests/run_all_tests.py -c event_extraction # 运行事件抽取测试
python tests/run_all_tests.py -c integration      # 运行集成测试
python tests/run_all_tests.py -c utils            # 运行工具测试
```

### 显示详细输出

添加 `-v` 参数可以显示详细测试输出：

```bash
python tests/run_all_tests.py -v
```

### 模拟模式

对于依赖API的测试，设置环境变量 `MOCK_API=true` 可以启用模拟模式，避免实际调用API：

```bash
MOCK_API=true python tests/run_all_tests.py -c api
```

这对于CI/CD环境或无法访问API的情况特别有用。
python tests/run_all_tests.py -c integration      # 运行集成测试
python tests/run_all_tests.py -c utils            # 运行工具测试
```

### 显示详细测试输出

添加 `-v` 参数可以显示详细的测试输出：

```bash
python tests/run_all_tests.py -v
python tests/run_all_tests.py -c api -v
```

### 运行单个测试文件

也可以直接运行单个测试文件：

```bash
python tests/api_tests/test_api_integration.py
python tests/causal_linking_tests/test_linker.py
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
