#!/usr/bin/env python3
"""
阶段一测试包：抽象接口与通用模型测试

本包包含《凡人修仙传》因果事件图谱生成系统的阶段一测试。
阶段一测试主要验证系统的基础数据结构和接口定义。

包含模块：
1. test_models.py - 数据模型与工具类测试
   - 包括 EventItem、Chapter、CausalEdge 和 Treasure 等数据模型的测试
   - 包括 JsonLoader 和 TextSplitter 工具类的测试

2. test_interfaces.py - 抽象接口测试
   - 包括 AbstractExtractor、AbstractRefiner、AbstractLinker 和 
     AbstractGraphRenderer 等接口的测试
   - 使用模拟对象验证接口的定义和行为

3. run_tests.py - 测试运行器
   - 提供统一的测试执行入口
   - 集成所有测试用例并生成测试报告
"""
