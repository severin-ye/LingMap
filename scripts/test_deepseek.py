#!/usr/bin/env python3
"""
DeepSeek API 测试脚本，用于验证 DeepSeek API 配置是否正确
"""

import os
import sys
from pathlib import Path
import dotenv

# 获取项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 加载环境变量
dotenv.load_dotenv(os.path.join(project_root, ".env"))

import dotenv
from event_extraction.repository.llm_client import LLMClient


def test_deepseek_api():
    """测试 DeepSeek API 连接"""
    print("=== DeepSeek API 测试 ===")
    
    # 加载环境变量
    dotenv.load_dotenv(os.path.join(project_root, ".env"))
    
    # 确保环境变量大小写一致
    if "deepseek_api_key" in os.environ:
        os.environ["DEEPSEEK_API_KEY"] = os.environ["deepseek_api_key"]
    
    # 获取API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("错误：未找到 DeepSeek API 密钥")
        print("请确保 .env 文件中包含 deepseek_api_key=YOUR_API_KEY")
        return False
        
    try:
        print(f"使用 API 密钥: {api_key[:5]}...{api_key[-4:]}")
        
        # 初始化客户端
        client = LLMClient(
            api_key=api_key,
            model="deepseek-chat",
            provider="deepseek"
        )
        
        # 进行简单测试
        print("发送测试请求到 DeepSeek API...")
        response = client.call_llm(
            system="你是一个有用的助手。",
            user="《凡人修仙传》是谁写的？请简短回答。"
        )
        
        if response["success"]:
            print("\n成功接收到响应:")
            print("-" * 40)
            print(response["content"])
            print("-" * 40)
            print(f"使用的模型: {response['model']}")
            print("\nDeepSeek API 测试成功!")
            return True
        else:
            print("\n调用失败:")
            print(response["error"])
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_deepseek_api()
    sys.exit(0 if success else 1)
