from typing import List, Dict, Any, Optional
import os
import re
from concurrent.futures import ThreadPoolExecutor

from common.interfaces.extractor import AbstractExtractor
from common.models.chapter import Chapter
from common.models.event import EventItem
from event_extraction.domain.base_extractor import BaseExtractor
from event_extraction.repository.llm_client import LLMClient


class EventExtractor(BaseExtractor):
    """
    # [CN] 事件抽取器实现类，使用LLM抽取事件
    # [EN] Event extractor implementation class using LLM to extract events
    """
    
    def __init__(
        self, 
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: int = 3,
        provider: str = "openai"
    ):
        """
        # [CN] 初始化事件抽取器
        # [EN] Initialize event extractor
        
        Args:
            model: # [CN] 使用的LLM模型 [EN] LLM model to use
            prompt_path: # [CN] 提示词模板路径 [EN] Prompt template path
            api_key: # [CN] API密钥 [EN] API key
            base_url: # [CN] 自定义API基础URL [EN] Custom API base URL
            max_workers: # [CN] 并行处理的最大工作线程数 [EN] Maximum number of worker threads for parallel processing
            provider: # [CN] API提供商，"openai"或"deepseek" [EN] API provider, "openai" or "deepseek"
        """
        if not prompt_path:
            # [CN] 导入path_utils获取配置文件路径
            # [EN] Import path_utils to get configuration file path
            from common.utils.path_utils import get_config_path
            prompt_path = get_config_path("prompt_event_extraction.json")
            
        super().__init__(prompt_path)
        
        self.provider = provider
        
        # [CN] 如果未提供API密钥，尝试从环境变量获取
        # [EN] If no API key provided, try to get from environment variables
        if not api_key:
            if provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
                if not self.api_key:
                    raise ValueError("请提供 OpenAI API 密钥")  # [CN] 请提供 OpenAI API 密钥 [EN] Please provide OpenAI API key
            else:  # deepseek
                self.api_key = os.environ.get("DEEPSEEK_API_KEY")
                if not self.api_key:
                    raise ValueError("请提供 DeepSeek API 密钥")  # [CN] 请提供 DeepSeek API 密钥 [EN] Please provide DeepSeek API key
        else:
            self.api_key = api_key
            
        self.model = model
        self.base_url = base_url
        self.max_workers = max_workers
        
        # [CN] 初始化LLM客户端
        # [EN] Initialize LLM client
        self.llm_client = LLMClient(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            provider=self.provider
        )
        
    def extract(self, chapter: Chapter) -> List[EventItem]:
        """
        # [CN] 从章节中抽取事件
        # [EN] Extract events from chapter
        
        Args:
            chapter: # [CN] 章节数据 [EN] Chapter data
            
        Returns:
            # [CN] 抽取的事件列表
            # [EN] List of extracted events
        """
        if not chapter.segments:
            # [CN] 如果章节没有预定义的分段，创建分段
            # [EN] If chapter has no predefined segments, create segments
            from common.utils.text_splitter import TextSplitter
            chapter.segments = TextSplitter.split_chapter(chapter.content)
            
        all_events = []
        
        # [CN] 使用线程池并行处理每个段落
        # [EN] Use thread pool to process each segment in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for segment in chapter.segments:
                future = executor.submit(
                    self.extract_from_segment,
                    segment["text"],
                    chapter.chapter_id,
                    segment["seg_id"]
                )
                futures.append(future)
                
            # 收集所有结果
            for future in futures:
                events = future.result()
                if events:
                    all_events.extend(events)
                    
        return all_events
    
    def extract_from_segment(self, text: str, chapter_id: str, segment_id: str) -> List[EventItem]:
        """
        从单个文本段落中提取事件
        
        Args:
            text: 文本段落
            chapter_id: 章节ID
            segment_id: 段落ID
            
        Returns:
            提取的事件列表
        """
        prompt = self.format_prompt(text)
        response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
        
        if response["success"] and "json_content" in response:
            return self.parse_response(response["json_content"], chapter_id, segment_id)
        else:
            print(f"段落 {segment_id} 的事件提取失败: {response.get('error', '未知错误')}")
            return []
            
    def parse_response(self, response: Dict[str, Any], chapter_id: str, segment_id: str) -> List[EventItem]:
        """
        解析LLM响应，提取事件
        
        Args:
            response: LLM响应
            chapter_id: 章节ID
            segment_id: 段落ID
            
        Returns:
            提取的事件列表
        """
        events = []
        
        # 处理响应中可能的多种格式
        if isinstance(response, list):
            # 如果响应直接是事件列表
            event_list = response
        elif "events" in response:
            # 如果响应包含events字段
            event_list = response["events"]
        else:
            # 假设响应本身就是单个事件
            event_list = [response]
            
        for i, event_data in enumerate(event_list):
            # 检查是否为有效事件数据
            if not isinstance(event_data, dict) or not event_data.get("description"):
                continue
                
            # 生成事件ID，如果没有提供的话
            if not event_data.get("event_id"):
                # 从segment_id提取章节部分，如"第一章-1"提取"第一章"
                chapter_match = re.search(r'(第[^-]+章)', segment_id)
                chapter_part = chapter_match.group(1) if chapter_match else segment_id.split('-')[0]
                event_data["event_id"] = f"{chapter_part}-{i+1}"
                
            # 确保chapter_id已设置
            event_data["chapter_id"] = chapter_id
            
            # 创建EventItem对象
            event = EventItem.from_dict(event_data)
            events.append(event)
            
        return events
