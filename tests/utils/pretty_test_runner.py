#!/usr/bin/env python3
"""
美化测试结果输出的TestRunner

本文件实现了一个自定义的TestRunner类，用于美化测试输出，使测试结果更加易读。
它捕获测试中的标准输出和标准错误，并以格式化方式显示。

功能特点：
1. 彩色输出测试结果（成功为绿色，失败为红色，错误为黄色）
2. 捕获每个测试用例的输出，并以格式化方式显示
3. 汇总测试结果，提供整体统计信息
4. 支持详细模式，显示每个测试的运行时间

使用方法：
1. 替代标准的TextTestRunner: runner = PrettyTestRunner(verbosity=2)
2. 运行测试套件: result = runner.run(test_suite)
"""

import unittest
import sys
import time
import io
from contextlib import redirect_stdout, redirect_stderr


# 终端颜色定义
class TermColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class PrettyTestResult(unittest.TextTestResult):
    """美化的测试结果类"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_outputs = {}
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def startTest(self, test):
        """开始测试前，设置测试名称和捕获输出"""
        super().startTest(test)
        
        # 打印测试名称
        if self.showAll:
            method_name = test._testMethodName
            class_name = test.__class__.__name__
            self.stream.write(f"\n{TermColors.BLUE}{class_name}.{method_name}{TermColors.END} ... ")
            self.stream.flush()
        
        # 设置输出捕获缓冲区
        self.output_buffer = io.StringIO()
        self.error_buffer = io.StringIO()
        
        # 捕获stdout和stderr
        sys.stdout = self.output_buffer
        sys.stderr = self.error_buffer
        
        # 记录开始时间
        self.test_start_time = time.time()
    
    def stopTest(self, test):
        """测试结束后，恢复输出并显示捕获的内容"""
        # 计算测试用时
        test_time = time.time() - self.test_start_time
        
        # 恢复原始stdout和stderr
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
        # 获取捕获的输出
        output = self.output_buffer.getvalue().strip()
        error_output = self.error_buffer.getvalue().strip()
        
        # 保存测试输出
        self.test_outputs[test] = {
            'output': output, 
            'error_output': error_output,
            'time': test_time
        }
        
        # 如果测试有输出且为详细模式，显示测试输出
        if (output or error_output) and self.showAll:
            self.stream.write("\n")
            self.stream.write("-" * 70 + "\n")
            self.stream.write(f"{test} 的输出 (耗时: {test_time:.3f}秒):\n")
            self.stream.write("-" * 70 + "\n")
            
            if output:
                self.stream.write(f"{output}\n")
                
            if error_output:
                self.stream.write(f"{TermColors.YELLOW}错误/警告输出:{TermColors.END}\n{error_output}\n")
                
            self.stream.write("-" * 70 + "\n")
        
        super().stopTest(test)
    
    def addSuccess(self, test):
        """测试成功时的处理"""
        super().addSuccess(test)
        if self.showAll:
            self.stream.write(f"{TermColors.GREEN}通过{TermColors.END}\n")
            
    def addError(self, test, err):
        """测试错误时的处理"""
        super().addError(test, err)
        if self.showAll:
            self.stream.write(f"{TermColors.YELLOW}错误{TermColors.END}\n")
            
    def addFailure(self, test, err):
        """测试失败时的处理"""
        super().addFailure(test, err)
        if self.showAll:
            self.stream.write(f"{TermColors.RED}失败{TermColors.END}\n")
            
    def addSkip(self, test, reason):
        """测试跳过时的处理"""
        super().addSkip(test, reason)
        if self.showAll:
            self.stream.write(f"{TermColors.CYAN}跳过{TermColors.END} ({reason})\n")


class PrettyTestRunner(unittest.TextTestRunner):
    """美化输出的测试运行器"""
    
    def __init__(self, stream=None, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None, warnings=None,
                 *, tb_locals=False):
        stream = stream or sys.stderr
        resultclass = resultclass or PrettyTestResult
        super().__init__(stream, descriptions, verbosity,
                         failfast, buffer, resultclass, warnings, tb_locals=tb_locals)
    
    def run(self, test):
        """运行测试套件并返回结果"""
        result = super().run(test)
        
        run = result.testsRun
        failed = len(result.failures)
        errored = len(result.errors)
        skipped = len(result.skipped)
        
        # 已经在TextTestRunner.run中打印了一些统计，这里补充一些彩色的总结信息
        if result.wasSuccessful():
            self.stream.write(f"{TermColors.GREEN}全部通过！✅{TermColors.END}\n")
        else:
            self.stream.write(f"{TermColors.RED}失败: {failed}{TermColors.END}, ")
            self.stream.write(f"{TermColors.YELLOW}错误: {errored}{TermColors.END}, ")
            self.stream.write(f"{TermColors.CYAN}跳过: {skipped}{TermColors.END}\n")
        
        return result
