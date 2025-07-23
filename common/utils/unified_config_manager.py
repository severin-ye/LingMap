#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一配置管理系统
提供环境变量管理、配置验证、热重载等功能
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

# 创建一个简化的 YAML 处理器（如果项目中没有 PyYAML）
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    
    class SimpleYAMLError(Exception):
        pass
    
    class yaml:
        @staticmethod
        def safe_load(f):
            raise SimpleYAMLError("PyYAML not installed. Please install with: pip install PyYAML")
        
        @staticmethod
        def dump(data, f, **kwargs):
            raise SimpleYAMLError("PyYAML not installed. Please install with: pip install PyYAML")


class ConfigEnvironment(Enum):
    """配置环境类型"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class APIConfig:
    """API配置"""
    provider: str = "openai"
    model: str = "gpt-4o"
    base_url: str = ""
    timeout: int = 30
    max_retries: int = 3
    batch_size: int = 10


@dataclass
class PerformanceConfig:
    """性能配置"""
    max_workers: int = 8
    enable_cache: bool = True
    cache_ttl_hours: int = 24
    memory_limit_mb: int = 2048
    enable_batch_processing: bool = True


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    console_enabled: bool = True
    max_file_size_mb: int = 50
    backup_count: int = 5


@dataclass
class ProjectConfig:
    """项目总配置"""
    environment: ConfigEnvironment = ConfigEnvironment.DEVELOPMENT
    api: APIConfig = field(default_factory=APIConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    custom: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        self._config: Optional[ProjectConfig] = None
        self._watchers: List[callable] = []
        
        # 环境变量映射
        self.env_mappings = {
            "ENVIRONMENT": "environment",
            "API_PROVIDER": "api.provider",
            "API_MODEL": "api.model",
            "API_BASE_URL": "api.base_url",
            "MAX_WORKERS": "performance.max_workers",
            "ENABLE_CACHE": "performance.enable_cache",
            "LOG_LEVEL": "logging.level",
        }
    
    def load_config(self, config_file: Optional[str] = None) -> ProjectConfig:
        """
        加载配置
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            项目配置对象
        """
        # 1. 加载默认配置
        config = ProjectConfig()
        
        # 2. 从配置文件加载
        if config_file:
            config = self._load_from_file(config_file, config)
        else:
            # 按环境自动选择配置文件
            env = os.getenv("ENVIRONMENT", "development")
            config_file = self.config_dir / f"{env}.yaml"
            if config_file.exists():
                config = self._load_from_file(str(config_file), config)
        
        # 3. 从环境变量覆盖
        config = self._load_from_env(config)
        
        # 4. 验证配置
        self._validate_config(config)
        
        self._config = config
        return config
    
    def _load_from_file(self, file_path: str, config: ProjectConfig) -> ProjectConfig:
        """从文件加载配置"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logging.warning(f"Config file not found: {file_path}")
            return config
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # 更新配置对象
            config = self._merge_config(config, data)
            logging.info(f"Loaded config from: {file_path}")
            
        except Exception as e:
            logging.error(f"Failed to load config from {file_path}: {e}")
        
        return config
    
    def _load_from_env(self, config: ProjectConfig) -> ProjectConfig:
        """从环境变量加载配置"""
        for env_key, config_path in self.env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value:
                self._set_nested_value(config, config_path, env_value)
        
        return config
    
    def _merge_config(self, config: ProjectConfig, data: Dict[str, Any]) -> ProjectConfig:
        """合并配置数据"""
        if "environment" in data:
            config.environment = ConfigEnvironment(data["environment"])
        
        if "api" in data:
            api_data = data["api"]
            config.api = APIConfig(
                provider=api_data.get("provider", config.api.provider),
                model=api_data.get("model", config.api.model),
                base_url=api_data.get("base_url", config.api.base_url),
                timeout=api_data.get("timeout", config.api.timeout),
                max_retries=api_data.get("max_retries", config.api.max_retries),
                batch_size=api_data.get("batch_size", config.api.batch_size)
            )
        
        if "performance" in data:
            perf_data = data["performance"]
            config.performance = PerformanceConfig(
                max_workers=perf_data.get("max_workers", config.performance.max_workers),
                enable_cache=perf_data.get("enable_cache", config.performance.enable_cache),
                cache_ttl_hours=perf_data.get("cache_ttl_hours", config.performance.cache_ttl_hours),
                memory_limit_mb=perf_data.get("memory_limit_mb", config.performance.memory_limit_mb),
                enable_batch_processing=perf_data.get("enable_batch_processing", config.performance.enable_batch_processing)
            )
        
        if "logging" in data:
            log_data = data["logging"]
            config.logging = LoggingConfig(
                level=log_data.get("level", config.logging.level),
                format=log_data.get("format", config.logging.format),
                file_enabled=log_data.get("file_enabled", config.logging.file_enabled),
                console_enabled=log_data.get("console_enabled", config.logging.console_enabled),
                max_file_size_mb=log_data.get("max_file_size_mb", config.logging.max_file_size_mb),
                backup_count=log_data.get("backup_count", config.logging.backup_count)
            )
        
        if "custom" in data:
            config.custom.update(data["custom"])
        
        return config
    
    def _set_nested_value(self, obj: Any, path: str, value: str):
        """设置嵌套属性值"""
        parts = path.split('.')
        current = obj
        
        for part in parts[:-1]:
            current = getattr(current, part)
        
        # 类型转换
        final_key = parts[-1]
        if hasattr(current, final_key):
            current_value = getattr(current, final_key)
            if isinstance(current_value, bool):
                value = value.lower() in ['true', '1', 'yes']
            elif isinstance(current_value, int):
                value = int(value)
            elif isinstance(current_value, float):
                value = float(value)
        
        setattr(current, final_key, value)
    
    def _validate_config(self, config: ProjectConfig):
        """验证配置"""
        errors = []
        
        # 验证API配置
        if not config.api.provider:
            errors.append("API provider cannot be empty")
        
        if config.api.timeout <= 0:
            errors.append("API timeout must be positive")
        
        # 验证性能配置
        if config.performance.max_workers <= 0:
            errors.append("Max workers must be positive")
        
        if config.performance.memory_limit_mb <= 0:
            errors.append("Memory limit must be positive")
        
        # 验证日志配置
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if config.logging.level not in valid_levels:
            errors.append(f"Invalid log level: {config.logging.level}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def save_config(self, config: ProjectConfig, file_path: Optional[str] = None):
        """保存配置到文件"""
        if not file_path:
            file_path = self.config_dir / f"{config.environment.value}.yaml"
        
        config_dict = {
            "environment": config.environment.value,
            "api": {
                "provider": config.api.provider,
                "model": config.api.model,
                "base_url": config.api.base_url,
                "timeout": config.api.timeout,
                "max_retries": config.api.max_retries,
                "batch_size": config.api.batch_size
            },
            "performance": {
                "max_workers": config.performance.max_workers,
                "enable_cache": config.performance.enable_cache,
                "cache_ttl_hours": config.performance.cache_ttl_hours,
                "memory_limit_mb": config.performance.memory_limit_mb,
                "enable_batch_processing": config.performance.enable_batch_processing
            },
            "logging": {
                "level": config.logging.level,
                "format": config.logging.format,
                "file_enabled": config.logging.file_enabled,
                "console_enabled": config.logging.console_enabled,
                "max_file_size_mb": config.logging.max_file_size_mb,
                "backup_count": config.logging.backup_count
            },
            "custom": config.custom
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
        
        logging.info(f"Config saved to: {file_path}")
    
    def get_config(self) -> Optional[ProjectConfig]:
        """获取当前配置"""
        return self._config
    
    def add_config_watcher(self, callback: callable):
        """添加配置变更监听器"""
        self._watchers.append(callback)
    
    def reload_config(self):
        """重新加载配置"""
        old_config = self._config
        new_config = self.load_config()
        
        # 通知监听器
        for watcher in self._watchers:
            try:
                watcher(old_config, new_config)
            except Exception as e:
                logging.error(f"Config watcher error: {e}")


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config() -> ProjectConfig:
    """获取全局配置"""
    if config_manager.get_config() is None:
        config_manager.load_config()
    return config_manager.get_config()


def init_config(config_dir: Optional[str] = None, config_file: Optional[str] = None) -> ProjectConfig:
    """初始化配置"""
    global config_manager
    if config_dir:
        config_manager = ConfigManager(config_dir)
    return config_manager.load_config(config_file)
