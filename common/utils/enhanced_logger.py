"""
增强日志模块

提供更丰富的日志记录功能，帮助调试系统问题
"""

import os
import sys
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Get project root directory
try:
    from common.utils.path_utils import get_project_root
    PROJECT_ROOT = get_project_root()
except ImportError:
    current_file = Path(__file__).resolve()
    PROJECT_ROOT = current_file.parent.parent.parent


class EnhancedLogger:
    """增强日志记录器，提供更丰富的日志记录功能"""
    
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    def __init__(
        self, 
        name: str, 
        log_level: str = "INFO", 
        log_file: Optional[str] = None,
        console_output: bool = True
    ):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_level: 日志级别，可选值："DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            log_file: 日志文件路径，如果为None则自动生成
            console_output: 是否输出到控制台
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.LOG_LEVELS.get(log_level.upper(), logging.INFO))
        
        # Avoid adding duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
            
        # Create log format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add console output
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Add file output
        if log_file:
            log_path = log_file
        else:
            logs_dir = PROJECT_ROOT / "logs"
            logs_dir.mkdir(exist_ok=True)
            current_date = datetime.now().strftime('%Y%m%d')
            log_path = logs_dir / f"{name}_{current_date}.log"
            
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.log_path = log_path
    
    def debug(self, message: str, **kwargs):
        """记录调试级别日志"""
        if kwargs:
            message = f"{message} | {self._format_kwargs(kwargs)}"
        self.logger.debug(message)
    
    def info(self, message: str, **kwargs):
        """记录信息级别日志"""
        if kwargs:
            message = f"{message} | {self._format_kwargs(kwargs)}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """记录警告级别日志"""
        if kwargs:
            message = f"{message} | {self._format_kwargs(kwargs)}"
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """记录错误级别日志"""
        if kwargs:
            message = f"{message} | {self._format_kwargs(kwargs)}"
        self.logger.error(message)
    
    def critical(self, message: str, **kwargs):
        """记录严重错误级别日志"""
        if kwargs:
            message = f"{message} | {self._format_kwargs(kwargs)}"
        self.logger.critical(message)
    
    def _format_kwargs(self, kwargs: Dict[str, Any]) -> str:
        """格式化关键字参数为字符串"""
        formatted = {}
        for key, value in kwargs.items():
            if isinstance(value, (dict, list)):
                try:
                    formatted[key] = json.dumps(value, ensure_ascii=False)
                except:
                    formatted[key] = str(value)
            else:
                formatted[key] = value
        
        return ", ".join(f"{k}={v}" for k, v in formatted.items())
    
    def log_api_request(
        self, 
        provider: str, 
        endpoint: str, 
        payload: Dict[str, Any], 
        success: bool = True,
        response: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Log API request"""
        # Hide sensitive information
        safe_payload = self._mask_sensitive_info(payload)
        
        if success:
            self.debug(
                f"API请求成功",
                provider=provider,
                endpoint=endpoint,
                payload=safe_payload,
                response_preview=self._get_response_preview(response)
            )
        else:
            self.error(
                f"API请求失败",
                provider=provider,
                endpoint=endpoint,
                payload=safe_payload,
                error=error
            )
    
    def _mask_sensitive_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """遮盖敏感信息，如API密钥等"""
        if not isinstance(data, dict):
            return data
            
        masked_data = {}
        sensitive_keys = ["api_key", "key", "secret", "password", "token"]
        
        for key, value in data.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                masked_data[key] = "********"
            elif isinstance(value, dict):
                masked_data[key] = self._mask_sensitive_info(value)
            else:
                masked_data[key] = value
                
        return masked_data
    
    def _get_response_preview(self, response: Optional[Dict[str, Any]]) -> str:
        """生成响应预览（截断过长内容）"""
        if not response:
            return "无响应"
            
        try:
            response_str = json.dumps(response, ensure_ascii=False)
            if len(response_str) > 200:
                return response_str[:200] + "..."
            return response_str
        except:
            return str(response)[:200]


# Default logger instance
default_logger = EnhancedLogger("fanren_system")

# Export convenience functions
debug = default_logger.debug
info = default_logger.info
warning = default_logger.warning
error = default_logger.error
critical = default_logger.critical
log_api_request = default_logger.log_api_request
