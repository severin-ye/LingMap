#!/usr/bin/env python3
"""
因果链接模块测试脚本

测试因果链接服务的完整功能，包括提示词生成、API调用和结果解析
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

from common.models.event import EventItem
from common.utils.enhanced_logger import EnhancedLogger
from causal_linking.di.provider import provide_linker
from event_extraction.repository.llm_client import LLMClient

# 创建日志记录器
logger = EnhancedLogger("causal_linking_test", log_level="DEBUG")

def create_test_events():
    """创建测试事件"""
    event1 = EventItem(
        event_id="event_1",
        description="韩立在洗灵池中炼体",
        characters=["韩立"],
        treasures=["洗灵池"],
        time="",
        location="七玄门",
        result="韩立的体质得到了显著增强"
    )
    
    event2 = EventItem(
        event_id="event_2", 
        description="韩立突破至练气期第三层",
        characters=["韩立"],
        treasures=[],
        time="",
        location="七玄门",
        result="韩立的修为提升至练气期第三层"
    )
    
    event3 = EventItem(
        event_id="event_3",
        description="韩立遇到墨大夫",
        characters=["韩立", "墨大夫"],
        treasures=[],
        time="",
        location="七玄门",
        result="墨大夫成为韩立的师父"
    )
    
    return [event1, event2, event3]

def test_causal_linker_initialization():
    """测试因果链接器初始化"""
    print("="*80)
    print("1. 因果链接器初始化测试")
    print("="*80)
    
    try:
        linker = provide_linker()
        
        print(f"✓ 因果链接器初始化成功")
        print(f"  - 提供商: {getattr(linker, 'provider', '未知')}")
        print(f"  - 模型: {getattr(linker, 'model', '未知')}")
        print(f"  - API密钥前缀: {getattr(linker, 'api_key', '')[:10] if getattr(linker, 'api_key', '') else '未知'}...")
        print(f"  - 最大工作线程: {getattr(linker, 'max_workers', '未知')}")
        
        # 检查强度映射
        expected_mapping = {"高": 3, "中": 2, "低": 1}
        strength_mapping = getattr(linker, 'strength_mapping', {})
        if strength_mapping == expected_mapping:
            print("  ✓ 强度映射配置正确")
        else:
            print(f"  ⚠️  强度映射配置异常: {strength_mapping}")
        
        return True, linker
    except Exception as e:
        print(f"❌ 因果链接器初始化失败: {str(e)}")
        return False, None

def test_direct_api_call():
    """测试直接API调用"""
    print("\n" + "="*80)
    print("2. 直接API调用测试")
    print("="*80)
    
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 未找到API密钥")
        return False
    
    # 创建测试事件
    events = create_test_events()
    event1, event2 = events[0], events[1]
    
    # 读取提示词模板
    template_path = '/home/severin/CodeLib_linux/KNU_Class/Digital_Huma/Fianl_HW/common/config/prompt_causal_linking.json'
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            prompt_template = json.load(f)
    except Exception as e:
        print(f"❌ 无法加载提示词模板: {str(e)}")
        return False
    
    # 构建提示词
    system_prompt = prompt_template.get('system', '')
    instruction = prompt_template.get('instruction', '').format(
        event1=json.dumps(event1.to_dict(), ensure_ascii=False),
        event2=json.dumps(event2.to_dict(), ensure_ascii=False)
    )
    
    print("系统提示词:")
    print(system_prompt)
    print("\n用户提示词:")
    print(instruction[:200] + "..." if len(instruction) > 200 else instruction)
    
    # 调用API
    client = LLMClient(
        api_key=api_key,
        model="deepseek-chat",
        provider="deepseek"
    )
    
    response = client.call_with_json_response(system_prompt, instruction)
    
    if response['success'] and 'json_content' in response:
        json_content = response['json_content']
        print("\n✓ API调用成功")
        print("响应内容:")
        print(json.dumps(json_content, ensure_ascii=False, indent=2))
        return True
    else:
        print(f"❌ API调用失败: {response.get('error', '未知错误')}")
        return False

def test_causal_analysis():
    """测试因果分析功能"""
    print("\n" + "="*80)
    print("3. 因果分析功能测试")
    print("="*80)
    
    success, linker = test_causal_linker_initialization()
    if not success:
        return False
    
    events = create_test_events()
    
    # 测试单个事件对的因果分析
    print("测试单个事件对的因果分析...")
    event1, event2 = events[0], events[1]
    
    try:
        # 检查linker是否为None
        if not linker:
            print(f"❌ 因果链接器未初始化")
            return False
            
        # 使用getattr安全调用方法
        analyze_func = getattr(linker, 'analyze_causal_relation', None)
        if not analyze_func:
            print(f"❌ 因果链接器没有analyze_causal_relation方法")
            return False
            
        edge = analyze_func(event1, event2)
        
        if edge:
            print(f"✓ 发现因果关系: {edge.from_id} -> {edge.to_id}")
            print(f"  强度: {edge.strength}")
            print(f"  理由: {edge.reason}")
            return True
        else:
            print("- 未发现因果关系")
            return True
    except Exception as e:
        print(f"❌ 因果分析失败: {str(e)}")
        return False

def test_full_causal_linking():
    """测试完整的因果链接流程"""
    print("\n" + "="*80)
    print("4. 完整因果链接流程测试")
    print("="*80)
    
    success, linker = test_causal_linker_initialization()
    if not success:
        return False
    
    events = create_test_events()
    print(f"测试事件数量: {len(events)}")
    
    try:
        # 检查linker是否为None
        if not linker:
            print(f"❌ 因果链接器未初始化")
            return False
            
        # 使用getattr安全调用方法
        link_events_func = getattr(linker, 'link_events', None)
        if not link_events_func:
            print(f"❌ 因果链接器没有link_events方法")
            return False
            
        # 分析所有事件之间的因果关系
        causal_links = link_events_func(events)
        
        print(f"\n✓ 因果链接分析完成")
        print(f"发现的因果关系数量: {len(causal_links)}")
        
        if causal_links:
            print("\n因果关系详情:")
            for i, link in enumerate(causal_links, 1):
                print(f"  {i}. {link.from_id} -> {link.to_id}")
                print(f"     强度: {link.strength}")
                print(f"     理由: {link.reason}")
        
        return True
    except Exception as e:
        print(f"❌ 完整因果链接流程失败: {str(e)}")
        return False

def test_dag_construction():
    """测试DAG构建功能"""
    print("\n" + "="*80)
    print("5. DAG构建测试")
    print("="*80)
    
    success, linker = test_causal_linker_initialization()
    if not success:
        return False
    
    events = create_test_events()
    
    try:
        # 检查linker是否为None
        if not linker:
            print(f"❌ 因果链接器未初始化")
            return False
            
        # 使用getattr安全调用方法
        link_events_func = getattr(linker, 'link_events', None)
        if not link_events_func:
            print(f"❌ 因果链接器没有link_events方法")
            return False
            
        # 先获取因果关系
        causal_links = link_events_func(events)
        
        if causal_links:
            # 检查build_dag方法
            build_dag_func = getattr(linker, 'build_dag', None)
            if not build_dag_func:
                print(f"❌ 因果链接器没有build_dag方法")
                return False
                
            # 构建DAG
            processed_events, dag_edges = build_dag_func(events, causal_links)
            
            print(f"✓ DAG构建完成")
            print(f"原始边数: {len(causal_links)}")
            print(f"DAG中保留的边数: {len(dag_edges)}")
            print(f"移除的边数: {len(causal_links) - len(dag_edges)}")
            
            if dag_edges:
                print("\nDAG中的边:")
                for edge in dag_edges:
                    print(f"  {edge.from_id} -> {edge.to_id} (强度: {edge.strength})")
            
            return True
        else:
            print("⚠️  没有发现因果关系，无法构建DAG")
            return True
    except Exception as e:
        print(f"❌ DAG构建失败: {str(e)}")
        return False

def main():
    """运行因果链接模块测试"""
    print("因果链接模块测试套件")
    print("="*80)
    
    tests = [
        ("因果链接器初始化", lambda: test_causal_linker_initialization()[0]),
        ("直接API调用", test_direct_api_call),
        ("因果分析功能", test_causal_analysis),
        ("完整因果链接流程", test_full_causal_linking),
        ("DAG构建", test_dag_construction)
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
        print("🎉 所有因果链接测试通过！")
    else:
        print("⚠️  部分测试失败，请检查配置和实现")

if __name__ == "__main__":
    main()
