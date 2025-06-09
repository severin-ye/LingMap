#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础因果链接器
实现基本的因果链接器功能，这个模块将被统一链接器继承使用
"""

import json
import os
from typing import Dict, Any, List, Tuple

from common.interfaces.linker import AbstractLinker
from common.models.causal_edge import CausalEdge
from common.models.event import EventItem


class BaseLinker(AbstractLinker):
    """
    基础因果链接器
    提供基础的提示模板加载和接口实现
    """
    
    def __init__(self, prompt_path: str = ""):
        """
        初始化基础链接器
        
        Args:
            prompt_path: 提示词模板路径
        """
        self.prompt_path = prompt_path
        
        # 加载提示词模板
        if prompt_path and os.path.exists(prompt_path):
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    self.prompt_template = json.load(f)
            except json.JSONDecodeError:
                print(f"警告: 无法解析提示词模板 {prompt_path}，将使用默认模板")
                self._init_default_prompt_template()
        else:
            self._init_default_prompt_template()
    
    def _init_default_prompt_template(self):
        """初始化默认提示词模板"""
        self.prompt_template = {
            "system": "你是一个因果关系分析助手，你需要分析两个事件之间是否存在因果关系。",
            "instruction": "请分析以下两个事件之间是否存在因果关系:\n\n事件1: {event1}\n\n事件2: {event2}\n\n请以JSON格式回答，包含以下字段:\n- has_causal_relation: 布尔值，表示是否存在因果关系\n- direction: 如果存在因果关系，请指明方向(事件1→事件2 或 事件2→事件1)\n- strength: 因果关系强度(高/中/低)\n- reason: 关系存在的理由或不存在的解释"
        }
    
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        """
        识别事件之间的因果关系
        
        Args:
            events: 事件列表
            
        Returns:
            事件因果边列表
            
        Note:
            这是AbstractLinker接口的实现，但在基础类中是空实现
            子类需要覆盖此方法提供具体实现
        """
        raise NotImplementedError("子类必须实现link_events方法")
    
    def build_dag(self, events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        构建有向无环图（DAG）
        
        Args:
            events: 事件列表
            edges: 因果边列表
            
        Returns:
            处理后的事件列表和因果边列表
            
        Note:
            这是AbstractLinker接口的实现，但在基础类中是空实现
            子类需要覆盖此方法提供具体实现
        """
        raise NotImplementedError("子类必须实现build_dag方法")
    
    def format_prompt(self, event1: EventItem, event2: EventItem) -> Dict[str, str]:
        """
        格式化提示词
        
        Args:
            event1: 第一个事件
            event2: 第二个事件
            
        Returns:
            格式化后的提示词字典，包含system和instruction
        """
        # 格式化事件1描述
        event1_desc = f"""
事件ID: {event1.event_id}
描述: {event1.description}
相关角色: {', '.join(event1.characters) if event1.characters else '无'}
相关宝物: {', '.join(event1.treasures) if event1.treasures else '无'}
发生地点: {event1.location or '未知'}
章节: {event1.chapter_id or '未知'}
结果: {event1.result or '未知'}
        """.strip()
        
        # 格式化事件2描述
        event2_desc = f"""
事件ID: {event2.event_id}
描述: {event2.description}
相关角色: {', '.join(event2.characters) if event2.characters else '无'}
相关宝物: {', '.join(event2.treasures) if event2.treasures else '无'}
发生地点: {event2.location or '未知'}
章节: {event2.chapter_id or '未知'}
结果: {event2.result or '未知'}
        """.strip()
        
        # 从模板中获取系统提示和指令
        system_prompt = self.prompt_template.get("system", "")
        instruction = self.prompt_template.get("instruction", "").format(
            event1=event1_desc,
            event2=event2_desc
        )
        
        return {
            "system": system_prompt,
            "instruction": instruction
        }
