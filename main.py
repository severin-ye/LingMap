#!/usr/bin/env python3
"""
# [CN] 《凡人修仙传》因果事件图谱生成系统 - 主入口文件
# [EN] A Record of a Mortal's Journey to Immortality Causal Event Graph Generation System - Main Entry File

# [CN] 基于R2框架的因果事件图谱生成系统，用于从《凡人修仙传》小说文本中自动抽取事件，并建立因果关系图谱。
# [EN] A causal event graph generation system based on R2 framework for automatically extracting events from A Record of a Mortal's Journey to Immortality novel text and establishing causal relationship graphs.

# [CN] 支持事件抽取、幻觉修复、因果关系链接和图谱可视化功能。
# [EN] Supports event extraction, hallucination refinement, causal relationship linking and graph visualization functions.

# [CN] 使用示例:
# [EN] Usage examples:
    python main.py                         # [CN] 交互式模式 [EN] Interactive mode
    python main.py --demo                  # [CN] 运行演示 [EN] Run demo
    python main.py --input novel/test.txt  # [CN] 处理指定文件 [EN] Process specified file
    python main.py --batch novel/          # [CN] 批量处理目录 [EN] Batch process directory
"""

import os
import sys
import time
import logging
import argparse
import multiprocessing
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

# [CN] 示例小说文件路径
# [EN] Example novel file path
file_name= Path(__file__).parent / "novel" / "test.txt"

# [CN] 确保项目路径正确
# [EN] Ensure project path is correct
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# [CN] 导入并行处理配置和线程监控
# [EN] Import parallel processing configuration and thread monitoring
from common.utils.parallel_config import ParallelConfig
from common.utils.thread_monitor import ThreadUsageMonitor

# [CN] 初始化并行配置
# [EN] Initialize parallel configuration
ParallelConfig.initialize()

# [CN] 设置日志
# [EN] Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

# [CN] 初始化线程监控
# [EN] Initialize thread monitoring
thread_monitor = ThreadUsageMonitor.get_instance()


def print_banner():
    """
    # [CN] 打印系统横幅
    # [EN] Print system banner
    """
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                  《凡人修仙传》因果事件图谱生成系统                               ║
║                                                                              ║
║    基于R2框架的智能因果关系图谱生成系统                                          ║
║    支持事件抽取、幻觉修复、因果分析、图谱可视化                                    ║
║                                                                              ║
║    🧠 事件抽取    🔧 幻觉修复    🔗 因果分析    📊 图谱生成                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def setup_environment():
    """
    # [CN] 设置运行环境
    # [EN] Set up runtime environment
    """
    # [CN] 尝试加载.env文件
    # [EN] Try to load .env file
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logger.info("已加载 .env 文件")  # [CN] 已加载 .env 文件 [EN] Loaded .env file
            
            # [CN] 确保API密钥可用（大写变量名）
            # [EN] Ensure API keys are available (uppercase variable names)
            if "openai_api_key" in os.environ:
                os.environ["OPENAI_API_KEY"] = os.environ["openai_api_key"]
                logger.info("已设置 OpenAI API 密钥")  # [CN] 已设置 OpenAI API 密钥 [EN] Set OpenAI API key
                
            if "deepseek_api_key" in os.environ:
                os.environ["DEEPSEEK_API_KEY"] = os.environ["deepseek_api_key"]
                logger.info("已设置 DeepSeek API 密钥")  # [CN] 已设置 DeepSeek API 密钥 [EN] Set DeepSeek API key
                
        except ImportError:
            logger.warning("未安装 python-dotenv，跳过 .env 文件加载")  # [CN] 未安装 python-dotenv，跳过 .env 文件加载 [EN] python-dotenv not installed, skipping .env file loading
    else:
        # [CN] 创建示例.env文件如果不存在
        # [EN] Create example .env file if it doesn't exist
        env_example = PROJECT_ROOT / ".env.example"
        if env_example.exists() and not env_file.exists():
            logger.info("未找到 .env 文件，正在创建默认配置...")  # [CN] 未找到 .env 文件，正在创建默认配置... [EN] .env file not found, creating default configuration...
            try:
                import shutil
                shutil.copy(env_example, env_file)
                logger.info(f"已创建 .env 文件，请编辑 {env_file} 设置您的 API 密钥")  # [CN] 已创建 .env 文件，请编辑 {env_file} 设置您的 API 密钥 [EN] Created .env file, please edit {env_file} to set your API keys
            except Exception as e:
                logger.warning(f"创建 .env 文件失败: {e}")  # [CN] 创建 .env 文件失败: {e} [EN] Failed to create .env file: {e}
    
    # [CN] 创建必要的目录
    # [EN] Create necessary directories
    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    
    temp_dir = PROJECT_ROOT / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    novel_dir = PROJECT_ROOT / "novel"
    novel_dir.mkdir(exist_ok=True)
    
    # [CN] 设置系统环境变量
    # [EN] Set system environment variables
    if "MAX_WORKERS" not in os.environ:
        cpu_count = multiprocessing.cpu_count()
        optimal_workers = max(2, min(8, cpu_count))
        os.environ["MAX_WORKERS"] = str(optimal_workers)
    
    if "LLM_PROVIDER" not in os.environ:
        os.environ["LLM_PROVIDER"] = "deepseek"  # [CN] 默认使用 DeepSeek [EN] Default to DeepSeek
        
    # [CN] 初始化并行配置
    # [EN] Initialize parallel configuration
    ParallelConfig.initialize()


def create_example_novel():
    """
    # [CN] 创建示例小说文件
    # [EN] Create example novel file
    """
    test_file = file_name
    example_content = """《凡人修仙传》

作者：忘语

第一章山边小村

二愣子睁大着双眼，直直望着茅草和烂泥糊成的黑屋顶，身上盖着的旧棉被，已呈深黄色，看不出原来的本来面目，还若有若无的散着淡淡的霉味。

在他身边紧挨着的另一人，是二哥韩铸，酣睡的十分香甜，从他身上不时传来轻重不一的阵阵打呼声。

离床大约半丈远的地方，是一堵黄泥糊成的土墙，因为时间过久，墙壁上裂开了几丝不起眼的细长口子，从这些裂纹中，隐隐约约的传来韩母唠唠叨叨的埋怨声，偶尔还掺杂着韩父，抽旱烟杆的"啪嗒""啪嗒"吸允声。

二愣子缓缓的闭上已有些涩的双目，迫使自己尽早进入深深的睡梦中。他心里非常清楚，再不老实入睡的话，明天就无法早起些了，也就无法和其他约好的同伴一起进山拣干柴。

二愣子姓韩名立，这么像模像样的名字,他父母可起不出来，这是他父亲用两个粗粮制成的窝头，求村里老张叔给起的名字。

老张叔年轻时，曾经跟城里的有钱人当过几年的伴读书童，是村里唯一认识几个字的读书人，村里小孩子的名字，倒有一多半是他给起的。
"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(example_content)
    
    return test_file


def check_environment():
    """
    # [CN] 检查运行环境
    # [EN] Check runtime environment
    """
    print("🔍 检查运行环境...")  # [CN] 检查运行环境... [EN] Checking runtime environment...
    
    # [CN] 检查Python版本
    # [EN] Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8+")  # [CN] Python版本过低，需要Python 3.8+ [EN] Python version too low, requires Python 3.8+
        return False
    
    print(f"✅ Python版本: {sys.version.split()[0]}")  # [CN] Python版本: [EN] Python version:
    
    # [CN] 检查必要的包
    # [EN] Check required packages
    required_packages = [
        'requests', 'openai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    # [CN] 单独检查python-dotenv（因为它可能会以不同方式安装）
    # [EN] Separately check python-dotenv (as it might be installed differently)
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing_packages.append('python-dotenv')
    
    if missing_packages:
        print(f"⚠️ 缺少以下包: {', '.join(missing_packages)}")  # [CN] 缺少以下包: [EN] Missing packages:
        print("💡 可运行: pip install -r requirements.txt")  # [CN] 可运行: pip install -r requirements.txt [EN] You can run: pip install -r requirements.txt
    else:
        print("✅ 所有必要的包都已安装")  # [CN] 所有必要的包都已安装 [EN] All required packages are installed
    
    # [CN] 检查API密钥
    # [EN] Check API keys
    has_api_key = False
    if os.getenv('OPENAI_API_KEY'):
        print("✅ 检测到 OpenAI API 密钥")  # [CN] 检测到 OpenAI API 密钥 [EN] Detected OpenAI API key
        has_api_key = True
    if os.getenv('DEEPSEEK_API_KEY'):
        print("✅ 检测到 DeepSeek API 密钥")  # [CN] 检测到 DeepSeek API 密钥 [EN] Detected DeepSeek API key
        has_api_key = True
    
    if not has_api_key:
        print("⚠️ 未检测到API密钥，请设置环境变量或.env文件")  # [CN] 未检测到API密钥，请设置环境变量或.env文件 [EN] No API keys detected, please set environment variables or .env file
        print("💡 支持的API: OPENAI_API_KEY, DEEPSEEK_API_KEY")  # [CN] 支持的API: OPENAI_API_KEY, DEEPSEEK_API_KEY [EN] Supported APIs: OPENAI_API_KEY, DEEPSEEK_API_KEY
    
    # [CN] 检查配置文件
    # [EN] Check configuration files
    config_file = PROJECT_ROOT / "common" / "config" / "config.json"
    if not config_file.exists():
        print(f"⚠️ 配置文件不存在: {config_file}")  # [CN] 配置文件不存在: [EN] Configuration file does not exist:
    else:
        print("✅ 配置文件存在")  # [CN] 配置文件存在 [EN] Configuration file exists
    
    # [CN] 检查测试数据
    # [EN] Check test data
    test_file = PROJECT_ROOT / "novel" / "test.txt"
    if not test_file.exists():
        print(f"⚠️ 测试文件不存在: {test_file}")  # [CN] 测试文件不存在: [EN] Test file does not exist:
    else:
        print("✅ 测试文件存在")  # [CN] 测试文件存在 [EN] Test file exists
    
    print("✅ 环境检查完成\n")  # [CN] 环境检查完成 [EN] Environment check completed
    return True


def run_demo(provider: str = "deepseek") -> bool:
    """
    # [CN] 运行演示模式
    # [EN] Run demo mode
    """
    print("🎬 运行演示模式...")  # [CN] 运行演示模式... [EN] Running demo mode...
    
    # [CN] 检查演示文件
    # [EN] Check demo file
    demo_file = PROJECT_ROOT / "novel" / "test.txt"
    if not demo_file.exists():
        print(f"❌ 演示文件不存在: {demo_file}")  # [CN] 演示文件不存在: [EN] Demo file does not exist:
        return False
    
    # [CN] 运行演示
    # [EN] Run demo
    from api_gateway.main import process_text
    
    output_dir = PROJECT_ROOT / "output" / f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    temp_dir = output_dir / "temp"
    
    try:
        process_text(
            text_path=str(demo_file),
            output_dir=str(output_dir),
            temp_dir=str(temp_dir),
            provider=provider
        )
        print(f"\n🎉 演示完成！结果保存在: {output_dir}")  # [CN] 演示完成！结果保存在: [EN] Demo completed! Results saved in:
        return True
    except Exception as e:
        print(f"❌ 演示运行失败: {e}")  # [CN] 演示运行失败: [EN] Demo run failed:
        logger.exception("演示运行失败")  # [CN] 演示运行失败 [EN] Demo run failed
        return False


def run_tests():
    """
    # [CN] 运行测试套件
    # [EN] Run test suite
    """
    print("🧪 运行测试套件...")  # [CN] 运行测试套件... [EN] Running test suite...
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "tests.run_all_tests"
        ], cwd=PROJECT_ROOT)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")  # [CN] 运行测试失败: [EN] Running tests failed:
        logger.exception("运行测试失败")  # [CN] 运行测试失败 [EN] Running tests failed
        return False


def run_benchmark():
    """
    # [CN] 运行性能基准测试
    # [EN] Run performance benchmark test
    """
    print("⚡ 运行性能基准测试...")  # [CN] 运行性能基准测试... [EN] Running performance benchmark test...
    
    try:
        # [CN] 使用subprocess运行性能测试脚本
        # [EN] Use subprocess to run performance test script
        import subprocess
        benchmark_script = PROJECT_ROOT / "scripts" / "performance_benchmark.py"
        
        if not benchmark_script.exists():
            print(f"❌ 性能测试脚本不存在: {benchmark_script}")  # [CN] 性能测试脚本不存在: [EN] Performance test script does not exist:
            return False
            
        result = subprocess.run(
            [sys.executable, str(benchmark_script)],
            cwd=PROJECT_ROOT
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")  # [CN] 性能测试失败: [EN] Performance test failed:
        logger.exception("性能测试失败")  # [CN] 性能测试失败 [EN] Performance test failed
        return False


def process_file(input_file: Path, output_dir: Path, provider: str = "deepseek") -> bool:
    """
    # [CN] 处理单个文件
    # [EN] Process single file
    """
    print(f"\n📄 处理文件: {input_file.name}")  # [CN] 处理文件: [EN] Processing file:
    
    if not input_file.exists():
        print(f"❌ 文件不存在: {input_file}")  # [CN] 文件不存在: [EN] File does not exist:
        return False
    
    try:
        from api_gateway.main import process_text
        process_text(
            text_path=str(input_file),
            output_dir=str(output_dir),
            provider=provider
        )
        print(f"✅ 处理完成！结果保存在: {output_dir}")  # [CN] 处理完成！结果保存在: [EN] Processing completed! Results saved in:
        return True
    except Exception as e:
        print(f"❌ 处理失败: {e}")  # [CN] 处理失败: [EN] Processing failed:
        logger.exception(f"处理文件 {input_file} 失败")  # [CN] 处理文件 {input_file} 失败 [EN] Processing file {input_file} failed
        return False


def process_directory(input_dir: Path, output_dir: Path, provider: str = "deepseek") -> bool:
    """
    # [CN] 批量处理目录
    # [EN] Batch process directory
    """
    print(f"\n📂 批量处理目录: {input_dir}")  # [CN] 批量处理目录: [EN] Batch processing directory:
    
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"❌ 目录不存在: {input_dir}")  # [CN] 目录不存在: [EN] Directory does not exist:
        return False
    
    # [CN] 获取所有txt文件
    # [EN] Get all txt files
    txt_files = list(input_dir.glob("*.txt"))
    if not txt_files:
        print(f"❌ 目录中没有找到txt文件: {input_dir}")  # [CN] 目录中没有找到txt文件: [EN] No txt files found in directory:
        return False
    
    print(f"📚 找到 {len(txt_files)} 个txt文件")  # [CN] 找到 {len(txt_files)} 个txt文件 [EN] Found {len(txt_files)} txt files
    
    try:
        from api_gateway.main import process_directory as api_process_directory
        api_process_directory(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            provider=provider
        )
        print(f"✅ 批量处理完成！结果保存在: {output_dir}")  # [CN] 批量处理完成！结果保存在: [EN] Batch processing completed! Results saved in:
        return True
    except Exception as e:
        print(f"❌ 批量处理失败: {e}")  # [CN] 批量处理失败: [EN] Batch processing failed:
        logger.exception(f"处理目录 {input_dir} 失败")  # [CN] 处理目录 {input_dir} 失败 [EN] Processing directory {input_dir} failed
        return False


def run_interactive():
    """
    # [CN] 运行交互式模式
    # [EN] Run interactive mode
    """
    print("🔄 进入交互式模式...")  # [CN] 进入交互式模式... [EN] Entering interactive mode...
    
    # [CN] 检查是否有示例文件
    # [EN] Check if example file exists
    test_file = PROJECT_ROOT / "novel" / "test.txt"
    if not test_file.exists():
        print("\n⚠️  未找到示例文件 novel/test.txt")  # [CN] 未找到示例文件 novel/test.txt [EN] Example file novel/test.txt not found
        create_test = input("是否要创建示例小说文件？(y/n) [y]: ").strip().lower() or "y"  # [CN] 是否要创建示例小说文件？(y/n) [y]: [EN] Do you want to create an example novel file? (y/n) [y]:
        if create_test in ["y", "yes"]:
            try:
                create_example_novel()
                print("✅ 示例小说文件已创建")  # [CN] 示例小说文件已创建 [EN] Example novel file created
            except Exception as e:
                print(f"❌ 无法创建示例文件: {e}")  # [CN] 无法创建示例文件: [EN] Unable to create example file:
    
    while True:
        print("\n" + "=" * 60)
        print("📋 可用操作：")  # [CN] 可用操作： [EN] Available operations:
        print("1. 🎬 运行演示")  # [CN] 运行演示 [EN] Run demo
        print("2. 📄 处理单个文件")  # [CN] 处理单个文件 [EN] Process single file
        print("3. 📂 批量处理目录")  # [CN] 批量处理目录 [EN] Batch process directory
        print("4. 🧪 运行测试")  # [CN] 运行测试 [EN] Run tests
        print("5. ⚡ 性能基准测试")  # [CN] 性能基准测试 [EN] Performance benchmark
        print("6. 🔍 检查环境")  # [CN] 检查环境 [EN] Check environment
        print("0. 🚪 退出")  # [CN] 退出 [EN] Exit
        print("=" * 60)
        
        choice = input("请输入选择 (0-6): ").strip()  # [CN] 请输入选择 (0-6): [EN] Please enter your choice (0-6):
        
        if choice == "0":
            print("👋 再见！")  # [CN] 再见！ [EN] Goodbye!
            break
        elif choice == "1":
            provider = input("选择API提供商 (deepseek/openai) [默认: deepseek]: ").strip() or "deepseek"  # [CN] 选择API提供商 (deepseek/openai) [默认: deepseek]: [EN] Choose API provider (deepseek/openai) [default: deepseek]:
            run_demo(provider)
        elif choice == "2":
            run_single_file_interactive()
        elif choice == "3":
            run_batch_interactive()
        elif choice == "4":
            run_tests()
        elif choice == "5":
            run_benchmark()
        elif choice == "6":
            check_environment()
        else:
            print("❌ 无效选择，请重新输入")  # [CN] 无效选择，请重新输入 [EN] Invalid choice, please try again


def run_single_file_interactive():
    """
    # [CN] 交互式单文件处理
    # [EN] Interactive single file processing
    """
    print("\n📄 单文件处理模式")  # [CN] 单文件处理模式 [EN] Single file processing mode
    
    # [CN] 列出可用的测试文件
    # [EN] List available test files
    novel_dir = PROJECT_ROOT / "novel"
    if novel_dir.exists():
        txt_files = list(novel_dir.glob("*.txt"))
        if txt_files:
            print("\n📚 可用的测试文件：")  # [CN] 可用的测试文件： [EN] Available test files:
            for i, file in enumerate(txt_files, 1):
                print(f"  {i}. {file.name}")
            print(f"  {len(txt_files) + 1}. 自定义路径")  # [CN] 自定义路径 [EN] Custom path
            
            try:
                choice = int(input(f"\n请选择文件 (1-{len(txt_files) + 1}): "))  # [CN] 请选择文件 (1-{len(txt_files) + 1}): [EN] Please select file (1-{len(txt_files) + 1}):
                if 1 <= choice <= len(txt_files):
                    input_file = txt_files[choice - 1]
                elif choice == len(txt_files) + 1:
                    input_path = input("请输入文件路径: ").strip()  # [CN] 请输入文件路径: [EN] Please enter file path:
                    input_file = Path(input_path)
                else:
                    print("❌ 无效选择")  # [CN] 无效选择 [EN] Invalid choice
                    return
            except ValueError:
                print("❌ 请输入有效数字")  # [CN] 请输入有效数字 [EN] Please enter a valid number
                return
    else:
        input_path = input("请输入文件路径: ").strip()  # [CN] 请输入文件路径: [EN] Please enter file path:
        input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"❌ 文件不存在: {input_file}")  # [CN] 文件不存在: [EN] File does not exist:
        return
    
    # [CN] 选择API提供商
    # [EN] Choose API provider
    provider = input("选择API提供商 (deepseek/openai) [默认: deepseek]: ").strip() or "deepseek"  # [CN] 选择API提供商 (deepseek/openai) [默认: deepseek]: [EN] Choose API provider (deepseek/openai) [default: deepseek]:
    
    # [CN] 设置输出目录
    # [EN] Set output directory
    output_dir = PROJECT_ROOT / "output" / f"{input_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # [CN] 处理文件
    # [EN] Process file
    process_file(input_file, output_dir, provider)


def run_batch_interactive():
    """
    # [CN] 交互式批量处理
    # [EN] Interactive batch processing
    """
    print("\n📂 批量处理模式")  # [CN] 批量处理模式 [EN] Batch processing mode
    
    # [CN] 默认推荐novel目录
    # [EN] Recommend novel directory by default
    novel_dir = PROJECT_ROOT / "novel"
    if novel_dir.exists():
        print(f"📁 推荐目录: {novel_dir}")  # [CN] 推荐目录: [EN] Recommended directory:
        use_default = input("使用推荐目录？(y/n) [默认: y]: ").strip().lower()  # [CN] 使用推荐目录？(y/n) [默认: y]: [EN] Use recommended directory? (y/n) [default: y]:
        if use_default in ['', 'y', 'yes']:
            input_dir = novel_dir
        else:
            input_path = input("请输入目录路径: ").strip()  # [CN] 请输入目录路径: [EN] Please enter directory path:
            input_dir = Path(input_path)
    else:
        input_path = input("请输入目录路径: ").strip()  # [CN] 请输入目录路径: [EN] Please enter directory path:
        input_dir = Path(input_path)
    
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"❌ 目录不存在: {input_dir}")  # [CN] 目录不存在: [EN] Directory does not exist:
        return
    
    # [CN] 检查目录中的txt文件
    # [EN] Check txt files in directory
    txt_files = list(input_dir.glob("*.txt"))
    if not txt_files:
        print(f"❌ 目录中没有找到txt文件: {input_dir}")  # [CN] 目录中没有找到txt文件: [EN] No txt files found in directory:
        return
    
    print(f"📚 找到 {len(txt_files)} 个txt文件")  # [CN] 找到 {len(txt_files)} 个txt文件 [EN] Found {len(txt_files)} txt files
    for file in txt_files:
        print(f"  - {file.name}")
    
    # [CN] 确认处理
    # [EN] Confirm processing
    if input("\n确认批量处理这些文件？(y/n): ").strip().lower() not in ['y', 'yes']:  # [CN] 确认批量处理这些文件？(y/n): [EN] Confirm batch processing these files? (y/n):
        print("❌ 已取消")  # [CN] 已取消 [EN] Cancelled
        return
    
    # [CN] 选择API提供商
    # [EN] Choose API provider
    provider = input("选择API提供商 (deepseek/openai) [默认: deepseek]: ").strip() or "deepseek"  # [CN] 选择API提供商 (deepseek/openai) [默认: deepseek]: [EN] Choose API provider (deepseek/openai) [default: deepseek]:
    
    # [CN] 设置输出目录
    # [EN] Set output directory
    output_dir = PROJECT_ROOT / "output" / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # [CN] 批量处理
    # [EN] Batch processing
    process_directory(input_dir, output_dir, provider)


def main():
    """
    # [CN] 主函数
    # [EN] Main function
    """
    parser = argparse.ArgumentParser(
        description="《凡人修仙传》因果事件图谱生成系统",  # [CN] 《凡人修仙传》因果事件图谱生成系统 [EN] A Record of a Mortal's Journey to Immortality Causal Event Graph Generation System
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
# [CN] 使用示例:
# [EN] Usage examples:
  python main.py                          # [CN] 交互式模式 [EN] Interactive mode
  python main.py --demo                   # [CN] 运行演示 [EN] Run demo
  python main.py --input novel/test.txt   # [CN] 处理指定文件 [EN] Process specified file
  python main.py --batch novel/           # [CN] 批量处理目录 [EN] Batch process directory
  python main.py --test                   # [CN] 运行测试套件 [EN] Run test suite
  python main.py --benchmark              # [CN] 运行性能基准测试 [EN] Run performance benchmark
  python main.py --check-env              # [CN] 检查环境 [EN] Check environment

# [CN] 支持的API提供商:
# [EN] Supported API providers:
  - deepseek ([CN] 默认 [EN] default)
  - openai
        """
    )
    
    # [CN] 互斥的模式选项
    # [EN] Mutually exclusive mode options
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--demo", action="store_true", help="运行演示模式")  # [CN] 运行演示模式 [EN] Run demo mode
    mode_group.add_argument("--test", action="store_true", help="运行测试套件")  # [CN] 运行测试套件 [EN] Run test suite
    mode_group.add_argument("--benchmark", action="store_true", help="运行性能基准测试")  # [CN] 运行性能基准测试 [EN] Run performance benchmark
    mode_group.add_argument("--check-env", action="store_true", help="检查运行环境")  # [CN] 检查运行环境 [EN] Check runtime environment
    
    # [CN] 文件处理选项
    # [EN] File processing options
    parser.add_argument("--input", "-i", help="输入文件路径")  # [CN] 输入文件路径 [EN] Input file path
    parser.add_argument("--output", "-o", help="输出目录路径")  # [CN] 输出目录路径 [EN] Output directory path
    parser.add_argument("--batch", "-b", metavar="DIR", help="批量处理目录")  # [CN] 批量处理目录 [EN] Batch process directory
    parser.add_argument("--provider", "-p", choices=["openai", "deepseek"], 
                       default="deepseek", help="LLM API提供商 (默认: deepseek)")  # [CN] LLM API提供商 (默认: deepseek) [EN] LLM API provider (default: deepseek)
    
    # [CN] 性能选项
    # [EN] Performance options
    parser.add_argument("--no-parallel", action="store_true", help="禁用并行处理")  # [CN] 禁用并行处理 [EN] Disable parallel processing
    parser.add_argument("--threads", type=int, help="指定工作线程数量")  # [CN] 指定工作线程数量 [EN] Specify number of worker threads
    
    # [CN] 其他选项
    # [EN] Other options
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")  # [CN] 静默模式 [EN] Quiet mode
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")  # [CN] 详细输出 [EN] Verbose output
    
    args = parser.parse_args()
    
    # [CN] 设置日志级别
    # [EN] Set logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # [CN] 打印横幅（除非在静默模式）
    # [EN] Print banner (unless in quiet mode)
    if not args.quiet:
        print_banner()
    
    # [CN] 设置环境
    # [EN] Set up environment
    setup_environment()
    
    # [CN] 配置并行处理选项
    # [EN] Configure parallel processing options
    parallel_options = {
        "enabled": not args.no_parallel,
    }
    if args.threads:
        parallel_options["max_workers"] = args.threads
        
    ParallelConfig.initialize(parallel_options)
    
    if not args.quiet:
        if ParallelConfig.is_enabled():
            max_workers = ParallelConfig.get_max_workers()
            print(f"✅ 已启用并行处理 (工作线程数: {max_workers})")  # [CN] 已启用并行处理 (工作线程数: {max_workers}) [EN] Parallel processing enabled (worker threads: {max_workers})
            
            # [CN] 记录各模块配置的线程数
            # [EN] Log thread count configured for each module
            print("各模块线程配置:")  # [CN] 各模块线程配置: [EN] Thread configuration for each module:
            for module, workers in ParallelConfig._config["default_workers"].items():
                print(f"  - {module}: {workers} 线程")  # [CN] 线程 [EN] threads
                
            # [CN] 记录自适应配置
            # [EN] Log adaptive configuration
            if ParallelConfig._config["adaptive"]["enabled"]:
                io_factor = ParallelConfig._config["adaptive"]["io_bound_factor"]
                cpu_factor = ParallelConfig._config["adaptive"]["cpu_bound_factor"]
                io_threads = int(max_workers * io_factor)
                cpu_threads = int(max_workers * cpu_factor)
                print(f"自适应线程配置已启用:")  # [CN] 自适应线程配置已启用: [EN] Adaptive thread configuration enabled:
                print(f"  - IO密集型任务: {io_threads} 线程 (系数: {io_factor})")  # [CN] IO密集型任务: {io_threads} 线程 (系数: {io_factor}) [EN] IO-intensive tasks: {io_threads} threads (factor: {io_factor})
                print(f"  - CPU密集型任务: {cpu_threads} 线程 (系数: {cpu_factor})")  # [CN] CPU密集型任务: {cpu_threads} 线程 (系数: {cpu_factor}) [EN] CPU-intensive tasks: {cpu_threads} threads (factor: {cpu_factor})
            
            # [CN] 记录到线程监控
            # [EN] Log to thread monitoring
            thread_monitor.log_system_thread_usage()
        else:
            print("ℹ️ 已禁用并行处理，使用顺序执行模式")  # [CN] 已禁用并行处理，使用顺序执行模式 [EN] Parallel processing disabled, using sequential execution mode
    
    # [CN] 检查环境
    # [EN] Check environment
    if args.check_env:
        check_environment()
        return
    
    # [CN] 基本环境检查
    # [EN] Basic environment check
    check_environment()
    
    try:
        # [CN] 运行相应的模式
        # [EN] Run corresponding mode
        if args.demo:
            run_demo(args.provider)
        
        elif args.test:
            run_tests()
        
        elif args.benchmark:
            run_benchmark()
        
        elif args.input:
            # [CN] 单文件处理模式
            # [EN] Single file processing mode
            input_file = Path(args.input)
            output_dir = Path(args.output) if args.output else \
                        PROJECT_ROOT / "output" / f"{input_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # [CN] 检查输入文件是否存在
            # [EN] Check if input file exists
            if not input_file.exists():
                print(f"❌ 输入文件不存在: {input_file}")  # [CN] 输入文件不存在: [EN] Input file does not exist:
                sys.exit(1)
                
            process_file(input_file, output_dir, args.provider)
        
        elif args.batch:
            # [CN] 批量处理模式
            # [EN] Batch processing mode
            input_dir = Path(args.batch)
            output_dir = Path(args.output) if args.output else \
                        PROJECT_ROOT / "output" / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # [CN] 检查输入目录是否存在
            # [EN] Check if input directory exists
            if not input_dir.exists() or not input_dir.is_dir():
                print(f"❌ 输入目录不存在: {input_dir}")  # [CN] 输入目录不存在: [EN] Input directory does not exist:
                sys.exit(1)
                
            # [CN] 检查是否有txt文件
            # [EN] Check if there are txt files
            if not list(input_dir.glob("*.txt")):
                print(f"❌ 目录中没有.txt文件: {input_dir}")  # [CN] 目录中没有.txt文件: [EN] No .txt files in directory:
                print("请确保小说文本文件以.txt格式保存")  # [CN] 请确保小说文本文件以.txt格式保存 [EN] Please ensure novel text files are saved in .txt format
                sys.exit(1)
                
            process_directory(input_dir, output_dir, args.provider)
        
        else:
            # [CN] 默认交互式模式
            # [EN] Default interactive mode
            run_interactive()
    
    except FileNotFoundError as e:
        print(f"\n❌ 文件未找到: {e}")  # [CN] 文件未找到: [EN] File not found:
        print("请确保所有必要的配置文件和目录都存在")  # [CN] 请确保所有必要的配置文件和目录都存在 [EN] Please ensure all necessary configuration files and directories exist
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")  # [CN] 用户中断操作 [EN] User interrupted operation
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")  # [CN] 发生错误: [EN] An error occurred:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print("💡 运行带 --verbose 参数以查看详细错误信息")  # [CN] 运行带 --verbose 参数以查看详细错误信息 [EN] Run with --verbose parameter to see detailed error information
        sys.exit(1)


if __name__ == "__main__":
    main()
