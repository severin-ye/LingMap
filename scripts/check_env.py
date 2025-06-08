#!/usr/bin/env python3
"""
环境测试脚本，用于验证依赖是否正确安装以及API密钥是否有效
"""

import os
import sys
import importlib
import platform

# 设置彩色输出
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'


def print_success(message):
    """打印成功消息"""
    print(f"{GREEN}[✓] {message}{ENDC}")


def print_error(message):
    """打印错误消息"""
    print(f"{RED}[✗] {message}{ENDC}")


def print_warning(message):
    """打印警告消息"""
    print(f"{YELLOW}[!] {message}{ENDC}")


def print_info(message):
    """打印信息消息"""
    print(f"{BLUE}[i] {message}{ENDC}")


def check_python_version():
    """检查Python版本"""
    print_info("检查Python版本...")
    version = platform.python_version()
    major, minor, _ = version.split('.')
    
    if int(major) >= 3 and int(minor) >= 8:
        print_success(f"Python版本 {version} 满足要求（3.8+）")
        return True
    else:
        print_error(f"Python版本 {version} 不满足要求（需要3.8+）")
        return False


def check_dependencies():
    """检查依赖是否安装"""
    print_info("检查依赖...")
    required_packages = [
        "openai",
        "tenacity",
        "numpy",
        "tqdm"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print_success(f"依赖 {package} 已安装")
        except ImportError:
            print_error(f"依赖 {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print_warning(f"缺少依赖：{', '.join(missing_packages)}")
        print_info("请运行：pip install -r requirements.txt 安装依赖")
        return False
    
    return True


def check_api_key():
    """检查API密钥是否设置"""
    print_info("检查API密钥...")
    openai_key = os.environ.get("OPENAI_API_KEY")
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    
    openai_status = False
    deepseek_status = False
    
    # 检查OpenAI API密钥
    if openai_key:
        print_success("OpenAI API密钥已设置")
        
        # 尝试验证API密钥（可选）
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print_success("OpenAI API密钥有效，已成功调用API")
            openai_status = True
        except Exception as e:
            print_error(f"OpenAI API密钥无效或调用失败：{str(e)}")
    else:
        print_warning("OpenAI API密钥未设置")
        print_info("要使用OpenAI，请设置环境变量：export OPENAI_API_KEY=\"your-api-key\"")
    
    # 检查DeepSeek API密钥
    if deepseek_key:
        print_success("DeepSeek API密钥已设置")
        
        # 尝试验证API密钥
        try:
            import openai
            client = openai.OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com/v1")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "你好"}],
                max_tokens=5
            )
            print_success("DeepSeek API密钥有效，已成功调用API")
            deepseek_status = True
        except Exception as e:
            print_error(f"DeepSeek API密钥无效或调用失败：{str(e)}")
    else:
        print_warning("DeepSeek API密钥未设置")
        print_info("要使用DeepSeek，请设置环境变量：export DEEPSEEK_API_KEY=\"your-api-key\"")
            
    # 如果任一API有效，则返回成功
    if openai_status or deepseek_status:
        return True
    else:
        print_error("所有API密钥都无效或未设置")
        return False


def check_project_structure():
    """检查项目结构是否完整"""
    print_info("检查项目结构...")
    
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # 检查必要的目录
    required_dirs = [
        "common",
        "text_ingestion",
        "event_extraction",
        "hallucination_refine",
        "causal_linking",
        "graph_builder",
        "api_gateway"
    ]
    
    missing_dirs = []
    
    for directory in required_dirs:
        dir_path = os.path.join(project_root, directory)
        if os.path.isdir(dir_path):
            print_success(f"目录 {directory} 存在")
        else:
            print_error(f"目录 {directory} 不存在")
            missing_dirs.append(directory)
    
    if missing_dirs:
        print_warning(f"项目结构不完整，缺少目录：{', '.join(missing_dirs)}")
        return False
    
    return True


def check_system_config():
    """检查系统配置文件和路径工具"""
    print_info("检查系统配置...")
    
    try:
        # 添加项目根目录到Python路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        import sys
        sys.path.insert(0, project_root)
        
        from common.utils.path_utils import get_project_root, get_config_path, get_novel_path
        from common.utils.json_loader import JsonLoader
        
        # 测试项目根目录
        project_root = get_project_root()
        print_success(f"项目根目录: {project_root}")
        
        # 测试配置文件
        config_files = [
            "config.json",
            "prompt_event_extraction.json", 
            "prompt_hallucination_refine.json",
            "prompt_causal_linking.json"
        ]
        
        config_ok = True
        for config_file in config_files:
            try:
                config_path = get_config_path(config_file)
                if os.path.exists(config_path):
                    print_success(f"配置文件 {config_file} 存在")
                    
                    # 尝试加载JSON配置
                    if config_file.endswith('.json'):
                        try:
                            JsonLoader.load_json(config_path)
                            print_success(f"配置文件 {config_file} 格式正确")
                        except Exception as e:
                            print_error(f"配置文件 {config_file} 格式错误: {str(e)}")
                            config_ok = False
                else:
                    print_warning(f"配置文件 {config_file} 不存在")
                    config_ok = False
            except Exception as e:
                print_error(f"检查配置文件 {config_file} 时出错: {str(e)}")
                config_ok = False
        
        # 测试小说文件目录
        try:
            test_novel = get_novel_path("test.txt")
            if os.path.exists(test_novel):
                print_success("测试小说文件 test.txt 存在")
            else:
                print_warning("测试小说文件 test.txt 不存在")
        except Exception as e:
            print_error(f"检查小说文件时出错: {str(e)}")
            config_ok = False
        
        return config_ok
    except Exception as e:
        print_error(f"系统配置检查失败: {str(e)}")
        return False


def main():
    """主函数"""
    print_info("=== 《凡人修仙传》因果图谱生成系统 - 环境检查 ===")
    
    # 检查Python版本
    python_ok = check_python_version()
    
    # 检查依赖
    deps_ok = check_dependencies()
    
    # 检查API密钥
    api_ok = check_api_key()
    
    # 检查项目结构
    structure_ok = check_project_structure()
    
    # 检查系统配置
    config_ok = check_system_config()
    
    # 输出总结
    print_info("\n=== 检查结果汇总 ===")
    all_passed = python_ok and deps_ok and api_ok and structure_ok and config_ok
    
    if all_passed:
        print_success("所有检查都已通过！系统已准备就绪。")
        print_info("您可以运行 python scripts/demo_run.py 来测试系统。")
    else:
        print_warning("部分检查未通过，请解决上述问题后再试。")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
