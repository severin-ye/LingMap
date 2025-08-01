from typing import Dict, Any, List, Optional, Union, Literal
import json
import openai
import os
import time
import random
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

# Create a dedicated logger
logger = logging.getLogger("llm_client")


class LLMClient:
    """LLM API client, wraps OpenAI/DeepSeek API calls"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.0,
        base_url: Optional[str] = None,
        max_tokens: int = 4000,
        timeout: int = 120,  # Increase timeout to 120 seconds
        provider: Union[Literal["openai", "deepseek"], str] = "openai"
    ):
        """
        Initialize LLM client
        
        Args:
            api_key: API key
            model: Model to use, default gpt-4o
            temperature: Temperature parameter, controls randomness, default 0.0 (deterministic output)
            base_url: Custom API base URL, for proxy or API compatibility
            max_tokens: Maximum output token count
            timeout: API call timeout (seconds)
            provider: API provider, "openai" or "deepseek"
        """
        self.provider = provider
        
        # If API key is not provided, try to get it from environment variables
        if api_key is None:
            if provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
            elif provider == "deepseek":
                api_key = os.environ.get("DEEPSEEK_API_KEY")
                
            # If not in environment variables, try to read from .env file
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
            raise ValueError(f"No {provider} API key provided")
            
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        # Initialize client
        openai_kwargs = {"api_key": self.api_key, "timeout": self.timeout}
        
        # Set base URL according to provider
        if provider == "deepseek" and not base_url:
            openai_kwargs["base_url"] = "https://api.deepseek.com/v1"
        elif base_url:
            openai_kwargs["base_url"] = base_url
            
        self.client = openai.OpenAI(**openai_kwargs)
        
    @retry(
        stop=stop_after_attempt(8),  # Retry up to 8 times
        wait=wait_exponential(min=1, max=15),  # Exponential backoff wait time
        before_sleep=before_sleep_log(logger, logging.WARNING),  # Log before sleeping
        reraise=True  # Raise the original exception on the last retry
    )
    def call_llm(self, system: str, user: str, response_format: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Call LLM API
        
        Args:
            system: System prompt
            user: User prompt
            response_format: Response format, e.g. {"type": "json_object"}
            
        Returns:
            LLM response content
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
            # Add a small delay before API call to avoid too many concurrent requests
            if random.random() < 0.3:  # 30% chance to add random delay
                delay = random.uniform(0.1, 1.5)
                time.sleep(delay)
                
            # Send API request    
            response = self.client.chat.completions.create(**kwargs)
            return {
                "content": response.choices[0].message.content,
                "success": True,
                "model": response.model
            }
        except Exception as e:
            error_msg = str(e)
            # Add random delay to prevent immediate retry after concurrent request failure
            if "timeout" in error_msg.lower():
                delay = random.uniform(1, 3)
                time.sleep(delay)  # Add random delay in case of timeout
                logger.warning(f"API timeout, added {delay:.1f} seconds random delay")
                
            logger.error(f"API call failed: {error_msg}")
            return {
                "content": None,
                "success": False,
                "error": error_msg
            }
        
    def call_with_json_response(self, system: str, user: str) -> Dict[str, Any]:
        """
        Call LLM API and require JSON format
        
        Args:
            system: System prompt
            user: User prompt
            
        Returns:
            Parsed JSON response
        """
        # Ensure the prompt contains the json keyword, which is necessary for DeepSeek API
        if self.provider == "deepseek" and "json" not in system.lower() and "json" not in user.lower():
            # Add json keyword to system prompt
            system = system + "\nPlease reply in JSON format."
            
        response = self.call_llm(system, user, response_format={"type": "json_object"})
        
        if response["success"] and response["content"]:
            try:
                # Parse JSON response
                json_content = json.loads(response["content"])
                response["json_content"] = json_content
                return response
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {str(e)}")
                response["success"] = False
                response["error"] = f"JSON parsing error: {str(e)}"
                
        return response
