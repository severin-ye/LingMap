#!/usr/bin/env python3
"""
系统配置和环境测试脚本

测试系统配置、路径工具、提示词模板和环境变量
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from common.utils.path_utils import get_project_root, get_config_path, get_novel_path, get_output_path
from common.utils.json_loader import JsonLoader
from common.utils.enhanced_logger import EnhancedLogger

# 创建日志记录器
logger = EnhancedLogger("system_config_test", log_level="DEBUG")

def test_environment_variables():
    """测试环境变量配置"""
    print("="*80)
    print("1. 环境变量测试")
    print("="*80)
    
    # 检查.env文件
    env_file = project_root / ".env"
    print(f"检查.env文件: {env_file}")
    print(f"文件存在: {env_file.exists()}")
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"文件内容长度: {len(content)} 字符")
        
        # 显示文件内容（隐藏敏感信息）
        lines = content.strip().split('\n')
        print("文件内容:")
        for line in lines:
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                if 'API_KEY' in key:
                    print(f"  {key}={value[:10]}...")
                else:
                    print(f"  {line}")
            else:
                print(f"  {line}")
    
    # 检查环境变量
    required_vars = ["LLM_PROVIDER", "DEEPSEEK_API_KEY", "DEEPSEEK_MODEL"]
    print(f"\n检查必要的环境变量:")
    
    all_vars_present = True
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            if 'API_KEY' in var:
                print(f"  ✓ {var}: {value[:10]}...")
            else:
                print(f"  ✓ {var}: {value}")
        else:
            print(f"  ❌ {var}: 未设置")
            all_vars_present = False
    
    return all_vars_present

def test_path_utilities():
    """测试路径工具函数"""
    print("\n" + "="*80)
    print("2. 路径工具测试")
    print("="*80)
    
    # 测试项目根目录
    project_root = get_project_root()
    print(f"项目根目录: {project_root}")
    print(f"目录存在: {project_root.exists()}")
    
    if project_root.exists():
        items = [p.name for p in project_root.iterdir() if not p.name.startswith('.')][:10]
        print(f"目录内容(前10项): {items}")
    
    # 测试配置文件路径
    print(f"\n配置文件路径测试:")
    config_files = [
        "config.json",
        "prompt_event_extraction.json", 
        "prompt_hallucination_refine.json",
        "prompt_causal_linking.json"
    ]
    
    config_results = []
    for config_file in config_files:
        path = get_config_path(config_file)
        exists = os.path.exists(path)
        config_results.append((config_file, exists))
        print(f"  {config_file}: {'✓' if exists else '❌'} {path}")
    
    # 测试小说目录
    novel_dir = get_novel_path()
    print(f"\n小说目录: {novel_dir}")
    print(f"目录存在: {os.path.exists(novel_dir)}")
    
    if os.path.exists(novel_dir):
        txt_files = [f for f in os.listdir(novel_dir) if f.endswith('.txt')]
        print(f"找到.txt文件: {len(txt_files)} 个")
        print(f"文件列表: {txt_files}")
    
    # 测试输出目录
    output_dir = get_output_path()
    print(f"\n输出目录: {output_dir}")
    print(f"目录存在: {os.path.exists(output_dir)}")
    
    if os.path.exists(output_dir):
        subdirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
        print(f"子目录数量: {len(subdirs)}")
    
    return all(result for _, result in config_results)

def test_prompt_templates():
    """测试提示词模板"""
    print("\n" + "="*80)
    print("3. 提示词模板测试")
    print("="*80)
    
    templates = [
        "prompt_event_extraction.json",
        "prompt_hallucination_refine.json", 
        "prompt_causal_linking.json"
    ]
    
    template_results = []
    for template_name in templates:
        print(f"\n测试模板: {template_name}")
        template_path = get_config_path(template_name)
        
        try:
            template = JsonLoader.load_json(template_path)
            print(f"  ✓ 成功加载模板")
            
            # 检查必要字段
            required_fields = ["system", "instruction", "output_format"]
            missing_fields = [field for field in required_fields if field not in template]
            
            if missing_fields:
                print(f"  ❌ 缺少必要字段: {missing_fields}")
                template_results.append(False)
            else:
                print(f"  ✓ 包含所有必要字段")
                
                # 检查system字段是否包含json关键字(DeepSeek需要)
                system_content = template.get("system", "").lower()
                if "json" in system_content:
                    print(f"  ✓ 系统提示包含JSON关键字")
                else:
                    print(f"  ⚠️  系统提示不包含JSON关键字，DeepSeek API可能需要")
                
                # 测试格式化
                instruction = template.get("instruction", "")
                if "{" in instruction:
                    print(f"  ✓ 指令模板包含占位符")
                else:
                    print(f"  ⚠️  指令模板不包含占位符")
                
                template_results.append(True)
                
        except Exception as e:
            print(f"  ❌ 加载失败: {e}")
            template_results.append(False)
    
    return all(template_results)

def test_json_loader():
    """测试JSON加载器"""
    print("\n" + "="*80)
    print("4. JSON加载器测试")
    print("="*80)
    
    # 测试加载配置文件
    config_path = get_config_path("config.json")
    print(f"测试加载: {config_path}")
    
    try:
        config = JsonLoader.load_json(config_path)
        print(f"✓ 成功加载配置文件")
        print(f"配置内容键: {list(config.keys()) if isinstance(config, dict) else 'Not a dict'}")
        
        # 测试保存功能
        test_data = {"test": "data", "timestamp": "2025-06-08"}
        test_path = project_root / "debug" / "test_json.json"
        test_path.parent.mkdir(exist_ok=True)
        
        JsonLoader.save_json(test_data, str(test_path))
        
        # 验证保存的文件
        if test_path.exists():
            loaded_test = JsonLoader.load_json(str(test_path))
            if loaded_test == test_data:
                print(f"✓ JSON保存和加载功能正常")
                test_path.unlink()  # 清理测试文件
                return True
            else:
                print(f"❌ JSON保存/加载数据不一致")
                return False
        else:
            print(f"❌ JSON文件保存失败")
            return False
            
    except Exception as e:
        print(f"❌ JSON加载器测试失败: {e}")
        return False

def test_logger():
    """测试日志系统"""
    print("\n" + "="*80)
    print("5. 日志系统测试")
    print("="*80)
    
    try:
        # 创建测试日志器
        test_logger = EnhancedLogger("system_test", log_level="DEBUG")
        
        # 测试不同级别的日志
        test_logger.debug("这是调试信息")
        test_logger.info("这是信息日志")
        test_logger.warning("这是警告日志")
        test_logger.error("这是错误日志")
        
        # 测试结构化日志
        test_logger.info("结构化日志测试", extra_field="额外数据", count=42)
        
        print("✓ 日志系统测试完成")
        
        # 检查日志文件是否生成
        logs_dir = project_root / "logs"
        if logs_dir.exists():
            log_files = list(logs_dir.glob("system_test_*.log"))
            if log_files:
                print(f"✓ 日志文件已生成: {len(log_files)} 个")
                return True
            else:
                print("⚠️  未找到日志文件")
                return True
        else:
            print("⚠️  日志目录不存在")
            return True
            
    except Exception as e:
        print(f"❌ 日志系统测试失败: {e}")
        return False

def main():
    """运行系统配置测试"""
    print("系统配置和环境测试套件")
    print("="*80)
    
    tests = [
        ("环境变量配置", test_environment_variables),
        ("路径工具函数", test_path_utilities),
        ("提示词模板", test_prompt_templates),
        ("JSON加载器", test_json_loader),
        ("日志系统", test_logger)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 发生异常: {str(e)}")
            results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有系统配置测试通过！")
    else:
        print("⚠️  部分测试失败，请检查系统配置")

if __name__ == "__main__":
    main()
