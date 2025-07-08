# 新的测试目录结构

本目录包含重新组织和优化后的测试代码，按照功能和测试类型进行了清晰的分类。

## 目录结构

```
tests_new/
├── unit/               # 单元测试
│   ├── test_models.py     # 数据模型单元测试
│   └── test_interfaces.py # 接口单元测试
├── integration/        # 集成测试
│   ├── test_api_integration.py    # API集成测试 (合并5个相似文件)
│   ├── test_event_extraction.py  # 事件抽取集成测试 (合并2个文件)
│   └── test_causal_linking.py    # 因果链接集成测试 (合并4个文件)
├── e2e/               # 端到端测试
│   └── test_complete_pipeline.py # 完整流程测试 (合并3个文件)
├── utils/             # 工具测试
│   └── test_common_utils.py      # 通用工具测试
└── README.md          # 本文件
```

## 测试分类说明

### 单元测试 (unit/)
- **test_models.py**: 测试所有数据模型类 (Chapter, EventItem, CausalEdge, Treasure)
- **test_interfaces.py**: 测试抽象接口定义

### 集成测试 (integration/)
- **test_api_integration.py**: 合并了以下文件的API测试功能
  - test_api_integration.py (原)
  - test_api_integration_improved.py
  - test_api_integration_new.py
  - test_api_integration_fixed.py
  - test_api_integration_scripts.py

- **test_event_extraction.py**: 合并了以下文件的事件抽取测试
  - test_event_extraction.py (原)
  - test_event_extraction_scripts.py

- **test_causal_linking.py**: 合并了以下文件的因果链接测试
  - test_candidate_generator.py
  - test_causal_linking_optimized.py
  - test_linker.py
  - test_smart_candidate_generator.py

### 端到端测试 (e2e/)
- **test_complete_pipeline.py**: 合并了以下文件的完整流程测试
  - complete_test.py
  - complete_test_scripts.py
  - test_end_to_end_integration.py

### 工具测试 (utils/)
- **test_common_utils.py**: 测试通用工具函数

## 运行测试

### 运行所有测试
```bash
cd tests_new
pytest -v
```

### 运行特定类型的测试
```bash
# 单元测试
pytest unit/ -v

# 集成测试
pytest integration/ -v

# 端到端测试
pytest e2e/ -v

# 工具测试
pytest utils/ -v
```

### 运行特定测试文件
```bash
# API集成测试
pytest integration/test_api_integration.py -v

# 数据模型测试
pytest unit/test_models.py -v

# 完整流程测试
pytest e2e/test_complete_pipeline.py -v
```

## 测试特性

### 1. 模拟模式支持
所有集成测试都支持模拟模式，通过环境变量 `MOCK_API=true` 启用：
```bash
MOCK_API=true pytest integration/ -v
```

### 2. 错误处理
- 所有测试都包含适当的错误处理和异常捕获
- 导入失败时会优雅降级到模拟模式
- 提供详细的错误信息和日志

### 3. 配置灵活性
- 支持通过环境变量配置API超时时间
- 支持调试模式以获取更详细的输出
- 兼容不同的LLM提供商 (OpenAI, DeepSeek)

### 4. 测试报告
每个测试都会生成详细的测试报告，包括：
- 执行状态和结果
- 性能指标 (响应时间、处理数量等)
- 错误信息和调试信息

## 优化说明

### 代码去重
- 将功能相同的测试文件合并为单一文件
- 消除了重复的测试逻辑和设置代码
- 统一了测试接口和响应格式

### 结构优化
- 按照测试金字塔原则组织目录结构
- 单元测试 -> 集成测试 -> 端到端测试 的清晰层次
- 每个测试文件职责单一、功能明确

### 可维护性提升
- 所有测试都使用pytest框架
- 统一的测试基类和工具函数
- 一致的错误处理和日志记录方式
- 完善的文档和注释

## 迁移指南

如果需要从旧的测试目录迁移，请参考以下映射关系：

### API测试迁移
```
tests/api_tests/ → tests_new/integration/test_api_integration.py
```

### 事件抽取测试迁移
```
tests/event_extraction_tests/ → tests_new/integration/test_event_extraction.py
```

### 因果链接测试迁移
```
tests/causal_linking_tests/ → tests_new/integration/test_causal_linking.py
```

### 完整流程测试迁移
```
tests/integration_tests/ → tests_new/e2e/test_complete_pipeline.py
tests/stage_6/ → tests_new/e2e/test_complete_pipeline.py
```

### 单元测试迁移
```
tests/stage_1/ → tests_new/unit/
```

## 注意事项

1. **环境要求**: 确保已安装所有依赖包 (`pip install -r requirements.txt`)
2. **环境变量**: 需要设置适当的API密钥环境变量
3. **模拟模式**: 在CI/CD环境中建议使用模拟模式避免API调用
4. **日志输出**: 测试日志会保存到 `logs/` 目录中

## 后续计划

1. 添加更多的单元测试覆盖未测试的组件
2. 完善性能测试和压力测试
3. 添加自动化的回归测试
4. 集成代码覆盖率报告
