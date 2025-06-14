# "Mortal's Journey to Immortality" Causal Event Knowledge Graph Generation System

## WEB: https://fanrenxiuxianzhuan-fm16b8k.gamma.site/

## 📚 Project Documentation

### Design Documents
- [Code Structure Design](docs/Code_Structure_Design.md) - Detailed design of project architecture and module division
- [Project Logic Design](docs/Project_Logic_Design.md) - System workflow and business logic explanation
- [Development Plan](docs/Development_Plan.md) - Project development plan and implementation scheme
- [Theoretical Support](docs/Theoretical_Support.md) - Project-related theoretical foundation and research background
- [File Tree](docs/note/File_Tree) - Complete project directory structure description

🚀 **Project Status**: Production Ready | **Test Coverage**: All 125 test cases passed ✅

This project is an AI-based automation tool specially designed to analyze the novel "Mortal's Journey to Immortality", extract key events, identify causal relationships, and generate visualized causal event knowledge graphs. The system adopts an advanced microservice architecture, integrates multiple large language models, and implements intelligent event extraction, hallucination repair, causal linking, and graph visualization functions.

## ✨ Core Features

- 🧠 **AI-driven**: Intelligent text analysis based on GPT-4o and DeepSeek
- 🔍 **Precise Extraction**: Automatically identifies events, characters, and treasure relationships in the novel
- 🔗 **Causal Analysis**: Intelligently identifies causal relationships between events and quantifies intensity
- 📊 **Visualization**: Generates intuitive Mermaid flowcharts
- 🛠️ **Ease of Use**: Friendly CLI interface, supporting batch processing
- 🏗️ **Enterprise Grade**: Complete test coverage, production-ready code quality

## 🚀 Quick Start

### 1. Environment Preparation
```bash
# Clone the project
git clone <repository-url>
cd Fianl_HW

# Install Python dependencies
pip install -r requirements.txt

# Configure API key (choose one)
export OPENAI_API_KEY="your-openai-api-key"
# or
export DEEPSEEK_API_KEY="your-deepseek-api-key"
```

### 2. Run Demo
```bash
# Experience system functionality
python main.py --demo
```

### 3. Process Custom Files
```bash
# Single file processing
python main.py --input your_novel.txt

# Batch processing directory
python main.py --batch input_directory/

# Environment check
python main.py --check-env
```

### 4. Interactive Mode
```bash
# Start interactive interface
python main.py
```

## 🏗️ System Architecture

The system adopts a microservice architecture, including 6 core modules:

### Core Modules
1. **📚 Text Ingestion** - Text file reading and chapter segmentation
2. **🔍 Event Extraction** - LLM-based intelligent event identification
3. **🛠️ Hallucination Adjustment and Refinement (HAR)** - Event information verification and correction
4. **🔗 Causal Pattern Connection (CPC)** - Causal relationship identification and DAG construction
5. **📊 Graph Building** - Mermaid graph generation
6. **🌐 API Gateway** - Unified service call interface

### Data Flow
```
Raw Text → Chapter Parsing → Event Extraction → Hallucination Correction → Causal Linking → Graph Rendering → Visual Output
```

## ⚙️ Installation and Configuration

### System Requirements
- **Python**: 3.10+ (3.10.12 recommended)
- **Operating System**: Linux / macOS / Windows
- **Memory**: Minimum 4GB, 8GB+ recommended
- **Storage**: At least 1GB available space

### API Provider Support
- **OpenAI GPT-4o** (recommended)
- **DeepSeek Chat** (economical choice)

### Detailed Installation Steps

1. **Python Environment Preparation**
```bash
# Check Python version
python --version  # requires 3.10+

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

2. **Install Project Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Keys**
```bash
# Method 1: Environment variables (recommended)
export OPENAI_API_KEY="sk-your-openai-api-key"
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# Method 2: Configuration file
cp .env.example .env
# Edit the .env file and fill in the keys
```

## 📖 Usage Guide

### Command Line Parameter Description

| Parameter | Description | Example |
|------|------|------|
| `--demo` | Run demo mode | `python main.py --demo` |
| `--input <file>` | Process a single file | `python main.py --input novel.txt` |
| `--batch <dir>` | Batch process directory | `python main.py --batch novels/` |
| `--test` | Run system tests | `python main.py --test` |
| `--benchmark` | Run performance benchmark | `python main.py --benchmark` |
| `--check-env` | Check environment configuration | `python main.py --check-env` |
| `--verbose` | Display detailed logs | `python main.py --input file.txt --verbose` |

### Output File Description

The system creates timestamped folders in the `output/` directory, containing:

- **`events.json`** - Extracted structured event data
- **`refined_events.json`** - Corrected event data
- **`causal_edges.json`** - Identified causal relationship data
- **`causal_graph.mmd`** - Causal graph in Mermaid format
- **`processing_log.txt`** - Detailed processing log

### Output Examples

#### Event Data Example (events.json)
```json
{
  "events": [
    {
      "id": "E1-1",
      "description": "Han Li consumes Gathering Spirit Pill to break through Qi Condensation Stage",
      "characters": ["Han Li"],
      "treasures": ["Gathering Spirit Pill"],
      "location": "Green Bull Town",
      "timestamp": "Early cultivation period",
      "event_type": "cultivation"
    }
  ]
}
```

#### Mermaid Graph Example
```mermaid
graph TD
    E1["Han Li consumes<br/>Gathering Spirit Pill<br/>to break through Qi Condensation Stage"]
    E2["Obtains mysterious bottle<br/>discovers green liquid effect"]
    
    E1 -->|leads to| E2
    
    classDef cultivation fill:#e1f5fe
    classDef treasure fill:#fff3e0
    class E1 cultivation
    class E2 treasure
```

## 🧪 Testing and Quality Assurance

### Running Tests

```bash
# Run all tests (125 test cases)
python tests/run_all_tests.py

# Run specific stage tests
python tests/stage_1/run_tests.py  # Basic model tests
python tests/stage_2/run_tests.py  # Text ingestion tests
python tests/stage_3/run_tests.py  # Hallucination correction tests
python tests/stage_4/run_tests.py  # Causal linking tests
python tests/stage_5/run_tests.py  # Graph building tests
python tests/stage_6/run_tests.py  # Integration tests
```

### Test Coverage
- **Total Test Cases**: 125
- **Pass Rate**: 100% ✅
- **Code Coverage**: 95%+
- **Module Coverage**: All core modules fully covered

## 🔧 Technical Architecture Details

### Dependency Injection System
The system uses a lightweight DI container to manage dependencies:

```python
from common.models.dependency_provider import DependencyProvider

# Get service instance
extractor = DependencyProvider.get_event_extractor()
linker = DependencyProvider.get_causal_linker()
```

### LLM Integration
Seamless switching between multiple LLM providers:

```python
from event_extraction.repository.llm_client import LLMClient

# Automatically select available API provider
client = LLMClient()
response = client.call_llm(system_prompt, user_prompt)
```

## 📊 Performance Metrics

### Processing Capacity
- **Small Files** (<10KB): Processing time <30 seconds
- **Medium Files** (10-100KB): Processing time <2 minutes
- **Large Files** (>100KB): Processing time increases linearly with file size

### Resource Usage
- **Memory Usage**: Peak <500MB
- **Concurrent Processing**: Supports 2-4 concurrent event extraction tasks
- **API Calls**: Smart frequency control, avoiding rate limits

### Scalability
- **Event Count**: Supports 1000+ events
- **Relationship Count**: Supports 5000+ causal relationships
- **Batch Processing**: Supports 100+ files

## 🚨 Common Issues

### Q: What if API calls fail?
**A**: Check API key configuration, confirm sufficient quota, use `--check-env` to check environment.

### Q: How to optimize slow processing?
**A**: Adjust concurrency count, use faster API providers, or segment large files for processing.

### Q: What if the output graph is not accurate enough?
**A**: Parameters can be adjusted, or use stronger models like GPT-4o. The system continuously optimizes algorithms.

### Q: How to process other types of novels?
**A**: Currently optimized specifically for "Mortal's Journey to Immortality", processing other novels may require prompt adjustments.

## 🤝 Contribution Guidelines

Community contributions are welcome! Please follow these steps:

1. Fork this project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Environment Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run code formatting
black .

# Run type checking
mypy .

# Run complete test suite
python tests/run_all_tests.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- **"Mortal's Journey to Immortality"** - Written by Wang Yu, providing rich analysis material for this project
- **OpenAI & DeepSeek** - Providing powerful language model support
- **Mermaid** - Excellent chart rendering tool
- **Python Community** - Rich open-source ecosystem

---

> 🌟 If this project is helpful to you, please give us a Star!
