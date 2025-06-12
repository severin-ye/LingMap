#!/usr/bin/env python3
"""
事件抽取模块测试脚本

测试事件抽取服务的完整功能，包括文本加载、事件抽取和结果验证
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from common.models.chapter import Chapter
from common.utils.path_utils import get_novel_path, get_config_path
from common.utils.json_loader import JsonLoader
from common.utils.enhanced_logger import EnhancedLogger
from event_extraction.di.provider import provide_extractor
from event_extraction.service.enhanced_extractor_service import EnhancedEventExtractor

# 创建日志记录器
logger = EnhancedLogger("event_extraction_test", log_level="DEBUG")

def load_test_chapter():
    """加载测试章节数据"""
    print("="*80)
    print("1. 加载测试章节数据")
    print("="*80)
    
    # 尝试加载测试文件
    test_novel_path = get_novel_path("test.txt")
    print(f"检查测试文件: {test_novel_path}")
    
    if os.path.exists(test_novel_path):
        with open(test_novel_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ 从测试文件加载了 {len(content)} 个字符")
        source = "test.txt"
    else:
        # 如果测试文件不存在，使用第1章
        chapter_path = get_novel_path("1.txt")
        print(f"测试文件不存在，尝试加载: {chapter_path}")
        
        if not os.path.exists(chapter_path):
            print(f"❌ 未找到任何小说文件")
            return None, None
        
        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read(2000)  # 只读取前2000个字符用于测试
        print(f"✓ 从第1章加载了 {len(content)} 个字符")
        source = "1.txt (前2000字符)"
    
    # 创建Chapter对象
    chapter = Chapter(
        chapter_id="第一章",
        title="第一章",
        content=content,
        segments=[]  # 让抽取器自动分段
    )
    
    print(f"章节信息:")
    print(f"  - ID: {chapter.chapter_id}")
    print(f"  - 标题: {chapter.title}")
    print(f"  - 内容长度: {len(chapter.content)} 字符")
    print(f"  - 来源: {source}")
    
    return chapter, source

def test_extractor_initialization():
    """测试事件抽取器初始化"""
    print("\n" + "="*80)
    print("2. 事件抽取器初始化测试")
    print("="*80)
    
    try:
        # 使用provider获取抽取器
        extractor = provide_extractor()
        
        print(f"✓ 事件抽取器初始化成功")
        print(f"  - 提供商: {getattr(extractor, 'provider', '未知')}")
        print(f"  - 模型: {getattr(extractor, 'model', '未知')}")
        print(f"  - API密钥前缀: {getattr(extractor, 'api_key', '')[:10] if getattr(extractor, 'api_key', '') else '未知'}...")
        print(f"  - 最大工作线程: {getattr(extractor, 'max_workers', '未知')}")
        print(f"  - 调试模式: {getattr(extractor, 'debug_mode', False)}")
        
        return True, extractor
    except Exception as e:
        print(f"❌ 事件抽取器初始化失败: {str(e)}")
        return False, None

def test_prompt_template():
    """测试事件抽取提示词模板"""
    print("\n" + "="*80)
    print("3. 事件抽取提示词模板测试")
    print("="*80)
    
    # 加载提示词模板
    prompt_path = get_config_path("prompt_event_extraction.json")
    print(f"提示词模板路径: {prompt_path}")
    
    try:
        template = JsonLoader.load_json(prompt_path)
        print(f"✓ 成功加载提示词模板")
        
        # 检查必要字段
        required_fields = ["system", "instruction", "output_format"]
        missing_fields = [field for field in required_fields if field not in template]
        
        if missing_fields:
            print(f"❌ 缺少必要字段: {missing_fields}")
            return False
        
        print(f"✓ 包含所有必要字段: {required_fields}")
        
        # 检查指令模板
        instruction = template.get("instruction", "")
        if "{text}" in instruction:
            print(f"✓ 指令模板包含文本占位符")
        else:
            print(f"❌ 指令模板缺少{{text}}占位符")
            return False
        
        # 检查输出格式
        output_format = template.get("output_format", {})
        if isinstance(output_format, dict) and output_format:
            print(f"✓ 输出格式定义完整")
            print(f"  输出格式字段: {list(output_format.keys())}")
        else:
            print(f"❌ 输出格式定义不完整")
            return False
        
        # 测试格式化功能
        sample_text = "韩立从储物袋中取出一颗灵乳，小心翼翼地服下..."
        try:
            formatted_instruction = instruction.format(text=sample_text)
            print(f"✓ 模板格式化功能正常")
        except Exception as e:
            print(f"❌ 模板格式化失败: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 提示词模板测试失败: {e}")
        return False

def test_direct_extraction():
    """测试直接事件抽取功能"""
    print("\n" + "="*80)
    print("4. 直接事件抽取测试")
    print("="*80)
    
    # 获取测试章节
    chapter, source = load_test_chapter()
    if not chapter:
        return False
    
    # 初始化抽取器
    success, extractor = test_extractor_initialization()
    if not success:
        return False
    
    print(f"\n开始事件抽取...")
    print(f"输入文本长度: {len(chapter.content)} 字符")
    
    try:
        # 检查extractor是否为None
        if not extractor:
            print(f"\n❌ 抽取器初始化失败")
            return False
            
        events = extractor.extract(chapter)
        
        if events:
            print(f"\n✓ 成功抽取 {len(events)} 个事件")
            
            # 显示前3个事件的详细信息
            for i, event in enumerate(events[:3], 1):
                print(f"\n事件 {i}:")
                print(f"  ID: {event.event_id}")
                print(f"  描述: {event.description}")
                print(f"  角色: {', '.join(event.characters) if event.characters else '无'}")
                print(f"  宝物: {', '.join(event.treasures) if event.treasures else '无'}")
                print(f"  位置: {event.location or '无'}")
                print(f"  时间: {event.time or '无'}")
                print(f"  结果: {event.result or '无'}")
            
            if len(events) > 3:
                print(f"\n... 还有 {len(events) - 3} 个事件")
            
            # 保存事件到调试文件
            debug_dir = project_root / "debug"
            debug_dir.mkdir(exist_ok=True)
            
            events_file = debug_dir / "extracted_events_test.json"
            with open(events_file, 'w', encoding='utf-8') as f:
                json.dump([event.to_dict() for event in events], f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ 事件已保存到: {events_file}")
            
            return True
        else:
            print(f"\n❌ 未能抽取任何事件")
            return False
            
    except Exception as e:
        print(f"\n❌ 事件抽取失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_extraction_quality():
    """测试事件抽取质量"""
    print("\n" + "="*80)
    print("5. 事件抽取质量评估")
    print("="*80)
    
    # 加载已保存的事件数据
    debug_dir = project_root / "debug"
    events_file = debug_dir / "extracted_events_test.json"
    
    if not events_file.exists():
        print("❌ 未找到事件数据文件，请先运行事件抽取测试")
        return False
    
    try:
        with open(events_file, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        
        print(f"✓ 加载了 {len(events_data)} 个事件")
        
        # 质量检查指标
        total_events = len(events_data)
        events_with_description = sum(1 for e in events_data if e.get('description'))
        events_with_characters = sum(1 for e in events_data if e.get('characters'))
        events_with_treasures = sum(1 for e in events_data if e.get('treasures'))
        events_with_location = sum(1 for e in events_data if e.get('location'))
        events_with_result = sum(1 for e in events_data if e.get('result'))
        
        print(f"\n质量指标:")
        print(f"  有描述的事件: {events_with_description}/{total_events} ({events_with_description/total_events*100:.1f}%)")
        print(f"  有角色的事件: {events_with_characters}/{total_events} ({events_with_characters/total_events*100:.1f}%)")
        print(f"  有宝物的事件: {events_with_treasures}/{total_events} ({events_with_treasures/total_events*100:.1f}%)")
        print(f"  有位置的事件: {events_with_location}/{total_events} ({events_with_location/total_events*100:.1f}%)")
        print(f"  有结果的事件: {events_with_result}/{total_events} ({events_with_result/total_events*100:.1f}%)")
        
        # 检查事件ID的唯一性
        event_ids = [e.get('event_id') for e in events_data if e.get('event_id')]
        unique_ids = set(event_ids)
        
        if len(event_ids) == len(unique_ids):
            print(f"  ✓ 事件ID唯一性: 通过")
        else:
            print(f"  ❌ 事件ID唯一性: 失败 ({len(event_ids)} vs {len(unique_ids)})")
        
        # 基本质量评分
        quality_score = (
            (events_with_description / total_events) * 0.3 +
            (events_with_characters / total_events) * 0.25 +
            (events_with_location / total_events) * 0.15 +
            (events_with_result / total_events) * 0.2 +
            (len(unique_ids) / len(event_ids) if event_ids else 0) * 0.1
        ) * 100
        
        print(f"\n总体质量评分: {quality_score:.1f}/100")
        
        if quality_score >= 80:
            print("✓ 抽取质量优秀")
        elif quality_score >= 60:
            print("⚠️  抽取质量良好")
        else:
            print("❌ 抽取质量需要改进")
        
        return quality_score >= 60
        
    except Exception as e:
        print(f"❌ 质量评估失败: {e}")
        return False

def main():
    """运行事件抽取模块测试"""
    print("事件抽取模块测试套件")
    print("="*80)
    
    tests = [
        ("加载测试章节", lambda: load_test_chapter()[0] is not None),
        ("抽取器初始化", lambda: test_extractor_initialization()[0]),
        ("提示词模板", test_prompt_template),
        ("直接事件抽取", test_direct_extraction),
        ("抽取质量评估", test_extraction_quality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n正在运行测试: {test_name}")
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
        print("🎉 所有事件抽取测试通过！")
    else:
        print("⚠️  部分测试失败，请检查配置和实现")

if __name__ == "__main__":
    main()
