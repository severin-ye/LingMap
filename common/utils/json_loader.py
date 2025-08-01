import json
import os
from typing import Dict, Any, Union, List

from common.models.chapter import Chapter


class JsonLoader:
    """JSON configuration and data loading utility"""
    
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """
        Load JSON file
        
        Args:
            file_path: JSON file path
            
        Returns:
            Loaded JSON data dictionary
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    @staticmethod
    def save_json(data: Union[Dict, List], file_path: str) -> None:
        """
        Save data as JSON file
        
        Args:
            data: Data to save
            file_path: Save path
        """
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_chapter_json(file_path: str) -> Chapter:
        """
        Load chapter JSON file and convert to Chapter object
        
        Args:
            file_path: JSON file path
            
        Returns:
            Chapter object
        """
        data = JsonLoader.load_json(file_path)
        return Chapter.from_dict(data)
