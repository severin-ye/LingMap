#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[已弃用] 优化版因果链接器实现 - 请使用 unified_linker_service.py
此文件仅为向后兼容保留，不再维护。

采用"两条路径，合并汇流"策略：
1. 方法一：同章节事件配对
2. 方法二：实体共现跨章配对
3. 合并配对结果，去重
4. 送入LLM进行因果关系分析

降低整体时间复杂度，从O(N²)降低到O(N·avg_m²) + O(E × k²)
"""

import warnings

warnings.warn(
    "optimized_linker_service.py已弃用，请使用unified_linker_service.py中的UnifiedCausalLinker", 
    DeprecationWarning, 
    stacklevel=2
)

# 从统一版导入，以保持向后兼容
from .unified_linker_service import OptimizedCausalLinker
