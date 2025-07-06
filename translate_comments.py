#!/usr/bin/env python3
"""
Script to translate Chinese comments to English in all Python files
"""

import os
import re
import sys
from typing import Dict

# Translation dictionary for common Chinese comments
TRANSLATION_MAP = {
    # Common phrases
    "将项目根目录添加到": "Add project root directory to",
    "添加项目根目录到": "Add project root directory to",
    "将项目根目录添加到路径": "Add project root directory to path",
    "将项目根目录添加到系统路径": "Add project root directory to system path",
    "导入": "Import",
    "加载": "Load",
    "检查": "Check",
    "获取": "Get",
    "创建": "Create", 
    "使用": "Use",
    "设置": "Set",
    "配置": "Configure",
    "初始化": "Initialize",
    "验证": "Verify",
    "测试": "Test",
    "运行": "Run",
    "执行": "Execute",
    "处理": "Process",
    "生成": "Generate",
    "构建": "Build",
    "输出": "Output",
    "保存": "Save",
    "读取": "Read",
    "写入": "Write",
    "返回": "Return",
    "抽取": "Extract",
    "提取": "Extract",
    "事件": "event",
    "章节": "chapter",
    "因果": "causal",
    "链接": "linking", 
    "修复": "refine",
    "幻觉": "hallucination",
    "模型": "model",
    "线程": "thread",
    "并行": "parallel",
    "工作线程数": "worker threads",
    "环境变量": "environment variables",
    "配置文件": "configuration file",
    "API密钥": "API key",
    "提供商": "provider",
    "客户端": "client",
    
    # Full sentence translations
    "加载.env文件中的环境变量": "Load environment variables from .env file",
    "检查API提供商环境变量": "Check API provider environment variable",
    "根据提供商获取相应的API密钥": "Get corresponding API key based on provider",
    "使用path_utils获取配置文件路径": "Use path_utils to get configuration file path",
    "记录线程使用情况": "Log thread usage information",
    "初始化LLM客户端": "Initialize LLM client",
    "如果未提供API密钥，尝试从环境变量获取": "If no API key provided, try to get from environment variables",
    "批处理模式": "Batch processing mode",
    "单文件模式": "Single file mode",
    "错误": "Error",
    "成功": "Successfully",
    "失败": "Failed",
    "完成": "Completed",
    "开始": "Start",
    "结束": "End",
    "正在": "Processing",
    "简单返回输入": "Simply return input",
    "简单返回输入的事件": "Simply return input events",
    "返回基于小说内容的测试事件": "Return test events based on novel content",
    "返回基于小说内容的因果关系": "Return causal relationships based on novel content",
    "返回简单的Mermaid字符串": "Return simple Mermaid string",
    "验证模拟方法被调用": "Verify mock method was called",
    "验证返回类型": "Verify return type",
    "验证事件内容与小说有关": "Verify event content is related to novel",
    "验证事件内容仍然保留": "Verify event content is still preserved",
    "验证边的属性": "Verify edge properties",
    "验证结果内容": "Verify result content",
    "简单验证返回的Mermaid字符串格式": "Simply verify returned Mermaid string format",
    "如果找不到第二章，则使用全文": "If second chapter not found, use full text",
    "只在开头部分查找": "Only search in the beginning part",
    "打印一些统计信息": "Print some statistics",
    "打印进度": "Print progress",
    "匹配章节标题": "Match chapter titles",
    "分段": "Segment text",
    "为每个segment添加chapter_id前缀": "Add chapter_id prefix to each segment",
    "事件抽取是IO密集型任务，适合使用更多线程": "Event extraction is IO-intensive, suitable for more threads",
    "幻觉修复是IO密集型任务，适合使用更多线程": "Hallucination refinement is IO-intensive, suitable for more threads",
    "因果分析是IO和CPU混合型任务，使用默认线程配置": "Causal analysis is IO and CPU mixed task, use default thread configuration",
    "使用线程池并行处理每个事件": "Use thread pool to process each event in parallel",
    "优化后的实现 - 使用as_completed等待完成的任务": "Optimized implementation - use as_completed to wait for completed tasks",
    "同时提交所有事件处理任务": "Submit all event processing tasks simultaneously",
    "统计完成的任务数量": "Count completed tasks",
    "实时收集已完成的任务结果": "Collect completed task results in real time",
    "如果处理失败，保留原始事件": "If processing fails, keep the original event",
    "DeepSeek模型名称": "DeepSeek model name",
    "根据系统资源和配置动态设置并发数": "Dynamically set concurrency based on system resources and configuration",
    "启用调试模式以记录详细日志": "Enable debug mode for detailed logging",
}

def translate_comment(comment_text: str) -> str:
    """Translate Chinese comment to English"""
    # Remove leading # and whitespace
    content = comment_text.lstrip('# ')
    
    # Check for exact matches first
    for chinese, english in TRANSLATION_MAP.items():
        if chinese in content:
            content = content.replace(chinese, english)
    
    # If still contains Chinese characters, provide a generic translation
    if re.search(r'[\u4e00-\u9fff]', content):
        # Try to handle common patterns
        content = re.sub(r'(.*)使用工作线程数', r'\1using worker threads', content)
        content = re.sub(r'(.*)使用(.*)个工作线程并行处理(.*)个事件', r'\1processing \3 events in parallel using \2 worker threads', content)
        content = re.sub(r'对事件(.*)进行第(.*)次精修', r'Performing refinement iteration \2 on event \1', content)
        content = re.sub(r'事件(.*)精修完成，无幻觉', r'Event \1 refinement completed, no hallucinations', content)
        content = re.sub(r'事件(.*)的精修请求失败', r'Refinement request failed for event \1', content)
        content = re.sub(r'处理事件(.*)时出错', r'Error processing event \1', content)
        content = re.sub(r'幻觉修复进度', r'Hallucination refinement progress', content)
        
        # Generic fallback for remaining Chinese text
        if re.search(r'[\u4e00-\u9fff]', content):
            # Mark as needing manual translation
            content = f"TODO: Translate - {content}"
    
    return f"# {content}"

def process_file(file_path: str) -> bool:
    """Process a single Python file to translate Chinese comments"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        
        for line in lines:
            # Check if line contains a comment with Chinese characters
            if '#' in line and re.search(r'[\u4e00-\u9fff]', line):
                # Find the comment part
                comment_start = line.find('#')
                code_part = line[:comment_start]
                comment_part = line[comment_start:]
                
                # Translate the comment
                translated_comment = translate_comment(comment_part.rstrip('\n'))
                new_line = code_part + translated_comment + '\n'
                new_lines.append(new_line)
                modified = True
            else:
                new_lines.append(line)
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"Translated comments in: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all Python files"""
    project_root = "/home/severin/CodeLib_linux/KNU_Class/Digital_Huma/Fianl_HW"
    
    files_processed = 0
    files_modified = 0
    
    # Walk through all Python files
    for root, dirs, files in os.walk(project_root):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                files_processed += 1
                
                if process_file(file_path):
                    files_modified += 1
    
    print(f"\nProcessing complete:")
    print(f"Files processed: {files_processed}")
    print(f"Files modified: {files_modified}")

if __name__ == "__main__":
    main()
