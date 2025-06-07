from typing import List, Dict, Any, Optional, Tuple, Set
import os
import json
from concurrent.futures import ThreadPoolExecutor
import itertools

from common.interfaces.linker import AbstractLinker
from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from causal_linking.domain.base_linker import BaseLinker
from event_extraction.repository.llm_client import LLMClient


class CausalLinker(BaseLinker):
    """因果链接器实现类，识别事件之间的因果关系并构建DAG"""
    
    def __init__(
        self,
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: int = 3,
        strength_mapping: Dict[str, int] = {},
        provider: str = "openai"
    ):
        """
        初始化因果链接器
        
        Args:
            model: 使用的LLM模型
            prompt_path: 提示词模板路径
            api_key: OpenAI API密钥
            base_url: 自定义API基础URL
            max_workers: 并行处理的最大工作线程数
            strength_mapping: 因果强度映射，用于权重比较
        """
        if not prompt_path:
            # 导入path_utils获取配置文件路径
            from common.utils.path_utils import get_config_path
            prompt_path = get_config_path("prompt_causal_linking.json")
            
        super().__init__(prompt_path)
        
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
        
        # 设置强度映射
        self.strength_mapping = strength_mapping or {
            "高": 3,
            "中": 2,
            "低": 1
        }
        
        # 初始化LLM客户端
        self.llm_client = LLMClient(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            provider=self.provider
        )
    
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        """
        识别事件之间的因果关系
        
        Args:
            events: 事件列表
            
        Returns:
            事件因果边列表
        """
        # 创建事件对组合
        event_pairs = list(itertools.combinations(events, 2))
        print(f"分析 {len(event_pairs)} 对事件的因果关系...")
        
        edges = []
        
        # 使用线程池并行处理事件对
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for event1, event2 in event_pairs:
                future = executor.submit(self.analyze_causal_relation, event1, event2)
                futures.append(future)
            
            # 收集所有结果
            for future in futures:
                edge = future.result()
                if edge:
                    edges.append(edge)
        
        print(f"发现 {len(edges)} 个因果关系")
        return edges
    
    def analyze_causal_relation(self, event1: EventItem, event2: EventItem) -> Optional[CausalEdge]:
        """
        分析两个事件之间的因果关系
        
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
    
    def build_dag(self, events: List[EventItem], edges: List[CausalEdge]) -> Tuple[List[EventItem], List[CausalEdge]]:
        """
        构建有向无环图（DAG）
        
        Args:
            events: 事件列表
            edges: 因果边列表
            
        Returns:
            处理后的事件列表和因果边列表
        """
        # 创建事件ID到索引的映射
        event_map = {event.event_id: i for i, event in enumerate(events)}
        
        # 按强度降序排序边
        sorted_edges = sorted(
            edges,
            key=lambda e: self.strength_mapping.get(e.strength, 0),
            reverse=True
        )
        
        # 创建邻接表表示的图
        graph = [[] for _ in range(len(events))]
        
        # 保留的边列表
        dag_edges = []
        
        # 记录已经添加的边，避免重复
        added_edges = set()
        
        # 遍历排序后的边，贪心构建DAG
        for edge in sorted_edges:
            # 检查事件是否在映射中
            if edge.from_id not in event_map or edge.to_id not in event_map:
                continue
                
            from_idx = event_map[edge.from_id]
            to_idx = event_map[edge.to_id]
            
            # 检查是否已添加相同的边
            edge_key = (from_idx, to_idx)
            if edge_key in added_edges:
                continue
                
            # 检查添加这条边是否会形成环
            if not self._will_form_cycle(graph, from_idx, to_idx):
                # 添加边到图中
                graph[from_idx].append(to_idx)
                added_edges.add(edge_key)
                dag_edges.append(edge)
        
        print(f"构建DAG完成，保留 {len(dag_edges)} 条边，移除 {len(edges) - len(dag_edges)} 条边")
        return events, dag_edges
    
    def _will_form_cycle(self, graph: List[List[int]], from_idx: int, to_idx: int) -> bool:
        """
        检查添加边是否会形成环
        
        Args:
            graph: 当前图的邻接表
            from_idx: 边的起始节点索引
            to_idx: 边的终止节点索引
            
        Returns:
            如果会形成环则返回True，否则返回False
        """
        # 如果to_idx已经可以到达from_idx，添加边会形成环
        return self._is_reachable(graph, to_idx, from_idx, set())
    
    def _is_reachable(self, graph: List[List[int]], start: int, end: int, visited: Set[int]) -> bool:
        """
        检查在图中是否存在从start到end的路径
        
        Args:
            graph: 图的邻接表
            start: 起始节点索引
            end: 目标节点索引
            visited: 已访问节点集合
            
        Returns:
            如果存在路径则返回True，否则返回False
        """
        if start == end:
            return True
            
        visited.add(start)
        
        for neighbor in graph[start]:
            if neighbor not in visited and self._is_reachable(graph, neighbor, end, visited):
                return True
                
        return False
