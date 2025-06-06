# 基于R2的《凡人修仙传》因果事件图谱生成系统

本项目是一个自动化工具，用于从小说《凡人修仙传》文本中提取事件、宝物和人物关系，构建事件因果图谱。系统采用模块化设计，使用R2（ReAct-Reflect）框架调用大语言模型，实现了事件抽取、幻觉修复、因果链接和图谱可视化等功能。

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

### 配置API密钥

设置环境变量（选择一种API提供商）：

```bash
# 使用OpenAI API
export OPENAI_API_KEY="your-openai-api-key-here"

# 或者使用DeepSeek API
export DEEPSEEK_API_KEY="your-deepseek-api-key-here"
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

分析事件之间的因果关系，识别关系方向和强度，并构建有向无环图（DAG）。

### 图谱构建模块（graph_builder）

将事件和因果关系渲染为Mermaid格式的图谱，方便可视化。

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
- **贪心断环算法**：通过权重优先和入度排序构建有向无环图

## 许可证

MIT License
