├── FINAL_SYSTEM_REPORT.md  # 系统最终报告文档，总结系统的功能、性能和改进。
├── PROJECT_COMPLETION_SUMMARY.md  # 项目完成总结，记录项目完成情况、成果和亮点。
├── README.md  # 项目概览、安装、使用说明和基本介绍。
├── __pycache__  # Python编译缓存目录 (可忽略)
│   └── main.cpython-310.pyc  # 主应用入口文件的编译缓存 (可忽略)
├── api_gateway  # API网关服务，统一外部请求入口
│   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   └── main.cpython-310.pyc  # API网关主应用的编译缓存 (可忽略)
│   └── main.py  # API网关主应用入口脚本。
├── causal_linking  # 因果链接微服务，负责分析和建立事件间的因果关系
│   ├── app.py  # 因果链接服务的应用入口脚本。
│   ├── controller  # API控制器目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── linker_controller.cpython-310.pyc  # 链接器控制器的编译缓存 (可忽略)
│   │   └── linker_controller.py  # 因果链接相关的API控制器。
│   ├── di  # 依赖注入配置目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── provider.cpython-310.pyc  # 依赖注入提供者的编译缓存 (可忽略)
│   │   └── provider.py  # 配置和提供服务依赖的脚本。
│   ├── domain  # 领域模型和核心逻辑目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── base_linker.cpython-310.pyc  # 链接器抽象基类的编译缓存 (可忽略)
│   │   └── base_linker.py  # 定义链接器抽象基类或核心领域逻辑。
│   ├── repository  # 数据仓库或外部服务访问层目录 (当前为空，可用于LLM客户端等)。
│   └── service  # 业务逻辑服务层目录
│       ├── README.md  # 因果链接服务模块的说明文档。
│       ├── __pycache__  # Python编译缓存目录 (可忽略)
│       │   ├── base_causal_linker.cpython-310.pyc  # 基础因果链接器的编译缓存 (可忽略)
│       │   ├── candidate_generator.cpython-310.pyc  # 候选生成器的编译缓存 (可忽略)
│       │   ├── graph_filter.cpython-310.pyc  # 图过滤器的编译缓存 (可忽略)
│       │   ├── linker_service.cpython-310.pyc  # 链接器服务的编译缓存 (可忽略)
│       │   ├── optimized_linker_service.cpython-310.pyc  # 优化链接器服务的编译缓存 (可忽略)
│       │   ├── pair_analyzer.cpython-310.pyc  # 对分析器的编译缓存 (可忽略)
│       │   └── unified_linker_service.cpython-310.pyc  # 统一链接器服务的编译缓存 (可忽略)
│       ├── base_causal_linker.py  # 基础因果链接器的实现，定义链接抽象与基本功能。
│       ├── candidate_generator.py  # 候选事件对生成器，用于优化因果分析的配对过程。
│       ├── graph_filter.py  # 图过滤器，用于过滤和优化生成的因果关系图。
│       ├── pair_analyzer.py  # 事件对分析器，分析事件对之间的因果关系。
│       ├── unified_linker_service.py  # 统一版因果链接服务，可兼容不同链接策略。
│       └── unified_linker_service.py.bak  # 统一链接器服务的备份文件。
├── common  # 项目共享通用模块目录
│   ├── config  # 配置文件目录
│   │   ├── config.json  # 项目全局或共享的JSON配置文件。
│   │   ├── parallel_config.json  # 并行处理配置文件，控制各模块线程使用。
│   │   ├── prompt_causal_linking.json  # 因果链接任务的LLM提示模板。
│   │   ├── prompt_event_extraction.json  # 事件抽取任务的LLM提示模板。
│   │   └── prompt_hallucination_refine.json  # 幻觉修正任务的LLM提示模板。
│   ├── interfaces  # 抽象接口定义目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   ├── extractor.cpython-310.pyc  # 抽取器接口的编译缓存 (可忽略)
│   │   │   ├── graph_renderer.cpython-310.pyc  # 图谱渲染器接口的编译缓存 (可忽略)
│   │   │   ├── linker.cpython-310.pyc  # 链接器接口的编译缓存 (可忽略)
│   │   │   └── refiner.cpython-310.pyc  # 精炼器接口的编译缓存 (可忽略)
│   │   ├── extractor.py  # 定义事件抽取器的抽象接口。
│   │   ├── graph_renderer.py  # 定义图谱渲染器的抽象接口。
│   │   ├── linker.py  # 定义因果链接器的抽象接口。
│   │   └── refiner.py  # 定义事件精炼器的抽象接口。
│   ├── models  # 数据模型定义目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   ├── causal_edge.cpython-310.pyc  # 因果边模型的编译缓存 (可忽略)
│   │   │   ├── chapter.cpython-310.pyc  # 章节模型的编译缓存 (可忽略)
│   │   │   ├── event.cpython-310.pyc  # 事件模型的编译缓存 (可忽略)
│   │   │   └── treasure.cpython-310.pyc  # 宝物模型的编译缓存 (可忽略)
│   │   ├── causal_edge.py  # 定义因果关系边的数据模型。
│   │   ├── chapter.py  # 定义小说章节的数据模型。
│   │   ├── event.py  # 定义事件的数据模型。
│   │   └── treasure.py  # 定义宝物的数据模型。
│   └── utils  # 通用工具函数模块目录
│       ├── __pycache__  # Python编译缓存目录 (可忽略)
│       │   ├── config_writer.cpython-310.pyc  # 配置写入工具的编译缓存 (可忽略)
│       │   ├── enhanced_logger.cpython-310.pyc  # 增强日志工具的编译缓存 (可忽略)
│       │   ├── id_processor.cpython-310.pyc  # ID处理工具的编译缓存 (可忽略)
│       │   ├── json_loader.cpython-310.pyc  # JSON加载工具的编译缓存 (可忽略)
│       │   ├── parallel_config.cpython-310.pyc  # 并行配置工具的编译缓存 (可忽略)
│       │   ├── path_utils.cpython-310.pyc  # 路径处理工具的编译缓存 (可忽略)
│       │   ├── text_splitter.cpython-310.pyc  # 文本分割工具的编译缓存 (可忽略)
│       │   └── thread_monitor.cpython-310.pyc  # 线程监控工具的编译缓存 (可忽略)
│       ├── config_writer.py  # 配置文件写入和更新工具。
│       ├── enhanced_logger.py  # 提供增强的日志记录功能。
│       ├── id_processor.py  # 用于处理和维护ID的工具。
│       ├── json_loader.py  # 用于加载和处理JSON文件的工具。
│       ├── parallel_config.py  # 并行处理配置管理工具，提供统一线程管理。
│       ├── path_utils.py  # 提供路径操作相关的工具函数。
│       ├── text_splitter.py  # 用于将文本分割成块或句子的工具。
│       └── thread_monitor.py  # 线程使用情况监控工具，记录各模块线程使用。
├── debug  # 调试文件输出目录
│   ├── api_response.json  # 存储API调用的响应示例，用于调试。
│   ├── event_extraction  # 事件抽取相关的调试文件子目录。
│   ├── extracted_events.json  # 存储抽取出的事件数据示例，用于调试。
│   └── extracted_events_test.json  # 存储用于测试的抽取事件数据。
├── event_extraction  # 事件抽取微服务，负责从文本中识别和提取事件信息
│   ├── app.py  # 事件抽取服务的应用入口脚本。
│   ├── controller  # API控制器目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── extractor_controller.cpython-310.pyc  # 抽取器控制器的编译缓存 (可忽略)
│   │   └── extractor_controller.py  # 事件抽取相关的API控制器。
│   ├── di  # 依赖注入配置目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── provider.cpython-310.pyc  # 依赖注入提供者的编译缓存 (可忽略)
│   │   └── provider.py  # 配置和提供服务依赖的脚本。
│   ├── domain  # 领域模型和核心逻辑目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── base_extractor.cpython-310.pyc  # 抽取器抽象基类的编译缓存 (可忽略)
│   │   └── base_extractor.py  # 定义抽取器抽象基类或核心领域逻辑。
│   ├── repository  # 数据仓库或外部服务访问层目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── llm_client.cpython-310.pyc  # LLM客户端的编译缓存 (可忽略)
│   │   └── llm_client.py  # 与大语言模型(LLM)交互的客户端。
│   └── service  # 业务逻辑服务层目录
│       ├── __pycache__  # Python编译缓存目录 (可忽略)
│       │   ├── enhanced_extractor_service.cpython-310.pyc  # 增强版抽取器服务的编译缓存 (可忽略)
│       │   └── extractor_service.cpython-310.pyc  # 基础抽取器服务的编译缓存 (可忽略)
│       ├── enhanced_extractor_service.py  # 增强版事件抽取服务实现。
│       └── extractor_service.py  # 基础版事件抽取服务实现。
├── graph_builder  # 图谱构建微服务，负责将抽取的事件和关系转换为可视化图谱格式
│   ├── app.py  # 图谱构建服务的应用入口脚本。
│   ├── controller  # API控制器目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── graph_controller.cpython-310.pyc  # 图谱控制器的编译缓存 (可忽略)
│   │   └── graph_controller.py  # 图谱构建相关的API控制器。
│   ├── domain  # 领域模型和核心逻辑目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── base_renderer.cpython-310.pyc  # 渲染器抽象基类的编译缓存 (可忽略)
│   │   └── base_renderer.py  # 定义图谱渲染器的抽象基类。
│   ├── service  # 业务逻辑服务层目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── mermaid_renderer.cpython-310.pyc  # Mermaid渲染器服务的编译缓存 (可忽略)
│   │   └── mermaid_renderer.py  # 将图谱数据渲染为Mermaid格式的脚本。
│   └── utils  # 服务特定的工具函数目录
│       ├── __pycache__  # Python编译缓存目录 (可忽略)
│       │   ├── color_map.cpython-310.pyc  # 颜色映射工具的编译缓存 (可忽略)
│       │   └── node_id_processor.cpython-310.pyc  # 节点ID处理工具的编译缓存 (可忽略)
│       ├── color_map.py  # 为图谱节点或边提供颜色映射的工具。
│       └── node_id_processor.py  # 节点ID处理工具，确保图谱中节点ID的唯一性。
├── hallucination_refine  # 幻觉修正微服务，负责使用HAR等技术精炼LLM的输出结果
│   ├── app.py  # 幻觉修正服务的应用入口脚本。
│   ├── controller  # API控制器目录
│   │   └── har_controller.py  # 幻觉修正相关的API控制器。
│   ├── di  # 依赖注入配置目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── provider.cpython-310.pyc  # 依赖注入提供者的编译缓存 (可忽略)
│   │   └── provider.py  # 配置和提供服务依赖的脚本。
│   ├── domain  # 领域模型和核心逻辑目录
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   └── base_refiner.cpython-310.pyc  # 精炼器抽象基类的编译缓存 (可忽略)
│   │   └── base_refiner.py  # 定义精炼器抽象基类或核心领域逻辑。
│   ├── repository  # 数据仓库或外部服务访问层目录 (当前为空)。
│   └── service  # 业务逻辑服务层目录
│       ├── __pycache__  # Python编译缓存目录 (可忽略)
│       │   └── har_service.cpython-310.pyc  # HAR服务的编译缓存 (可忽略)
│       └── har_service.py  # 基于HAR（Hallucination Auto-Refinement）的事件精炼服务。
├── log_doc  # 项目文档和日志目录
│   ├── 修复计划.md  # 项目问题修复和改进计划文档。
│   ├── 因果图逻辑改造.md  # 因果图谱构建逻辑的改造方案文档。
│   ├── 并行处理优化总结报告.md  # 并行处理优化的总结报告。
│   ├── 并行处理优化报告.md  # 并行处理优化的详细报告文档。
│   ├── 测试修复完成报告.md  # 测试修复完成情况报告文档。
│   └── 脚本整合优化报告.md  # 脚本整合和优化报告文档。
├── logs  # 日志文件存储目录
├── main.py  # 项目主入口脚本，用于串联执行核心流程或启动整个应用。
├── novel  # 存放小说原始文本文件的目录
│   ├── 1.txt  # 小说分卷或章节的文本文件1。
│   ├── 2.txt  # 小说分卷或章节的文本文件2。
│   └── test.txt  # 用于测试的小说文本文件。
├── output  # 存放脚本运行输出结果的目录 (例如生成的图谱文件)。
├── pytest.ini  # pytest测试框架的配置文件。
├── reports  # 报告输出目录
│   ├── parallel_config_report_20250611_001707.md  # 2025年06月11日00:17生成的并行配置报告。
│   ├── parallel_config_report_20250611_001915.md  # 2025年06月11日00:19生成的并行配置报告。
│   └── parallel_config_report_20250611_002013.md  # 2025年06月11日00:20生成的并行配置报告。
├── requirements.txt  # 列出项目运行所需的Python依赖包及其版本。
├── scripts  # 存放辅助脚本的目录 (如测试、部署、数据处理等)
│   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   ├── check_env.cpython-310.pyc  # 环境检查脚本的编译缓存 (可忽略)
│   │   ├── complete_test.cpython-310-pytest-8.4.0.pyc  # 完整测试脚本的pytest缓存 (可忽略)
│   │   ├── demo_run.cpython-310.pyc  # 演示运行脚本的编译缓存 (可忽略)
│   │   ├── fix_duplicate_event_ids.cpython-310.pyc  # 修复重复事件ID脚本的编译缓存 (可忽略)
│   │   ├── performance_benchmark.cpython-310.pyc  # 性能基准测试脚本的编译缓存 (可忽略)
│   │   ├── test_api_integration.cpython-310-pytest-8.4.0.pyc  # API集成测试的pytest缓存 (可忽略)
│   │   ├── test_event_extraction.cpython-310-pytest-8.4.0.pyc  # 事件抽取测试的pytest缓存 (可忽略)
│   │   ├── test_linker.cpython-310-pytest-8.4.0.pyc  # 链接器测试的pytest缓存 (可忽略)
│   │   └── test_linker.cpython-310.pyc  # 链接器测试脚本的编译缓存 (可忽略)
│   ├── check_env.py  # 环境检查脚本：验证依赖、API密钥、项目结构和系统配置。
│   ├── complete_test.py  # 完整流程测试：端到端测试整个系统工作流程。
│   ├── generate_parallel_report.py  # 生成并行配置报告的脚本。
│   ├── parallel_benchmark.py  # 并行处理性能基准测试脚本。
│   ├── run_demo.py  # 演示脚本：一键演示系统全部功能。
│   ├── test_api_integration.py  # API集成测试：测试API连接和响应功能。
│   ├── test_event_extraction.py  # 事件抽取测试：测试事件抽取服务的功能。
│   ├── test_linker.py  # 链接器测试：测试因果链接功能。
│   └── test_parallel_config.py  # 并行配置测试：测试并行处理配置机制。
├── temp  # 临时文件存储目录。
├── tests  # 测试代码和相关资源的主目录
│   ├── PROJECT_COMPLETION_SUMMARY.md  # 项目完成总结文档。
│   ├── README.md  # 测试模块的说明文档。
│   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   ├── run_all_tests.cpython-310.pyc  # 运行所有测试脚本的编译缓存 (可忽略)
│   │   ├── test_stage1_interfaces.cpython-310.pyc  # 阶段1接口测试的编译缓存 (可忽略)
│   │   ├── test_stage1_interfaces_fixed.cpython-310.pyc  # 修复后阶段1接口测试的编译缓存 (可忽略)
│   │   ├── test_stage1_models.cpython-310.pyc  # 阶段1模型测试的编译缓存 (可忽略)
│   │   ├── test_stage1_models_fixed.cpython-310.pyc  # 修复后阶段1模型测试的编译缓存 (可忽略)
│   │   └── test_text_ingestion.cpython-310-pytest-8.3.4.pyc  # 文本摄入pytest测试的编译缓存 (可忽略)
│   ├── run_all_tests.py  # 运行所有测试阶段中测试用例的脚本。
│   ├── stage_1  # 第一阶段测试：基础组件 (模型、接口等)
│   │   ├── Stage_1_Test_Report.md  # 第一阶段测试报告。
│   │   ├── __init__.py  # Python包初始化文件。
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   ├── __init__.cpython-310.pyc  # 包初始化文件的编译缓存 (可忽略)
│   │   │   ├── run_tests.cpython-310.pyc  # 运行测试脚本的编译缓存 (可忽略)
│   │   │   ├── test_interfaces.cpython-310-pytest-8.4.0.pyc  # 接口测试的pytest缓存 (可忽略)
│   │   │   ├── test_interfaces.cpython-310.pyc  # 接口测试脚本的编译缓存 (可忽略)
│   │   │   ├── test_models.cpython-310-pytest-8.4.0.pyc  # 模型测试的pytest缓存 (可忽略)
│   │   │   └── test_models.cpython-310.pyc  # 模型测试脚本的编译缓存 (可忽略)
│   │   ├── run_tests.py  # 运行第一阶段所有测试的脚本。
│   │   ├── test_interfaces.py  # 测试common/interfaces中定义的接口。
│   │   └── test_models.py  # 测试common/models中定义的数据模型。
│   ├── stage_2  # 第二阶段测试：单个微服务功能
│   │   ├── Stage_2_Test_Report.md  # 第二阶段测试报告。
│   │   ├── __init__.py  # Python包初始化文件。
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   ├── __init__.cpython-310.pyc  # 包初始化文件的编译缓存 (可忽略)
│   │   │   ├── run_tests.cpython-310.pyc  # 运行测试脚本的编译缓存 (可忽略)
│   │   │   ├── test_event_extraction.cpython-310-pytest-8.4.0.pyc  # 事件抽取测试的pytest缓存 (可忽略)
│   │   │   ├── test_event_extraction.cpython-310.pyc  # 事件抽取测试脚本的编译缓存 (可忽略)
│   │   │   ├── test_text_ingestion.cpython-310-pytest-8.4.0.pyc  # 文本摄入测试的pytest缓存 (可忽略)
│   │   │   └── test_text_ingestion.cpython-310.pyc  # 文本摄入测试脚本的编译缓存 (可忽略)
│   │   ├── run_tests.py  # 运行第二阶段所有测试的脚本。
│   │   ├── test_event_extraction.py  # 测试事件抽取服务的功能。
│   │   └── test_text_ingestion.py  # 测试文本摄入服务的功能。
│   ├── stage_3  # 第三阶段测试：多服务集成和复杂流程
│   │   ├── STAGE3_COMPREHENSIVE_TEST_REPORT.md  # 第三阶段综合测试报告。
│   │   ├── Stage_3_Test_Report.md  # 第三阶段测试报告。
│   │   ├── __init__.py  # Python包初始化文件。
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   ├── __init__.cpython-310.pyc  # 包初始化文件的编译缓存 (可忽略)
│   │   │   ├── run_tests.cpython-310.pyc  # 运行测试脚本的编译缓存 (可忽略)
│   │   │   ├── test_causal_linking.cpython-310-pytest-8.4.0.pyc  # 因果链接pytest测试的编译缓存 (可忽略)
│   │   │   ├── test_causal_linking.cpython-310.pyc  # 因果链接测试脚本的编译缓存 (可忽略)
│   │   │   ├── test_hallucination_refine.cpython-310-pytest-8.4.0.pyc  # 幻觉修正pytest测试的编译缓存 (可忽略)
│   │   │   └── test_hallucination_refine.cpython-310.pyc  # 幻觉修正测试脚本的编译缓存 (可忽略)
│   │   ├── run_tests.py  # 运行第三阶段所有测试的脚本。
│   │   └── test_hallucination_refine.py  # 测试幻觉修正服务的功能。
│   ├── stage_4  # 第四阶段测试：因果模块与集成优化
│   │   ├── Stage_4_Test_Report.md  # 第四阶段测试报告。
│   │   ├── __init__.py  # Python包初始化文件。
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   ├── __init__.cpython-310.pyc  # 包初始化文件的编译缓存 (可忽略)
│   │   │   ├── run_tests.cpython-310.pyc  # 运行测试脚本的编译缓存 (可忽略)
│   │   │   ├── test_causal_linking.cpython-310-pytest-8.4.0.pyc  # 因果链接pytest测试的编译缓存 (可忽略)
│   │   │   ├── test_cpc_module.cpython-310-pytest-8.4.0.pyc  # CPC模块pytest测试的编译缓存 (可忽略)
│   │   │   ├── test_unified_cpc.cpython-310-pytest-8.4.0.pyc  # 统一CPC模块pytest测试的编译缓存 (可忽略)
│   │   │   └── test_unified_cpc.cpython-310.pyc  # 统一CPC测试脚本的编译缓存 (可忽略)
│   │   ├── run_tests.py  # 运行第四阶段所有测试的脚本。
│   │   ├── test_causal_linking.py.bak  # 因果链接测试脚本的备份。
│   │   ├── test_cpc_module.py.bak  # CPC模块测试脚本的备份。
│   │   └── test_unified_cpc.py  # 测试统一CPC模块的功能。
│   ├── stage_5  # 第五阶段测试：图谱构建与可视化
│   │   ├── Stage_5_Test_Report.md  # 第五阶段测试报告。
│   │   ├── __init__.py  # Python包初始化文件。
│   │   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   │   ├── __init__.cpython-310.pyc  # 包初始化文件的编译缓存 (可忽略)
│   │   │   ├── run_tests.cpython-310.pyc  # 运行测试脚本的编译缓存 (可忽略)
│   │   │   ├── test_color_map.cpython-310.pyc  # 颜色映射测试脚本的编译缓存 (可忽略)
│   │   │   ├── test_graph_builder_integration.cpython-310.pyc  # 图谱构建集成测试的编译缓存 (可忽略)
│   │   │   ├── test_graph_controller.cpython-310.pyc  # 图谱控制器测试的编译缓存 (可忽略)
│   │   │   └── test_mermaid_renderer.cpython-310.pyc  # Mermaid渲染器测试的编译缓存 (可忽略)
│   │   ├── run_tests.py  # 运行第五阶段所有测试的脚本。
│   │   ├── test_color_map.py  # 测试颜色映射工具的功能。
│   │   ├── test_graph_builder_integration.py  # 测试图谱构建服务的集成功能。
│   │   ├── test_graph_controller.py  # 测试图谱控制器的功能。
│   │   └── test_mermaid_renderer.py  # 测试Mermaid渲染器的功能。
│   └── stage_6  # 第六阶段测试：系统集成和终端用户功能
│       ├── Stage_6_Test_Report.md  # 第六阶段测试报告。
│       ├── __init__.py  # Python包初始化文件。
│       ├── __pycache__  # Python编译缓存目录 (可忽略)
│       │   ├── __init__.cpython-310.pyc  # 包初始化文件的编译缓存 (可忽略)
│       │   ├── run_tests.cpython-310.pyc  # 运行测试脚本的编译缓存 (可忽略)
│       │   ├── test_api_gateway_cli.cpython-310.pyc  # API网关CLI测试的编译缓存 (可忽略)
│       │   └── test_end_to_end_integration.cpython-310.pyc  # 端到端集成测试的编译缓存 (可忽略)
│       ├── run_tests.py  # 运行第六阶段所有测试的脚本。
│       ├── test_api_gateway_cli.py  # 测试API网关命令行接口的功能。
│       └── test_end_to_end_integration.py  # 测试系统的端到端集成功能。
├── text_ingestion  # 文本摄入微服务，负责加载原始文本并转换为标准格式
│   ├── __pycache__  # Python编译缓存目录 (可忽略)
│   │   └── chapter_loader.cpython-310.pyc  # 章节加载器脚本的编译缓存 (可忽略)
│   ├── app.py  # 文本摄入服务的应用入口脚本。
│   └── chapter_loader.py  # 从文本文件加载并处理章节内容的脚本。
├── tree.md  # 项目目录结构说明（旧版本）。
├── 代码结构设计.md  # 项目代码结构和模块设计的详细文档。
├── 开发方案.md  # 项目整体或特定功能的开发方案文档。
├── 理论支持.md  # 项目相关理论基础和研究支撑文档。
├── 要处理的问题.md  # 待解决问题和任务列表文档。
└── 项目逻辑设计.md  # 项目核心业务逻辑和流程设计文档。