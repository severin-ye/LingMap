from typing import Dict, Any, List, Optional


class ColorMap:
    """Tool class for assigning colors to event nodes"""
    
    DEFAULT_COLORS = {
        "default": "#CCCCCC",  # Default color
        "character": "#BDE5F8",  # Character-related event color
        "treasure": "#FDF6B2",  # Treasure-related event color
        "conflict": "#FCDCDC",  # Conflict event color
        "cultivation": "#D5F5E3",  # Cultivation-related event color
    }
    
    @staticmethod
    def get_node_color(event_description: str, treasures: List[str], characters: List[str]) -> Dict[str, str]:
        """
        Get node color based on event content
        
        Args:
            event_description: Event description
            treasures: List of involved treasures
            characters: List of involved characters
            
        Returns:
            Dictionary of fill and border colors
        """
        conflict_keywords = ["battle", "conflict", "attack", "fight", "kill", "chase", "combat", "escape", "crisis", "ambush"]
        cultivation_keywords = ["cultivate", "breakthrough", "practice", "foundation", "core_formation", "nascent_soul", "spell", "technique", "cultivation_level", "spiritual_power"]
        
        # Check event type
        has_treasure = len(treasures) > 0
        has_conflict = any(keyword in event_description for keyword in conflict_keywords)
        has_cultivation = any(keyword in event_description for keyword in cultivation_keywords)
        
        # Determine color type
        if has_conflict:
            fill_color = ColorMap.DEFAULT_COLORS["conflict"]
            stroke_color = "#C74343"  # Conflict border color
        elif has_treasure:
            fill_color = ColorMap.DEFAULT_COLORS["treasure"]
            stroke_color = "#C19400"  # Treasure border color
        elif has_cultivation:
            fill_color = ColorMap.DEFAULT_COLORS["cultivation"]
            stroke_color = "#1E8449"  # Cultivation border color
        elif len(characters) > 0:
            fill_color = ColorMap.DEFAULT_COLORS["character"]
            stroke_color = "#2C82C9"  # Character border color
        else:
            fill_color = ColorMap.DEFAULT_COLORS["default"]
            stroke_color = "#999999"  # Default border color
            
        return {
            "fill": fill_color,
            "stroke": stroke_color
        }
        
    @staticmethod
    def get_edge_style(strength: str) -> Dict[str, str]:
        """
        Get edge style based on causal strength
        
        Args:
            strength: Causal strength (high/medium/low/temporal)
            
        Returns:
            Edge style dictionary
        """
        if strength == "高" or strength == "high":
            return {
                "stroke": "#2471A3",
                "stroke_width": "2px",
                "style": "normal"
            }
        elif strength == "中" or strength == "medium":
            return {
                "stroke": "#5499C7",
                "stroke_width": "1.5px",
                "style": "normal"
            }
        elif strength == "时序" or strength == "temporal":
            # Add special style for temporal relationships, use green dashed line
            return {
                "stroke": "#27AE60",  # Green
                "stroke_width": "1px",
                "style": "dashed"
            }
        else:  # Low intensity
            return {
                "stroke": "#7FB3D5",
                "stroke_width": "1px",
                "style": "dashed"
            }
