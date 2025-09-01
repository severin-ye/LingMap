"""
统一日志管理器
===========================

提供项目中所有日志功能的统一管理，包括：
- 性能报告记录
- 系统日志记录
- 文件输出管理
- 日志配置管理

作者: LingMap Team
创建时间: 2025-09-01
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogType(Enum):
    """日志类型枚举"""
    PERFORMANCE = "performance"
    SYSTEM = "system"
    TEST = "test"
    OPTIMIZATION = "optimization"
    API = "api"
    ERROR = "error"


@dataclass
class LogConfig:
    """日志配置类"""
    logs_dir: str = "logs"
    enable_console: bool = True
    enable_file: bool = True
    log_level: str = "INFO"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_format: str = "%(levelname)s: %(message)s"


class LogManager:
    """统一日志管理器"""
    
    def __init__(self, config: Optional[LogConfig] = None):
        """
        初始化日志管理器
        
        Args:
            config: 日志配置，如果为None则使用默认配置
        """
        self.config = config or LogConfig()
        self.logs_dir = Path(self.config.logs_dir)
        self._ensure_logs_dir()
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
    def _ensure_logs_dir(self):
        """确保日志目录存在"""
        self.logs_dir.mkdir(exist_ok=True)
        
    def _setup_logging(self):
        """设置logging配置"""
        # 清除已存在的handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        # 设置日志级别
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(level=log_level)
        
    def get_logger(self, name: str, log_type: LogType = LogType.SYSTEM) -> logging.Logger:
        """
        获取指定名称的logger
        
        Args:
            name: logger名称
            log_type: 日志类型
            
        Returns:
            配置好的logger实例
        """
        logger = logging.getLogger(name)
        
        # 如果logger已经有handlers，直接返回
        if logger.handlers:
            return logger
            
        logger.setLevel(getattr(logging, self.config.log_level.upper(), logging.INFO))
        
        # 添加控制台handler
        if self.config.enable_console:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(self.config.console_format)
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
        # 添加文件handler
        if self.config.enable_file:
            log_file = self._get_log_filename(name, log_type)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_formatter = logging.Formatter(
                self.config.file_format, 
                datefmt=self.config.date_format
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
        return logger
    
    def _get_log_filename(self, name: str, log_type: LogType) -> Path:
        """
        生成日志文件名
        
        Args:
            name: logger名称
            log_type: 日志类型
            
        Returns:
            日志文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{log_type.value}_{name}_{timestamp}.log"
        return self.logs_dir / filename
    
    def save_performance_report(
        self, 
        data: Dict[str, Any], 
        report_type: str = "performance",
        custom_filename: Optional[str] = None
    ) -> Path:
        """
        保存性能报告
        
        Args:
            data: 性能数据
            report_type: 报告类型
            custom_filename: 自定义文件名（不包含扩展名）
            
        Returns:
            保存的文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if custom_filename:
            filename = f"{custom_filename}_{timestamp}.json"
        else:
            filename = f"{report_type}_report_{timestamp}.json"
            
        filepath = self.logs_dir / filename
        
        # 添加元数据
        report_data = {
            "timestamp": datetime.now().strftime(self.config.date_format),
            "report_type": report_type,
            "generated_by": "LingMap LogManager",
            **data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"性能报告已保存: {filepath}")
        return filepath
    
    def save_optimization_report(
        self, 
        data: Dict[str, Any],
        include_summary: bool = True,
        custom_filename: Optional[str] = None
    ) -> tuple[Path, Optional[Path]]:
        """
        保存优化报告
        
        Args:
            data: 优化数据
            include_summary: 是否生成摘要文件
            custom_filename: 自定义文件名前缀
            
        Returns:
            (JSON报告路径, 摘要文件路径)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if custom_filename:
            json_filename = f"{custom_filename}_{timestamp}.json"
            txt_filename = f"{custom_filename}_summary_{timestamp}.txt"
        else:
            json_filename = f"optimization_report_{timestamp}.json"
            txt_filename = f"optimization_summary_{timestamp}.txt"
            
        # 保存JSON报告
        json_filepath = self.logs_dir / json_filename
        
        # 添加元数据
        report_data = {
            "timestamp": datetime.now().strftime(self.config.date_format),
            "report_type": "optimization",
            "generated_by": "LingMap LogManager",
            **data
        }
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"优化报告已保存: {json_filepath}")
        
        # 生成摘要文件
        txt_filepath = None
        if include_summary:
            txt_filepath = self.logs_dir / txt_filename
            self._generate_optimization_summary(data, txt_filepath)
            self.logger.info(f"优化摘要已保存: {txt_filepath}")
            
        return json_filepath, txt_filepath
    
    def _generate_optimization_summary(self, data: Dict[str, Any], filepath: Path):
        """生成优化报告摘要"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("LingMap - 项目优化总结报告\n")
            f.write("=" * 60 + "\n\n")
            
            # 基本信息
            if "project_info" in data:
                info = data["project_info"]
                f.write(f"项目名称: {info.get('name', 'N/A')}\n")
                f.write(f"优化时间: {info.get('optimization_date', 'N/A')}\n")
                f.write(f"版本: {info.get('version', 'N/A')}\n\n")
            
            # 性能改进
            if "optimization_achievements" in data:
                achievements = data["optimization_achievements"]
                if "performance_improvements" in achievements:
                    f.write("🎯 性能改进:\n")
                    for key, value in achievements["performance_improvements"].items():
                        f.write(f"  - {key}: {value}\n")
                    f.write("\n")
            
            # 创建的工具
            if "created_optimization_tools" in data:
                tools = data["created_optimization_tools"]
                if "核心优化工具" in tools:
                    f.write("🛠️ 核心优化工具:\n")
                    for tool in tools["核心优化工具"]:
                        f.write(f"  - {tool.get('name', 'N/A')}: {tool.get('description', 'N/A')}\n")
                        if "improvement" in tool:
                            f.write(f"    提升: {tool['improvement']}\n")
                    f.write("\n")
            
            # 演示结果
            if "demonstration_results" in data:
                demo = data["demonstration_results"]
                if "benchmark_results" in demo:
                    f.write("📊 基准测试结果:\n")
                    for key, value in demo["benchmark_results"].items():
                        f.write(f"  - {key}: {value}\n")
                    f.write("\n")
    
    def save_implementation_plan(
        self, 
        plan_data: Dict[str, Any],
        custom_filename: Optional[str] = None
    ) -> Path:
        """
        保存实施计划
        
        Args:
            plan_data: 计划数据
            custom_filename: 自定义文件名前缀
            
        Returns:
            保存的文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if custom_filename:
            filename = f"{custom_filename}_{timestamp}.json"
        else:
            filename = f"implementation_plan_{timestamp}.json"
            
        filepath = self.logs_dir / filename
        
        # 添加元数据
        plan_with_meta = {
            "timestamp": datetime.now().strftime(self.config.date_format),
            "plan_type": "implementation",
            "generated_by": "LingMap LogManager",
            **plan_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(plan_with_meta, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"实施计划已保存: {filepath}")
        return filepath
    
    def save_test_results(
        self, 
        test_data: Dict[str, Any],
        test_name: str,
        custom_filename: Optional[str] = None
    ) -> Path:
        """
        保存测试结果
        
        Args:
            test_data: 测试数据
            test_name: 测试名称
            custom_filename: 自定义文件名前缀
            
        Returns:
            保存的文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if custom_filename:
            filename = f"{custom_filename}_{timestamp}.json"
        else:
            filename = f"test_{test_name}_{timestamp}.json"
            
        filepath = self.logs_dir / filename
        
        # 添加元数据
        test_with_meta = {
            "timestamp": datetime.now().strftime(self.config.date_format),
            "test_name": test_name,
            "test_type": "automated",
            "generated_by": "LingMap LogManager",
            **test_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_with_meta, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"测试结果已保存: {filepath}")
        return filepath
    
    def log_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None,
        save_to_file: bool = True
    ):
        """
        记录错误信息
        
        Args:
            error: 异常对象
            context: 上下文信息
            save_to_file: 是否保存到文件
        """
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().strftime(self.config.date_format),
            "context": context or {}
        }
        
        # 记录到日志
        self.logger.error(f"错误发生: {error_info['error_type']} - {error_info['error_message']}")
        
        # 保存到文件
        if save_to_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_report_{timestamp}.json"
            filepath = self.logs_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(error_info, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"错误报告已保存: {filepath}")
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        清理旧日志文件
        
        Args:
            days_to_keep: 保留的天数
        """
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        removed_count = 0
        
        for log_file in self.logs_dir.iterdir():
            if log_file.is_file() and log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    removed_count += 1
                    self.logger.debug(f"删除旧日志文件: {log_file}")
                except Exception as e:
                    self.logger.warning(f"无法删除日志文件 {log_file}: {e}")
        
        if removed_count > 0:
            self.logger.info(f"清理完成，删除了 {removed_count} 个旧日志文件")
    
    def list_log_files(self, pattern: Optional[str] = None) -> List[Path]:
        """
        列出日志文件
        
        Args:
            pattern: 文件名模式（可选）
            
        Returns:
            日志文件路径列表
        """
        if pattern:
            return list(self.logs_dir.glob(pattern))
        else:
            return list(self.logs_dir.iterdir())
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        获取日志统计信息
        
        Returns:
            日志统计数据
        """
        files = self.list_log_files()
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        file_types = {}
        for file in files:
            if file.is_file():
                ext = file.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types,
            "logs_directory": str(self.logs_dir)
        }


# 全局日志管理器实例
_global_log_manager: Optional[LogManager] = None


def get_log_manager(config: Optional[LogConfig] = None) -> LogManager:
    """
    获取全局日志管理器实例
    
    Args:
        config: 日志配置（首次调用时使用）
        
    Returns:
        日志管理器实例
    """
    global _global_log_manager
    if _global_log_manager is None:
        _global_log_manager = LogManager(config)
    return _global_log_manager


def get_logger(name: str, log_type: LogType = LogType.SYSTEM) -> logging.Logger:
    """
    便捷函数：获取logger
    
    Args:
        name: logger名称
        log_type: 日志类型
        
    Returns:
        logger实例
    """
    return get_log_manager().get_logger(name, log_type)


def save_performance_report(data: Dict[str, Any], **kwargs) -> Path:
    """便捷函数：保存性能报告"""
    return get_log_manager().save_performance_report(data, **kwargs)


def save_optimization_report(data: Dict[str, Any], **kwargs) -> tuple[Path, Optional[Path]]:
    """便捷函数：保存优化报告"""
    return get_log_manager().save_optimization_report(data, **kwargs)


def save_implementation_plan(data: Dict[str, Any], **kwargs) -> Path:
    """便捷函数：保存实施计划"""
    return get_log_manager().save_implementation_plan(data, **kwargs)


if __name__ == "__main__":
    # 示例使用
    print("LingMap 统一日志管理器 - 测试")
    
    # 创建日志管理器
    log_manager = LogManager()
    
    # 获取logger
    logger = log_manager.get_logger("test_module", LogType.TEST)
    logger.info("这是一个测试日志消息")
    
    # 保存性能报告
    perf_data = {
        "test_name": "示例测试",
        "duration": 1.23,
        "success_rate": 100.0
    }
    perf_file = log_manager.save_performance_report(perf_data, "mock_analyzer_performance")
    print(f"性能报告已保存: {perf_file}")
    
    # 获取统计信息
    stats = log_manager.get_log_stats()
    print(f"日志统计: {stats}")
    
    print("测试完成！")
