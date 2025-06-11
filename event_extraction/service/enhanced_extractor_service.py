"""
增强型事件抽取服务

添加详细日志记录和错误处理，用于调试事件抽取问题
"""

from typing import List, Dict, Any, Optional, Union
import os
import re
import json
import time
import random
import multiprocessing
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from common.interfaces.extractor import AbstractExtractor
from common.models.chapter import Chapter
from common.models.event import EventItem
from common.utils.enhanced_logger import EnhancedLogger
from common.utils.unified_id_processor import UnifiedIdProcessor
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
        max_workers: int = 20, # 这个参数控制并行处理的最大工作线程数
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
        
        # 根据系统资源和设置调整实际使用的工作线程数
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        # 确保线程数适合CPU超线程能力, 最低6个线程
        effective_workers = max(6, min(self.max_workers, len(chapter.segments), cpu_count * 5))
        self.logger.info(f"使用 {effective_workers} 个并行线程处理 {len(chapter.segments)} 个段落 (CPU核心数: {cpu_count})")
            
        all_events = []
        failed_segments = []
        processed_count = 0
        api_failures = 0
        
        try:
            # 导入tqdm提供进度条（如果存在）
            try:
                from tqdm import tqdm
                has_tqdm = True
            except ImportError:
                has_tqdm = False
                
            # 考虑是否使用批处理
            should_batch = self._should_batch_segments(segments=chapter.segments)
            if should_batch:
                self.logger.info("启用批处理模式，将多个短段落合并处理")
                # 实现批处理逻辑 - 每2-3个段落为一组
                batch_size = 3  # 每批处理的段落数
                batch_segments = []
                batched_futures = {}
                
                # 使用线程池并行处理批次
                with ThreadPoolExecutor(max_workers=effective_workers) as executor:
                    # 按批次提交任务
                    for i, segment in enumerate(chapter.segments):
                        batch_segments.append(segment)
                        
                        # 当达到批次大小或是最后一个段落时提交任务
                        if len(batch_segments) >= batch_size or i == len(chapter.segments) - 1:
                            # 生成批次ID
                            first_id = batch_segments[0]["seg_id"]
                            last_id = batch_segments[-1]["seg_id"]
                            batch_id = f"{first_id}~{last_id}"
                            
                            # 提交批处理任务
                            future = executor.submit(
                                self._process_segments_in_batch,
                                batch_segments.copy(),
                                chapter.chapter_id
                            )
                            batched_futures[future] = (batch_id, batch_segments.copy())
                            batch_segments = []  # 清空当前批次
                    
                    # 设置进度条
                    total = len(batched_futures)
                    if has_tqdm:
                        pbar = tqdm(total=total, desc="提取事件(批处理)", unit="批次")
                    
                    # 实时处理已完成的批次
                    import concurrent.futures
                    for future in concurrent.futures.as_completed(batched_futures):
                        batch_id, segments = batched_futures[future]
                        processed_count += len(segments)
                        
                        try:
                            events = future.result()
                            if events:
                                self.logger.info(f"从批次 {batch_id} 提取到 {len(events)} 个事件")
                                all_events.extend(events)
                            else:
                                self.logger.warning(f"从批次 {batch_id} 未提取到任何事件")
                                api_failures += 1
                                for segment in segments:
                                    failed_segments.append(segment["seg_id"])
                        except Exception as e:
                            self.logger.error(f"处理批次 {batch_id} 时出错: {str(e)}")
                            api_failures += 1
                            for segment in segments:
                                failed_segments.append(segment["seg_id"])
                        
                        # 更新进度
                        if has_tqdm:
                            pbar.update(1)
                        else:
                            percent = (len(all_events) / total) * 100
                            self.logger.info(f"事件抽取进度: {len(all_events)}/{total} ({percent:.1f}%)")
                    
                    # 关闭进度条
                    if has_tqdm:
                        pbar.close()
            else:
                # 传统的逐段落并行处理
                with ThreadPoolExecutor(max_workers=effective_workers) as executor:
                    # 提交所有任务
                    future_to_segment = {
                        executor.submit(
                            self.extract_from_segment,
                            segment["text"],
                            chapter.chapter_id,
                            segment["seg_id"]
                        ): (segment["seg_id"], i)
                        for i, segment in enumerate(chapter.segments)
                    }
                    
                    # 设置进度条
                    total = len(future_to_segment)
                    completed = 0
                    
                    if has_tqdm:
                        pbar = tqdm(total=total, desc="提取事件", unit="段落")
                    
                    # 实时处理已完成的任务，使用as_completed获取最先完成的任务结果
                    import concurrent.futures
                    for future in concurrent.futures.as_completed(future_to_segment):
                        seg_id, idx = future_to_segment[future]
                        processed_count += 1
                        
                        try:
                            events = future.result()
                            if events:
                                self.logger.info(f"从段落 {seg_id} 提取到 {len(events)} 个事件")
                                all_events.extend(events)
                            else:
                                self.logger.warning(f"从段落 {seg_id} 未提取到任何事件")
                                failed_segments.append(seg_id)
                                api_failures += 1
                                
                                # 如果API失败率过高，中途切换到批处理模式
                                failure_rate = api_failures / processed_count
                                if not should_batch and processed_count > 5 and self._should_batch_segments(failure_rate=failure_rate):
                                    self.logger.warning(f"API失败率较高({failure_rate:.2%})，考虑后续使用批处理")
                                    # 在下次运行时会启用批处理
                                
                        except Exception as e:
                            self.logger.error(f"处理段落 {seg_id} 时出错: {str(e)}")
                            failed_segments.append(seg_id)
                            api_failures += 1
                        
                        # 更新进度
                        completed += 1
                        if has_tqdm:
                            pbar.update(1)
                        else:
                            percent = (completed / total) * 100
                            self.logger.info(f"事件抽取进度: {completed}/{total} ({percent:.1f}%)")
                    
                    # 关闭进度条
                    if has_tqdm:
                        pbar.close()
        
        except Exception as e:
            self.logger.error(f"事件抽取过程中发生错误: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
        # 处理完全失败的情况 - 尝试使用备用方法
        if len(all_events) == 0 and len(failed_segments) > 0:
            self.logger.warning(f"所有段落处理失败，尝试使用备用方法...")
            try:
                # 尝试将整个章节作为一个大段落处理
                if len(chapter.content) > 0:
                    self.logger.info("尝试将整个章节作为一个段落处理")
                    events = self.extract_from_segment(
                        chapter.content, 
                        chapter.chapter_id, 
                        f"{chapter.chapter_id}-full"
                    )
                    if events:
                        self.logger.info(f"从整个章节中提取到 {len(events)} 个事件")
                        all_events.extend(events)
            except Exception as e:
                self.logger.error(f"备用处理方法失败: {str(e)}")
                 # 在抽取服务中进行唯一ID处理（这是上游最早处理点，确保所有后续处理均使用唯一ID）
        if all_events:
            # 进行强制ID唯一性处理
            original_count = len(all_events)
            event_ids = [e.event_id for e in all_events]
            unique_id_count = len(set(event_ids))
            
            if len(event_ids) != unique_id_count:
                self.logger.warning(f"检测到重复ID：总事件 {original_count} 个，唯一ID仅有 {unique_id_count} 个")
                
                # 记录重复ID详情，帮助调试
                id_counts = {}
                for e_id in event_ids:
                    id_counts[e_id] = id_counts.get(e_id, 0) + 1
                duplicate_ids = [id for id, count in id_counts.items() if count > 1]
                for dup_id in duplicate_ids[:5]:  # 只记录前5个，避免日志过长
                    self.logger.warning(f"重复ID '{dup_id}' 出现 {id_counts[dup_id]} 次")
                if len(duplicate_ids) > 5:
                    self.logger.warning(f"... 另有 {len(duplicate_ids) - 5} 个重复ID未显示")
            
            all_events = UnifiedIdProcessor.ensure_unique_event_ids(all_events)
            final_count = len(all_events)
            
            if final_count != original_count:
                self.logger.warning(f"ID处理后合并了一些重复事件: {original_count} -> {final_count}")
            
            self.logger.info(f"ID唯一性处理完成，最终事件数: {final_count}，所有下游处理将使用唯一ID")
        
        # 汇报处理结果
        failure_rate = len(failed_segments) / len(chapter.segments) if chapter.segments else 0
        self.logger.info(
            f"章节事件抽取完成", 
            chapter_id=chapter.chapter_id,
            total_events=len(all_events),
            successful_segments=len(chapter.segments) - len(failed_segments),
            failed_segments=len(failed_segments),
            failure_rate=f"{failure_rate:.2%}"
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
        
        # 过滤太短的文本
        if len(text.strip()) < 10:
            self.logger.warning(f"段落 {segment_id} 内容过短，跳过处理")
            return []
        
        try:
            # 格式化提示词
            prompt = self.format_prompt(text)
            
            # 添加更详细的格式说明和提取指导
            if isinstance(prompt, dict) and "instruction" in prompt and "output_format" in self.prompt_template:
                # 添加明确的格式指导
                format_guidance = (
                    f"\n\n输出格式: {self.prompt_template['output_format']}\n"
                    f"重要提示：请确保返回的是有效的JSON格式。"
                    f"如果段落中没有明显的事件，请尝试提取任何可能的情节发展或状态变化。"
                    f"请确保每个事件至少包含'event_id'、'description'、'result'、'characters'字段。"
                )
                prompt["instruction"] += format_guidance
            
            # 保存调试信息
            if self.debug_mode:
                debug_file = self.debug_dir / f"{segment_id}_prompt.json"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump(prompt, f, ensure_ascii=False, indent=2)
            
            # 调用LLM API (添加重试机制)
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                self.logger.debug(f"发送段落 {segment_id} 的LLM请求 (尝试 {retry_count+1}/{max_retries})")
                response = self.llm_client.call_with_json_response(prompt['system'], prompt['instruction'])
                
                if response["success"] and "json_content" in response:
                    break  # 成功获取响应
                
                error_msg = response.get('error', '未知错误')
                self.logger.warning(f"段落 {segment_id} API调用第{retry_count+1}次尝试失败: {error_msg}")
                last_error = error_msg
                retry_count += 1
                
                # 添加随机延迟
                delay = random.uniform(1, 3)
                time.sleep(delay)
            
            # 保存API响应
            if self.debug_mode and "json_content" in response:
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
                error_msg = last_error or response.get('error', '未知错误')
                self.logger.error(f"段落 {segment_id} 的API调用失败: {error_msg}")
                return []
                
        except Exception as e:
            self.logger.error(f"处理段落 {segment_id} 时出现异常", error=str(e), traceback=traceback.format_exc())
            return []
            
    def _should_batch_segments(self, segments=None, failure_rate=None) -> bool:
        """
        判断是否应该批量处理段落
        
        Args:
            segments: 要处理的段落列表
            failure_rate: 当前API调用失败率
            
        Returns:
            是否应该批量处理
        """
        # 优先处理启用条件
        # 1. 如果段落数量多，文本长度适中，启用批处理可以提高效率
        if segments and len(segments) > 3:
            # 计算平均段落长度
            avg_length = sum(len(s.get('text', '')) for s in segments) / len(segments)
            # 如果平均长度适中(小于600字符)，启用批处理
            if avg_length < 600:
                self.logger.debug(f"启用批处理: 段落平均长度({avg_length:.1f}字符)适合批处理，总段落数{len(segments)}")
                return True
                
        # 2. 如果API失败率较高，尝试批处理减少API调用次数
        if failure_rate is not None and failure_rate > 0.2:
            self.logger.debug(f"启用批处理: API失败率({failure_rate:.2%})较高")
            return True
            
        # 3. 段落总数超过30，自动启用批处理以降低API负载
        if segments and len(segments) > 30:
            self.logger.debug(f"启用批处理: 段落数量过多({len(segments)}个)")
            return True
        
        # 获取环境变量配置，如果用户明确设置了启用批处理
        import os
        if os.environ.get("ENABLE_BATCH_PROCESSING", "").lower() in ["true", "1", "yes"]:
            self.logger.debug("启用批处理: 环境变量ENABLE_BATCH_PROCESSING设置为启用")
            return True
            
        return False  # 默认不启用批处理

    def _process_segments_in_batch(self, segments: List[Dict], chapter_id: str) -> List[EventItem]:
        """
        批量处理多个段落
        将多个小段落合并为一个请求，减少API调用次数
        
        Args:
            segments: 要处理的段落列表
            chapter_id: 章节ID
            
        Returns
            提取的事件列表
        """
        # 为提高处理效率，确保批次大小合适
        # 如果段落过多，可能会导致提示过长，拆分为更小的批次
        MAX_BATCH_SIZE = 5  # 最大批次大小
        MAX_CHARS = 4000    # 每批次最大字符数
        
        if len(segments) > MAX_BATCH_SIZE:
            # 将segments分成多个小批次处理
            self.logger.info(f"段落数量({len(segments)})超过批处理上限({MAX_BATCH_SIZE})，拆分为多个小批次")
            result_events = []
            # 按MAX_BATCH_SIZE大小拆分segment
            for i in range(0, len(segments), MAX_BATCH_SIZE):
                batch = segments[i:i+MAX_BATCH_SIZE]
                batch_events = self._process_segments_in_batch(batch, chapter_id)
                if batch_events:
                    result_events.extend(batch_events)
            return result_events
            
        # 检查批次文本总长度
        total_chars = sum(len(s.get('text', '')) for s in segments)
        if total_chars > MAX_CHARS:
            self.logger.info(f"批次总字符数({total_chars})超过上限({MAX_CHARS})，拆分为更小批次")
            # 找到一个合适的分割点，使两部分字符数尽量接近
            mid = len(segments) // 2
            batch1 = segments[:mid]
            batch2 = segments[mid:]
            
            # 递归处理两个批次
            events1 = self._process_segments_in_batch(batch1, chapter_id)
            events2 = self._process_segments_in_batch(batch2, chapter_id)
            
            # 合并结果
            return events1 + events2
        
        # 合并文本，使用分隔符清晰区分不同段落
        segment_texts = []
        for i, segment in enumerate(segments):
            # 添加段落编号和分隔符，帮助模型识别不同段落
            segment_texts.append(f"[段落 {i+1}]\n{segment['text']}\n")
        
        combined_text = "\n---\n".join(segment_texts)
        segment_ids = [s["seg_id"] for s in segments]
        combined_id = f"{segment_ids[0]}~{segment_ids[-1]}"
        
        self.logger.debug(f"批量处理段落 {combined_id}，共 {len(segments)} 个段落，总字符数: {len(combined_text)}")
        
        # 提取事件
        all_batch_events = self.extract_from_segment(combined_text, chapter_id, combined_id)
        
        # 没有提取到事件，直接返回空列表
        if not all_batch_events:
            return []
            
        # 智能分配事件到原始段落
        result_events = []
        
        # 根据事件描述中的关键词，尝试将事件映射到对应段落
        for event in all_batch_events:
            # 查找事件描述中是否包含段落编号指示符，如"[段落1]"、"段落2"等
            segment_idx = None
            desc = event.description.lower()
            
            # 检查是否有明确的段落标记
            for i in range(len(segments)):
                markers = [f"[段落{i+1}]", f"段落{i+1}", f"段落 {i+1}"]
                for marker in markers:
                    if marker.lower() in desc:
                        segment_idx = i
                        break
                if segment_idx is not None:
                    break
            
            # 如果没找到明确标记，尝试基于内容匹配
            if segment_idx is None:
                # 在各段落中寻找与事件描述最匹配的段落
                max_overlap = 0
                best_idx = 0
                
                for i, segment in enumerate(segments):
                    # 计算事件描述与段落内容的重叠度
                    text = segment["text"].lower()
                    # 简单计算重叠的单词数量
                    words = set(desc.split()) & set(text.split())
                    overlap = len(words)
                    
                    if overlap > max_overlap:
                        max_overlap = overlap
                        best_idx = i
                
                segment_idx = best_idx
            
            # 更新事件ID以反映正确的段落
            if segment_idx is not None:
                segment = segments[segment_idx]
                event_id_parts = event.event_id.split('-')
                if len(event_id_parts) >= 2:
                    new_id = f"{segment['seg_id'].split('-')[0]}-{event_id_parts[-1]}"
                    event.event_id = new_id
                    
            result_events.append(event)
        
        return result_events
            
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
            # 尝试处理各种可能的响应格式
            event_list = []
            
            # 处理响应中可能的多种格式
            if isinstance(response, list):
                # 如果响应直接是事件列表
                event_list = response
                self.logger.debug("响应是事件列表格式")
            elif isinstance(response, dict):
                if "events" in response:
                    # 如果响应包含events字段
                    event_list = response["events"]
                    self.logger.debug("响应是包含events字段的字典格式")
                elif any(key in response for key in ["description", "event_id", "characters"]):
                    # 如果响应本身看起来就是一个事件
                    event_list = [response]
                    self.logger.debug("响应本身是单个事件格式")
                else:
                    # 处理其他可能的字典格式，查找可能的事件列表
                    for key, value in response.items():
                        if isinstance(value, list) and len(value) > 0:
                            # 检查列表的第一个元素是否像事件对象
                            first_item = value[0]
                            if isinstance(first_item, dict) and any(k in first_item for k in ["description", "event_id"]):
                                event_list = value
                                self.logger.debug(f"从响应的'{key}'字段找到事件列表")
                                break
            
            # 如果没有找到任何事件列表，尝试创建默认事件
            if not event_list:
                self.logger.warning(f"段落 {segment_id} 未找到有效的事件列表格式，尝试构建默认事件")
                
                # 尝试从响应中提取文本内容作为事件描述
                description = ""
                if isinstance(response, dict):
                    # 寻找可能包含描述的字段
                    for field in ["content", "text", "summary", "description"]:
                        if field in response and isinstance(response[field], str) and len(response[field]) > 10:
                            description = response[field]
                            break
                elif isinstance(response, str) and len(response) > 10:
                    description = response
                
                if description:
                    # 创建默认事件
                    default_event = {
                        "event_id": f"{segment_id}-1",
                        "description": description[:200],  # 限制长度
                        "characters": [],
                        "result": "未明确",
                        "chapter_id": chapter_id
                    }
                    event_list = [default_event]
                    self.logger.debug("构建了默认事件")                # 处理每个事件
            for i, event_data in enumerate(event_list):
                # 检查是否为有效事件数据
                if not isinstance(event_data, dict):
                    self.logger.warning(f"跳过非字典格式的事件数据: {event_data}")
                    continue
                    
                # 确保事件包含描述
                if not event_data.get("description"):
                    self.logger.warning(f"跳过缺少描述的事件数据: {event_data}")
                    continue
                    
                # 生成事件ID，如果没有提供的话
                if not event_data.get("event_id"):
                    # 从segment_id提取章节部分，如"第一章-1"提取"第一章"
                    chapter_match = re.search(r'(第[^-~]+章)', segment_id)
                    chapter_part = chapter_match.group(1) if chapter_match else segment_id.split('-')[0]
                    
                    # 使用UnifiedIdProcessor对ID进行标准化
                    event_id = f"{chapter_part}-{i+1}"
                    normalized_id = UnifiedIdProcessor.normalize_event_id(event_id, chapter_id, i+1)
                    
                    event_data["event_id"] = normalized_id
                    self.logger.debug(f"为事件生成标准化ID: {event_data['event_id']}")
                    
                # 确保必要字段存在
                required_fields = {
                    "chapter_id": chapter_id,
                    "characters": [],
                    "result": "未知",
                    "location": "未指定",
                    "time": "未指定"
                }
                
                for field, default_value in required_fields.items():
                    if field not in event_data or not event_data[field]:
                        event_data[field] = default_value
                
                # 创建EventItem对象
                try:
                    event = EventItem.from_dict(event_data)
                    events.append(event)
                    short_desc = (event.description[:30] + "...") if len(event.description) > 30 else event.description
                    self.logger.debug(f"成功创建事件: {event.event_id} - {short_desc}")
                except Exception as e:
                    self.logger.error(f"创建事件对象失败", error=str(e), event_data=event_data)
        except Exception as e:
            self.logger.error(f"解析响应时出现异常", error=str(e), traceback=traceback.format_exc())
            
        return events
