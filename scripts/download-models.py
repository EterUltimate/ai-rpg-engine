#!/usr/bin/env python3
"""
模型下载脚本 - AI-RPG Engine

功能:
- 下载嵌入模型
- 下载重排序模型
- 下载 LLM 模型（可选）
- 支持断点续传
- 验证模型完整性

用法:
    python scripts/download-models.py
    python scripts/download-models.py --llm  # 同时下载 LLM
    python scripts/download-models.py --lite  # 下载 Lite 模式模型
"""

import os
import sys
import platform
import argparse
import time
from pathlib import Path
from typing import Optional, List
import subprocess


class Colors:
    """跨平台颜色输出"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def enable_windows_colors():
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass


Colors.enable_windows_colors()


class ModelDownloader:
    """模型下载器"""
    
    def __init__(self, project_root: Path, lite_mode: bool = False):
        self.root = project_root
        self.lite_mode = lite_mode
        self.models_dir = project_root / "models"
        
        # 确保目录存在
        (self.models_dir / "embeddings").mkdir(parents=True, exist_ok=True)
        (self.models_dir / "rerankers").mkdir(parents=True, exist_ok=True)
        (self.models_dir / "llm").mkdir(parents=True, exist_ok=True)
    
    def download_embedding_model(self) -> bool:
        """下载嵌入模型"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   下载嵌入模型{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        # 选择模型
        if self.lite_mode:
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            size = "~80MB"
        else:
            model_name = "BAAI/bge-large-en-v1.5"
            size = "~1.3GB"
        
        print(f"模型: {model_name}")
        print(f"大小: {size}\n")
        
        target_dir = self.models_dir / "embeddings" / model_name.split('/')[-1]
        
        if target_dir.exists():
            print(f"{Colors.OKCYAN}ℹ 模型已存在，跳过下载{Colors.ENDC}")
            print(f"路径: {target_dir.relative_to(self.root)}\n")
            return True
        
        try:
            from sentence_transformers import SentenceTransformer
            print(f"{Colors.BOLD}下载中...{Colors.ENDC}\n")
            model = SentenceTransformer(model_name, cache_folder=str(target_dir.parent))
            model.save(str(target_dir))
            print(f"\n{Colors.OKGREEN}✓ 嵌入模型下载成功{Colors.ENDC}\n")
            return True
        except ImportError:
            print(f"{Colors.FAIL}✗ sentence-transformers 未安装{Colors.ENDC}")
            print(f"请先运行: pip install sentence-transformers\n")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}✗ 下载失败: {e}{Colors.ENDC}\n")
            return False
    
    def download_reranker_model(self) -> bool:
        """下载重排序模型"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   下载重排序模型{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        if self.lite_mode:
            print(f"{Colors.OKCYAN}ℹ Lite 模式禁用重排序器，跳过下载{Colors.ENDC}\n")
            return True
        
        # 选择模型
        if self.lite_mode:
            model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
            size = "~80MB"
        else:
            model_name = "BAAI/bge-reranker-large"
            size = "~1.3GB"
        
        print(f"模型: {model_name}")
        print(f"大小: {size}\n")
        
        target_dir = self.models_dir / "rerankers" / model_name.split('/')[-1]
        
        if target_dir.exists():
            print(f"{Colors.OKCYAN}ℹ 模型已存在，跳过下载{Colors.ENDC}")
            print(f"路径: {target_dir.relative_to(self.root)}\n")
            return True
        
        try:
            from sentence_transformers import CrossEncoder
            print(f"{Colors.BOLD}下载中...{Colors.ENDC}\n")
            model = CrossEncoder(model_name)
            model.save(str(target_dir))
            print(f"\n{Colors.OKGREEN}✓ 重排序模型下载成功{Colors.ENDC}\n")
            return True
        except ImportError:
            print(f"{Colors.FAIL}✗ sentence-transformers 未安装{Colors.ENDC}")
            print(f"请先运行: pip install sentence-transformers\n")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}✗ 下载失败: {e}{Colors.ENDC}\n")
            return False
    
    def download_llm_model(self, model_url: Optional[str] = None, 
                          model_file: Optional[str] = None) -> bool:
        """下载 LLM 模型"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   下载 LLM 模型{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        # 推荐的模型
        recommended_models = {
            "lite": {
                "qwen-1.8b": {
                    "name": "Qwen-1.8B-Chat (推荐中文)",
                    "url": "https://huggingface.co/Qwen/Qwen-1_8B-Chat-GGUF/resolve/main/qwen1_8b-chat-q4_k_m.gguf",
                    "file": "qwen-1.8b-chat-q4_k_m.gguf",
                    "size": "~1.1GB"
                },
                "phi-2": {
                    "name": "Phi-2 (推荐英文)",
                    "url": "https://huggingface.co/microsoft/phi-2-gguf/resolve/main/phi-2-q4_k_m.gguf",
                    "file": "phi-2-q4_k_m.gguf",
                    "size": "~1.6GB"
                }
            },
            "standard": {
                "qwen-7b": {
                    "name": "Qwen-7B-Chat (推荐中文)",
                    "url": "https://huggingface.co/Qwen/Qwen-7B-Chat-GGUF/resolve/main/qwen7b-chat-q4_k_m.gguf",
                    "file": "qwen-7b-chat-q4_k_m.gguf",
                    "size": "~4.4GB"
                },
                "llama-3-8b": {
                    "name": "Llama-3-8B-Instruct (推荐英文)",
                    "url": "https://huggingface.co/lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
                    "file": "llama-3-8b-instruct-q4_k_m.gguf",
                    "size": "~5.7GB"
                }
            }
        }
        
        # 检查已有模型
        llm_dir = self.models_dir / "llm"
        existing_models = list(llm_dir.glob("*.gguf"))
        if existing_models:
            print(f"{Colors.OKCYAN}ℹ 已有 LLM 模型:{Colors.ENDC}")
            for model_file in existing_models:
                size_mb = model_file.stat().st_size / (1024**2)
                print(f"  • {model_file.name} ({size_mb:.0f} MB)")
            print(f"\n{Colors.OKCYAN}跳过下载。如需下载其他模型，请手动指定。{Colors.ENDC}\n")
            return True
        
        # 如果没有指定模型，让用户选择
        if not model_url or not model_file:
            mode = "lite" if self.lite_mode else "standard"
            models = recommended_models[mode]
            
            print(f"{Colors.BOLD}推荐模型:{Colors.ENDC}\n")
            for idx, (key, info) in enumerate(models.items(), 1):
                print(f"  [{idx}] {info['name']}")
                print(f"      大小: {info['size']}")
                print(f"      文件: {info['file']}\n")
            
            print(f"  [0] 跳过 LLM 模型下载\n")
            print(f"{Colors.WARNING}提示: LLM 模型较大，建议手动下载后放入 models/llm/ 目录{Colors.ENDC}\n")
            
            try:
                choice = input(f"请选择 [0-{len(models)}]: ").strip()
                if choice == '0':
                    print(f"\n{Colors.OKCYAN}跳过 LLM 模型下载{Colors.ENDC}\n")
                    return True
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(models):
                    selected = list(models.values())[choice_idx]
                    model_url = selected['url']
                    model_file = selected['file']
                else:
                    print(f"\n{Colors.FAIL}无效选择{Colors.ENDC}\n")
                    return False
            except:
                print(f"\n{Colors.FAIL}输入错误{Colors.ENDC}\n")
                return False
        
        # 下载模型
        print(f"模型: {model_file}")
        print(f"URL: {model_url}\n")
        
        target_file = llm_dir / model_file
        
        # 使用 wget 或 curl 下载
        print(f"{Colors.BOLD}开始下载...{Colors.ENDC}")
        print(f"{Colors.WARNING}注意: 大文件下载可能需要较长时间{Colors.ENDC}\n")
        
        try:
            # 尝试使用 wget
            result = subprocess.run(
                ['wget', '-c', '-O', str(target_file), model_url],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # 尝试使用 curl
                print(f"{Colors.WARNING}wget 失败，尝试 curl...{Colors.ENDC}\n")
                result = subprocess.run(
                    ['curl', '-L', '-C', '-', '-o', str(target_file), model_url],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"{Colors.FAIL}✗ 下载失败{Colors.ENDC}")
                    print(f"请手动下载: {model_url}\n")
                    return False
            
            # 验证文件
            if target_file.exists() and target_file.stat().st_size > 0:
                size_mb = target_file.stat().st_size / (1024**2)
                print(f"\n{Colors.OKGREEN}✓ LLM 模型下载成功 ({size_mb:.0f} MB){Colors.ENDC}\n")
                return True
            else:
                print(f"\n{Colors.FAIL}✗ 下载的文件无效{Colors.ENDC}\n")
                return False
                
        except FileNotFoundError:
            print(f"{Colors.FAIL}✗ 需要 wget 或 curl 工具{Colors.ENDC}")
            print(f"请手动下载: {model_url}\n")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}✗ 下载失败: {e}{Colors.ENDC}\n")
            return False
    
    def print_summary(self, results: dict):
        """打印下载总结"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   下载总结{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        for model_type, success in results.items():
            status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if success else f"{Colors.FAIL}✗{Colors.ENDC}"
            print(f"  {status} {model_type}")
        
        print()
        
        if all(results.values()):
            print(f"{Colors.OKGREEN}✅ 所有模型下载成功！{Colors.ENDC}\n")
            print("下一步:")
            print("  1. 配置环境: cp .env.example .env")
            print("  2. 启动服务: python scripts/dev.py\n")
        else:
            print(f"{Colors.WARNING}⚠️  部分模型下载失败{Colors.ENDC}\n")
            print("请检查网络连接或手动下载模型文件。\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI-RPG Engine 模型下载脚本')
    parser.add_argument('--llm', action='store_true',
                       help='下载 LLM 模型')
    parser.add_argument('--lite', action='store_true',
                       help='下载 Lite 模式模型')
    parser.add_argument('--llm-url', type=str,
                       help='LLM 模型下载 URL')
    parser.add_argument('--llm-file', type=str,
                       help='LLM 模型文件名')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"\n{Colors.HEADER}{'═'*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}   AI-RPG Engine 模型下载{Colors.ENDC}")
    print(f"{Colors.HEADER}{'═'*60}{Colors.ENDC}\n")
    
    print(f"下载时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目路径: {project_root}")
    print(f"模型目录: {project_root / 'models'}\n")
    
    if args.lite:
        print(f"{Colors.OKCYAN}Lite 模式: 启用{Colors.ENDC}\n")
    
    downloader = ModelDownloader(project_root, lite_mode=args.lite)
    
    results = {}
    
    # 下载嵌入模型
    results['嵌入模型'] = downloader.download_embedding_model()
    
    # 下载重排序模型
    results['重排序模型'] = downloader.download_reranker_model()
    
    # 下载 LLM 模型
    if args.llm or args.llm_url:
        results['LLM模型'] = downloader.download_llm_model(
            model_url=args.llm_url,
            model_file=args.llm_file
        )
    
    # 打印总结
    downloader.print_summary(results)
    
    # 返回退出码
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
