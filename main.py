#!/usr/bin/env python3
"""
《凡人修仙传》因果事件图谱生成系统 - 主入口文件

基于R2框架的因果事件图谱生成系统，用于从《凡人修仙传》小说文本中自动抽取事件，并建立因果关系图谱。
支持事件抽取、幻觉修复、因果关系链接和图谱可视化功能。

使用示例:
    python main.py                         # 交互式模式
    python main.py --demo                  # 运行演示
    python main.py --input novel/test.txt  # 处理指定文件
    python main.py --batch novel/          # 批量处理目录
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

# 确保项目路径正确
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# 导入并行处理配置和线程监控
from common.utils.parallel_config import ParallelConfig
from common.utils.thread_monitor import ThreadUsageMonitor

# 初始化并行配置
ParallelConfig.initialize()

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

# 初始化线程监控
thread_monitor = ThreadUsageMonitor.get_instance()


def print_banner():
    """打印系统横幅"""
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
    """设置运行环境"""
    # 尝试加载.env文件
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            logger.info("已加载 .env 文件")
            
            # 确保API密钥可用（大写变量名）
            if "openai_api_key" in os.environ:
                os.environ["OPENAI_API_KEY"] = os.environ["openai_api_key"]
                logger.info("已设置 OpenAI API 密钥")
                
            if "deepseek_api_key" in os.environ:
                os.environ["DEEPSEEK_API_KEY"] = os.environ["deepseek_api_key"]
                logger.info("已设置 DeepSeek API 密钥")
                
        except ImportError:
            logger.warning("未安装 python-dotenv，跳过 .env 文件加载")
    else:
        # 创建示例.env文件如果不存在
        env_example = PROJECT_ROOT / ".env.example"
        if env_example.exists() and not env_file.exists():
            logger.info("未找到 .env 文件，正在创建默认配置...")
            try:
                import shutil
                shutil.copy(env_example, env_file)
                logger.info(f"已创建 .env 文件，请编辑 {env_file} 设置您的 API 密钥")
            except Exception as e:
                logger.warning(f"创建 .env 文件失败: {e}")
    
    # 创建必要的目录
    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    
    temp_dir = PROJECT_ROOT / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    novel_dir = PROJECT_ROOT / "novel"
    novel_dir.mkdir(exist_ok=True)
    
    # 设置系统环境变量
    if "MAX_WORKERS" not in os.environ:
        cpu_count = multiprocessing.cpu_count()
        optimal_workers = max(2, min(8, cpu_count))
        os.environ["MAX_WORKERS"] = str(optimal_workers)
    
    if "LLM_PROVIDER" not in os.environ:
        os.environ["LLM_PROVIDER"] = "deepseek"  # 默认使用 DeepSeek
        
    # 初始化并行配置
    ParallelConfig.initialize()


def create_example_novel():
    """创建示例小说文件"""
    test_file = PROJECT_ROOT / "novel" / "test.txt"
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
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    
    print(f"✅ Python版本: {sys.version.split()[0]}")
    
    # 检查必要的包
    required_packages = [
        'requests', 'openai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    # 单独检查python-dotenv（因为它可能会以不同方式安装）
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing_packages.append('python-dotenv')
    
    if missing_packages:
        print(f"⚠️ 缺少以下包: {', '.join(missing_packages)}")
        print("💡 可运行: pip install -r requirements.txt")
    else:
        print("✅ 所有必要的包都已安装")
    
    # 检查API密钥
    has_api_key = False
    if os.getenv('OPENAI_API_KEY'):
        print("✅ 检测到 OpenAI API 密钥")
        has_api_key = True
    if os.getenv('DEEPSEEK_API_KEY'):
        print("✅ 检测到 DeepSeek API 密钥")
        has_api_key = True
    
    if not has_api_key:
        print("⚠️ 未检测到API密钥，请设置环境变量或.env文件")
        print("💡 支持的API: OPENAI_API_KEY, DEEPSEEK_API_KEY")
    
    # 检查配置文件
    config_file = PROJECT_ROOT / "common" / "config" / "config.json"
    if not config_file.exists():
        print(f"⚠️ 配置文件不存在: {config_file}")
    else:
        print("✅ 配置文件存在")
    
    # 检查测试数据
    test_file = PROJECT_ROOT / "novel" / "test.txt"
    if not test_file.exists():
        print(f"⚠️ 测试文件不存在: {test_file}")
    else:
        print("✅ 测试文件存在")
    
    print("✅ 环境检查完成\n")
    return True


def run_demo(provider: str = "deepseek") -> bool:
    """运行演示模式"""
    print("🎬 运行演示模式...")
    
    # 检查演示文件
    demo_file = PROJECT_ROOT / "novel" / "test.txt"
    if not demo_file.exists():
        print(f"❌ 演示文件不存在: {demo_file}")
        return False
    
    # 运行演示
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
        print(f"\n🎉 演示完成！结果保存在: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ 演示运行失败: {e}")
        logger.exception("演示运行失败")
        return False


def run_tests():
    """运行测试套件"""
    print("🧪 运行测试套件...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "tests.run_all_tests"
        ], cwd=PROJECT_ROOT)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        logger.exception("运行测试失败")
        return False


def run_benchmark():
    """运行性能基准测试"""
    print("⚡ 运行性能基准测试...")
    
    try:
        # 使用subprocess运行性能测试脚本
        import subprocess
        benchmark_script = PROJECT_ROOT / "scripts" / "performance_benchmark.py"
        
        if not benchmark_script.exists():
            print(f"❌ 性能测试脚本不存在: {benchmark_script}")
            return False
            
        result = subprocess.run(
            [sys.executable, str(benchmark_script)],
            cwd=PROJECT_ROOT
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        logger.exception("性能测试失败")
        return False


def process_file(input_file: Path, output_dir: Path, provider: str = "deepseek") -> bool:
    """处理单个文件"""
    print(f"\n📄 处理文件: {input_file.name}")
    
    if not input_file.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    try:
        from api_gateway.main import process_text
        process_text(
            text_path=str(input_file),
            output_dir=str(output_dir),
            provider=provider
        )
        print(f"✅ 处理完成！结果保存在: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        logger.exception(f"处理文件 {input_file} 失败")
        return False


def process_directory(input_dir: Path, output_dir: Path, provider: str = "deepseek") -> bool:
    """批量处理目录"""
    print(f"\n📂 批量处理目录: {input_dir}")
    
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"❌ 目录不存在: {input_dir}")
        return False
    
    # 获取所有txt文件
    txt_files = list(input_dir.glob("*.txt"))
    if not txt_files:
        print(f"❌ 目录中没有找到txt文件: {input_dir}")
        return False
    
    print(f"📚 找到 {len(txt_files)} 个txt文件")
    
    try:
        from api_gateway.main import process_directory as api_process_directory
        api_process_directory(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            provider=provider
        )
        print(f"✅ 批量处理完成！结果保存在: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ 批量处理失败: {e}")
        logger.exception(f"处理目录 {input_dir} 失败")
        return False


def run_interactive():
    """运行交互式模式"""
    print("🔄 进入交互式模式...")
    
    # 检查是否有示例文件
    test_file = PROJECT_ROOT / "novel" / "test.txt"
    if not test_file.exists():
        print("\n⚠️  未找到示例文件 novel/test.txt")
        create_test = input("是否要创建示例小说文件？(y/n) [y]: ").strip().lower() or "y"
        if create_test in ["y", "yes"]:
            try:
                create_example_novel()
                print("✅ 示例小说文件已创建")
            except Exception as e:
                print(f"❌ 无法创建示例文件: {e}")
    
    while True:
        print("\n" + "=" * 60)
        print("📋 可用操作：")
        print("1. 🎬 运行演示")
        print("2. 📄 处理单个文件")
        print("3. 📂 批量处理目录")
        print("4. 🧪 运行测试")
        print("5. ⚡ 性能基准测试")
        print("6. 🔍 检查环境")
        print("0. 🚪 退出")
        print("=" * 60)
        
        choice = input("请输入选择 (0-6): ").strip()
        
        if choice == "0":
            print("👋 再见！")
            break
        elif choice == "1":
            provider = input("选择API提供商 (deepseek/openai) [默认: deepseek]: ").strip() or "deepseek"
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
            print("❌ 无效选择，请重新输入")


def run_single_file_interactive():
    """交互式单文件处理"""
    print("\n📄 单文件处理模式")
    
    # 列出可用的测试文件
    novel_dir = PROJECT_ROOT / "novel"
    if novel_dir.exists():
        txt_files = list(novel_dir.glob("*.txt"))
        if txt_files:
            print("\n📚 可用的测试文件：")
            for i, file in enumerate(txt_files, 1):
                print(f"  {i}. {file.name}")
            print(f"  {len(txt_files) + 1}. 自定义路径")
            
            try:
                choice = int(input(f"\n请选择文件 (1-{len(txt_files) + 1}): "))
                if 1 <= choice <= len(txt_files):
                    input_file = txt_files[choice - 1]
                elif choice == len(txt_files) + 1:
                    input_path = input("请输入文件路径: ").strip()
                    input_file = Path(input_path)
                else:
                    print("❌ 无效选择")
                    return
            except ValueError:
                print("❌ 请输入有效数字")
                return
    else:
        input_path = input("请输入文件路径: ").strip()
        input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"❌ 文件不存在: {input_file}")
        return
    
    # 选择API提供商
    provider = input("选择API提供商 (deepseek/openai) [默认: deepseek]: ").strip() or "deepseek"
    
    # 设置输出目录
    output_dir = PROJECT_ROOT / "output" / f"{input_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 处理文件
    process_file(input_file, output_dir, provider)


def run_batch_interactive():
    """交互式批量处理"""
    print("\n📂 批量处理模式")
    
    # 默认推荐novel目录
    novel_dir = PROJECT_ROOT / "novel"
    if novel_dir.exists():
        print(f"📁 推荐目录: {novel_dir}")
        use_default = input("使用推荐目录？(y/n) [默认: y]: ").strip().lower()
        if use_default in ['', 'y', 'yes']:
            input_dir = novel_dir
        else:
            input_path = input("请输入目录路径: ").strip()
            input_dir = Path(input_path)
    else:
        input_path = input("请输入目录路径: ").strip()
        input_dir = Path(input_path)
    
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"❌ 目录不存在: {input_dir}")
        return
    
    # 检查目录中的txt文件
    txt_files = list(input_dir.glob("*.txt"))
    if not txt_files:
        print(f"❌ 目录中没有找到txt文件: {input_dir}")
        return
    
    print(f"📚 找到 {len(txt_files)} 个txt文件")
    for file in txt_files:
        print(f"  - {file.name}")
    
    # 确认处理
    if input("\n确认批量处理这些文件？(y/n): ").strip().lower() not in ['y', 'yes']:
        print("❌ 已取消")
        return
    
    # 选择API提供商
    provider = input("选择API提供商 (deepseek/openai) [默认: deepseek]: ").strip() or "deepseek"
    
    # 设置输出目录
    output_dir = PROJECT_ROOT / "output" / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 批量处理
    process_directory(input_dir, output_dir, provider)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="《凡人修仙传》因果事件图谱生成系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                          # 交互式模式
  python main.py --demo                   # 运行演示
  python main.py --input novel/test.txt   # 处理指定文件
  python main.py --batch novel/           # 批量处理目录
  python main.py --test                   # 运行测试套件
  python main.py --benchmark              # 运行性能基准测试
  python main.py --check-env              # 检查环境

支持的API提供商:
  - deepseek (默认)
  - openai
        """
    )
    
    # 互斥的模式选项
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--demo", action="store_true", help="运行演示模式")
    mode_group.add_argument("--test", action="store_true", help="运行测试套件")
    mode_group.add_argument("--benchmark", action="store_true", help="运行性能基准测试")
    mode_group.add_argument("--check-env", action="store_true", help="检查运行环境")
    
    # 文件处理选项
    parser.add_argument("--input", "-i", help="输入文件路径")
    parser.add_argument("--output", "-o", help="输出目录路径")
    parser.add_argument("--batch", "-b", metavar="DIR", help="批量处理目录")
    parser.add_argument("--provider", "-p", choices=["openai", "deepseek"], 
                       default="deepseek", help="LLM API提供商 (默认: deepseek)")
    
    # 性能选项
    parser.add_argument("--no-parallel", action="store_true", help="禁用并行处理")
    parser.add_argument("--threads", type=int, help="指定工作线程数量")
    
    # 其他选项
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 打印横幅（除非在静默模式）
    if not args.quiet:
        print_banner()
    
    # 设置环境
    setup_environment()
    
    # 配置并行处理选项
    parallel_options = {
        "enabled": not args.no_parallel,
    }
    if args.threads:
        parallel_options["max_workers"] = args.threads
        
    ParallelConfig.initialize(parallel_options)
    
    if not args.quiet:
        if ParallelConfig.is_enabled():
            max_workers = ParallelConfig.get_max_workers()
            print(f"✅ 已启用并行处理 (工作线程数: {max_workers})")
            
            # 记录各模块配置的线程数
            print("各模块线程配置:")
            for module, workers in ParallelConfig._config["default_workers"].items():
                print(f"  - {module}: {workers} 线程")
                
            # 记录自适应配置
            if ParallelConfig._config["adaptive"]["enabled"]:
                io_factor = ParallelConfig._config["adaptive"]["io_bound_factor"]
                cpu_factor = ParallelConfig._config["adaptive"]["cpu_bound_factor"]
                io_threads = int(max_workers * io_factor)
                cpu_threads = int(max_workers * cpu_factor)
                print(f"自适应线程配置已启用:")
                print(f"  - IO密集型任务: {io_threads} 线程 (系数: {io_factor})")
                print(f"  - CPU密集型任务: {cpu_threads} 线程 (系数: {cpu_factor})")
            
            # 记录到线程监控
            thread_monitor.log_system_thread_usage()
        else:
            print("ℹ️ 已禁用并行处理，使用顺序执行模式")
    
    # 检查环境
    if args.check_env:
        check_environment()
        return
    
    # 基本环境检查
    check_environment()
    
    try:
        # 运行相应的模式
        if args.demo:
            run_demo(args.provider)
        
        elif args.test:
            run_tests()
        
        elif args.benchmark:
            run_benchmark()
        
        elif args.input:
            # 单文件处理模式
            input_file = Path(args.input)
            output_dir = Path(args.output) if args.output else \
                        PROJECT_ROOT / "output" / f"{input_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 检查输入文件是否存在
            if not input_file.exists():
                print(f"❌ 输入文件不存在: {input_file}")
                sys.exit(1)
                
            process_file(input_file, output_dir, args.provider)
        
        elif args.batch:
            # 批量处理模式
            input_dir = Path(args.batch)
            output_dir = Path(args.output) if args.output else \
                        PROJECT_ROOT / "output" / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 检查输入目录是否存在
            if not input_dir.exists() or not input_dir.is_dir():
                print(f"❌ 输入目录不存在: {input_dir}")
                sys.exit(1)
                
            # 检查是否有txt文件
            if not list(input_dir.glob("*.txt")):
                print(f"❌ 目录中没有.txt文件: {input_dir}")
                print("请确保小说文本文件以.txt格式保存")
                sys.exit(1)
                
            process_directory(input_dir, output_dir, args.provider)
        
        else:
            # 默认交互式模式
            run_interactive()
    
    except FileNotFoundError as e:
        print(f"\n❌ 文件未找到: {e}")
        print("请确保所有必要的配置文件和目录都存在")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print("💡 运行带 --verbose 参数以查看详细错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
