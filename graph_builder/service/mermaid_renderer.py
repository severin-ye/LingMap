from typing import List, Dict, Any, Optional
import os

from common.interfaces.graph_renderer import AbstractGraphRenderer
from common.models.causal_edge import CausalEdge
from common.models.event import EventItem
from graph_builder.domain.base_renderer import BaseRenderer
from graph_builder.utils.color_map import ColorMap


class MermaidRenderer(BaseRenderer):
    """Mermaid图谱渲染器实现类"""
    
    def __init__(self, default_options: Dict[str, Any] = None):
        """
        初始化Mermaid渲染器
        
        Args:
            default_options: 默认渲染选项
        """
        super().__init__(default_options)
        
    def render(self, events: List[EventItem], edges: List[CausalEdge], format_options: Dict[str, Any] = None) -> str:
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
        event_map = {event.event_id: event for event in events}
        
        # 生成Mermaid图定义头部
        mermaid = ["```mermaid", "graph TD"]
        
        # 生成节点定义
        for event in events:
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
            
            mermaid.append(node_def)
            mermaid.append(style)
        
        # 生成边定义
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
                edge_id = f"edge_{edge.from_id}_{edge.to_id}"
                linkStyle = f'    linkStyle {len(mermaid) - len(events) * 2 - 3} stroke:{edge_style["stroke"]},stroke-width:{edge_style["stroke_width"]}'
                
                if edge_style["style"] == "dashed":
                    linkStyle += ",stroke-dasharray:5 5"
                
                mermaid.append(linkStyle)
        
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
