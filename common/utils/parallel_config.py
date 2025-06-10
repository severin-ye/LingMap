#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并行处理配置模块

提供全局并行处理配置，用于控制系统中的多线程并行处理行为。
支持从配置文件加载配置，确保系统中使用统一的线程数。
"""

import os
import json
import multiprocessing
from typing import Dict, Any, Optional
from pathlib import Path


class ParallelConfig:
    """
    并行处理配置类
    
    负责管理系统中的并行处理配置，包括是否启用并行、线程数量等。
    所有模块使用同一份配置，确保线程数的一致性。
    """
    
    # 默认配置
    _config = {
        "enabled": True,  # 默认启用并行处理
        "description": "是否启用并行处理，设置为false时所有模块将使用单线程",
        "max_workers": None,  # 自动设置工作线程数
        "max_workers_description": "全局默认最大工作线程数，通常设置为CPU核心数或略高于核心数",
        "adaptive": {
            "enabled": True,  # 是否启用自适应调整
            "enabled_description": "是否启用自适应线程分配，根据任务类型动态调整线程数",
            "io_bound_factor": 1.5,  # IO密集型任务的线程数因子
            "io_bound_factor_description": "IO密集型任务（如API调用）的线程系数，通常设置>1",
            "cpu_bound_factor": 0.8,  # CPU密集型任务的线程数因子
            "cpu_bound_factor_description": "CPU密集型任务（如图形渲染）的线程系数，通常设置<1"
        },
        "default_workers": {  # 各模块默认线程数
            "event_extraction": None,
            "event_extraction_description": "事件抽取：IO密集型任务，API调用多，适合较多线程",
            "hallucination_refine": None,
            "hallucination_refine_description": "幻觉修复：IO密集型任务，API调用多，适合较多线程",
            "causal_linking": None,
            "causal_linking_description": "因果链接：混合型任务，既有计算也有API调用，使用标准线程数",
            "graph_builder": None,
            "graph_builder_description": "图形构建：CPU密集型任务，主要是计算和渲染，适合较少线程"
        },
        "default_workers_description": "各模块的默认线程数，可以覆盖全局设置"
    }
    
    @classmethod
    def initialize(cls, options: Dict[str, Any] = None) -> None:
        """
        初始化并行处理配置
        
        Args:
            options: 配置选项，包括:
                - enabled: 是否启用并行处理
                - max_workers: 最大工作线程数
                - adaptive: 自适应调整配置
                - default_workers: 各模块默认线程数
        """
        if options is None:
            options = {}
            
        # 首先尝试从配置文件加载
        config_loaded = cls._load_from_config_file()
        
        # 检查环境变量
        env_enabled = os.environ.get("PARALLEL_ENABLED", "").lower()
        if env_enabled in ["false", "0", "no"]:
            cls._config["enabled"] = False
        elif env_enabled in ["true", "1", "yes"]:
            cls._config["enabled"] = True
            
        # 环境变量中的线程配置（覆盖配置文件）
        env_workers = os.environ.get("MAX_WORKERS")
        if env_workers and env_workers.isdigit():
            cls._config["max_workers"] = int(env_workers)
            
        # 参数覆盖环境变量和配置文件
        if "enabled" in options:
            cls._config["enabled"] = bool(options["enabled"])
        if "max_workers" in options:
            cls._config["max_workers"] = options["max_workers"]
        if "adaptive" in options:
            if isinstance(options["adaptive"], dict):
                for key, value in options["adaptive"].items():
                    if key in cls._config["adaptive"]:
                        cls._config["adaptive"][key] = value
            elif isinstance(options["adaptive"], bool):
                cls._config["adaptive"]["enabled"] = options["adaptive"]
                
        # 如果未指定线程数，根据CPU核心数设置
        if cls._config["max_workers"] is None and cls._config["enabled"]:
            cpu_count = multiprocessing.cpu_count()
            # 默认使用CPU核心数，但设置上下限
            cls._config["max_workers"] = max(2, min(16, cpu_count))
            
        # 设置各模块的工作线程数为统一配置
        for module in cls._config["default_workers"]:
            if cls._config["default_workers"][module] is None:
                cls._config["default_workers"][module] = cls._config["max_workers"]
            
        # 如果禁用并行处理，强制设置线程数为1
        if not cls._config["enabled"]:
            cls._config["max_workers"] = 1
            for module in cls._config["default_workers"]:
                cls._config["default_workers"][module] = 1
    
    @classmethod
    def _load_from_config_file(cls) -> bool:
        """
        从配置文件加载并行配置
        
        Returns:
            是否成功加载配置
        """
        # 尝试找到配置文件路径
        try:
            from common.utils.path_utils import get_config_path
            config_file = get_config_path("parallel_config.json")
        except ImportError:
            # 如果找不到path_utils，尝试直接查找配置文件
            current_dir = Path(__file__).parent.absolute()
            project_root = current_dir.parent.parent.parent
            config_file = project_root / "common" / "config" / "parallel_config.json"
            
        if not os.path.exists(config_file):
            return False
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # 解析配置数据
            if "parallel" in config_data:
                parallel_config = config_data["parallel"]
                
                # 基本配置
                if "enabled" in parallel_config:
                    cls._config["enabled"] = bool(parallel_config["enabled"])
                if "max_workers" in parallel_config:
                    cls._config["max_workers"] = int(parallel_config["max_workers"])
                    
                # 自适应配置
                if "adaptive" in parallel_config and isinstance(parallel_config["adaptive"], dict):
                    for key, value in parallel_config["adaptive"].items():
                        if key in cls._config["adaptive"] or key == "enabled":
                            cls._config["adaptive"][key] = value
                            
                # 各模块默认线程数
                if "default_workers" in parallel_config and isinstance(parallel_config["default_workers"], dict):
                    for module, workers in parallel_config["default_workers"].items():
                        if module in cls._config["default_workers"]:
                            cls._config["default_workers"][module] = workers
                
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载并行配置文件失败: {e}")
            return False
    
    @classmethod
    def is_enabled(cls) -> bool:
        """
        检查是否启用并行处理
        
        Returns:
            是否启用并行处理
        """
        return cls._config["enabled"]
    
    @classmethod
    def get_max_workers(cls, task_type: str = "default") -> int:
        """
        获取最大工作线程数
        
        Args:
            task_type: 任务类型，可用于针对不同任务调整线程数
            
        Returns:
            最大工作线程数
        """
        if not cls._config["enabled"]:
            return 1
            
        max_workers = cls._config["max_workers"]
        
        # 针对特定任务类型的调整
        if cls._config["adaptive"]:
            if task_type == "io_bound":
                # IO密集型任务可以使用更多线程
                return max(4, max_workers)
            elif task_type == "cpu_bound":
                # CPU密集型任务限制线程数
                return min(max_workers, max(2, multiprocessing.cpu_count() - 1))
        
        return max_workers
    
    @classmethod
    def set_enabled(cls, enabled: bool) -> None:
        """
        设置是否启用并行处理
        
        Args:
            enabled: 是否启用
        """
        cls._config["enabled"] = enabled
        if not enabled:
            cls._config["max_workers"] = 1
    
    @classmethod
    def set_max_workers(cls, max_workers: int) -> None:
        """
        设置最大工作线程数
        
        Args:
            max_workers: 最大线程数
        """
        cls._config["max_workers"] = max(1, max_workers)
    
    @classmethod
    def get_optimal_batch_size(cls, total_items: int, task_type: str = "default") -> int:
        """
        计算最优批处理大小
        
        Args:
            total_items: 总项目数
            task_type: 任务类型
            
        Returns:
            最优批处理大小
        """
        max_workers = cls.get_max_workers(task_type)
        
        if max_workers <= 1 or total_items <= max_workers:
            return total_items
            
        # 计算每个工作线程处理的项目数
        items_per_worker = max(1, (total_items + max_workers - 1) // max_workers)
        
        # 返回合理的批处理大小
        return items_per_worker
    
    @classmethod
    def get_description(cls, key: str) -> Optional[str]:
        """
        获取配置项的描述信息
        
        Args:
            key: 配置项的键
            
        Returns:
            配置项的描述信息
        """
        keys = key.split(".")
        config = cls._config
        
        for k in keys:
            if k in config and isinstance(config[k], dict):
                config = config[k]
            else:
                return None
            
        return config.get("description")
