#!/usr/bin/env python3
"""
提示词模板测试脚本

用于测试提示词模板的加载和使用
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到sys.path
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from common.utils.json_loader import JsonLoader
from common.utils.path_utils import get_config_path

def test_prompt_templates():
    """测试提示词模板加载和使用"""
    print("="*60)
    print("提示词模板测试")
    print("="*60)
    
    templates = [
        "prompt_event_extraction.json",
        "prompt_hallucination_refine.json",
        "prompt_causal_linking.json"
    ]
    
    for template_name in templates:
        print(f"测试模板: {template_name}")
        template_path = get_config_path(template_name)
        
        try:
            template = JsonLoader.load_json(template_path)
            print(f"  ✓ 成功加载模板")
            
            # 检查必要字段
            required_fields = ["system", "instruction", "output_format"]
            missing_fields = [field for field in required_fields if field not in template]
            
            if missing_fields:
                print(f"  ✗ 缺少必要字段: {missing_fields}")
            else:
                print(f"  ✓ 包含所有必要字段")
            
            # 尝试格式化内容
            if "instruction" in template and "{text}" in template["instruction"]:
                sample_text = "韩立从储物袋中取出一颗灵乳..."
                formatted = template["instruction"].format(text=sample_text)
                print(f"  ✓ 成功格式化指令")
            else:
                print(f"  ✗ 无法格式化指令，缺少{{text}}占位符")
            
        except Exception as e:
            print(f"  ✗ 加载失败: {e}")
        
        print()
    
    print("="*60)

if __name__ == "__main__":
    test_prompt_templates()
