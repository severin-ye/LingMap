#!/usr/bin/env python3
"""
路径工具测试脚本

用于测试path_utils模块的路径计算是否正确
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到sys.path
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from common.utils.path_utils import get_project_root, get_config_path, get_novel_path, get_output_path

def test_path_utils():
    """测试路径工具函数"""
    print("="*60)
    print("路径工具测试")
    print("="*60)
    
    # 打印项目根目录
    project_root = get_project_root()
    print(f"项目根目录: {project_root}")
    print(f"该目录是否存在: {project_root.exists()}")
    print(f"该目录中的文件和文件夹: {[p.name for p in project_root.iterdir() if p.name[0] != '.'][:10]}")
    print()
    
    # 测试配置路径
    config_files = ["config.json", "prompt_event_extraction.json", "prompt_hallucination_refine.json", "prompt_causal_linking.json"]
    print("配置文件路径测试:")
    for config_file in config_files:
        path = get_config_path(config_file)
        exists = os.path.exists(path)
        print(f"  {config_file}: {path}")
        print(f"  文件存在: {exists}")
        if exists:
            try:
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"  配置有效: 是 (包含 {len(data)} 个顶级键)")
            except Exception as e:
                print(f"  配置有效: 否 (错误: {e})")
        print()
    
    # 测试小说路径
    print("小说目录路径测试:")
    novel_dir = get_novel_path()
    print(f"  小说目录: {novel_dir}")
    print(f"  目录存在: {os.path.exists(novel_dir)}")
    if os.path.exists(novel_dir):
        txt_files = [f for f in os.listdir(novel_dir) if f.endswith('.txt')]
        print(f"  .txt文件数量: {len(txt_files)}")
        print(f"  文件列表: {txt_files}")
    print()
    
    # 测试输出路径
    print("输出目录路径测试:")
    output_dir = get_output_path()
    print(f"  输出目录: {output_dir}")
    print(f"  目录存在: {os.path.exists(output_dir)}")
    if os.path.exists(output_dir):
        subdirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
        print(f"  子目录数量: {len(subdirs)}")
        print(f"  最近的5个子目录: {subdirs[-5:] if len(subdirs) > 5 else subdirs}")
    
    print("="*60)

if __name__ == "__main__":
    test_path_utils()
