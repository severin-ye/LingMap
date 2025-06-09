#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件对因果关系分析器
负责分析事件对之间的因果关系，包括：
1. 生成问题提示
2. 调用LLM分析因果关系
3. 解析LLM响应
"""

import os
from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor

from common.models.event import EventItem
from common.models.causal_edge import CausalEdge
from event_extraction.repository.llm_client import LLMClient


class PairAnalyzer:
    """
    事件对因果关系分析器
    负责分析事件对之间的因果关系
    """
    
    def __init__(
        self,
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: int = 3,
        provider: str = "openai"
    ):
        """
        初始化事件对分析器
        
        Args:
            model: 使用的LLM模型
            prompt_path: 提示词模板路径
            api_key: API密钥
            base_url: 自定义API基础URL
            max_workers: 并行处理的最大工作线程数
            provider: API提供商，如"openai"或"deepseek"
        """
        # 如果未提供API密钥，尝试从环境变量获取
        if not api_key:
            if provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
                if not self.api_key:
                    raise ValueError("请提供 OpenAI API 密钥")
            elif provider == "deepseek":
                self.api_key = os.environ.get("DEEPSEEK_API_KEY")
                if not self.api_key:
                    raise ValueError("请提供 DeepSeek API 密钥")
            else:
                raise ValueError(f"不支持的 API 提供商: {provider}")
        else:
            self.api_key = api_key
            
        self.model = model
        self.base_url = base_url
        self.max_workers = max_workers
        self.provider = provider
        self.prompt_path = prompt_path
        
        # 加载提示模板
        self.prompt_template = self._load_prompt_template(prompt_path)
        
        # 初始化LLM客户端
        self.llm_client = LLMClient(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            provider=self.provider
        )
    
    def _load_prompt_template(self, prompt_path: str) -> Dict[str, str]:
        """
        加载提示模板
        
        Args:
            prompt_path: 提示模板文件路径
            
        Returns:
            提示模板字典
        """
        import json
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"加载提示模板失败: {e}")
            return {
                "system": "你是一个因果关系分析助手，你需要分析两个事件之间是否存在因果关系。",
                "instruction": "请分析以下两个事件之间是否存在因果关系:\n\n事件1: {event1}\n\n事件2: {event2}\n\n请以JSON格式回答，包含以下字段:\n- has_causal_relation: 布尔值，表示是否存在因果关系\n- direction: 如果存在因果关系，请指明方向(事件1→事件2 或 事件2→事件1)\n- strength: 因果关系强度(高/中/低)\n- reason: 关系存在的理由或不存在的解释"
            }
    
    def analyze_batch(self, event_pairs: List[Tuple[EventItem, EventItem]]) -> List[CausalEdge]:
        """
        批量分析事件对因果关系
        
        Args:
            event_pairs: 事件对列表
            
        Returns:
            因果边列表
        """
        edges = []
        
        # 使用线程池并行处理事件对
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for event1, event2 in event_pairs:
                future = executor.submit(self.analyze_pair, event1, event2)
                futures.append(future)
            
            # 收集所有结果
            for future in futures:
                edge = future.result()
                if edge:
                    edges.append(edge)
        
        return edges
    
    def analyze_pair(self, event1: EventItem, event2: EventItem) -> Optional[CausalEdge]:
        """
        分析一对事件的因果关系
        
        Args:
            event1: 第一个事件
            event2: 第二个事件
            
        Returns:
            因果边对象，如果不存在因果关系则返回None
        """
        # 格式化提示
        prompt = self.format_prompt(event1, event2)
        
        # 调用LLM
        response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
        
        if not response["success"] or "json_content" not in response:
            print(f"事件 {event1.event_id} 和 {event2.event_id} 的因果分析失败: {response.get('error', '未知错误')}")
            return None
            
        # 解析响应
        edge = self.parse_response(response["json_content"], event1.event_id, event2.event_id)
        
        if edge:
            print(f"发现因果关系: {edge.from_id} -> {edge.to_id}, 强度: {edge.strength}")
            
        return edge
    
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
    
    def parse_response(self, response: Dict[str, Any], event1_id: str, event2_id: str) -> Optional[CausalEdge]:
        """
        解析LLM响应，提取因果关系
        
        Args:
            response: LLM响应
            event1_id: 第一个事件ID
            event2_id: 第二个事件ID
            
        Returns:
            因果边对象，如果不存在因果关系则返回None
        """
        # 检查是否存在因果关系
        has_causal = response.get("has_causal_relation", False)
        if not has_causal:
            return None
        
        # 获取因果方向
        direction = response.get("direction", "")
        
        if direction == "event1->event2":
            from_id = event1_id
            to_id = event2_id
        elif direction == "event2->event1":
            from_id = event2_id
            to_id = event1_id
        else:
            print(f"无法解析因果方向: {direction}")
            return None
        
        # 获取因果强度和理由
        strength = response.get("strength", "中")
        reason = response.get("reason", "")
        
        return CausalEdge(
            from_id=from_id,
            to_id=to_id,
            strength=strength,
            reason=reason
        )
