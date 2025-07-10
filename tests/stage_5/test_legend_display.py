#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证图例修改是否生效
"""

import os
import sys

# 将项目根目录添加到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from graph_builder.service.mermaid_renderer import MermaidRenderer

def test_legend_display():
    """测试图例显示是否符合要求"""
    # 创建测试数据
    events = [
        EventItem(
            event_id="E01",
            description="测试事件1",
            characters=["角色A"],
            location="地点1"
        ),
        EventItem(
            event_id="E02",
            description="测试事件2",
            characters=["角色A", "角色B"],
            location="地点2"
        )
    ]
    
    edges = [
        CausalEdge(
            from_id="E01",
            to_id="E02",
            strength="高",
            reason="因果关系测试"
        )
    ]
    
    # 创建渲染器
    renderer = MermaidRenderer()
    
    # 渲染有图例的图表
    mermaid_content = renderer.render(
        events=events,
        edges=edges,
        format_options={"show_legend": True}
    )
    
    # 输出到文件
    output_file = "legend_test.mmd"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(mermaid_content)
    
    print(f"已生成测试图表: {output_file}")
    
    # 检查图例内容
    print("\n验证图例内容:")
    print("-" * 50)
    
    # 检查不应出现的项
    unwanted_elements = [
        "legend_high_edge",
        "legend_medium_edge", 
        "legend_low_edge",
        "legend_time_edge",
        "legend_time_connection",
    ]
    
    # 提取图例部分
    legend_start = mermaid_content.find("subgraph 图例")
    legend_end = mermaid_content.find("end", legend_start)
    if legend_start >= 0 and legend_end >= 0:
        legend_content = mermaid_content[legend_start:legend_end]
    else:
        legend_content = ""
        print("❌ 错误: 未找到图例部分")
    
    # 检查图例中是否包含连线
    if " --> " in legend_content:
        print(f"❌ 错误: 图例中不应包含连线，但找到了连线")
    else:
        print(f"✅ 通过: 图例中不包含连线")
    
    for element in unwanted_elements:
        if element in mermaid_content:
            print(f"❌ 错误: 图例中不应出现 '{element}'，但找到了该元素")
        else:
            print(f"✅ 通过: 图例中不包含 '{element}'")
    
    print("-" * 50)
    
    # 应该包含的项
    expected_elements = [
        "subgraph 图例",
        "legend_character[人物事件]",
        "legend_treasure[宝物事件]",
        "legend_conflict[冲突事件]",
        "legend_cultivation[修炼事件]"
    ]
    
    for element in expected_elements:
        if element in mermaid_content:
            print(f"✅ 通过: 图例包含 '{element}'")
        else:
            print(f"❌ 错误: 图例应该包含 '{element}'，但未找到该元素")

if __name__ == "__main__":
    test_legend_display()
