from typing import List, Dict, Any, Optional, Set
import os
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from common.interfaces.graph_renderer import AbstractGraphRenderer
from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from graph_builder.domain.base_renderer import BaseRenderer
from graph_builder.utils.color_map import ColorMap
from common.utils.parallel_config import ParallelConfig


class MermaidRenderer(BaseRenderer):
    """Mermaid图谱渲染器实现类"""
    
    def __init__(self, default_options: Dict[str, Any] = {}):
        """
        初始化Mermaid渲染器
        
        Args:
            default_options: Default rendering options
        """
        super().__init__(default_options)
        
        # TODO: Translate - Use模块特定Configure决定thread数（确保与模块特定Configure一致）
        if ParallelConfig.is_enabled():
            module_specific_workers = ParallelConfig._config["default_workers"]["graph_builder"]
            self.max_workers = module_specific_workers
        else:
            self.max_workers = 1
            
        # TODO: Translate - 记录Use的thread数
        logging.info(f"图形构建模块使用工作线程数: {self.max_workers}")
        
        # TODO: Translate - Usethread监控工具记录
        from common.utils.thread_monitor import log_thread_usage
        log_thread_usage("graph_builder", self.max_workers, "cpu_bound")
        
    def render(self, events: List[EventItem], edges: List[CausalEdge], format_options: Dict[str, Any] = {}) -> str:
        """
        将事件图谱渲染为Mermaid格式
        
        Args:
            events: 事件列表
            edges: 事件因果边列表
            format_options: 格式选项，如颜色、样式等
                - connect_isolated_nodes: 是否自动连接孤立节点，默认为True
            
        Returns:
            Mermaid格式的图谱字符串
        """
        # TODO: Translate - 合并选项
        options = {**self.default_options, **(format_options or {})}
        
        # TODO: Translate - Process重复节点ID：检测并重命名重复的节点ID
        events, edges = self._handle_duplicate_ids(events, edges)
        
        # TODO: Translate - CreateeventID到event的映射
        event_map = {event.event_id: event for event in events}
        
        # TODO: Translate - 检测并连接孤立节点
        if options.get("connect_isolated_nodes", True):  # TODO: Translate - 默认启用此功能
            edges = self._connect_isolated_nodes(events, edges)
            
        # TODO: Translate - GenerateMermaid图定义头部
        mermaid = ["```mermaid", "graph TD"]
        
        # TODO: Translate - parallelGenerate节点定义
        node_definitions = []
        
        def process_node(event):
            # TODO: Translate - Get节点颜色
            colors = ColorMap.get_node_color(
                event.description,
                event.treasures,
                event.characters
            )
            
            # TODO: Translate - 节点定义
            node_def = f'    {event.event_id}["{self._escape_text(event.description)}"]'
            
            # TODO: Translate - 节点样式
            style = f'    style {event.event_id} fill:{colors["fill"]},stroke:{colors["stroke"]}'
            
            return (node_def, style)
        
        # TODO: Translate - 从模块特定ConfigureGetthread数
        module_workers = ParallelConfig._config["default_workers"]["graph_builder"]
        actual_workers = module_workers if ParallelConfig.is_enabled() else 1
        logging.info(f"图形渲染节点处理使用线程数: {actual_workers} (模块配置: {module_workers})")
        
        # TODO: Translate - 更新实例变量，确保一致性
        self.max_workers = actual_workers
        
        # TODO: Translate - Usethread池parallelProcess节点
        with ThreadPoolExecutor(max_workers=actual_workers) as executor:
            # TODO: Translate - 提交所有任务
            future_to_event = {executor.submit(process_node, event): event for event in events}
            
            # TODO: Translate - 收集结果
            for future in as_completed(future_to_event):
                try:
                    node_def, style = future.result()
                    mermaid.append(node_def)
                    mermaid.append(style)
                except Exception as e:
                    print(f"处理节点时出错: {e}")
        
        # TODO: Translate - Generate边定义
        link_style_index = 0
        for edge in edges:
            # TODO: Translate - Get边样式
            edge_style = ColorMap.get_edge_style(edge.strength)
            
            # TODO: Translate - Create基本边
            edge_def = f'    {edge.from_id} --> {edge.to_id}'
            
            # TODO: Translate - 如果有边标签（强度或原因）
            if options.get("show_edge_labels", True) and edge.reason:
                # TODO: Translate - Use简短理由作为标签
                short_reason = self._truncate_text(edge.reason, 20)
                edge_def = f'    {edge.from_id} -->|"{short_reason}"| {edge.to_id}'
            
            # TODO: Translate - 添加边定义
            mermaid.append(edge_def)
            
            # TODO: Translate - 如果需要自定义边样式
            if options.get("custom_edge_style", True):
                # TODO: Translate - 为边分配唯一ID
                linkStyle = f'    linkStyle {link_style_index} stroke:{edge_style["stroke"]},stroke-width:{edge_style["stroke_width"]}'
                
                if edge_style["style"] == "dashed":
                    linkStyle += ",stroke-dasharray:5 5"
                
                mermaid.append(linkStyle)
                link_style_index += 1
        
        # TODO: Translate - 添加图例
        if options.get("show_legend", False):
            mermaid.extend(self._generate_legend())
        
        # TODO: Translate - EndMermaid定义
        mermaid.append("```")
        
        return "\n".join(mermaid)
    
    def _generate_legend(self) -> List[str]:
        """生成图例"""
        legend = [
            "    subgraph 图例",
            "    legend_character[人物事件]",
            "    legend_treasure[宝物事件]",
            "    legend_conflict[冲突事件]",
            "    legend_cultivation[修炼事件]",
            "    end",
            f'    style legend_character fill:{ColorMap.DEFAULT_COLORS["character"]},stroke:{ColorMap.get_node_color("", [], ["角色"])["stroke"]}',
            f'    style legend_treasure fill:{ColorMap.DEFAULT_COLORS["treasure"]},stroke:{ColorMap.get_node_color("", ["宝物"], [])["stroke"]}',
            f'    style legend_conflict fill:{ColorMap.DEFAULT_COLORS["conflict"]},stroke:{ColorMap.get_node_color("战斗", [], [])["stroke"]}',
            f'    style legend_cultivation fill:{ColorMap.DEFAULT_COLORS["cultivation"]},stroke:{ColorMap.get_node_color("修炼", [], [])["stroke"]}'
        ]
        
        return legend
    
    def _escape_text(self, text: str) -> str:
        """
        转义Mermaid文本中的特殊字符
        
        Args:
            text: 原始文本
            
        Returns:
            转义后的文本
        """
        # TODO: Translate - 转义常见特殊字符
        escaped = text.replace('"', '\\"')
        return escaped
    
    def _truncate_text(self, text: str, max_length: int = 20) -> str:
        """
        截断文本到指定长度
        
        Args:
            text: 原始文本
            max_length: 最大长度
            
        Returns:
            截断后的文本
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
        
    def _connect_isolated_nodes(self, events: List[EventItem], edges: List[CausalEdge]) -> List[CausalEdge]:
        """
        检测孤立节点并按时间顺序连接它们
        
        Args:
            events: 事件列表
            edges: 现有边列表
            
        Returns:
            更新后的边列表，包括连接孤立节点的新边
        """
        # TODO: Translate - Build节点连接图 (找出已连接节点)
        connected_nodes = set()
        for edge in edges:
            connected_nodes.add(edge.from_id)
            connected_nodes.add(edge.to_id)
            
        # TODO: Translate - Get所有节点ID
        all_node_ids = {event.event_id for event in events}
        
        # TODO: Translate - 找出孤立节点
        isolated_nodes = all_node_ids - connected_nodes
        
        if isolated_nodes:
            logging.info(f"检测到 {len(isolated_nodes)} 个孤立节点，准备按时间顺序连接")
            
            # TODO: Translate - Get所有孤立event
            isolated_events = [e for e in events if e.event_id in isolated_nodes]
            
            # TODO: Translate - 根据eventID排序，假设格式为"Echapter-序号"
            # TODO: Translate - 首先按chapter号排序，然后按序号排序
            def extract_chapter_and_sequence(event_id):
                # TODO: Translate - 假设格式为 Echapter号-序号 或 Echapter号-序号_子序号
                parts = event_id.strip('E').split('-')
                if len(parts) >= 2:
                    chapter = int(parts[0]) if parts[0].isdigit() else 0
                    # TODO: Translate - Process可能包含下划线的序号部分
                    seq_parts = parts[1].split('_')
                    sequence = int(seq_parts[0]) if seq_parts[0].isdigit() else 0
                    return (chapter, sequence)
                return (0, 0)  # TODO: Translate - 默认值
                
            # TODO: Translate - 按Extract的chapter和序号排序
            isolated_events.sort(key=lambda e: extract_chapter_and_sequence(e.event_id))
            
            # TODO: Translate - 对所有event也进行相同的排序
            all_events_sorted = sorted(events, key=lambda e: extract_chapter_and_sequence(e.event_id))
            
            # TODO: Translate - 连接孤立节点
            new_edges = []
            
            # TODO: Translate - 为每个孤立节点Create到下一个节点的边
            for event in isolated_events:
                # TODO: Translate - 找出当前event在排序后列表中的位置
                current_index = next((idx for idx, e in enumerate(all_events_sorted) if e.event_id == event.event_id), -1)
                
                # TODO: Translate - 如果找到当前event且不是最后一个event
                if current_index != -1 and current_index < len(all_events_sorted) - 1:
                    # TODO: Translate - Get下一个event
                    next_event = all_events_sorted[current_index + 1]
                    
                    # TODO: Translate - Create新边
                    new_edge = CausalEdge(
                        from_id=event.event_id,
                        to_id=next_event.event_id,
                        strength="时序",  # TODO: Translate - Use特殊的"时序"强度，表示这是时间顺序而非causal关系
                        reason="时间顺序连接"
                    )
                    
                    new_edges.append(new_edge)
                    logging.info(f"创建时间顺序连接: {event.event_id} -> {next_event.event_id}")
            
            # TODO: Translate - 添加新边到现有边列表
            edges.extend(new_edges)
            logging.info(f"添加了 {len(new_edges)} 条新边连接孤立节点")
                
        return edges
    
    def _handle_duplicate_ids(self, events: List[EventItem], edges: List[CausalEdge]) -> tuple[List[EventItem], List[CausalEdge]]:
        """
        处理重复的节点ID
        
        Args:
            events: 事件列表
            edges: 事件因果边列表
            
        Returns:
            处理后的事件列表和边列表
        """
        # TODO: Translate - Check是否有重复ID
        event_id_count = {}
        for event in events:
            if event.event_id in event_id_count:
                event_id_count[event.event_id] += 1
            else:
                event_id_count[event.event_id] = 1
        
        # TODO: Translate - 如果没有重复ID，直接Return原始数据
        if all(count == 1 for count in event_id_count.values()):
            return events, edges
        
        # TODO: Translate - Process重复ID
        id_map = {}  # TODO: Translate - 原始ID到新ID的映射
        updated_events = []
        
        for event in events:
            original_id = event.event_id
            if event_id_count[original_id] > 1:
                # TODO: Translate - 为重复IDCreate新ID (例如 E1 -> E1_1, E1_2, E1_3)
                if original_id not in id_map:
                    id_map[original_id] = []
                
                # TODO: Translate - 为当前event分配新ID
                new_id = f"{original_id}_{len(id_map[original_id]) + 1}"
                id_map[original_id].append(new_id)
                
                # TODO: Translate - Create更新后的event
                updated_event = EventItem(
                    event_id=new_id,
                    description=event.description,
                    characters=event.characters,
                    treasures=event.treasures,
                    result=event.result,
                    location=event.location,
                    time=event.time,
                    chapter_id=event.chapter_id
                )
                updated_events.append(updated_event)
            else:
                # TODO: Translate - 非重复ID，保持不变
                updated_events.append(event)
                # TODO: Translate - 添加到映射表，便于后续Process边
                if original_id not in id_map:
                    id_map[original_id] = [original_id]
        
        # TODO: Translate - 更新边的引用
        updated_edges = []
        for edge in edges:
            original_from_id = edge.from_id
            original_to_id = edge.to_id
            
            # TODO: Translate - 如果边引用了重复ID，需要Process多个可能的边
            # TODO: Translate - 这里采用简单策略：为每个可能的源节点到每个可能的目标节点Create边
            for from_id in id_map.get(original_from_id, [original_from_id]):
                for to_id in id_map.get(original_to_id, [original_to_id]):
                    updated_edge = CausalEdge(
                        from_id=from_id,
                        to_id=to_id,
                        strength=edge.strength,
                        reason=edge.reason
                    )
                    updated_edges.append(updated_edge)
        
        return updated_events, updated_edges
