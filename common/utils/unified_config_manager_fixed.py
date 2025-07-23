#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一配置管理器 - 固定版本
提供项目级别的配置管理，支持环境变量覆盖、配置验证和热重载
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

# 简化的 YAML 处理
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

logger = logging.getLogger(__name__)

class Environment(Enum):
    """环境类型枚举"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"

@dataclass
class ProjectConfig:
    """项目配置数据类"""
    # 环境设置
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    
    # API 配置
    api_timeout: int = 30
    api_retries: int = 3
    api_rate_limit: int = 100
    
    # 性能配置
    max_workers: int = 4
    batch_size: int = 10
    cache_size: int = 1000
    
    # 路径配置
    input_path: str = "novel"
    output_path: str = "output"
    
    # 模型配置
    model_config: Dict[str, Any] = field(default_factory=dict)
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # 自定义配置
    custom_settings: Dict[str, Any] = field(default_factory=dict)

class ConfigManager:
    """统一配置管理器"""
    
    def __init__(self, config_dir: Union[str, Path] = "common/config"):
        self.config_dir = Path(config_dir)
        self._config: Optional[ProjectConfig] = None
        self._watchers: List[Callable] = []
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"配置管理器初始化: {self.config_dir}")
    
    def get_config(self) -> Optional[ProjectConfig]:
        """获取当前配置"""
        if self._config is None:
            self.load_config()
        return self._config
    
    def load_config(self, environment: Optional[str] = None) -> bool:
        """加载配置"""
        try:
            # 确定环境
            env = environment or os.getenv('ENV', 'development')
            
            # 查找配置文件
            config_file_path: Optional[str] = None
            
            # 检查 YAML 文件（如果支持）
            if HAS_YAML:
                yaml_file = self.config_dir / f"{env}.yaml"
                if yaml_file.exists():
                    config_file_path = str(yaml_file)
            
            # 检查 JSON 文件
            if not config_file_path:
                json_file = self.config_dir / f"{env}.json"
                if json_file.exists():
                    config_file_path = str(json_file)
            
            # 检查默认配置
            if not config_file_path:
                default_file = self.config_dir / "config.json"
                if default_file.exists():
                    config_file_path = str(default_file)
            
            # 加载配置
            if config_file_path:
                self._config = self._load_from_file(config_file_path)
            else:
                self._config = ProjectConfig()  # 使用默认配置
            
            # 应用环境变量覆盖
            self._apply_env_overrides(self._config)
            
            # 验证配置
            self._validate_config(self._config)
            
            # 通知观察者
            self._notify_watchers()
            
            logger.info(f"配置加载成功: {env}")
            return True
            
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            return False
    
    def _load_from_file(self, file_path: str) -> ProjectConfig:
        """从文件加载配置"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml'] and HAS_YAML:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # 转换为 ProjectConfig
            return self._dict_to_config(data)
            
        except Exception as e:
            logger.error(f"配置文件解析失败 {file_path}: {e}")
            raise
    
    def _dict_to_config(self, data: Dict[str, Any]) -> ProjectConfig:
        """将字典转换为 ProjectConfig"""
        config_data = {}
        
        # 处理环境
        if 'environment' in data:
            env_value = data['environment']
            if isinstance(env_value, str):
                config_data['environment'] = Environment(env_value)
        
        # 处理其他基本字段
        basic_fields = ['debug', 'api_timeout', 'api_retries', 'api_rate_limit',
                       'max_workers', 'batch_size', 'cache_size', 'input_path',
                       'output_path', 'log_level', 'log_file']
        
        for field in basic_fields:
            if field in data:
                config_data[field] = data[field]
        
        # 处理复杂字段
        if 'model_config' in data:
            config_data['model_config'] = data['model_config']
        
        if 'custom_settings' in data:
            config_data['custom_settings'] = data['custom_settings']
        
        return ProjectConfig(**config_data)
    
    def _apply_env_overrides(self, config: ProjectConfig) -> None:
        """应用环境变量覆盖"""
        env_mappings = {
            'DEBUG': ('debug', bool),
            'API_TIMEOUT': ('api_timeout', int),
            'API_RETRIES': ('api_retries', int),
            'MAX_WORKERS': ('max_workers', int),
            'BATCH_SIZE': ('batch_size', int),
            'LOG_LEVEL': ('log_level', str),
            'INPUT_PATH': ('input_path', str),
            'OUTPUT_PATH': ('output_path', str),
        }
        
        for env_var, (attr_name, value_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    if value_type == bool:
                        converted_value = env_value.lower() in ['true', '1', 'yes']
                    elif value_type == int:
                        converted_value = int(env_value)
                    elif value_type == float:
                        converted_value = float(env_value)
                    else:
                        converted_value = env_value
                    
                    setattr(config, attr_name, converted_value)
                    logger.debug(f"环境变量覆盖: {attr_name} = {converted_value}")
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"环境变量类型转换失败 {env_var}: {e}")
    
    def _validate_config(self, config: ProjectConfig) -> None:
        """验证配置"""
        validations = [
            (config.api_timeout > 0, "API 超时时间必须大于 0"),
            (config.api_retries >= 0, "API 重试次数不能为负数"),
            (config.max_workers > 0, "最大工作线程数必须大于 0"),
            (config.batch_size > 0, "批处理大小必须大于 0"),
            (config.cache_size >= 0, "缓存大小不能为负数"),
        ]
        
        for condition, message in validations:
            if not condition:
                raise ValueError(f"配置验证失败: {message}")
    
    def save_config(self, config: Optional[ProjectConfig] = None, 
                   file_path: Optional[str] = None) -> bool:
        """保存配置到文件"""
        try:
            config = config or self._config
            if not config:
                logger.error("没有配置可保存")
                return False
            
            # 确定保存路径
            if not file_path:
                file_path = str(self.config_dir / f"{config.environment.value}.json")
            
            # 转换为字典
            config_dict = self._config_to_dict(config)
            
            # 保存到文件
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml'] and HAS_YAML:
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置保存成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"配置保存失败: {e}")
            return False
    
    def _config_to_dict(self, config: ProjectConfig) -> Dict[str, Any]:
        """将 ProjectConfig 转换为字典"""
        return {
            'environment': config.environment.value,
            'debug': config.debug,
            'api_timeout': config.api_timeout,
            'api_retries': config.api_retries,
            'api_rate_limit': config.api_rate_limit,
            'max_workers': config.max_workers,
            'batch_size': config.batch_size,
            'cache_size': config.cache_size,
            'input_path': config.input_path,
            'output_path': config.output_path,
            'model_config': config.model_config,
            'log_level': config.log_level,
            'log_file': config.log_file,
            'custom_settings': config.custom_settings,
        }
    
    def add_config_watcher(self, callback: Callable[[ProjectConfig], None]):
        """添加配置变化观察者"""
        self._watchers.append(callback)
    
    def _notify_watchers(self):
        """通知所有观察者配置已变化"""
        if self._config:
            for watcher in self._watchers:
                try:
                    watcher(self._config)
                except Exception as e:
                    logger.error(f"配置观察者回调失败: {e}")

# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_project_config() -> ProjectConfig:
    """获取项目配置"""
    config_manager = get_config_manager()
    config = config_manager.get_config()
    if config is None:
        # 返回默认配置
        return ProjectConfig()
    return config

def reload_config(environment: Optional[str] = None) -> bool:
    """重新加载配置"""
    config_manager = get_config_manager()
    return config_manager.load_config(environment)

if __name__ == "__main__":
    # 测试代码
    config = get_project_config()
    print(f"当前环境: {config.environment.value}")
    print(f"调试模式: {config.debug}")
    print(f"最大工作线程: {config.max_workers}")
