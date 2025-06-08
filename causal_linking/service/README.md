# 因果链接器统一说明

## 背景和目的

在系统开发过程中，我们实现了两个因果链接器：
1. `CausalLinker` - 原始版本，使用简单的全事件两两配对策略，复杂度为 O(N²)
2. `OptimizedCausalLinker` - 优化版本，使用两条路径策略（同章节配对+实体共现配对）并添加实体频率反向权重，将复杂度降低到 O(N·avg_m²) + O(E × k²)

为了简化代码维护，避免功能重复和代码冗余，我们将这两个实现合并为一个统一的 `UnifiedCausalLinker` 类。

## 统一实现的优势

1. **代码维护性提升**：
   - 将所有链接器逻辑集中在一个文件中
   - 避免在多个地方修改相同功能
   - 减少代码冗余，消除可能的不一致性

2. **向后兼容**：
   - 保留了原有的 `CausalLinker` 和 `OptimizedCausalLinker` 类作为兼容层
   - 这些类现在是 `UnifiedCausalLinker` 的简单包装器
   - 确保现有代码不会因重构而失效

3. **功能灵活性**：
   - 通过单一参数 `use_optimization` 控制使用哪种策略
   - 可根据需要随时切换模式
   - 默认启用优化策略获得最佳性能

## 使用方法

### 1. 使用统一版实现（推荐）

```python
from causal_linking.service.unified_linker_service import UnifiedCausalLinker

# 默认使用优化版策略
linker = UnifiedCausalLinker(
    model="gpt-4o",
    provider="openai",
    use_optimization=True,  # 控制是否使用优化策略
    use_entity_weights=True,  # 控制是否使用实体频率权重
    max_events_per_chapter=20,
    min_entity_support=2
)

# 执行因果链接
edges = linker.link_events(events)
```

### 2. 使用向后兼容层（不推荐，但仍然可用）

```python
# 原始版本
from causal_linking.service.linker_service import CausalLinker
linker = CausalLinker(model="gpt-4o", provider="openai")

# 或优化版本
from causal_linking.service.optimized_linker_service import OptimizedCausalLinker
optimized_linker = OptimizedCausalLinker(
    model="gpt-4o",
    provider="openai",
    use_entity_weights=True
)
```

### 3. 使用依赖注入提供者（推荐用于生产环境）

```python
from causal_linking.di.provider import provide_linker

# 获取链接器实例（参数控制是否使用优化版）
linker = provide_linker(use_optimized=True)  # 默认为True

# 环境变量配置优化参数
# export USE_ENTITY_WEIGHTS="true"
# export MIN_ENTITY_SUPPORT="2"
# export MAX_EVENTS_PER_CHAPTER="20"
# export MAX_CANDIDATE_PAIRS="10000"
# export MAX_CHAPTER_SPAN="10"
```

## 实体频率权重反向调整

统一版链接器继承了优化版的所有功能，包括实体频率权重反向调整，详情可参考 `因果图逻辑改造.md` 文档。

优化策略：
- 高频实体（如"韩立"）被赋予较低权重
- 权重计算公式：`weight = 1 / log(frequency + 1.1)`
- 显著减少候选事件对，提高因果链接效率
- 经测试可将候选对数量减少约88%
