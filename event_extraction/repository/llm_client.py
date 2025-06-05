from typing import Dict, Any, List, Optional, Union, Literal
import json
import openai
import os
from tenacity import retry, stop_after_attempt, wait_exponential


class LLMClient:
    """LLM API 客户端，封装 OpenAI/DeepSeek API 调用"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.0,
        base_url: Optional[str] = None,
        max_tokens: int = 4000,
        timeout: int = 60,
        provider: Union[Literal["openai", "deepseek"], str] = "openai"
    ):
        """
        初始化 LLM 客户端
        
        Args:
            api_key: API 密钥
            model: 使用的模型，默认 gpt-4o
            temperature: 温度参数，控制随机性，默认 0.0（确定性输出）
            base_url: 自定义 API 基础 URL，用于代理或兼容 API
            max_tokens: 最大输出 token 数
            timeout: API 调用超时时间（秒）
            provider: API提供商，"openai" 或 "deepseek"
        """
        self.provider = provider
        
        # 如果未提供API密钥，尝试从环境变量获取
        if api_key is None:
            if provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
            elif provider == "deepseek":
                api_key = os.environ.get("DEEPSEEK_API_KEY")
                
            # 如果环境变量中没有，尝试从.env文件读取
            if api_key is None:
                try:
                    from dotenv import load_dotenv
                    load_dotenv()
                    if provider == "openai":
                        api_key = os.environ.get("OPENAI_API_KEY")
                    elif provider == "deepseek":
                        api_key = os.environ.get("DEEPSEEK_API_KEY")
                except ImportError:
                    pass
        
        if api_key is None:
            raise ValueError(f"未提供 {provider} API 密钥")
            
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        # 初始化客户端
        openai_kwargs = {"api_key": self.api_key, "timeout": self.timeout}
        
        # 根据提供商设置基础URL
        if provider == "deepseek" and not base_url:
            openai_kwargs["base_url"] = "https://api.deepseek.com/v1"
        elif base_url:
            openai_kwargs["base_url"] = base_url
            
        self.client = openai.OpenAI(**openai_kwargs)
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    def call_llm(self, system: str, user: str, response_format: Optional[Dict] = None) -> Dict[str, Any]:
        """
        调用 LLM API
        
        Args:
            system: 系统提示词
            user: 用户提示词
            response_format: 响应格式，如 {"type": "json_object"}
            
        Returns:
            LLM 响应内容
        """
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        try:
            response = self.client.chat.completions.create(**kwargs)
            return {
                "content": response.choices[0].message.content,
                "success": True,
                "model": response.model
            }
        except Exception as e:
            print(f"API 调用失败: {str(e)}")
            return {
                "content": None,
                "success": False,
                "error": str(e)
            }
        
    def call_with_json_response(self, system: str, user: str) -> Dict[str, Any]:
        """
        调用 LLM API 并要求返回 JSON 格式
        
        Args:
            system: 系统提示词
            user: 用户提示词
            
        Returns:
            解析后的 JSON 响应
        """
        response = self.call_llm(system, user, response_format={"type": "json_object"})
        
        if response["success"] and response["content"]:
            try:
                # 解析 JSON 响应
                json_content = json.loads(response["content"])
                response["json_content"] = json_content
                return response
            except json.JSONDecodeError as e:
                print(f"JSON 解析失败: {str(e)}")
                response["success"] = False
                response["error"] = f"JSON 解析错误: {str(e)}"
                
        return response
