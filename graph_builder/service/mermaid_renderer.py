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
            
        Returns:
            Mermaid格式的图谱字符串
        """
        # 合并选项
        options = {**self.default_options, **(format_options or {})}
        
        # 创建事件ID到事件的映射
        # 注意：现在我们假设所有节点ID已经是唯一的（由CPC模块处理）
        event_map = {event.event_id: event for event in events}
        
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
