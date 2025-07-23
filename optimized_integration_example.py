
# 在 unified_linker_service.py 中集成优化版本

class UnifiedLinkerService:
    def __init__(self, config_path: str = "common/config/config.json"):
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 选择分析器版本
        if self.config.get("use_optimized_analyzer", True):
            from causal_linking.service.optimized_pair_analyzer import OptimizedPairAnalyzer
            self.pair_analyzer = OptimizedPairAnalyzer(
                model=self.config.get("model", "gpt-4o"),
                enable_cache=self.config.get("enable_cache", True),
                enable_performance_tracking=True,
                max_workers=self.config.get("max_workers", 3)
            )
            print("✅ 使用优化版因果分析器")
        else:
            from causal_linking.service.pair_analyzer import PairAnalyzer  
            self.pair_analyzer = PairAnalyzer(
                model=self.config.get("model", "gpt-4o"),
                max_workers=self.config.get("max_workers", 3)
            )
            print("⚠️ 使用原版因果分析器")
    
    def analyze_causal_relationships(self, events):
        """分析因果关系 - 保持接口兼容性"""
        # 生成事件对
        event_pairs = self._generate_event_pairs(events)
        
        # 批量分析（接口统一）
        edges = self.pair_analyzer.analyze_batch(event_pairs)
        
        # 性能监控（如果支持）
        if hasattr(self.pair_analyzer, 'get_performance_stats'):
            stats = self.pair_analyzer.get_performance_stats()
            self._log_performance(stats)
        
        return edges
    
    def _log_performance(self, stats):
        """记录性能数据"""
        print(f"性能统计: 处理 {stats['total_pairs_analyzed']} 对事件")
        print(f"缓存命中率: {stats['cache_hit_rate_percent']:.1f}%")
        print(f"成功率: {stats['success_rate_percent']:.1f}%")
