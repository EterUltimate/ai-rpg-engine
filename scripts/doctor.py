#!/usr/bin/env python3
"""
统一诊断脚本 - AI-RPG Engine

功能:
- 基础环境检查
- 依赖状态检查
- 模型状态检查
- 端口状态检查
- 目录权限检查
- 配置一致性检查
- 服务健康检查

用法:
    python scripts/doctor.py
    python scripts/doctor.py --verbose  # 详细输出
    python scripts/doctor.py --fix      # 尝试自动修复
"""

import os
import sys
import subprocess
import platform
import json
import socket
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CheckStatus(Enum):
    """检查状态"""
    PASS = "✓"
    FAIL = "✗"
    WARN = "⚠"
    INFO = "ℹ"


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
    UNDERLINE = '\033[4m'
    
    @staticmethod
    def enable_windows_colors():
        """在Windows上启用ANSI颜色"""
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass

# 启用颜色支持
Colors.enable_windows_colors()


@dataclass
class CheckResult:
    """检查结果"""
    category: str
    name: str
    status: CheckStatus
    message: str
    details: Optional[str] = None
    fix_hint: Optional[str] = None


class Doctor:
    """AI-RPG Engine 诊断医生"""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.root = project_root
        self.verbose = verbose
        self.results: List[CheckResult] = []
        self.fix_mode = False
        
    def run_all_checks(self) -> Tuple[int, int, int]:
        """运行所有检查，返回 (通过, 警告, 失败) 数量"""
        
        print(f"\n{Colors.HEADER}{'═'*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   AI-RPG Engine 系统诊断{Colors.ENDC}")
        print(f"{Colors.HEADER}{'═'*60}{Colors.ENDC}\n")
        
        print(f"诊断时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"系统平台: {platform.system()} {platform.release()}")
        print(f"项目路径: {self.root}\n")
        
        # 执行各项检查
        self._check_basic_environment()
        self._check_dependencies()
        self._check_models()
        self._check_ports()
        self._check_directories()
        self._check_config()
        self._check_services()
        
        # 输出结果
        self._print_results()
        
        # 统计
        passed = sum(1 for r in self.results if r.status == CheckStatus.PASS)
        warned = sum(1 for r in self.results if r.status == CheckStatus.WARN)
        failed = sum(1 for r in self.results if r.status == CheckStatus.FAIL)
        
        return passed, warned, failed
    
    def _check_basic_environment(self):
        """检查基础环境"""
        print(f"{Colors.BOLD}[1/7] 基础环境检查{Colors.ENDC}\n")
        
        # Node.js
        version = self._get_version('node')
        if version:
            major = int(version.replace('v', '').split('.')[0])
            if major >= 18:
                self._add_result(CheckStatus.PASS, "基础环境", "Node.js", 
                               f"Node.js {version}", 
                               "满足要求 (≥18)")
            else:
                self._add_result(CheckStatus.WARN, "基础环境", "Node.js",
                               f"Node.js {version}",
                               f"版本过低，建议 ≥18", 
                               "请升级 Node.js")
        else:
            self._add_result(CheckStatus.FAIL, "基础环境", "Node.js",
                           "未安装", fix_hint="请安装 Node.js 18+")
        
        # Python
        version = self._get_version('python') or self._get_version('python3')
        if version:
            parts = version.split('.')
            major, minor = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
            if major == 3 and minor >= 10:
                self._add_result(CheckStatus.PASS, "基础环境", "Python",
                               f"Python {version}",
                               "满足要求 (≥3.10)")
            else:
                self._add_result(CheckStatus.WARN, "基础环境", "Python",
                               f"Python {version}",
                               f"版本过低，建议 ≥3.10",
                               "请升级 Python")
        else:
            self._add_result(CheckStatus.FAIL, "基础环境", "Python",
                           "未安装", fix_hint="请安装 Python 3.10+")
        
        # Go (可选)
        version = self._get_version('go')
        if version:
            self._add_result(CheckStatus.PASS, "基础环境", "Go",
                           f"Go {version}",
                           "API网关可用")
        else:
            self._add_result(CheckStatus.WARN, "基础环境", "Go",
                           "未安装",
                           "API网关不可用（可选）",
                           "如需网关功能，请安装 Go 1.22+")
        
        # Git (可选)
        version = self._get_version('git')
        if version:
            self._add_result(CheckStatus.PASS, "基础环境", "Git",
                           f"Git {version}",
                           "版本控制工具可用")
        else:
            self._add_result(CheckStatus.INFO, "基础环境", "Git",
                           "未安装",
                           "建议安装以便版本管理")
        
        print()
    
    def _check_dependencies(self):
        """检查依赖状态"""
        print(f"{Colors.BOLD}[2/7] 依赖状态检查{Colors.ENDC}\n")
        
        # 前端依赖
        node_modules = self.root / "frontend" / "node_modules"
        if node_modules.exists():
            count = len(list(node_modules.iterdir()))
            self._add_result(CheckStatus.PASS, "依赖状态", "前端依赖",
                           f"已安装 ({count} 个包)")
        else:
            self._add_result(CheckStatus.FAIL, "依赖状态", "前端依赖",
                           "未安装",
                           fix_hint="运行: cd frontend && npm install")
        
        # 游戏引擎依赖
        game_venv = self.root / "backend" / "services" / "game-engine" / "venv"
        if game_venv.exists():
            self._add_result(CheckStatus.PASS, "依赖状态", "游戏引擎虚拟环境",
                           "已创建")
            # 检查关键依赖
            self._check_python_deps(game_venv, "游戏引擎", 
                                   ["fastapi", "uvicorn", "sqlalchemy"])
        else:
            self._add_result(CheckStatus.WARN, "依赖状态", "游戏引擎虚拟环境",
                           "未创建",
                           fix_hint="运行: scripts/setup.bat")
        
        # AI引擎依赖
        ai_venv = self.root / "backend" / "services" / "ai-engine" / "venv"
        if ai_venv.exists():
            self._add_result(CheckStatus.PASS, "依赖状态", "AI引擎虚拟环境",
                           "已创建")
            # 检查关键依赖
            self._check_python_deps(ai_venv, "AI引擎",
                                   ["fastapi", "uvicorn", "chromadb", "sentence_transformers"])
        else:
            self._add_result(CheckStatus.WARN, "依赖状态", "AI引擎虚拟环境",
                           "未创建",
                           fix_hint="运行: scripts/setup.bat")
        
        # Go依赖
        go_mod = self.root / "backend" / "gateway" / "go.mod"
        if go_mod.exists():
            go_sum = go_mod.parent / "go.sum"
            if go_sum.exists():
                self._add_result(CheckStatus.PASS, "依赖状态", "Go模块依赖",
                               "已下载")
            else:
                self._add_result(CheckStatus.WARN, "依赖状态", "Go模块依赖",
                               "未下载",
                               fix_hint="运行: cd backend/gateway && go mod download")
        
        print()
    
    def _check_python_deps(self, venv_path: Path, service_name: str, packages: List[str]):
        """检查Python包依赖"""
        if platform.system() == 'Windows':
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:
            pip_path = venv_path / "bin" / "pip"
        
        if not pip_path.exists():
            pip_path = venv_path / "Scripts" / "pip" if platform.system() == 'Windows' else venv_path / "bin" / "pip"
        
        for package in packages:
            try:
                result = subprocess.run(
                    [str(pip_path), "show", package],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # 提取版本
                    version_line = [l for l in result.stdout.split('\n') if l.startswith('Version:')]
                    version = version_line[0].split(':')[1].strip() if version_line else "unknown"
                    self._add_result(CheckStatus.PASS, "依赖状态", f"{service_name} - {package}",
                                   f"已安装 ({version})")
                else:
                    self._add_result(CheckStatus.WARN, "依赖状态", f"{service_name} - {package}",
                                   "未安装",
                                   fix_hint=f"运行: pip install {package}")
            except:
                self._add_result(CheckStatus.WARN, "依赖状态", f"{service_name} - {package}",
                               "检查失败")
    
    def _check_models(self):
        """检查模型状态"""
        print(f"{Colors.BOLD}[3/7] 模型状态检查{Colors.ENDC}\n")
        
        models_dir = self.root / "models"
        
        # 嵌入模型
        embeddings_dir = models_dir / "embeddings"
        if embeddings_dir.exists():
            files = list(embeddings_dir.rglob("*"))
            if any(f.is_file() for f in files):
                self._add_result(CheckStatus.PASS, "模型状态", "嵌入模型",
                               "已下载")
            else:
                self._add_result(CheckStatus.WARN, "模型状态", "嵌入模型",
                               "目录为空",
                               fix_hint="运行: scripts/download-models.bat")
        else:
            self._add_result(CheckStatus.WARN, "模型状态", "嵌入模型",
                           "未下载",
                           fix_hint="运行: scripts/download-models.bat")
        
        # 重排序模型
        rerankers_dir = models_dir / "rerankers"
        if rerankers_dir.exists():
            files = list(rerankers_dir.rglob("*"))
            if any(f.is_file() for f in files):
                self._add_result(CheckStatus.PASS, "模型状态", "重排序模型",
                               "已下载")
            else:
                self._add_result(CheckStatus.WARN, "模型状态", "重排序模型",
                               "目录为空",
                               fix_hint="运行: scripts/download-models.bat")
        else:
            self._add_result(CheckStatus.WARN, "模型状态", "重排序模型",
                           "未下载",
                           fix_hint="运行: scripts/download-models.bat")
        
        # LLM模型
        llm_dir = models_dir / "llm"
        if llm_dir.exists():
            gguf_files = list(llm_dir.glob("*.gguf"))
            if gguf_files:
                total_size = sum(f.stat().st_size for f in gguf_files) / (1024**3)
                self._add_result(CheckStatus.PASS, "模型状态", "LLM模型",
                               f"已下载 ({len(gguf_files)} 个文件, {total_size:.2f} GB)",
                               "\n".join(f"  - {f.name}" for f in gguf_files[:3]))
            else:
                self._add_result(CheckStatus.WARN, "模型状态", "LLM模型",
                               "目录为空",
                               fix_hint="下载 GGUF 格式的模型文件")
        else:
            self._add_result(CheckStatus.WARN, "模型状态", "LLM模型",
                           "未下载",
                           fix_hint="下载 GGUF 格式的模型文件")
        
        print()
    
    def _check_ports(self):
        """检查端口状态"""
        print(f"{Colors.BOLD}[4/7] 端口状态检查{Colors.ENDC}\n")
        
        ports = {
            8000: "API网关",
            8001: "游戏引擎",
            8002: "AI引擎",
            5173: "前端开发服务器"
        }
        
        for port, service in ports.items():
            if self._is_port_in_use(port):
                # 尝试识别占用进程
                process = self._get_port_process(port)
                self._add_result(CheckStatus.WARN, "端口状态", f"端口 {port} ({service})",
                               f"已被占用" + (f" (PID: {process})" if process else ""),
                               fix_hint=f"关闭占用进程或修改配置使用其他端口")
            else:
                self._add_result(CheckStatus.PASS, "端口状态", f"端口 {port} ({service})",
                               "可用")
        
        print()
    
    def _check_directories(self):
        """检查目录和权限"""
        print(f"{Colors.BOLD}[5/7] 目录权限检查{Colors.ENDC}\n")
        
        dirs_to_check = [
            ("database", "数据库目录"),
            ("logs", "日志目录"),
            ("models", "模型目录"),
            ("data-core", "RAG数据目录"),
        ]
        
        for dir_name, desc in dirs_to_check:
            dir_path = self.root / dir_name
            
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self._add_result(CheckStatus.INFO, "目录权限", desc,
                                   "已自动创建")
                except PermissionError:
                    self._add_result(CheckStatus.FAIL, "目录权限", desc,
                                   "无法创建",
                                   fix_hint=f"手动创建目录: {dir_path}")
                    continue
            
            # 测试写权限
            test_file = dir_path / ".write_test"
            try:
                test_file.write_text("test", encoding='utf-8')
                test_file.unlink()
                self._add_result(CheckStatus.PASS, "目录权限", desc,
                               "可读写")
            except Exception as e:
                self._add_result(CheckStatus.FAIL, "目录权限", desc,
                               f"无写权限: {e}",
                               fix_hint="检查目录权限设置")
        
        print()
    
    def _check_config(self):
        """检查配置一致性"""
        print(f"{Colors.BOLD}[6/7] 配置一致性检查{Colors.ENDC}\n")
        
        # .env 文件
        env_example = self.root / ".env.example"
        env_file = self.root / ".env"
        
        if env_example.exists():
            self._add_result(CheckStatus.PASS, "配置一致性", ".env.example",
                           "存在")
        else:
            self._add_result(CheckStatus.WARN, "配置一致性", ".env.example",
                           "不存在",
                           fix_hint="从模板创建环境配置文件")
        
        if env_file.exists():
            self._add_result(CheckStatus.PASS, "配置一致性", ".env配置文件",
                           "存在")
            
            # 检查关键配置项
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    env_content = f.read()
                
                configs = [
                    ('DATABASE_URL', '数据库路径'),
                    ('CHROMADB_PATH', 'ChromaDB路径'),
                    ('LLM_MODEL_PATH', 'LLM模型路径'),
                    ('EMBEDDING_MODEL', '嵌入模型'),
                ]
                
                for key, desc in configs:
                    if key in env_content:
                        # 提取值
                        for line in env_content.split('\n'):
                            if line.startswith(f'{key}='):
                                value = line.split('=', 1)[1].strip()
                                self._add_result(CheckStatus.PASS, "配置一致性", desc,
                                               f"{key}={value}")
                                break
                    else:
                        self._add_result(CheckStatus.WARN, "配置一致性", desc,
                                       f"{key} 未配置",
                                       fix_hint=f"在 .env 中添加 {key}")
            except Exception as e:
                self._add_result(CheckStatus.WARN, "配置一致性", "配置文件",
                               f"读取失败: {e}")
        else:
            self._add_result(CheckStatus.INFO, "配置一致性", ".env配置文件",
                           "不存在（使用默认配置）",
                           fix_hint="复制 .env.example 为 .env 并修改配置")
        
        # Docker配置
        docker_compose = self.root / "docker-compose.yml"
        if docker_compose.exists():
            self._add_result(CheckStatus.PASS, "配置一致性", "Docker配置",
                           "存在")
        else:
            self._add_result(CheckStatus.INFO, "配置一致性", "Docker配置",
                           "不存在")
        
        print()
    
    def _check_services(self):
        """检查服务健康状态"""
        print(f"{Colors.BOLD}[7/7] 服务健康检查{Colors.ENDC}\n")
        
        services = {
            8000: ("API网关", "gateway"),
            8001: ("游戏引擎", "game-engine"),
            8002: ("AI引擎", "ai-engine"),
            5173: ("前端服务", "frontend")
        }
        
        for port, (name, _) in services.items():
            if self._is_port_in_use(port):
                # 尝试健康检查
                if self._check_health_endpoint(port):
                    self._add_result(CheckStatus.PASS, "服务健康", name,
                                   "运行正常")
                else:
                    self._add_result(CheckStatus.WARN, "服务健康", name,
                                   "端口已占用但健康检查失败")
            else:
                self._add_result(CheckStatus.INFO, "服务健康", name,
                               "未运行")
        
        print()
    
    def _add_result(self, status: CheckStatus, category: str, name: str,
                   message: str, details: Optional[str] = None,
                   fix_hint: Optional[str] = None):
        """添加检查结果"""
        result = CheckResult(
            category=category,
            name=name,
            status=status,
            message=message,
            details=details if self.verbose else None,
            fix_hint=fix_hint
        )
        self.results.append(result)
        
        # 打印结果
        status_colors = {
            CheckStatus.PASS: Colors.OKGREEN,
            CheckStatus.FAIL: Colors.FAIL,
            CheckStatus.WARN: Colors.WARNING,
            CheckStatus.INFO: Colors.OKCYAN
        }
        
        color = status_colors[status]
        print(f"  {color}{status.value} {name}: {message}{Colors.ENDC}")
        
        if details:
            for line in details.split('\n'):
                print(f"    {Colors.OKCYAN}{line}{Colors.ENDC}")
        
        if fix_hint and status != CheckStatus.PASS:
            print(f"    {Colors.WARNING}→ {fix_hint}{Colors.ENDC}")
    
    def _print_results(self):
        """打印结果汇总"""
        print(f"\n{Colors.HEADER}{'═'*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   诊断结果汇总{Colors.ENDC}")
        print(f"{Colors.HEADER}{'═'*60}{Colors.ENDC}\n")
        
        # 统计
        passed = sum(1 for r in self.results if r.status == CheckStatus.PASS)
        warned = sum(1 for r in self.results if r.status == CheckStatus.WARN)
        failed = sum(1 for r in self.results if r.status == CheckStatus.FAIL)
        info = sum(1 for r in self.results if r.status == CheckStatus.INFO)
        total = len(self.results)
        
        print(f"总计检查项: {total}")
        print(f"{Colors.OKGREEN}  ✓ 通过: {passed}{Colors.ENDC}")
        print(f"{Colors.WARNING}  ⚠ 警告: {warned}{Colors.ENDC}")
        print(f"{Colors.FAIL}  ✗ 失败: {failed}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}  ℹ 信息: {info}{Colors.ENDC}")
        print()
        
        # 总体状态
        if failed > 0:
            print(f"{Colors.FAIL}❌ 系统存在严重问题，需要修复{Colors.ENDC}\n")
            print("建议操作:")
            print("  1. 运行 scripts/setup.bat 安装依赖")
            print("  2. 运行 scripts/download-models.bat 下载模型")
            print("  3. 配置 .env 文件")
            print()
        elif warned > 0:
            print(f"{Colors.WARNING}⚠️  系统基本可用，但有部分问题需要关注{Colors.ENDC}\n")
            print("建议操作:")
            print("  1. 检查警告项并修复")
            print("  2. 运行 scripts/dev.py 启动服务")
            print()
        else:
            print(f"{Colors.OKGREEN}✅ 系统状态良好，可以正常使用{Colors.ENDC}\n")
            print("下一步:")
            print("  1. 运行 scripts/dev.py 启动开发环境")
            print("  2. 访问 http://localhost:5173 开始游戏")
            print()
        
        # 失败项汇总
        if failed > 0:
            print(f"{Colors.FAIL}失败项列表:{Colors.ENDC}")
            for r in self.results:
                if r.status == CheckStatus.FAIL:
                    print(f"  • {r.name}: {r.message}")
                    if r.fix_hint:
                        print(f"    → {r.fix_hint}")
            print()
    
    def _get_version(self, command: str) -> Optional[str]:
        """获取命令版本"""
        try:
            result = subprocess.run(
                [command, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.split('\n')[0].strip()
        except:
            pass
        return None
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return False
        except:
            return True
    
    def _get_port_process(self, port: int) -> Optional[str]:
        """获取占用端口的进程"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(
                    ['netstat', '-ano'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if parts:
                            return parts[-1]  # PID
            else:
                result = subprocess.run(
                    ['lsof', '-i', f':{port}'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        return parts[1] if len(parts) > 1 else None
        except:
            pass
        return None
    
    def _check_health_endpoint(self, port: int) -> bool:
        """检查健康检查端点"""
        try:
            url = f"http://localhost:{port}/health"
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except:
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AI-RPG Engine 统一诊断脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='显示详细信息')
    parser.add_argument('--json', action='store_true',
                       help='输出JSON格式结果')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 运行诊断
    doctor = Doctor(project_root, verbose=args.verbose)
    passed, warned, failed = doctor.run_all_checks()
    
    # JSON输出
    if args.json:
        result = {
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "total": len(doctor.results),
            "checks": [
                {
                    "category": r.category,
                    "name": r.name,
                    "status": r.status.value,
                    "message": r.message,
                    "fix_hint": r.fix_hint
                }
                for r in doctor.results
            ]
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 返回退出码
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
