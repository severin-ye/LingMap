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
            default_options: 默认渲染选项
        """
        super().__init__(default_options)
        
        # 使用模块特定配置决定线程数（确保与模块特定配置一致）
        if ParallelConfig.is_enabled():
            module_specific_workers = ParallelConfig._config["default_workers"]["graph_builder"]
            self.max_workers = module_specific_workers
        else:
            self.max_workers = 1
            
        # 记录使用的线程数
        logging.info(f"图形构建模块使用工作线程数: {self.max_workers}")
        
        # 使用线程监控工具记录
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
        # 合并选项
        options = {**self.default_options, **(format_options or {})}
        
        # 创建事件ID到事件的映射
        # 注意：现在我们假设所有节点ID已经是唯一的（由CPC模块处理）
        event_map = {event.event_id: event for event in events}
        
        # 检测并连接孤立节点
        if options.get("connect_isolated_nodes", True):  # 默认启用此功能
            edges = self._connect_isolated_nodes(events, edges)
            
        # 生成Mermaid图定义头部
        mermaid = ["```mermaid", "graph TD"]
        
        # 并行生成节点定义
        node_definitions = []
        
        def process_node(event):
            # 获取节点颜色
            colors = ColorMap.get_node_color(
                event.description,
                event.treasures,
                event.characters
            )
            
            # 节点定义
            node_def = f'    {event.event_id}["{self._escape_text(event.description)}"]'
            
            # 节点样式
            style = f'    style {event.event_id} fill:{colors["fill"]},stroke:{colors["stroke"]}'
            
            return (node_def, style)
        
        # 从模块特定配置获取线程数
        module_workers = ParallelConfig._config["default_workers"]["graph_builder"]
        actual_workers = module_workers if ParallelConfig.is_enabled() else 1
        logging.info(f"图形渲染节点处理使用线程数: {actual_workers} (模块配置: {module_workers})")
        
        # 更新实例变量，确保一致性
        self.max_workers = actual_workers
        
        # 使用线程池并行处理节点
        with ThreadPoolExecutor(max_workers=actual_workers) as executor:
            # 提交所有任务
            future_to_event = {executor.submit(process_node, event): event for event in events}
            
            # 收集结果
            for future in as_completed(future_to_event):
                try:
                    node_def, style = future.result()
                    mermaid.append(node_def)
                    mermaid.append(style)
                except Exception as e:
                    print(f"处理节点时出错: {e}")
        
        # 生成边定义
        link_style_index = 0
        for edge in edges:
            # 获取边样式
            edge_style = ColorMap.get_edge_style(edge.strength)
            
            # 创建基本边
            edge_def = f'    {edge.from_id} --> {edge.to_id}'
            
            # 如果有边标签（强度或原因）
            if options.get("show_edge_labels", True) and edge.reason:
                # 使用简短理由作为标签
                short_reason = self._truncate_text(edge.reason, 20)
                edge_def = f'    {edge.from_id} -->|"{short_reason}"| {edge.to_id}'
            
            # 添加边定义
            mermaid.append(edge_def)
            
            # 如果需要自定义边样式
            if options.get("custom_edge_style", True):
                # 为边分配唯一ID
                linkStyle = f'    linkStyle {link_style_index} stroke:{edge_style["stroke"]},stroke-width:{edge_style["stroke_width"]}'
                
                if edge_style["style"] == "dashed":
                    linkStyle += ",stroke-dasharray:5 5"
                
                mermaid.append(linkStyle)
                link_style_index += 1
        
        # 添加图例
        if options.get("show_legend", False):
            mermaid.extend(self._generate_legend())
        
        # 结束Mermaid定义
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
            "    legend_time_connection[时序连接]",
            "    end",
            f'    style legend_character fill:{ColorMap.DEFAULT_COLORS["character"]},stroke:{ColorMap.get_node_color("", [], ["角色"])["stroke"]}',
            f'    style legend_treasure fill:{ColorMap.DEFAULT_COLORS["treasure"]},stroke:{ColorMap.get_node_color("", ["宝物"], [])["stroke"]}',
            f'    style legend_conflict fill:{ColorMap.DEFAULT_COLORS["conflict"]},stroke:{ColorMap.get_node_color("战斗", [], [])["stroke"]}',
            f'    style legend_cultivation fill:{ColorMap.DEFAULT_COLORS["cultivation"]},stroke:{ColorMap.get_node_color("修炼", [], [])["stroke"]}'
        ]
        
        # 添加边的图例
        edge_index = 0
        
        # 高强度边的图例
        legend.append(f'    legend_high_edge[高强度因果] --> legend_medium_edge[中强度因果]')
        high_edge_style = ColorMap.get_edge_style("高")
        legend.append(f'    linkStyle {edge_index} stroke:{high_edge_style["stroke"]},stroke-width:{high_edge_style["stroke_width"]}')
        edge_index += 1
        
        # 低强度边的图例
        legend.append(f'    legend_medium_edge --> legend_low_edge[低强度因果]')
        medium_edge_style = ColorMap.get_edge_style("中")
        legend.append(f'    linkStyle {edge_index} stroke:{medium_edge_style["stroke"]},stroke-width:{medium_edge_style["stroke_width"]}')
        edge_index += 1
        
        # 添加时序连接边的图例
        legend.append(f'    legend_low_edge --> legend_time_edge[时序连接]')
        low_edge_style = ColorMap.get_edge_style("低")
        legend.append(f'    linkStyle {edge_index} stroke:{low_edge_style["stroke"]},stroke-width:{low_edge_style["stroke_width"]},stroke-dasharray:5 5')
        edge_index += 1
        
        # 时序连接边的图例
        legend.append(f'    legend_time_edge --> legend_time_connection')
        time_edge_style = ColorMap.get_edge_style("时序")
        legend.append(f'    linkStyle {edge_index} stroke:{time_edge_style["stroke"]},stroke-width:{time_edge_style["stroke_width"]},stroke-dasharray:5 5')
        
        return legend
    
    def _escape_text(self, text: str) -> str:
        """
        转义Mermaid文本中的特殊字符
        
        Args:
            text: 原始文本
            
        Returns:
            转义后的文本
        """
        # 转义常见特殊字符
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
        # 构建节点连接图 (找出已连接节点)
        connected_nodes = set()
        for edge in edges:
            connected_nodes.add(edge.from_id)
            connected_nodes.add(edge.to_id)
            
        # 获取所有节点ID
        all_node_ids = {event.event_id for event in events}
        
        # 找出孤立节点
        isolated_nodes = all_node_ids - connected_nodes
        
        if isolated_nodes:
            logging.info(f"检测到 {len(isolated_nodes)} 个孤立节点，准备按时间顺序连接")
            
            # 获取所有孤立事件
            isolated_events = [e for e in events if e.event_id in isolated_nodes]
            
            # 根据事件ID排序，假设格式为"E章节-序号"
            # 首先按章节号排序，然后按序号排序
            def extract_chapter_and_sequence(event_id):
                # 假设格式为 E章节号-序号 或 E章节号-序号_子序号
                parts = event_id.strip('E').split('-')
                if len(parts) >= 2:
                    chapter = int(parts[0]) if parts[0].isdigit() else 0
                    # 处理可能包含下划线的序号部分
                    seq_parts = parts[1].split('_')
                    sequence = int(seq_parts[0]) if seq_parts[0].isdigit() else 0
                    return (chapter, sequence)
                return (0, 0)  # 默认值
                
            # 按提取的章节和序号排序
            isolated_events.sort(key=lambda e: extract_chapter_and_sequence(e.event_id))
            
            # 对所有事件也进行相同的排序
            all_events_sorted = sorted(events, key=lambda e: extract_chapter_and_sequence(e.event_id))
            
            # 连接孤立节点
            new_edges = []
            
            # 为每个孤立节点创建到下一个节点的边
            for event in isolated_events:
                # 找出当前事件在排序后列表中的位置
                current_index = next((idx for idx, e in enumerate(all_events_sorted) if e.event_id == event.event_id), -1)
                
                # 如果找到当前事件且不是最后一个事件
                if current_index != -1 and current_index < len(all_events_sorted) - 1:
                    # 获取下一个事件
                    next_event = all_events_sorted[current_index + 1]
                    
                    # 创建新边
                    new_edge = CausalEdge(
                        from_id=event.event_id,
                        to_id=next_event.event_id,
                        strength="时序",  # 使用特殊的"时序"强度，表示这是时间顺序而非因果关系
                        reason="时间顺序连接"
                    )
                    
                    new_edges.append(new_edge)
                    logging.info(f"创建时间顺序连接: {event.event_id} -> {next_event.event_id}")
            
            # 添加新边到现有边列表
            edges.extend(new_edges)
            logging.info(f"添加了 {len(new_edges)} 条新边连接孤立节点")
                
        return edges
