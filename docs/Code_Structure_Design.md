# Mortal's Journey to Immortality Causal Graph System - Code Structure Design

According to the project's final implementation, the "Mortal's Journey to Immortality Causal Graph System" adopts a **detailed microservice code structure and module implementation framework**, satisfying the following features:

* Microservice architecture (each functional domain as an independent service)
* Each service internally uses "module division + layered design"
* Clear interfaces defined using dependency injection + abstract base classes
* JSON configuration + flexible logging system
* Multiple linker implementations that can be dynamically switched (standard, optimized, unified versions)
* Comprehensive testing mechanisms (staged testing + module testing + integration testing)
* Parallel processing optimization (configurable parallel thread control)

---

# 🏗️ Top-level Directory Structure (Project Root)

```
Project Root/                 # Project root directory
├── FINAL_SYSTEM_REPORT.md    # Final system report, summarizing project results and completion status
├── README.md                 # Project documentation, including overview, installation and usage methods
├── api_gateway/              # API Gateway Service: Unified interface entry
│   └── main.py               # Gateway entry point
├── causal_linking/           # Causal Linking Service: Analyzes causal relationships between events
│   ├── app.py                # Service entry
├── graph_builder/            # Graph Building Service: Generates visualization graphs
│   ├── app.py                # Service entry
│   ├── controller/           # Controllers
│   │   └── graph_controller.py # Graph controller
│   ├── domain/               # Domain models
│   │   └── base_renderer.py  # Renderer base class
│   ├── service/              # Service implementations
│   │   └── mermaid_renderer.py # Mermaid renderer
│   └── utils/                # Utility functions
│       └── color_map.py      # Color mapping tool
├── hallucination_refine/     # Hallucination Refinement Service: Detects and repairs hallucinations
│   ├── app.py                # Service entry
│   ├── controller/           # Controllers
│   │   └── har_controller.py # Hallucination refinement controller
│   ├── di/                   # Dependency injection
│   │   └── provider.py       # Dependency provider
│   ├── domain/               # Domain models
│   │   └── base_refiner.py   # Refiner base class
│   ├── repository/           # Data repositories
│   └── service/              # Service implementations
│       └── har_service.py    # Hallucination refinement service
├── log_doc/                  # Project logs and documentation
│   ├── tree_compare.md       # File tree comparison document
│   ├── code_redundancy_merge_optimization_report.md  # Code optimization report
│   ├── repair_plan.md        # System repair plan
│   ├── causal_graph_logic_transformation.md       # Causal graph transformation document
│   ├── parallel_processing_optimization_summary_report.md  # Parallel processing optimization report
│   ├── parallel_processing_optimization_report.md     # Detailed parallel processing report
│   ├── test_repair_completion_report.md     # Test repair report
│   └── script_integration_optimization_report.md     # Script integration report
├── main.py                   # System main entry file
├── novel/                    # Novel text directory
│   ├── 1.txt                 # Novel chapter file 1
│   ├── 2.txt                 # Novel chapter file 2
│   └── test.txt              # Test novel text
├── reports/                  # Reports directory
│   └── parallel_config_report_*.md  # Parallel configuration reports
├── scripts/                  # Utility scripts
│   ├── check_env.py          # Environment check script
│   ├── complete_test.py      # Complete test script
│   ├── fix_ids.py            # ID fix script
│   ├── refactor_demo.py      # Refactoring demonstration script
│   ├── run_demo.py           # Run demonstration script
│   └── unified_parallel_tool.py # Unified parallel tool
├── tests/                    # Tests directory
│   ├── api_tests/            # API tests
│   ├── causal_linking_tests/ # Causal linking tests
│   ├── event_extraction_tests/ # Event extraction tests
│   ├── integration_tests/    # Integration tests
│   └── stage_1 ~ stage_6/    # Staged tests
├── text_ingestion/           # Text ingestion module
│   ├── app.py                # Module entry
│   └── chapter_loader.py     # Chapter loader
│   ├── controller/            # API controllers
│   │   └── linker_controller.py # Linker controller
│   ├── di/                    # Dependency injection
│   │   └── provider.py        # Dependency provider
│   ├── domain/                # Domain definitions
│   │   └── base_linker.py     # Linker base class
│   ├── repository/            # Data access layer
│   └── service/               # Business service implementations
│       ├── README.md          # Service documentation
│       ├── base_causal_linker.py  # Base linker
│       ├── candidate_generator.py # Candidate generator
│       ├── graph_filter.py    # Graph filter
│       ├── pair_analyzer.py   # Event pair analyzer
│       └── unified_linker_service.py # Unified linker
├── common/                    # Common components: shared tools and interfaces
│   ├── config/                # Configuration files
│   │   ├── config.json        # System main configuration
│   │   ├── parallel_config.json # Parallel processing configuration
│   │   ├── prompt_causal_linking.json # Causal linking prompt configuration
│   │   ├── prompt_event_extraction.json # Event extraction prompt configuration
│   │   └── prompt_hallucination_refine.json # Hallucination refinement prompt configuration
│   ├── interfaces/            # Interface definitions
│   │   ├── extractor.py       # Extractor interface
│   │   ├── graph_renderer.py  # Graph rendering interface
│   │   ├── linker.py          # Linker interface
│   │   └── refiner.py         # Refiner interface
│   ├── models/                # Data models
│   │   ├── causal_edge.py     # Causal edge model
│   │   ├── chapter.py         # Chapter model
│   │   ├── event.py           # Event model
│   │   └── treasure.py        # Treasure model
│   └── utils/                 # Utility functions
│       ├── config_writer.py   # Configuration writer tool
│       ├── enhanced_logger.py # Enhanced logging
│       ├── json_loader.py     # JSON loading tool
│       ├── parallel_config.py # Parallel configuration tool
│       ├── path_utils.py      # Path processing tool
│       ├── text_splitter.py   # Text splitting tool
│       ├── thread_monitor.py  # Thread monitoring tool
│       └── unified_id_processor.py # Unified ID processor
│   └── chapter_loader.py      # Chapter loader
├── common/                    # Shared components directory
│   ├── models/                # Domain model definitions: core data structures
│   │   ├── causal_edge.py     # Causal edge definition
│   │   ├── chapter.py         # Chapter model
│   │   ├── event.py           # Event model
│   │   └── treasure.py        # Treasure model
│   ├── interfaces/            # Abstract interface definitions: unified interface specifications
│   │   ├── extractor.py       # Extractor interface
│   │   ├── graph_renderer.py  # Graph renderer interface
│   │   ├── linker.py          # Linker interface
│   │   └── refiner.py         # Refiner interface
│   ├── config/                # Configuration management: prompt templates and configurations
│   │   ├── config.json        # Main configuration file
│   │   ├── prompt_causal_linking.json # Causal linking prompts
│   │   ├── prompt_event_extraction.json # Event extraction prompts
│   │   └── prompt_hallucination_refine.json # Hallucination correction prompts
│   └── utils/                 # Common utility functions: logging, serialization, etc.
│       ├── enhanced_logger.py # Enhanced logging tool
│       ├── json_loader.py     # JSON tool
│       ├── path_utils.py      # Path tool
│       └── text_splitter.py   # Text splitting tool
├── scripts/                   # Auxiliary scripts: testing, performance benchmarks, and demonstrations
│   ├── check_env.py           # Environment check
│   ├── complete_test.py       # Complete process test
│   ├── test_linker.py         # Unified linker test script
│   ├── test_event_extraction.py # Event extraction test
│   ├── run_demo.py            # Run demonstration
│   └── run_all_tests.py       # Run all tests
├── tests/                     # Test directory: organized by stages
│   ├── stage_1/               # First stage tests (basic models and interfaces)
│   │   ├── test_interfaces.py # Interface tests
│   │   └── test_models.py     # Model tests
│   ├── stage_2/               # Second stage tests (basic service functionality)
│   └── stage_3/               # Third stage tests (integration tests)
├── logs/                      # Logs directory
├── novel/                     # Original novel text directory
├── debug/                     # Debug output directory
├── output/                    # Output results directory
├── main.py                    # Main program entry
├── requirements.txt           # Dependencies
└── README.md                  # Project documentation
```

---

# 🧩 Each Microservice Structure Standard (Using `causal_linking` as an example)

```
causal_linking/
├── app.py                    # FastAPI entry or Worker script
├── controller/               # External interface layer (API calls / CLI interface)
│   └── linker_controller.py
├── service/                  # Business logic layer
│   ├── linker_service.py            # Basic linker service
│   ├── optimized_linker_service.py  # Optimized linker (performance optimization)
│   └── unified_linker_service.py    # Unified linker (compatible with different implementations)
├── repository/               # Data source or external module access
├── domain/                   # Domain models and abstract interfaces
│   └── base_linker.py        # ABC linker base class
├── di/                       # Dependency injection container
│   └── provider.py
```

---

# 🧱 Core Service Design List

| Service Name              | Main Responsibility                         | Output Type             |
| ------------------------- | ------------------------------------------- | ----------------------- |
| `text_ingestion`          | Load txt novel → standard chapter JSON       | `List[Chapter]`         |
| `event_extraction`        | Extract events, treasures, characters, etc.  | `List[EventItem]`       |
| `hallucination_refine`    | Use HAR to refine LLM output                | `List[EventItem]`       |
| `causal_linking`          | Build event pairs and their causal strength  | `List[CausalEdge]`      |
| `graph_builder`           | Build Mermaid format graph code              | `str`                   |
| `api_gateway`             | Integrate all services into unified CLI/API  | `REST / CLI`            |

---

# 📦 Abstract Interfaces and Implementation (Causal Linker Example)

`common/interfaces/linker.py`

```python
from abc import ABC, abstractmethod
from typing import List
from common.models.event import EventItem
from common.models.causal_edge import CausalEdge

class AbstractLinker(ABC):
    @abstractmethod
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        """Link events, find causal relationships"""
        pass
```

`causal_linking/service/unified_linker_service.py`

```python
class UnifiedCausalLinker(AbstractLinker):
    """Unified causal linker (supports three linking strategies)"""
    
    def __init__(self, api_key, model="gpt-4o", strategy="optimized"):
        self.api_key = api_key
        self.model = model
        self.strategy = strategy
        
        # Dynamically choose the actual linker based on strategy
        if strategy == "optimized":
            self._linker = OptimizedCausalLinker(api_key=api_key, model=model)
        elif strategy == "weighted":
            self._linker = WeightedCausalLinker(api_key=api_key, model=model)
        else:
            self._linker = CausalLinker(api_key=api_key, model=model)
    
    def link_events(self, events: List[EventItem]) -> List[CausalEdge]:
        return self._linker.link_events(events)
```

---

# 🧠 Dependency Injection Upgrade (Linker Strategy Selection)

`causal_linking/di/provider.py`

```python
from common.interfaces.linker import AbstractLinker
from causal_linking.service.linker_service import CausalLinker
from causal_linking.service.optimized_linker_service import OptimizedCausalLinker
from causal_linking.service.unified_linker_service import UnifiedCausalLinker

def provide_linker(use_optimized=False, strategy=None) -> AbstractLinker:
    """Provide linker instance
    
    Args:
        use_optimized: Whether to use optimized linker
        strategy: Unified linker strategy (None means don't use unified version)
    """
    api_key = os.environ.get("LLM_API_KEY")
    model = os.environ.get("LLM_MODEL", "gpt-4o")
    
    if strategy:
        # Use unified linker
        return UnifiedCausalLinker(api_key=api_key, model=model, strategy=strategy)
    elif use_optimized:
        # Use optimized linker
        return OptimizedCausalLinker(api_key=api_key, model=model)
    else:
        # Use basic linker
        return CausalLinker(api_key=api_key, model=model)
```

---

# 📈 Testing Framework and Integration Testing

`scripts/test_linker.py` combines three linker-related test scripts:
- `test_optimized_linker.py` - Optimized linker performance test
- `test_entity_weights.py` - Entity frequency weight test
- `test_unified_linker.py` - Unified linker compatibility test

```python
def main():
    """Main function: Select test items"""
    parser = argparse.ArgumentParser(description="Causal linker testing tool")
    
    parser.add_argument(
        "--test", 
        choices=["optimized", "entity_weights", "unified", "all"],
        default="all",
        help="Type of test to run"
    )
    
    args = parser.parse_args()
    
    if args.test in ["optimized", "all"]:
        test_optimized_vs_original()
        
    if args.test in ["entity_weights", "all"]:
        test_entity_frequency_weights()
        
    if args.test in ["unified", "all"]:
        test_unified_linker_compatibility()

if __name__ == "__main__":
    main()
```

The testing framework adopts a staged strategy, from basic components to complete integration:
- `tests/stage_1/`: Basic model and interface tests
- `tests/stage_2/`: Single service functionality tests
- `tests/stage_3/`: Multi-service integration tests

---

# 🚀 Startup and Invocation

* Each service can be started as an independent microservice via `python app.py`
* `main.py` provides a complete process serial call entry
* `scripts/run_demo.py` provides a demonstration case running tool

```bash
# Run complete demonstration
python scripts/run_demo.py --input "novel/test.txt" --output "output/graph.mmd"

# Only test linker performance
python scripts/test_linker.py --test optimized
```

---
