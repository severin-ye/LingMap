from typing import Dict, Any, List, Optional


class ColorMap:
    """为事件节点分配颜色的工具类"""
    
    DEFAULT_COLORS = {
        "default": "#CCCCCC",  # 默认颜色
        "character": "#BDE5F8",  # 角色相关事件颜色
        "treasure": "#FDF6B2",  # 宝物相关事件颜色
        "conflict": "#FCDCDC",  # 冲突事件颜色
        "cultivation": "#D5F5E3",  # 修炼相关事件颜色
    }
    
    @staticmethod
    def get_node_color(event_description: str, treasures: List[str], characters: List[str]) -> Dict[str, str]:
        """
        根据事件内容获取节点颜色
        
        Args:
            event_description: 事件描述
            treasures: 涉及的宝物列表
            characters: 涉及的角色列表
            
        Returns:
            填充和边框颜色字典
        """
        conflict_keywords = ["战斗", "冲突", "攻击", "战", "杀", "追杀", "对战", "逃", "危机", "暗算"]
        cultivation_keywords = ["修炼", "突破", "练功", "筑基", "结丹", "元婴", "法术", "功法", "修为", "灵力"]
        
        # 检查事件类型
        has_treasure = len(treasures) > 0
        has_conflict = any(keyword in event_description for keyword in conflict_keywords)
        has_cultivation = any(keyword in event_description for keyword in cultivation_keywords)
        
        # 决定颜色类型
        if has_conflict:
            fill_color = ColorMap.DEFAULT_COLORS["conflict"]
            stroke_color = "#C74343"  # 冲突边框色
        elif has_treasure:
            fill_color = ColorMap.DEFAULT_COLORS["treasure"]
            stroke_color = "#C19400"  # 宝物边框色
        elif has_cultivation:
            fill_color = ColorMap.DEFAULT_COLORS["cultivation"]
            stroke_color = "#1E8449"  # 修炼边框色
        elif len(characters) > 0:
            fill_color = ColorMap.DEFAULT_COLORS["character"]
            stroke_color = "#2C82C9"  # 角色边框色
        else:
            fill_color = ColorMap.DEFAULT_COLORS["default"]
            stroke_color = "#999999"  # 默认边框色
            
        return {
            "fill": fill_color,
            "stroke": stroke_color
        }
        
    @staticmethod
    def get_edge_style(strength: str) -> Dict[str, str]:
        """
        根据因果强度获取边样式
        
        Args:
            strength: 因果强度（高/中/低/时序）
            
        Returns:
            边样式字典
        """
        if strength == "高":
            return {
                "stroke": "#2471A3",
                "stroke_width": "2px",
                "style": "normal"
            }
        elif strength == "中":
            return {
                "stroke": "#5499C7",
                "stroke_width": "1.5px",
                "style": "normal"
            }
        elif strength == "时序":
            # 为时序关系添加特殊样式，使用绿色虚线
            return {
                "stroke": "#27AE60",  # 绿色
                "stroke_width": "1px",
                "style": "dashed"
            }
        else:  # 低强度
            return {
                "stroke": "#7FB3D5",
                "stroke_width": "1px",
                "style": "dashed"
            }
