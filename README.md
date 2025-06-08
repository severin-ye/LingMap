# 基于R2的《凡人修仙传》因果事件图谱生成系统

本项目是一个自动化工具，用于从小说《凡人修仙传》文本中提取事件、宝物和人物关系，构建事件因果图谱。系统采用模块化设计，使用R2（Retrieval-Refinement）框架调用大语言模型，实现了事件抽取、幻觉修复、因果链接和图谱可视化等功能。

## 快速开始

1. **安装依赖**

```bash
pip install -r requirements.txt
```

2. **创建配置文件**

将`.env.example`复制为`.env`并填入您的API密钥。

3. **运行演示**

```bash
python main.py --demo
```

4. **处理自定义文件**

```bash
python main.py --input your_novel.txt
```

5. **交互式模式**

```bash
python main.py
```

## 系统架构

系统由以下核心模块组成：

1. **文本摄入模块（text_ingestion）**：将原始小说文本转换为标准化的章节JSON数据
2. **事件抽取模块（event_extraction）**：从章节内容中提取关键事件、人物、宝物等
3. **幻觉修复模块（hallucination_refine）**：使用HAR算法检测和修复LLM输出中的幻觉
4. **因果链接模块（causal_linking）**：分析事件之间的因果关系，构建有向无环图（DAG）
5. **图谱构建模块（graph_builder）**：将事件图谱渲染为Mermaid格式
6. **API网关模块（api_gateway）**：提供统一的CLI接口

## 安装与配置

### 环境要求

- Python 3.8+
- 支持以下API提供商之一：
  - OpenAI API密钥（用于调用GPT-4o模型）
  - DeepSeek API密钥（用于调用DeepSeek中文大模型）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置API密钥和系统参数

设置环境变量（选择一种API提供商）：

```bash
# 使用OpenAI API
export OPENAI_API_KEY="your-openai-api-key-here"

# 或者使用DeepSeek API
export DEEPSEEK_API_KEY="your-deepseek-api-key-here"

# 实体频率权重优化配置 (可选)
export USE_ENTITY_WEIGHTS="true"  # 启用实体权重优化，默认为true
```

或者在`.env`文件中配置：

```
# OpenAI API密钥
openai_api_key=your-openai-api-key-here

# DeepSeek API密钥
deepseek_api_key=your-deepseek-api-key-here
```

或者在`common/config/config.json`中配置：

```json
{
  "api": {
    "openai": {
      "api_key": "your-openai-api-key-here"
    },
    "deepseek": {
      "api_key": "your-deepseek-api-key-here"
    }
  }
}
```

## 使用方法

### 命令行接口

处理单个文本文件：

```bash
# 使用OpenAI API
python api_gateway/main.py --input "novel/test.txt" --output "output" --provider openai

# 使用DeepSeek API (默认)
python api_gateway/main.py --input "novel/test.txt" --output "output" --provider deepseek

# 禁用实体频率权重优化
python api_gateway/main.py --input "novel/test.txt" --output "output" --use-entity-weights false
```

批量处理文件夹中的所有文本：

```bash
# 使用OpenAI API
python api_gateway/main.py --input "novel" --output "output" --batch --provider openai

# 使用DeepSeek API
python api_gateway/main.py --input "novel" --output "output" --batch --provider deepseek
```

### 示例运行脚本

使用预设的示例运行脚本：

```bash
# 使用DeepSeek API (默认)
python scripts/demo_run.py

# 指定使用OpenAI API
python scripts/demo_run.py --provider openai
```

### 测试API连接

测试DeepSeek API是否正常工作：

```bash
python scripts/test_deepseek.py
```

检查环境和API配置：

```bash
python scripts/check_env.py
```

## 输出结果

系统会生成以下输出：

1. 章节JSON文件（包含分割的段落）
2. 事件JSON文件（从文本中提取的事件）
3. 精修后的事件JSON文件（幻觉修复后的事件）
4. 因果关系JSON文件（包含事件节点和因果边）
5. Mermaid格式的图谱文件（可在[Mermaid Live Editor](https://mermaid.live/)中查看）

## 模块详解

### 文本摄入模块（text_ingestion）

负责从TXT文件加载小说内容，识别章节信息，并将文本按段落分割为适合LLM处理的片段。

### 事件抽取模块（event_extraction）

使用大语言模型（OpenAI GPT-4o或DeepSeek中文模型）从文本中提取关键事件、人物和宝物，形成结构化的事件数据。该模块支持多种LLM提供商API，可根据需要切换。

### 幻觉修复模块（hallucination_refine）

使用HAR（Hallucination Assessment and Refinement）算法检测和修复事件中可能的幻觉或不准确内容。

### 因果链接模块（causal_linking）

分析事件之间的因果关系，识别关系方向和强度，并构建有向无环图（DAG）。采用"两条路径，合并汇流"策略（同章节配对+实体共现配对）结合实体频率权重反向调整技术，大幅优化候选事件对的生成效率，降低时间复杂度。

### 图谱构建模块（graph_builder）

将事件和因果关系渲染为Mermaid格式的图谱，方便可视化。

## 优化策略与性能

系统在因果链接模块采用了多项优化策略，显著提升了处理效率：

### 实体频率权重反向调整

针对像"韩立"这样在几乎所有事件中出现的高频实体，通过反向权重公式降低其对候选事件对生成的贡献：

- **优化原理**：高频实体共现往往不具备强因果关系指示意义
- **权重公式**：`weight = 1 / log(frequency + 1.1)`
- **效果**：测试中可减少约88%的候选事件对，显著降低LLM API调用成本

### 复杂度优化

- **优化前**：O(N²) - 需要分析所有事件对的组合
- **优化后**：O(N·avg_m²) + O(E × k²)
  - N为章节数，m为平均每章事件数
  - E为实体数，k为每实体平均关联事件数

### 配置参数

可通过环境变量或命令行参数控制优化行为：

```bash
# 环境变量配置
export USE_ENTITY_WEIGHTS="true"  # 启用/禁用实体权重优化
export MIN_ENTITY_SUPPORT="2"     # 实体最小支持度
```

### 测试脚本

可运行测试脚本验证优化效果：

```bash
python scripts/test_entity_weights.py
```

## 测试

运行单元测试：

```bash
python -m tests.run_all_tests

# 显示详细测试输出
python -m tests.run_all_tests -v
```

## 项目结构

```
r2-fanren/
├── api_gateway/           # API网关服务
│   ├── main.py            # 统一CLI入口
│   └── router/            # 扩展REST接口（可选）
├── common/                # 共享组件
│   ├── config/            # 配置文件
│   ├── interfaces/        # 抽象接口
│   ├── models/            # 数据模型
│   └── utils/             # 工具函数
├── event_extraction/      # 事件抽取模块
├── hallucination_refine/  # 幻觉修复模块
├── causal_linking/        # 因果链接模块
├── graph_builder/         # 图谱构建模块
├── text_ingestion/        # 文本摄入模块
├── scripts/               # 辅助脚本
├── tests/                 # 测试代码
└── output/                # 输出目录
```

## 理论支持

本系统基于R2框架，结合大语言模型实现了一套完整的文本信息抽取和因果推理流程。核心算法包括：

- **LLM-based信息抽取**：使用prompt工程引导语言模型进行高质量的信息提取
- **HAR幻觉检测与修复**：采用自迭代的方式检测和修复LLM输出中的幻觉
- **CPC因果对识别**：使用因果对比和推理技术识别事件间的因果关系
- **实体频率权重反向调整**：通过公式 `weight = 1 / log(frequency + 1.1)` 为高频实体分配较低权重，优化候选事件对生成，将复杂度从 O(N²) 降低到 O(N·avg_m²) + O(E × k²)
- **贪心断环算法**：通过权重优先和入度排序构建有向无环图

## 许可证

MIT License
