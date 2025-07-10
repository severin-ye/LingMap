#!/usr/bin/env python3
"""
工具函数单元测试

测试common/utils中的工具函数：
- enhanced_logger.py
- json_loader.py  
- path_utils.py
- text_splitter.py
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
import sys

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from common.utils.enhanced_logger import EnhancedLogger
from common.utils.json_loader import JsonLoader
from common.utils.path_utils import get_novel_path, get_config_path, get_output_path
from common.utils.text_splitter import TextSplitter

class TestEnhancedLogger:
    """增强日志记录器测试"""
    
    def test_logger_creation(self):
        """测试日志记录器创建"""
        logger = EnhancedLogger("test_logger", log_level="DEBUG")
        assert logger.logger.name == "test_logger"
    
    def test_logger_info(self):
        """测试信息日志"""
        logger = EnhancedLogger("test_info", log_level="INFO")
        # 这应该不会抛出异常
        logger.info("这是一条测试信息")
        logger.debug("这是一条调试信息")
        logger.warning("这是一条警告信息")
        logger.error("这是一条错误信息")

class TestJsonLoader:
    """JSON加载器测试"""
    
    def test_json_loader_creation(self):
        """测试JSON加载器创建"""
        loader = JsonLoader()
        assert loader is not None
    
    def test_load_valid_json(self):
        """测试加载有效的JSON文件"""
        # 创建临时JSON文件
        test_data = {"test": "data", "number": 123}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            loader = JsonLoader()
            loaded_data = loader.load_json(temp_file)
            assert loaded_data == test_data
            assert loaded_data["test"] == "data"
            assert loaded_data["number"] == 123
        finally:
            os.unlink(temp_file)
    
    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        loader = JsonLoader()
        try:
            result = loader.load_json("nonexistent_file.json")
            # 如果没有抛出异常，应该返回空结果
            assert result is None or isinstance(result, dict)
        except FileNotFoundError:
            # 这是预期的异常
            pass

class TestPathUtils:
    """路径工具测试"""
    
    def test_get_novel_path(self):
        """测试获取小说路径"""
        path = get_novel_path("test.txt")
        assert isinstance(path, (str, Path))
        assert "novel" in str(path)
        assert "test.txt" in str(path)
    
    def test_get_config_path(self):
        """测试获取配置路径"""
        path = get_config_path("config.json")
        assert isinstance(path, (str, Path))
        assert "config" in str(path)
        assert "config.json" in str(path)
    
    def test_get_output_path(self):
        """测试获取输出路径"""
        path = get_output_path("result.json")
        assert isinstance(path, (str, Path))
        assert "output" in str(path)
        assert "result.json" in str(path)

class TestTextSplitter:
    """文本分割器测试"""
    
    def test_text_splitter_creation(self):
        """测试文本分割器创建"""
        splitter = TextSplitter()
        assert splitter is not None
    
    def test_split_text_by_sentences(self):
        """测试按句子分割文本"""
        test_text = "这是第一句话。这是第二句话！这是第三句话？"
        
        sentences = TextSplitter.split_by_sentences(test_text)
        assert len(sentences) >= 1
        assert isinstance(sentences, list)
        assert len(sentences) == 3
    
    def test_split_text_by_length(self):
        """测试按段落分割文本"""
        test_text = "第一段内容。\n\n第二段内容。\n\n第三段内容。"
        
        paragraphs = TextSplitter.split_by_paragraphs(test_text)
        assert len(paragraphs) >= 1
        assert isinstance(paragraphs, list)
        assert len(paragraphs) == 3
    
    def test_split_empty_text(self):
        """测试分割空文本"""
        result = TextSplitter.split_by_sentences("")
        assert isinstance(result, list)
        assert len(result) == 0

def test_utils_integration():
    """测试工具函数集成"""
    # 测试日志记录器和路径工具的集成
    logger = EnhancedLogger("integration_test")
    
    # 测试路径获取
    novel_path = get_novel_path("test.txt")
    config_path = get_config_path("config.json")
    output_path = get_output_path("result.json")
    
    logger.info(f"小说路径: {novel_path}")
    logger.info(f"配置路径: {config_path}")
    logger.info(f"输出路径: {output_path}")
    
    # 验证路径类型
    assert isinstance(novel_path, (str, Path))
    assert isinstance(config_path, (str, Path))
    assert isinstance(output_path, (str, Path))

def test_json_and_text_processing():
    """测试JSON处理和文本处理的集成"""
    # 创建测试数据
    test_data = {
        "text": "这是测试文本。包含多个句子！用于测试处理功能？",
        "metadata": {
            "source": "test",
            "length": 100
        }
    }
    
    # 使用临时文件测试JSON处理
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, ensure_ascii=False)
        temp_file = f.name
    
    try:
        # 加载JSON
        loader = JsonLoader()
        loaded_data = loader.load_json(temp_file)
        
        if loaded_data:
            assert "text" in loaded_data
            
            # 处理文本
            text = loaded_data["text"]
            
            sentences = TextSplitter.split_by_sentences(text)
            assert len(sentences) > 0
    finally:
        os.unlink(temp_file)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
