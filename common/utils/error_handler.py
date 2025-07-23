#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一异常处理和错误管理
"""

import logging
import traceback
from typing import Dict, Any, Optional, Type
from functools import wraps


class ProjectException(Exception):
    """项目基础异常类"""
    
    def __init__(self, message: str, error_code: str = "UNKNOWN", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class APIException(ProjectException):
    """API调用异常"""
    pass


class EventExtractionException(ProjectException):
    """事件提取异常"""
    pass


class CausalLinkingException(ProjectException):
    """因果关系链接异常"""
    pass


class ConfigurationException(ProjectException):
    """配置相关异常"""
    pass


def handle_exceptions(
    default_return=None,
    exception_types: tuple = (Exception,),
    log_level: int = logging.ERROR
):
    """
    异常处理装饰器
    
    Args:
        default_return: 发生异常时的默认返回值
        exception_types: 要捕获的异常类型
        log_level: 日志级别
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                logger = logging.getLogger(func.__module__)
                
                error_info = {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs),
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
                
                if isinstance(e, ProjectException):
                    error_info.update({
                        'error_code': e.error_code,
                        'details': e.details
                    })
                
                logger.log(log_level, f"Exception in {func.__name__}: {str(e)}", extra=error_info)
                
                if log_level >= logging.ERROR:
                    logger.debug(traceback.format_exc())
                
                return default_return
        return wrapper
    return decorator


class ErrorReporter:
    """错误报告器"""
    
    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
    
    def report_api_error(self, operation: str, error: Exception, context: Optional[Dict[str, Any]] = None):
        """报告API错误"""
        self.logger.error(
            f"API Error in {operation}",
            extra={
                'operation': operation,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context or {}
            }
        )
    
    def report_processing_error(self, stage: str, item_id: str, error: Exception):
        """报告处理错误"""
        self.logger.error(
            f"Processing Error in {stage}",
            extra={
                'stage': stage,
                'item_id': item_id,
                'error_type': type(error).__name__,
                'error_message': str(error)
            }
        )
    
    def report_validation_error(self, field: str, value: Any, expected: str):
        """报告验证错误"""
        self.logger.warning(
            f"Validation Error for field {field}",
            extra={
                'field': field,
                'value': str(value),
                'expected': expected
            }
        )
