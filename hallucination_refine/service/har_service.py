from typing import List, Dict, Any, Optional
import json
import os
from concurrent.futures import ThreadPoolExecutor

from common.interfaces.refiner import AbstractRefiner
from common.models.event import EventItem
from hallucination_refine.domain.base_refiner import BaseRefiner
from event_extraction.repository.llm_client import LLMClient


class HallucinationRefiner(BaseRefiner):
    """幻觉修复器实现类，使用HAR算法修复LLM输出中可能的幻觉"""
    
    def __init__(
        self, 
        model: str = "gpt-4o", 
        prompt_path: str = "", 
        api_key: str = "",
        base_url: str = "",
        max_workers: int = 3,
        max_iterations: int = 2,
        provider: str = "openai"
    ):
        """
        初始化幻觉修复器
        
        Args:
            model: 使用的LLM模型
            prompt_path: 提示词模板路径
            api_key: OpenAI API密钥
            base_url: 自定义API基础URL
            max_workers: 并行处理的最大工作线程数
            max_iterations: 最大迭代次数，防止无限循环
        """
        if not prompt_path:
            # 导入path_utils获取配置文件路径
            from common.utils.path_utils import get_config_path
            prompt_path = get_config_path("prompt_hallucination_refine.json")
            
        super().__init__(prompt_path)
        
        # 如果未提供API密钥，尝试从环境变量获取
        if not api_key:
            if provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
                if not self.api_key:
                    raise ValueError("请提供 OpenAI API 密钥")
            elif provider == "deepseek":
                self.api_key = os.environ.get("DEEPSEEK_API_KEY")
                if not self.api_key:
                    raise ValueError("请提供 DeepSeek API 密钥")
            else:
                raise ValueError(f"不支持的 API 提供商: {provider}")
        else:
            self.api_key = api_key
            
        self.model = model
        self.base_url = base_url
        self.max_workers = max_workers
        self.max_iterations = max_iterations
        self.provider = provider
        
        # 初始化LLM客户端
        self.llm_client = LLMClient(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            provider=self.provider
        )
    
    def refine(self, events: List[EventItem], context: str = "") -> List[EventItem]:
        """
        对事件列表进行幻觉检测和修复
        
        Args:
            events: 待精修的事件列表
            context: 支持精修的上下文信息
            
        Returns:
            精修后的事件列表
        """
        if not context:
            context = "请基于您对《凡人修仙传》的了解，检测以下事件中可能存在的幻觉或错误。"
            
        refined_events = []
        
        # 使用线程池并行处理每个事件
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 优化后的实现 - 使用as_completed等待完成的任务
            # 同时提交所有事件处理任务
            future_to_event = {executor.submit(self.refine_event, event, context): event for event in events}
            
            print(f"使用 {self.max_workers} 个工作线程并行处理 {len(events)} 个事件")
            
            # 统计完成的任务数量
            completed = 0
            total = len(events)
            
            # 实时收集已完成的任务结果
            from concurrent.futures import as_completed
            for future in as_completed(future_to_event):
                original_event = future_to_event[future]
                completed += 1
                
                try:
                    refined_event = future.result()
                    refined_events.append(refined_event)
                    
                    # 打印进度
                    if completed % max(1, total // 10) == 0 or completed == total:
                        print(f"幻觉修复进度: {completed}/{total} ({(completed/total)*100:.1f}%)")
                        
                except Exception as e:
                    print(f"处理事件 {original_event.event_id} 时出错: {str(e)}")
                    # 如果处理失败，保留原始事件
                    refined_events.append(original_event)
                    
        return refined_events
    
    def refine_event(self, event: EventItem, context: str) -> EventItem:
        """
        对单个事件进行幻觉检测和修复
        
        Args:
            event: 待精修的事件
            context: 支持精修的上下文信息
            
        Returns:
            精修后的事件
        """
        current_event = event
        iterations = 0
        
        while iterations < self.max_iterations:
            print(f"对事件 {event.event_id} 进行第 {iterations+1} 次精修...")
            
            # 格式化提示
            prompt = self.format_prompt(current_event, context)
            
            # 调用LLM
            response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
            
            if not response["success"] or "json_content" not in response:
                print(f"事件 {event.event_id} 的精修请求失败: {response.get('error', '未知错误')}")
                break
                
            # 解析响应
            refined_event = self.parse_response(response["json_content"], current_event)
            
            # 检查是否还有幻觉
            has_hallucination = response["json_content"].get("has_hallucination", False)
            
            if not has_hallucination:
                # 如果没有检测到幻觉，返回当前版本
                print(f"事件 {event.event_id} 精修完成，无幻觉")
                return refined_event
                
            # 更新事件，进行下一次迭代
            current_event = refined_event
            iterations += 1
            
            # 打印修正信息
            if "issues" in response["json_content"]:
                for issue in response["json_content"]["issues"]:
                    print(f"- 修正: {issue.get('field')} 从 '{issue.get('original')}' 到 '{issue.get('corrected')}'")
        
        # 如果达到最大迭代次数，返回最终版本
        if iterations == self.max_iterations:
            print(f"事件 {event.event_id} 达到最大迭代次数 {self.max_iterations}，返回当前版本")
            
        return current_event
    
    def parse_response(self, response: Dict[str, Any], original_event: EventItem) -> EventItem:
        """
        解析LLM响应，更新事件
        
        Args:
            response: LLM响应
            original_event: 原始事件
            
        Returns:
            精修后的事件
        """
        # 检查响应中是否有精修后的事件
        if "refined_event" in response and isinstance(response["refined_event"], dict):
            # 使用精修后的事件创建新的EventItem对象
            refined_event_data = response["refined_event"]
            
            # 确保事件ID和章节ID保持不变
            refined_event_data["event_id"] = original_event.event_id
            if not refined_event_data.get("chapter_id") and original_event.chapter_id:
                refined_event_data["chapter_id"] = original_event.chapter_id
            
            # 对于不完整的响应，使用原始事件的字段填充缺失的字段
            original_data = original_event.to_dict()
            for field, value in original_data.items():
                if field not in refined_event_data or refined_event_data[field] is None:
                    refined_event_data[field] = value
                
            return EventItem.from_dict(refined_event_data)
        
        # 如果没有精修后的事件，检查是否有修正列表
        if "issues" in response and isinstance(response["issues"], list):
            # 创建原始事件的副本
            refined_data = original_event.to_dict()
            
            # 应用修正
            for issue in response["issues"]:
                field = issue.get("field")
                corrected = issue.get("corrected")
                
                if field and corrected is not None:
                    # 应用修正到相应字段
                    refined_data[field] = corrected
                    
            return EventItem.from_dict(refined_data)
            
        # 如果没有修正信息，返回原始事件
        return original_event
