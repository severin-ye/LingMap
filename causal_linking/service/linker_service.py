#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[已弃用] 原始因果链接器实现 - 请使用 unified_linker_service.py
此文件仅为向后兼容保留，不再维护。

该类使用全事件两两配对的简单方法，时间复杂度为O(N²)
"""

import warnings

warnings.warn(
    "linker_service.py已弃用，请使用unified_linker_service.py中的UnifiedCausalLinker", 
    DeprecationWarning, 
    stacklevel=2
)

# 从统一版导入，以保持向后兼容
from .unified_linker_service import CausalLinker
