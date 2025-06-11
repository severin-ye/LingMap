# 系统并行处理配置报告

生成时间: 2025-06-11 21:57:55

## 基本配置

- 并行处理状态: 启用
- 全局最大线程数: 10

## 自适应线程配置

- 自适应模式: 启用
- IO密集型任务系数: 1.5
- CPU密集型任务系数: 0.8
- IO密集型任务线程数: 15
- CPU密集型任务线程数: 8

## 模块特定配置

| 模块 | 配置线程数 |
|------|----------|
| event_extraction | 10 |
| event_extraction_description | 事件抽取：IO密集型任务，API调用多，适合较多线程 |
| hallucination_refine | 10 |
| hallucination_refine_description | 幻觉修复：IO密集型任务，API调用多，适合较多线程 |
| causal_linking | 10 |
| causal_linking_description | 因果链接：混合型任务，既有计算也有API调用，使用标准线程数 |
| graph_builder | 10 |
| graph_builder_description | 图形构建：CPU密集型任务，主要是计算和渲染，适合较少线程以减少竞争 |

## 实际线程使用情况

现在开始测试各模块实际使用的线程数...

### 事件抽取模块

✅ 事件抽取模块初始化成功


### 幻觉修复模块

✅ 幻觉修复模块初始化成功


### 因果链接模块

✅ 因果链接模块初始化成功


### 图形构建模块

✅ 图形构建模块初始化成功


## 线程使用摘要

| 模块 | 配置线程数 | 实际使用线程数 | 任务类型 |
|------|------------|--------------|--------|
| event_extraction | 10 | 10 | io_bound |
| event_extraction_description | 事件抽取：IO密集型任务，API调用多，适合较多线程 | 未知 | 未知 |
| hallucination_refine | 10 | 10 | io_bound |
| hallucination_refine_description | 幻觉修复：IO密集型任务，API调用多，适合较多线程 | 未知 | 未知 |
| causal_linking | 10 | 10 | default |
| causal_linking_description | 因果链接：混合型任务，既有计算也有API调用，使用标准线程数 | 未知 | 未知 |
| graph_builder | 10 | 10 | cpu_bound |
| graph_builder_description | 图形构建：CPU密集型任务，主要是计算和渲染，适合较少线程以减少竞争 | 未知 | 未知 |

## 结论和建议

### 优化建议

根据模块任务特性的不同，建议以下线程配置：

- IO密集型任务 (如API调用): 核心数 x 1.5
- CPU密集型任务 (如图形渲染): 核心数 x 0.8
- 混合型任务: 与核心数相当

当前系统中的分类：

- IO密集型：event_extraction, hallucination_refine
- CPU密集型：graph_builder
- 混合型：causal_linking
