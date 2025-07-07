import json
import os
from typing import Dict, Any, Union, List

from common.models.chapter import Chapter


class JsonLoader:
    """JSON 配置和数据加载工具"""
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """
        加载 JSON 文件
        
        Args:
            file_path: JSON 文件路径
            
        Returns:
            加载的 JSON 数据字典
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    @staticmethod
    def save_json(data: Union[Dict, List], file_path: str) -> None:
        """
        保存数据为 JSON 文件
        
        Args:
            data: 要保存的数据
            file_path: 保存路径
        """
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_chapter_json(file_path: str) -> Chapter:
        """
        加载章节 JSON 文件并转换为 Chapter 对象
        
        Args:
            file_path: JSON 文件路径
            
        Returns:
            章节对象
        """
        data = JsonLoader.load_json(file_path)
        return Chapter.from_dict(data)
