# 系统并行处理配置报告

生成时间: 2025-06-11 00:17:07

## 基本配置

- 并行处理状态: 启用
- 全局最大线程数: 6

## 自适应线程配置

- 自适应模式: 启用
- IO密集型任务系数: 1.5
- CPU密集型任务系数: 0.8
- IO密集型任务线程数: 9
- CPU密集型任务线程数: 4

## 模块特定配置

| 模块 | 配置线程数 |
|------|----------|
| event_extraction | 6 |
| hallucination_refine | 6 |
| causal_linking | 6 |
| graph_builder | 4 |

## 实际线程使用情况

现在开始测试各模块实际使用的线程数...

### 事件抽取模块


### 幻觉修复模块


### 因果链接模块


### 图形构建模块


## 线程使用摘要

| 模块 | 配置线程数 | 实际使用线程数 | 任务类型 |
|------|------------|--------------|--------|
| event_extraction | 6 | 6 | io_bound |
| hallucination_refine | 6 | 6 | io_bound |
| causal_linking | 6 | 6 | default |
| graph_builder | 4 | 6 | cpu_bound |

## 结论和建议

⚠️ 以下模块的线程使用与配置不一致:

- graph_builder: 期望 4，实际 6

建议检查这些模块的并行实现是否正确使用了ParallelConfig。

### 优化建议

根据模块任务特性的不同，建议以下线程配置：

- IO密集型任务 (如API调用): 核心数 x 1.5
- CPU密集型任务 (如图形渲染): 核心数 x 0.8
- 混合型任务: 与核心数相当

当前系统中的分类：

- IO密集型：event_extraction, hallucination_refine
- CPU密集型：graph_builder
- 混合型：causal_linking
