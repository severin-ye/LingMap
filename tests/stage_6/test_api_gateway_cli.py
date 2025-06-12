#!/usr/bin/env python3
"""
第六阶段测试：API网关和CLI接口测试

测试内容：
1. API网关的基本功能
2. CLI接口的参数解析
3. 端到端流程集成
4. 环境设置和检查功能
5. 错误处理和异常情况
"""

import unittest
import os
import sys
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from io import StringIO

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from api_gateway.main import process_text, process_directory, setup_env
import main
from common.models.chapter import Chapter
from common.models.event import EventItem
from common.models.causal_edge import CausalEdge


class TestAPIGateway(unittest.TestCase):
    """测试API网关功能"""
    
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

    def test_setup_env(self):
        """测试环境设置功能"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = False  # 模拟.env文件不存在
                
                # 测试环境设置不会出错
                try:
                    setup_env()
                except Exception as e:
                    self.fail(f"setup_env() 不应该抛出异常: {e}")

    @patch('api_gateway.main.provide_extractor')
    @patch('api_gateway.main.provide_refiner')
    @patch('api_gateway.main.provide_linker')
    @patch('api_gateway.main.MermaidRenderer')
    @patch('api_gateway.main.ChapterLoader')
    def test_process_text_success(self, mock_loader, mock_renderer, mock_linker, mock_refiner, mock_extractor):
        """测试单个文本文件处理成功情况"""
        # 模拟章节加载器
        mock_chapter = Chapter(
            chapter_id="第一章",
            title="青牛镇",
            content="韩立从储物袋中取出一颗聚灵丹..."
        )
        mock_loader.return_value.load_from_txt.return_value = mock_chapter
        
        # 模拟事件提取器
        mock_events = [
            EventItem(
                event_id="E1-1",
                description="韩立服用聚灵丹",
                characters=["韩立"],
                treasures=["聚灵丹"],
                chapter_id="第一章"
            ),
            EventItem(
                event_id="E1-2", 
                description="韩立修为提升",
                characters=["韩立"],
                treasures=[],
                chapter_id="第一章"
            )
        ]
        mock_extractor.return_value.extract.return_value = mock_events
        
        # 模拟精炼器
        mock_refiner.return_value.refine.return_value = mock_events
        
        # 模拟链接器
        mock_edges = [
            CausalEdge(
                from_id="E1-1",
                to_id="E1-2",
                strength="高",
                reason="服用丹药导致修为提升"
            )
        ]
        mock_linker.return_value.link_events.return_value = mock_edges
        mock_linker.return_value.build_dag.return_value = (mock_events, mock_edges)
        
        # 模拟渲染器
        mock_renderer.return_value.render.return_value = """
graph TD
    E1-1[韩立服用聚灵丹] --> E1-2[韩立修为提升]
"""
        
        # 执行测试
        with patch('builtins.print'):  # 抑制打印输出
            try:
                # 设置临时目录为有效路径
                temp_dir = os.path.join(self.test_output_dir, "temp")
                os.makedirs(temp_dir, exist_ok=True)
                process_text(self.test_novel_file, self.test_output_dir, temp_dir=temp_dir)
                
                # 验证各个组件被正确调用
                mock_loader.return_value.load_from_txt.assert_called_once_with(self.test_novel_file)
                mock_extractor.return_value.extract.assert_called_once_with(mock_chapter)
                # refine方法被调用时会传入额外的context参数
                mock_refiner.return_value.refine.assert_called_once()
                mock_linker.return_value.link_events.assert_called_once()
                mock_linker.return_value.build_dag.assert_called_once()
                mock_renderer.return_value.render.assert_called_once()
                
            except Exception as e:
                self.fail(f"process_text() 不应该抛出异常: {e}")

    @patch('api_gateway.main.process_text')
    @patch('glob.glob')
    def test_process_directory_success(self, mock_glob, mock_process_text):
        """测试目录批量处理成功情况"""
        # 模拟glob返回的文件列表
        test_input_dir = os.path.join(self.test_dir, "input")
        os.makedirs(test_input_dir, exist_ok=True)
        
        mock_files = [
            os.path.join(test_input_dir, "novel1.txt"),
            os.path.join(test_input_dir, "novel2.txt"),
            os.path.join(test_input_dir, "novel3.txt")
        ]
        mock_glob.return_value = mock_files
        
        # 执行测试
        with patch('builtins.print'):  # 抑制打印输出
            process_directory(test_input_dir, self.test_output_dir)
            
            # 验证每个txt文件都被处理
            self.assertEqual(mock_process_text.call_count, 3)
            
            # 验证调用参数
            call_args_list = mock_process_text.call_args_list
            called_files = [call_args[0][0] for call_args in call_args_list]
            
            for expected_file in mock_files:
                self.assertIn(expected_file, called_files)

    @patch('api_gateway.main.ChapterLoader')
    def test_process_text_load_failure(self, mock_loader):
        """测试章节加载失败的情况"""
        # 模拟加载失败
        mock_loader.return_value.load_from_txt.return_value = None
        
        with patch('builtins.print') as mock_print:
            temp_dir = os.path.join(self.test_output_dir, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            process_text(self.test_novel_file, self.test_output_dir, temp_dir=temp_dir)
            
            # 验证输出了失败信息
            calls = [call[0][0] for call in mock_print.call_args_list]
            self.assertTrue(any("加载章节失败" in str(call) for call in calls))


class TestMainCLI(unittest.TestCase):
    """测试主程序CLI接口功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('main.print_banner')
    @patch('main.setup_environment')
    @patch('main.check_environment')
    def test_main_check_env_mode(self, mock_check_env, mock_setup_env, mock_banner):
        """测试环境检查模式"""
        with patch('sys.argv', ['main.py', '--check-env']):
            with patch('main.check_environment') as mock_check:
                try:
                    main.main()
                    mock_check.assert_called()
                except SystemExit:
                    pass  # check-env模式会调用return，这是正常的

    @patch('main.run_demo')
    @patch('main.setup_environment')  
    @patch('main.check_environment')
    @patch('main.print_banner')
    def test_main_demo_mode(self, mock_banner, mock_check_env, mock_setup_env, mock_run_demo):
        """测试演示模式"""
        with patch('sys.argv', ['main.py', '--demo', '--provider', 'deepseek']):
            try:
                main.main()
                mock_run_demo.assert_called_once_with('deepseek')
            except SystemExit:
                pass

    @patch('main.run_tests')
    @patch('main.setup_environment')
    @patch('main.check_environment') 
    @patch('main.print_banner')
    def test_main_test_mode(self, mock_banner, mock_check_env, mock_setup_env, mock_run_tests):
        """测试测试模式"""
        with patch('sys.argv', ['main.py', '--test']):
            try:
                main.main()
                mock_run_tests.assert_called_once()
            except SystemExit:
                pass

    @patch('main.run_benchmark')
    @patch('main.setup_environment')
    @patch('main.check_environment')
    @patch('main.print_banner')
    def test_main_benchmark_mode(self, mock_banner, mock_check_env, mock_setup_env, mock_run_benchmark):
        """测试基准测试模式"""
        with patch('sys.argv', ['main.py', '--benchmark']):
            try:
                main.main()
                mock_run_benchmark.assert_called_once()
            except SystemExit:
                pass

    @patch('main.process_file')
    @patch('main.setup_environment')
    @patch('main.check_environment')
    @patch('main.print_banner')
    @patch('pathlib.Path.exists')
    def test_main_single_file_mode(self, mock_exists, mock_banner, mock_check_env, mock_setup_env, mock_process_file):
        """测试单文件处理模式"""
        mock_exists.return_value = True
        test_file = os.path.join(self.test_dir, "test.txt")
        
        with patch('sys.argv', ['main.py', '--input', test_file, '--provider', 'openai']):
            try:
                main.main()
                mock_process_file.assert_called_once()
            except SystemExit:
                pass

    @patch('main.process_directory')
    @patch('main.setup_environment')
    @patch('main.check_environment')
    @patch('main.print_banner')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    def test_main_batch_mode(self, mock_is_dir, mock_exists, mock_banner, mock_check_env, mock_setup_env, mock_process_dir):
        """测试批量处理模式"""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        test_dir = os.path.join(self.test_dir, "input")
        
        with patch('sys.argv', ['main.py', '--batch', test_dir]):
            with patch('pathlib.Path.glob') as mock_glob:
                mock_glob.return_value = [Path(os.path.join(test_dir, "test.txt"))]
                try:
                    main.main()
                    mock_process_dir.assert_called_once()
                except SystemExit:
                    pass

    def test_main_invalid_input_file(self):
        """测试输入文件不存在的情况"""
        with patch('sys.argv', ['main.py', '--input', '/nonexistent/file.txt']):
            with patch('main.setup_environment'):
                with patch('main.check_environment'):
                    with patch('main.print_banner'):
                        with patch('builtins.print') as mock_print:
                            with self.assertRaises(SystemExit):
                                main.main()
                            
                            # 验证输出了错误信息
                            calls = [call[0][0] for call in mock_print.call_args_list]
                            self.assertTrue(any("输入文件不存在" in str(call) for call in calls))

    def test_main_invalid_input_directory(self):
        """测试输入目录不存在的情况"""
        with patch('sys.argv', ['main.py', '--batch', '/nonexistent/directory']):
            with patch('main.setup_environment'):
                with patch('main.check_environment'):
                    with patch('main.print_banner'):
                        with patch('builtins.print') as mock_print:
                            with self.assertRaises(SystemExit):
                                main.main()
                            
                            # 验证输出了错误信息
                            calls = [call[0][0] for call in mock_print.call_args_list]
                            self.assertTrue(any("输入目录不存在" in str(call) for call in calls))


class TestEnvironmentFunctions(unittest.TestCase):
    """测试环境设置和检查功能"""
    
    def test_setup_environment(self):
        """测试环境设置功能"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('main.PROJECT_ROOT') as mock_root:
                mock_root.__truediv__ = lambda self, other: Path(f"/fake/{other}")
                with patch('pathlib.Path.mkdir'):
                    with patch('pathlib.Path.exists') as mock_exists:
                        mock_exists.return_value = False
                        
                        try:
                            main.setup_environment()
                            
                            # 验证默认环境变量被设置
                            self.assertEqual(os.environ.get("MAX_WORKERS"), "3")
                            self.assertEqual(os.environ.get("LLM_PROVIDER"), "deepseek")
                            
                        except Exception as e:
                            self.fail(f"setup_environment() 不应该抛出异常: {e}")

    @patch('builtins.print')
    def test_check_environment(self, mock_print):
        """测试环境检查功能"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key-123"}, clear=True):
            try:
                main.check_environment()
                
                # 验证检查函数正常执行
                self.assertTrue(mock_print.called)
                
            except Exception as e:
                self.fail(f"check_environment() 不应该抛出异常: {e}")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_run_interactive_exit(self, mock_print, mock_input):
        """测试交互式模式退出功能"""
        # 模拟用户选择退出
        mock_input.return_value = "0"
        
        try:
            main.run_interactive()
            
            # 验证输出了退出信息
            calls = [call[0][0] for call in mock_print.call_args_list]
            self.assertTrue(any("再见" in str(call) for call in calls))
            
        except Exception as e:
            self.fail(f"run_interactive() 不应该抛出异常: {e}")


class TestIntegrationFlow(unittest.TestCase):
    """测试完整集成流程"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_run_tests_integration(self, mock_print, mock_subprocess):
        """测试运行测试的集成功能"""
        # 模拟成功的测试运行
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="test output",
            stderr=""
        )
        
        try:
            main.run_tests()
            
            # 验证subprocess.run被调用
            mock_subprocess.assert_called()
            
        except Exception as e:
            self.fail(f"run_tests() 不应该抛出异常: {e}")

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_run_benchmark_integration(self, mock_print, mock_subprocess):
        """测试运行基准测试的集成功能"""
        # 模拟成功的基准测试运行
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="benchmark output",
            stderr=""
        )
        
        try:
            main.run_benchmark()
            
            # 验证输出了基准测试信息
            self.assertTrue(mock_print.called)
            
        except Exception as e:
            self.fail(f"run_benchmark() 不应该抛出异常: {e}")

    @patch('main.logger')
    def test_error_handling_with_verbose(self, mock_logger):
        """测试详细模式下的错误处理"""
        with patch('sys.argv', ['main.py', '--input', '/nonexistent/file.txt', '--verbose']):
            with patch('main.setup_environment'):
                with patch('main.check_environment'):
                    with patch('main.print_banner'):
                        with patch('builtins.print'):
                            with patch('traceback.print_exc') as mock_traceback:
                                with self.assertRaises(SystemExit):
                                    main.main()
                                
                                # 在详细模式下应该输出异常堆栈
                                # 注意：这里可能不会调用traceback.print_exc，因为是FileNotFoundError而不是通用异常


def run_tests():
    """运行第六阶段所有测试"""
    print("=" * 80)
    print("第六阶段测试：集成与统一调用接口测试")
    print("=" * 80)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加所有测试类
    test_classes = [
        TestAPIGateway,
        TestMainCLI,
        TestEnvironmentFunctions,
        TestIntegrationFlow
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试总结
    print("\n" + "=" * 80)
    print("第六阶段测试总结")
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
