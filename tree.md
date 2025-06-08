├── README.md  # 项目概览、安装、使用说明和基本介绍。
├── api_gateway  # API网关服务，统一外部请求入口
│   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   └── main.cpython-310.pyc  # API网关主应用的编译缓存 (可忽略)
│   ├── main.py  # API网关主应用入口脚本。
│   └── {router}  # 路由定义目录占位符，实际应包含具体的路由模块。
├── causal_linking  # 因果链接微服务，负责分析和建立事件间的因果关系
│   ├── app.py  # 因果链接服务的应用入口脚本。
│   ├── controller  # API控制器目录
│   │   └── linker_controller.py  # 因果链接相关的API控制器。
│   ├── di  # 依赖注入配置目录
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   └── provider.cpython-310.pyc  # 依赖注入提供者的编译缓存 (可忽略)
│   │   └── provider.py  # 配置和提供服务依赖的脚本。
│   ├── domain  # 领域模型和核心逻辑目录
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   └── base_linker.cpython-310.pyc  # 链接器抽象基类的编译缓存 (可忽略)
│   │   └── base_linker.py  # 定义链接器抽象基类或核心领域逻辑。
│   ├── repository  # 数据仓库或外部服务访问层目录 (当前为空，可用于LLM客户端等)。
│   └── service  # 业务逻辑服务层目录
│       ├── README.md  # 因果链接服务模块的说明文档。
│       ├── pycache  # Python编译缓存目录 (可忽略)
│       │   ├── linker_service.cpython-310.pyc  # 基础链接器服务的编译缓存 (可忽略)
│       │   ├── optimized_linker_service.cpython-310.pyc  # 优化链接器服务的编译缓存 (可忽略)
│       │   └── unified_linker_service.cpython-310.pyc  # 统一链接器服务的编译缓存 (可忽略)
│       ├── linker_service.py  # 基础版因果链接服务实现。
│       ├── optimized_linker_service.py  # 优化版因果链接服务实现。
│       └── unified_linker_service.py  # 统一版因果链接服务，可兼容不同链接策略。
├── common  # 项目共享通用模块目录
│   ├── config  # 配置文件目录
│   │   ├── config.json  # 项目全局或共享的JSON配置文件。
│   │   ├── prompt_causal_linking.json  # 因果链接任务的LLM提示模板。
│   │   ├── prompt_event_extraction.json  # 事件抽取任务的LLM提示模板。
│   │   └── prompt_hallucination_refine.json  # 幻觉修正任务的LLM提示模板。
│   ├── interfaces  # 抽象接口定义目录
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   ├── extractor.cpython-310.pyc  # 抽取器接口的编译缓存 (可忽略)
│   │   │   ├── graph_renderer.cpython-310.pyc  # 图谱渲染器接口的编译缓存 (可忽略)
│   │   │   ├── linker.cpython-310.pyc  # 链接器接口的编译缓存 (可忽略)
│   │   │   └── refiner.cpython-310.pyc  # 精炼器接口的编译缓存 (可忽略)
│   │   ├── extractor.py  # 定义事件抽取器的抽象接口。
│   │   ├── graph_renderer.py  # 定义图谱渲染器的抽象接口。
│   │   ├── linker.py  # 定义因果链接器的抽象接口。
│   │   └── refiner.py  # 定义事件精炼器的抽象接口。
│   ├── models  # 数据模型定义目录
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   ├── causal_edge.cpython-310.pyc  # 因果边模型的编译缓存 (可忽略)
│   │   │   ├── chapter.cpython-310.pyc  # 章节模型的编译缓存 (可忽略)
│   │   │   ├── event.cpython-310.pyc  # 事件模型的编译缓存 (可忽略)
│   │   │   └── treasure.cpython-310.pyc  # 宝物模型的编译缓存 (可忽略)
│   │   ├── causal_edge.py  # 定义因果关系边的数据模型。
│   │   ├── chapter.py  # 定义小说章节的数据模型。
│   │   ├── event.py  # 定义事件的数据模型。
│   │   └── treasure.py  # 定义宝物的数据模型。
│   └── utils  # 通用工具函数模块目录
│       ├── pycache  # Python编译缓存目录 (可忽略)
│       │   ├── enhanced_logger.cpython-310.pyc  # 增强日志工具的编译缓存 (可忽略)
│       │   ├── json_loader.cpython-310.pyc  # JSON加载工具的编译缓存 (可忽略)
│       │   ├── path_utils.cpython-310.pyc  # 路径处理工具的编译缓存 (可忽略)
│       │   └── text_splitter.cpython-310.pyc  # 文本分割工具的编译缓存 (可忽略)
│       ├── enhanced_logger.py  # 提供增强的日志记录功能。
│       ├── json_loader.py  # 用于加载和处理JSON文件的工具。
│       ├── path_utils.py  # 提供路径操作相关的工具函数。
│       └── text_splitter.py  # 用于将文本分割成块或句子的工具。
├── debug  # 调试文件输出目录
│   ├── api_response.json  # 存储API调用的响应示例，用于调试。
│   ├── event_extraction  # 事件抽取相关的调试文件子目录 (当前为空)。
│   ├── extracted_events.json  # 存储抽取出的事件数据示例，用于调试。
│   └── extracted_events_test.json  # 存储用于测试的抽取事件数据。
├── event_extraction  # 事件抽取微服务，负责从文本中识别和提取事件信息
│   ├── app.py  # 事件抽取服务的应用入口脚本。
│   ├── controller  # API控制器目录
│   │   └── extractor_controller.py  # 事件抽取相关的API控制器。
│   ├── di  # 依赖注入配置目录
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   └── provider.cpython-310.pyc  # 依赖注入提供者的编译缓存 (可忽略)
│   │   └── provider.py  # 配置和提供服务依赖的脚本。
│   ├── domain  # 领域模型和核心逻辑目录
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   └── base_extractor.cpython-310.pyc  # 抽取器抽象基类的编译缓存 (可忽略)
│   │   └── base_extractor.py  # 定义抽取器抽象基类或核心领域逻辑。
│   ├── repository  # 数据仓库或外部服务访问层目录
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   └── llm_client.cpython-310.pyc  # LLM客户端的编译缓存 (可忽略)
│   │   └── llm_client.py  # 与大语言模型(LLM)交互的客户端。
│   └── service  # 业务逻辑服务层目录
│       ├── pycache  # Python编译缓存目录 (可忽略)
│       │   ├── enhanced_extractor_service.cpython-310.pyc  # 增强版抽取器服务的编译缓存 (可忽略)
│       │   └── extractor_service.cpython-310.pyc  # 基础抽取器服务的编译缓存 (可忽略)
│       ├── enhanced_extractor_service.py  # 增强版事件抽取服务实现。
│       └── extractor_service.py  # 基础版事件抽取服务实现。
├── graph_builder  # 图谱构建微服务，负责将抽取的事件和关系转换为可视化图谱格式
│   ├── app.py  # 图谱构建服务的应用入口脚本。
│   ├── controller  # API控制器目录
│   │   └── graph_controller.py  # 图谱构建相关的API控制器。
│   ├── domain  # 领域模型和核心逻辑目录
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   └── base_renderer.cpython-310.pyc  # 渲染器抽象基类的编译缓存 (可忽略)
│   │   └── base_renderer.py  # 定义图谱渲染器的抽象基类。
│   ├── service  # 业务逻辑服务层目录
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   └── mermaid_renderer.cpython-310.pyc  # Mermaid渲染器服务的编译缓存 (可忽略)
│   │   └── mermaid_renderer.py  # 将图谱数据渲染为Mermaid格式的脚本。
│   └── utils  # 服务特定的工具函数目录
│       ├── pycache  # Python编译缓存目录 (可忽略)
│       │   └── color_map.cpython-310.pyc  # 颜色映射工具的编译缓存 (可忽略)
│       └── color_map.py  # 为图谱节点或边提供颜色映射的工具。
├── hallucination_refine  # 幻觉修正微服务，负责使用HAR等技术精炼LLM的输出结果
│   ├── app.py  # 幻觉修正服务的应用入口脚本。
│   ├── controller  # API控制器目录
│   │   └── har_controller.py  # 幻觉修正相关的API控制器。
│   ├── di  # 依赖注入配置目录
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   └── provider.cpython-310.pyc  # 依赖注入提供者的编译缓存 (可忽略)
│   │   └── provider.py  # 配置和提供服务依赖的脚本。
│   ├── domain  # 领域模型和核心逻辑目录
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   └── base_refiner.cpython-310.pyc  # 精炼器抽象基类的编译缓存 (可忽略)
│   │   └── base_refiner.py  # 定义精炼器抽象基类或核心领域逻辑。
│   ├── repository  # 数据仓库或外部服务访问层目录 (当前为空)。
│   └── service  # 业务逻辑服务层目录
│       ├── pycache  # Python编译缓存目录 (可忽略)
│       │   └── har_service.cpython-310.pyc  # HAR服务的编译缓存 (可忽略)
│       └── har_service.py  # 基于HAR（Hallucination Auto-Refinement）的事件精炼服务。
├── logs  # 日志文件存储目录
│   ├── api_integration_test_20250608.log  # API集成测试日志 (2025-06-08)。
│   ├── api_test_20250607.log  # API测试日志 (2025-06-07)。
│   ├── causal_linking_test_20250608.log  # 因果链接测试日志 (2025-06-08)。
│   ├── causal_prompt_test_20250608.log  # 因果链接提示词测试日志 (2025-06-08)。
│   ├── complete_test_20250607.log  # 完整流程测试日志 (2025-06-07)。
│   ├── complete_test_20250608.log  # 完整流程测试日志 (2025-06-08)。
│   ├── deepseek_causal_test_20250608.log  # 使用DeepSeek模型进行因果链接测试的日志 (2025-06-08)。
│   ├── event_extraction_test_20250608.log  # 事件抽取测试日志 (2025-06-08)。
│   ├── event_extractor_20250607.log  # 事件抽取器日志 (2025-06-07)。
│   ├── event_extractor_20250608.log  # 事件抽取器日志 (2025-06-08)。
│   ├── fanren_system_20250607.log  # 《凡人修仙传》系统整体运行日志 (2025-06-07)。
│   ├── fanren_system_20250608.log  # 《凡人修仙传》系统整体运行日志 (2025-06-08)。
│   ├── optimized_causal_linking_test_20250608.log  # 优化版因果链接测试日志 (2025-06-08)。
│   ├── system_config_test_20250608.log  # 系统配置测试日志 (2025-06-08)。
│   └── system_test_20250608.log  # 系统级测试日志 (2025-06-08)。
├── main.py  # 项目主入口脚本，用于串联执行核心流程或启动整个应用。
├── novel  # 存放小说原始文本文件的目录
│   ├── 1.txt  # 小说分卷或章节的文本文件1。
│   ├── 2.txt  # 小说分卷或章节的文本文件2。
│   └── test.txt  # 用于测试的小说文本文件。
├── output  # 存放脚本运行输出结果的目录 (例如生成的图谱文件)。
├── requirements.txt  # 列出项目运行所需的Python依赖包及其版本。
├── scripts  # 存放辅助脚本的目录 (如测试、部署、数据处理等)
│   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   ├── check_env.cpython-310.pyc  # 环境检查脚本的编译缓存 (可忽略)
│   │   └── performance_benchmark.cpython-310.pyc  # 性能基准测试脚本的编译缓存 (可忽略)
│   ├── check_env.py  # 检查运行环境配置是否正确的脚本。
│   ├── complete_test.py  # 执行完整端到端流程的测试脚本。
│   ├── debug_optimized_linker.py  # 用于调试优化版链接器的脚本。
│   ├── demo_run.py  # (可能与run_demo.py重复或为其一部分) 运行演示的脚本。
│   ├── run_all_tests.py  # 运行所有测试用例的脚本 (可能与tests/run_all_tests.py功能相似)。
│   ├── run_demo.py  # 运行项目演示流程的脚本。
│   ├── test_api_integration.py  # API集成测试脚本。
│   ├── test_causal_module.py  # 因果关系模块的测试脚本。
│   ├── test_entity_weights.py  # 测试实体频率权重调整功能的脚本。
│   ├── test_event_extraction.py  # 事件抽取模块的测试脚本。
│   ├── test_linker.py  # 综合测试不同链接器实现的脚本 (标准、优化、统一版)。
│   ├── test_optimized_linker.py  # 优化版链接器专项测试脚本。
│   ├── test_system_config.py  # 系统配置加载和有效性测试脚本。
│   └── test_unified_linker.py  # 统一版链接器兼容性和功能测试脚本。
├── temp  # 临时文件存储目录 (当前为空)。
├── tests  # 测试代码和相关资源的主目录
│   ├── README.md  # 测试模块的说明文档，介绍测试结构和运行方法。
│   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   ├── run_all_tests.cpython-310.pyc  # 运行所有测试脚本的编译缓存 (可忽略)
│   │   ├── test_stage1_interfaces.cpython-310.pyc  # (旧) 阶段1接口测试的编译缓存 (可忽略)
│   │   ├── test_stage1_interfaces_fixed.cpython-310.pyc  # (旧) 修复后阶段1接口测试的编译缓存 (可忽略)
│   │   ├── test_stage1_models.cpython-310.pyc  # (旧) 阶段1模型测试的编译缓存 (可忽略)
│   │   ├── test_stage1_models_fixed.cpython-310.pyc  # (旧) 修复后阶段1模型测试的编译缓存 (可忽略)
│   │   └── test_text_ingestion.cpython-310-pytest-8.3.4.pyc  # 文本摄入pytest测试的编译缓存 (可忽略)
│   ├── run_all_tests.py  # 运行所有测试阶段中测试用例的脚本。
│   ├── stage_1  # 第一阶段测试：基础组件 (模型、接口等)
│   │   ├── init.py  # Python包初始化文件，使stage_1可作为包导入。
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   ├── init.cpython-310.pyc  # 包初始化文件的编译缓存 (可忽略)
│   │   │   ├── run_tests.cpython-310.pyc  # 阶段1测试运行脚本的编译缓存 (可忽略)
│   │   │   ├── test_interfaces.cpython-310.pyc  # 接口测试脚本的编译缓存 (可忽略)
│   │   │   └── test_models.cpython-310.pyc  # 模型测试脚本的编译缓存 (可忽略)
│   │   ├── run_tests.py  # 运行第一阶段所有测试的脚本。
│   │   ├── test_interfaces.py  # 测试common/interfaces中定义的接口。
│   │   └── test_models.py  # 测试common/models中定义的数据模型。
│   ├── stage_2  # 第二阶段测试：单个微服务功能
│   │   ├── init.py  # Python包初始化文件，使stage_2可作为包导入。
│   │   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   │   ├── init.cpython-310.pyc  # 包初始化文件的编译缓存 (可忽略)
│   │   │   ├── run_tests.cpython-310.pyc  # 阶段2测试运行脚本的编译缓存 (可忽略)
│   │   │   ├── test_event_extraction.cpython-310.pyc  # 事件抽取服务测试的编译缓存 (可忽略)
│   │   │   └── test_text_ingestion.cpython-310.pyc  # 文本摄入服务测试的编译缓存 (可忽略)
│   │   ├── run_tests.py  # 运行第二阶段所有测试的脚本。
│   │   ├── test_event_extraction.py  # 测试事件抽取服务的功能。
│   │   └── test_text_ingestion.py  # 测试文本摄入服务的功能。
│   └── stage_3  # 第三阶段测试：多服务集成和复杂流程
│       ├── STAGE3_COMPREHENSIVE_TEST_REPORT.md  # 第三阶段综合测试报告。
│       ├── init.py  # Python包初始化文件，使stage_3可作为包导入。
│       ├── pycache  # Python编译缓存目录 (可忽略)
│       │   ├── init.cpython-310.pyc  # 包初始化文件的编译缓存 (可忽略)
│       │   ├── run_tests.cpython-310.pyc  # 阶段3测试运行脚本的编译缓存 (可忽略)
│       │   ├── test_causal_linking.cpython-310-pytest-8.4.0.pyc  # 因果链接pytest测试的编译缓存 (可忽略)
│       │   ├── test_causal_linking.cpython-310.pyc  # 因果链接服务测试的编译缓存 (可忽略)
│       │   ├── test_hallucination_refine.cpython-310-pytest-8.4.0.pyc  # 幻觉修正pytest测试的编译缓存 (可忽略)
│       │   └── test_hallucination_refine.cpython-310.pyc  # 幻觉修正服务测试的编译缓存 (可忽略)
│       ├── run_tests.py  # 运行第三阶段所有测试的脚本。
│       ├── test_causal_linking.py  # 测试因果链接服务的功能。
│       └── test_hallucination_refine.py  # 测试幻觉修正服务的功能。
├── text_ingestion  # 文本摄入微服务，负责加载原始文本并转换为标准格式
│   ├── pycache  # Python编译缓存目录 (可忽略)
│   │   └── chapter_loader.cpython-310.pyc  # 章节加载器脚本的编译缓存 (可忽略)
│   ├── app.py  # 文本摄入服务的应用入口脚本。
│   └── chapter_loader.py  # 从文本文件加载并处理章节内容的脚本。
├── 代码结构设计.md  # 项目代码结构和模块设计的详细文档。
├── 修复计划.md  # 项目问题修复和改进计划文档。
├── 因果图逻辑改造.md  # 因果图谱构建逻辑的改造方案文档。
├── 开发方案.md  # 项目整体或特定功能的开发方案文档。
├── 理论支持.md  # 项目相关理论基础和研究支撑文档。
└── 项目逻辑设计.md  # 项目核心业务逻辑和流程设计文档。