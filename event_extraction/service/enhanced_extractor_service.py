"""
增强型事件抽取服务

添加详细日志记录和错误处理，用于调试事件抽取问题
"""

from typing import List, Dict, Any, Optional
import os
import re
import json
import traceback
from concurrent.futures import ThreadPoolExecutor

from common.interfaces.extractor import AbstractExtractor
from common.models.chapter import Chapter
from common.models.event import EventItem
from common.utils.enhanced_logger import EnhancedLogger
from event_extraction.domain.base_extractor import BaseExtractor
from event_extraction.repository.llm_client import LLMClient


class EnhancedEventExtractor(BaseExtractor):
    """增强型事件抽取器，添加详细日志记录和错误处理"""
    
    def __init__(
        self, 
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: int = 3,
        provider: str = "openai",
        debug_mode: bool = False
    ):
        """
        初始化增强型事件抽取器
        
        Args:
            model: 使用的LLM模型
            prompt_path: 提示词模板路径
            api_key: API密钥
            base_url: 自定义API基础URL
            max_workers: 并行处理的最大工作线程数
            provider: API提供商，"openai"或"deepseek"
            debug_mode: 是否启用调试模式
        """
        # 创建专用的日志记录器
        self.logger = EnhancedLogger("event_extractor", log_level="DEBUG" if debug_mode else "INFO")
        self.debug_mode = debug_mode
        
        # 记录初始化信息
        self.logger.info("初始化增强型事件抽取器", 
                        model=model, 
                        provider=provider,
                        max_workers=max_workers,
                        debug_mode=debug_mode)
        
        if not prompt_path:
            # 导入path_utils获取配置文件路径
            from common.utils.path_utils import get_config_path
            prompt_path = get_config_path("prompt_event_extraction.json")
            self.logger.debug(f"使用默认提示词模板路径: {prompt_path}")
            
        super().__init__(prompt_path)
        
        self.provider = provider
        self.model = model
        
        # 如果未提供API密钥，尝试从环境变量获取
        if not api_key:
            if provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
                if not self.api_key:
                    self.logger.error("未提供OpenAI API密钥")
                    raise ValueError("请提供OpenAI API密钥")
            else:  # deepseek
                self.api_key = os.environ.get("DEEPSEEK_API_KEY")
                if not self.api_key:
                    self.logger.error("未提供DeepSeek API密钥")
                    raise ValueError("请提供DeepSeek API密钥")
        else:
            self.api_key = api_key
            
        self.base_url = base_url
        self.max_workers = max_workers
        
        # 初始化LLM客户端
        self.llm_client = LLMClient(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            provider=self.provider
        )
        
        # 创建调试目录
        if debug_mode:
            from pathlib import Path
            from common.utils.path_utils import get_project_root
            
            self.debug_dir = Path(get_project_root()) / "debug" / "event_extraction"
            self.debug_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"调试信息将保存到: {self.debug_dir}")
        
    def extract(self, chapter: Chapter) -> List[EventItem]:
        """
        从章节中抽取事件
        
        Args:
            chapter: 章节数据
            
        Returns:
            抽取的事件列表
        """
        self.logger.info(f"开始从章节中抽取事件", chapter_id=chapter.chapter_id, title=chapter.title)
        
        if not chapter.segments:
            # 如果章节没有预定义的分段，创建分段
            from common.utils.text_splitter import TextSplitter
            self.logger.debug("章节没有预定义分段，正在创建分段")
            chapter.segments = TextSplitter.split_chapter(chapter.content)
            self.logger.info(f"创建了 {len(chapter.segments)} 个文本分段")
            
        all_events = []
        failed_segments = []
        
        # 使用线程池并行处理每个段落
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for segment in chapter.segments:
                future = executor.submit(
                    self.extract_from_segment,
                    segment["text"],
                    chapter.chapter_id,
                    segment["seg_id"]
                )
                futures.append((segment["seg_id"], future))
                
            # 收集所有结果
            for seg_id, future in futures:
                try:
                    events = future.result()
                    if events:
                        self.logger.info(f"从段落 {seg_id} 提取到 {len(events)} 个事件")
                        all_events.extend(events)
                    else:
                        self.logger.warning(f"从段落 {seg_id} 未提取到任何事件")
                        failed_segments.append(seg_id)
                except Exception as e:
                    self.logger.error(f"处理段落 {seg_id} 时出错: {str(e)}")
                    failed_segments.append(seg_id)
                    
        self.logger.info(
            f"章节事件抽取完成", 
            chapter_id=chapter.chapter_id, 
            total_events=len(all_events),
            successful_segments=len(chapter.segments) - len(failed_segments),
            failed_segments=len(failed_segments)
        )
                    
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
        self.logger.debug(f"开始处理段落 {segment_id}", text_length=len(text))
        
        try:
            # 格式化提示词
            prompt = self.format_prompt(text)
            
            # 添加更详细的格式说明
            if isinstance(prompt, dict) and "instruction" in prompt and "output_format" in self.prompt_template:
                prompt["instruction"] += f"\n\n输出格式: {self.prompt_template['output_format']}"
            
            # 保存调试信息
            if self.debug_mode:
                debug_file = self.debug_dir / f"{segment_id}_prompt.json"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump(prompt, f, ensure_ascii=False, indent=2)
            
            # 调用LLM API
            self.logger.debug(f"发送段落 {segment_id} 的LLM请求")
            response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
            
            # 保存API响应
            if self.debug_mode:
                debug_file = self.debug_dir / f"{segment_id}_response.json"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump(response, f, ensure_ascii=False, indent=2)
            
            if response["success"] and "json_content" in response:
                # 解析响应
                events = self.parse_response(response["json_content"], chapter_id, segment_id)
                self.logger.debug(f"段落 {segment_id} 抽取到 {len(events)} 个事件")
                
                # 保存解析后的事件
                if self.debug_mode:
                    debug_file = self.debug_dir / f"{segment_id}_events.json"
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        json.dump([event.to_dict() for event in events], f, ensure_ascii=False, indent=2)
                
                return events
            else:
                error_msg = response.get('error', '未知错误')
                self.logger.error(f"段落 {segment_id} 的API调用失败: {error_msg}")
                return []
        except Exception as e:
            self.logger.error(f"处理段落 {segment_id} 时出现异常", error=str(e), traceback=traceback.format_exc())
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
        self.logger.debug(f"解析段落 {segment_id} 的响应")
        events = []
        
        try:
            # 处理响应中可能的多种格式
            if isinstance(response, list):
                # 如果响应直接是事件列表
                event_list = response
                self.logger.debug("响应是事件列表格式")
            elif isinstance(response, dict) and "events" in response:
                # 如果响应包含events字段
                event_list = response["events"]
                self.logger.debug("响应是包含events字段的字典格式")
            else:
                # 假设响应本身就是单个事件
                event_list = [response]
                self.logger.debug("响应被视为单个事件")
                
            for i, event_data in enumerate(event_list):
                # 检查是否为有效事件数据
                if not isinstance(event_data, dict):
                    self.logger.warning(f"跳过非字典格式的事件数据: {event_data}")
                    continue
                    
                if not event_data.get("description"):
                    self.logger.warning(f"跳过缺少描述的事件数据: {event_data}")
                    continue
                    
                # 生成事件ID，如果没有提供的话
                if not event_data.get("event_id"):
                    # 从segment_id提取章节部分，如"第一章-1"提取"第一章"
                    chapter_match = re.search(r'(第[^-]+章)', segment_id)
                    chapter_part = chapter_match.group(1) if chapter_match else segment_id.split('-')[0]
                    event_data["event_id"] = f"{chapter_part}-{i+1}"
                    self.logger.debug(f"为事件生成ID: {event_data['event_id']}")
                    
                # 确保chapter_id已设置
                event_data["chapter_id"] = chapter_id
                
                # 创建EventItem对象
                try:
                    event = EventItem.from_dict(event_data)
                    events.append(event)
                    self.logger.debug(f"成功创建事件: {event.event_id} - {event.description[:30]}...")
                except Exception as e:
                    self.logger.error(f"创建事件对象失败", error=str(e), event_data=event_data)
        except Exception as e:
            self.logger.error(f"解析响应时出现异常", error=str(e), traceback=traceback.format_exc())
            
        return events
