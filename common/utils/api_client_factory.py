#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API客户端工厂
统一管理API密钥获取和客户端创建逻辑
"""

import os
from typing import Optional
from event_extraction.repository.llm_client import LLMClient


class APIClientFactory:
    """API客户端工厂类，统一管理API客户端创建"""
    
    @staticmethod
    def get_api_key(provider: str) -> str:
        """
        获取API密钥
        
        Args:
            provider: API提供商 ("openai" 或 "deepseek")
            
        Returns:
            API密钥
            
        Raises:
            ValueError: 当无法获取API密钥时
        """
        if provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Please set OPENAI_API_KEY environment variable")
        elif provider == "deepseek":
            api_key = os.environ.get("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("Please set DEEPSEEK_API_KEY environment variable")
        else:
            raise ValueError(f"Unsupported API provider: {provider}")
        
        return api_key
    
    @staticmethod
    def create_llm_client(
        model: str = "gpt-4o",
        provider: str = "openai",
        api_key: Optional[str] = None,
        base_url: str = ""
    ) -> LLMClient:
        """
        创建LLM客户端
        
        Args:
            model: 模型名称
            provider: API提供商
            api_key: API密钥（可选，如果不提供则从环境变量获取）
            base_url: 自定义API基础URL
            
        Returns:
            LLM客户端实例
        """
        if not api_key:
            api_key = APIClientFactory.get_api_key(provider)
        
        return LLMClient(
            api_key=api_key,
            model=model,
            base_url=base_url,
            provider=provider
        )
