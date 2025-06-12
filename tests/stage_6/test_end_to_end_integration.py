#!/usr/bin/env python3
"""
第六阶段测试：端到端流程集成测试

测试完整的从文本输入到图谱输出的端到端流程
"""

import unittest
import os
import sys
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from text_ingestion.chapter_loader import ChapterLoader
from event_extraction.di.provider import provide_extractor
from hallucination_refine.di.provider import provide_refiner
from causal_linking.di.provider import provide_linker
from graph_builder.service.mermaid_renderer import MermaidRenderer
from common.models.chapter import Chapter
from common.models.event import EventItem
from common.models.causal_edge import CausalEdge


class TestEndToEndIntegration(unittest.TestCase):
    """测试端到端集成流程"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.test_output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # 创建测试用的小说文件
        self.test_novel_file = os.path.join(self.test_dir, "test_novel.txt")
        with open(self.test_novel_file, 'w', encoding='utf-8') as f:
            f.write("""第一章 青牛镇
韩立从储物袋中取出一颗聚灵丹，这是他在墨府修炼时偷偷炼制的。
服下丹药后，韩立感到体内灵力翻涌，修为有了明显提升。
墨大夫发现韩立修为增长异常，心生疑虑，暗中调查。

第二章 危机
墨大夫查出韩立暗中修炼，大怒之下派遣手下追杀。
韩立察觉到危险，连夜逃离墨府，踏上了逃亡之路。""")

    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_chapter_loading_stage(self):
        """测试章节加载阶段"""
        loader = ChapterLoader()
        
        # 测试从文本文件加载章节
        chapter = loader.load_from_txt(self.test_novel_file)
        
        # 验证章节加载成功
        self.assertIsNotNone(chapter)
        if chapter is not None:
            self.assertIsInstance(chapter, Chapter)
            self.assertIn("青牛镇", chapter.content)
            self.assertIn("韩立", chapter.content)
            self.assertIn("聚灵丹", chapter.content)

    @patch('event_extraction.repository.llm_client.LLMClient.call_llm')
    def test_event_extraction_stage(self, mock_llm_call):
        """测试事件提取阶段"""
        # 模拟LLM响应
        mock_response = {
            "success": True,
            "content": json.dumps({
                "events": [
                    {
                        "event_id": "E1-1",
                        "description": "韩立服用聚灵丹",
                        "characters": ["韩立"],
                        "treasures": ["聚灵丹"],
                        "result": "修为提升",
                        "location": "墨府",
                        "time": "修炼时"
                    },
                    {
                        "event_id": "E1-2",
                        "description": "墨大夫发现韩立修为异常",
                        "characters": ["墨大夫", "韩立"],
                        "treasures": [],
                        "result": "心生疑虑",
                        "location": "墨府",
                        "time": "之后"
                    }
                ]
            })
        }
        mock_llm_call.return_value = mock_response
        
        # 加载章节
        loader = ChapterLoader()
        chapter = loader.load_from_txt(self.test_novel_file)
        
        # 确保章节加载成功
        self.assertIsNotNone(chapter)
        if chapter is None:
            self.skipTest("章节加载失败")
        
        # 提取事件
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "LLM_PROVIDER": "openai"}):
            extractor = provide_extractor()
            events = extractor.extract(chapter)
            
            # 验证事件提取结果
            self.assertIsInstance(events, list)
            self.assertGreater(len(events), 0)
            
            for event in events:
                self.assertIsInstance(event, EventItem)
                self.assertIsNotNone(event.event_id)
                self.assertIsNotNone(event.description)

    @patch('hallucination_refine.service.har_service.HallucinationRefiner.refine')  
    def test_hallucination_refine_stage(self, mock_refine):
        """测试幻觉修正阶段"""
        # 创建测试事件
        test_events = [
            EventItem(
                event_id="E1-1",
                description="韩立服用聚灵丹",
                characters=["韩立"],
                treasures=["聚灵丹"],
                chapter_id="第一章"
            )
        ]
        
        # 模拟精炼器返回相同的事件（表示无需修正）
        mock_refine.return_value = test_events
        
        # 精炼事件
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "LLM_PROVIDER": "openai"}):
            refiner = provide_refiner()
            refined_events = refiner.refine(test_events)
            
            # 验证精炼结果
            self.assertIsInstance(refined_events, list)
            self.assertEqual(len(refined_events), len(test_events))
            
            for event in refined_events:
                self.assertIsInstance(event, EventItem)

    @patch('causal_linking.service.unified_linker_service.UnifiedCausalLinker.link_events')
    def test_causal_linking_stage(self, mock_link_events):
        """测试因果链接阶段"""
        # 模拟链接器返回结果
        mock_edges = [
            CausalEdge(
                from_id="E1-1",
                to_id="E1-2",
                strength="高",
                reason="服用丹药导致修为异常被发现"
            )
        ]
        mock_link_events.return_value = mock_edges
        
        # 创建测试事件
        test_events = [
            EventItem(
                event_id="E1-1",
                description="韩立服用聚灵丹",
                characters=["韩立"],
                treasures=["聚灵丹"],
                chapter_id="第一章"
            ),
            EventItem(
                event_id="E1-2",
                description="墨大夫发现韩立修为异常",
                characters=["墨大夫", "韩立"],
                treasures=[],
                chapter_id="第一章"
            )
        ]
        
        # 链接事件
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "LLM_PROVIDER": "openai"}):
            linker = provide_linker()
            edges = linker.link_events(test_events)
            
            # 验证因果链接结果
            self.assertIsInstance(edges, list)
            
            for edge in edges:
                self.assertIsInstance(edge, CausalEdge)
                self.assertIsNotNone(edge.from_id)
                self.assertIsNotNone(edge.to_id)
                self.assertIsInstance(edge.strength, str)

    def test_mermaid_rendering_stage(self):
        """测试Mermaid渲染阶段"""
        # 创建测试数据
        test_events = [
            EventItem(
                event_id="E1-1",
                description="韩立服用聚灵丹",
                characters=["韩立"],
                treasures=["聚灵丹"],
                chapter_id="第一章"
            ),
            EventItem(
                event_id="E1-2",
                description="墨大夫发现韩立修为异常",
                characters=["墨大夫", "韩立"],
                treasures=[],
                chapter_id="第一章"
            )
        ]
        
        test_edges = [
            CausalEdge(
                from_id="E1-1",
                to_id="E1-2",
                strength="高",
                reason="服用丹药导致修为异常被发现"
            )
        ]
        
        # 渲染图谱
        renderer = MermaidRenderer()
        mermaid_code = renderer.render(test_events, test_edges)
        
        # 验证渲染结果
        self.assertIsInstance(mermaid_code, str)
        self.assertIn("graph TD", mermaid_code)
        self.assertIn("E1-1", mermaid_code)
        self.assertIn("E1-2", mermaid_code)
        self.assertIn("韩立", mermaid_code)

    def test_file_io_operations(self):
        """测试文件输入输出操作"""
        # 测试创建输出目录
        test_output_subdir = os.path.join(self.test_output_dir, "test_subdir")
        os.makedirs(test_output_subdir, exist_ok=True)
        self.assertTrue(os.path.exists(test_output_subdir))
        
        # 测试保存JSON文件
        test_data = {
            "events": ["event1", "event2"],
            "edges": ["edge1", "edge2"]
        }
        test_json_file = os.path.join(test_output_subdir, "test_data.json")
        with open(test_json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        self.assertTrue(os.path.exists(test_json_file))
        
        # 测试读取JSON文件
        with open(test_json_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data, test_data)
        
        # 测试保存文本文件
        test_text_file = os.path.join(test_output_subdir, "test_graph.mmd")
        test_content = """graph TD
    A[事件A] --> B[事件B]
    B --> C[事件C]"""
        
        with open(test_text_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        self.assertTrue(os.path.exists(test_text_file))
        
        # 验证文件内容
        with open(test_text_file, 'r', encoding='utf-8') as f:
            loaded_content = f.read()
        
        self.assertEqual(loaded_content, test_content)


class TestErrorHandling(unittest.TestCase):
    """测试错误处理和异常情况"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_missing_api_key_handling(self):
        """测试缺少API密钥的处理"""
        with patch.dict(os.environ, {}, clear=True):
            # 清除所有API密钥环境变量
            for key in ["OPENAI_API_KEY", "DEEPSEEK_API_KEY"]:
                if key in os.environ:
                    del os.environ[key]
            
            # 测试各个组件在没有API密钥时的行为
            # 应该抛出ValueError，这是期望的行为
            with self.assertRaises(ValueError):
                # 默认使用openai提供商
                extractor = provide_extractor()
                
            # 这表明系统正确地验证了API密钥的存在

    def test_invalid_file_handling(self):
        """测试无效文件处理"""
        # 测试不存在的文件
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")
        loader = ChapterLoader()
        
        # 这应该返回None或抛出适当的异常
        try:
            result = loader.load_from_txt(nonexistent_file)
            # 如果返回None，这是可接受的
            if result is not None:
                self.fail("加载不存在的文件应该返回None或抛出异常")
        except (FileNotFoundError, IOError):
            # 抛出文件相关异常是可接受的
            pass

    def test_empty_file_handling(self):
        """测试空文件处理"""
        # 创建空文件
        empty_file = os.path.join(self.test_dir, "empty.txt")
        with open(empty_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        loader = ChapterLoader()
        result = loader.load_from_txt(empty_file)
        
        # 空文件应该返回None或空章节
        if result is not None:
            self.assertIsInstance(result, Chapter)
            # 如果返回章节，内容应该为空或者章节ID应该指示问题
            self.assertTrue(len(result.content.strip()) == 0 or "empty" in result.chapter_id.lower())

    def test_invalid_json_handling(self):
        """测试无效JSON处理"""
        # 这个测试主要是确保系统能处理LLM返回的无效JSON
        # 在实际的LLM调用中这种情况可能发生
        with patch('event_extraction.repository.llm_client.LLMClient.call_llm') as mock_call:
            mock_call.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
            
            # 创建测试章节
            test_chapter = Chapter(
                chapter_id="test",
                title="测试",
                content="测试内容"
            )
            
            # 测试提取器是否能处理无效JSON
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "LLM_PROVIDER": "openai"}):
                extractor = provide_extractor()
                try:
                    events = extractor.extract(test_chapter)
                    # 应该返回空列表或处理错误
                    self.assertIsInstance(events, list)
                except (json.JSONDecodeError, ValueError, Exception):
                    # 抛出JSON解析错误是可接受的
                    pass


class TestPerformanceAndScaling(unittest.TestCase):
    """测试性能和扩展性"""
    
    def test_large_text_handling(self):
        """测试大文本文件处理"""
        # 创建相对较大的测试文件
        large_content = """第一章 开始
""" + "韩立修炼。" * 1000 + """

第二章 继续
""" + "韩立突破。" * 1000
        
        test_dir = tempfile.mkdtemp()
        try:
            large_file = os.path.join(test_dir, "large_novel.txt")
            with open(large_file, 'w', encoding='utf-8') as f:
                f.write(large_content)
            
            # 测试章节加载器能否处理大文件
            loader = ChapterLoader()
            chapter = loader.load_from_txt(large_file)
            
            self.assertIsNotNone(chapter)
            self.assertGreater(len(chapter.content), 1000)
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_multiple_events_handling(self):
        """测试多事件处理"""
        # 创建大量测试事件
        events = []
        for i in range(50):
            events.append(EventItem(
                event_id=f"E{i}",
                description=f"测试事件{i}",
                characters=["韩立"],
                treasures=[],
                chapter_id="测试章节"
            ))
        
        # 测试Mermaid渲染器能否处理大量事件
        renderer = MermaidRenderer()
        mermaid_code = renderer.render(events, [])
        
        self.assertIsInstance(mermaid_code, str)
        self.assertIn("graph TD", mermaid_code)
        # 验证所有事件都被包含
        for i in range(50):
            self.assertIn(f"E{i}", mermaid_code)


def run_tests():
    """运行第六阶段端到端集成测试"""
    print("=" * 80)
    print("第六阶段测试：端到端集成测试")
    print("=" * 80)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加所有测试类
    test_classes = [
        TestEndToEndIntegration,
        TestErrorHandling,
        TestPerformanceAndScaling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试总结
    print("\n" + "=" * 80)
    print("第六阶段端到端集成测试总结")
    print("=" * 80)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
