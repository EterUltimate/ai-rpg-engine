#!/usr/bin/env python3
"""
项目设置脚本 - AI-RPG Engine

功能:
- 安装前端依赖
- 创建 Python 虚拟环境
- 安装后端依赖
- 创建必要的目录结构
- 验证安装结果

用法:
    python scripts/setup.py
    python scripts/setup.py --skip-frontend  # 跳过前端安装
    python scripts/setup.py --skip-backend   # 跳过后端安装
"""

import os
import sys
import subprocess
import platform
import time
import argparse
from pathlib import Path
from typing import List, Optional


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


class SetupManager:
    """安装管理器"""
    
    def __init__(self, project_root: Path):
        self.root = project_root
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None,
                   desc: str = "", capture_output: bool = False) -> bool:
        """运行命令"""
        try:
            print(f"{Colors.OKCYAN}执行: {' '.join(command)}{Colors.ENDC}")
            
            if capture_output:
                result = subprocess.run(
                    command,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                if result.returncode != 0:
                    print(f"{Colors.FAIL}错误: {result.stderr}{Colors.ENDC}")
                    return False
            else:
                result = subprocess.run(
                    command,
                    cwd=cwd,
                    encoding='utf-8',
                    errors='replace'
                )
                if result.returncode != 0:
                    return False
            
            return True
        except Exception as e:
            print(f"{Colors.FAIL}执行失败: {e}{Colors.ENDC}")
            return False
    
    def setup_frontend(self) -> bool:
        """安装前端依赖"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   安装前端依赖{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        frontend_dir = self.root / "frontend"
        
        if not frontend_dir.exists():
            print(f"{Colors.FAIL}[X] 前端目录不存在: {frontend_dir}{Colors.ENDC}\n")
            self.errors.append("前端目录不存在")
            return False
        
        # 检查 Node.js
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print(f"{Colors.FAIL}[X] Node.js 未安装{Colors.ENDC}\n")
                self.errors.append("Node.js 未安装")
                return False
            print(f"{Colors.OKGREEN}[OK] Node.js {result.stdout.strip()}{Colors.ENDC}\n")
        except:
            print(f"{Colors.FAIL}[X] Node.js 未安装{Colors.ENDC}\n")
            self.errors.append("Node.js 未安装")
            return False
        
        # 安装依赖
        print(f"{Colors.BOLD}[1/2] 安装 npm 依赖...{Colors.ENDC}\n")
        if self.run_command(['npm', 'install'], cwd=frontend_dir):
            print(f"\n{Colors.OKGREEN}[OK] npm 依赖安装成功{Colors.ENDC}\n")
        else:
            print(f"\n{Colors.FAIL}[X] npm 依赖安装失败{Colors.ENDC}\n")
            self.errors.append("npm 依赖安装失败")
            return False
        
        # 验证安装
        print(f"{Colors.BOLD}[2/2] 验证安装...{Colors.ENDC}\n")
        node_modules = frontend_dir / "node_modules"
        if node_modules.exists():
            count = len(list(node_modules.iterdir()))
            print(f"{Colors.OKGREEN}[OK] node_modules 存在 ({count} 个包){Colors.ENDC}\n")
            return True
        else:
            print(f"{Colors.FAIL}[X] node_modules 不存在{Colors.ENDC}\n")
            self.errors.append("node_modules 不存在")
            return False
    
    def setup_backend_service(self, service_name: str, service_path: Path) -> bool:
        """安装后端服务"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   安装 {service_name} 依赖{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        if not service_path.exists():
            print(f"{Colors.FAIL}[X] 服务目录不存在: {service_path}{Colors.ENDC}\n")
            self.warnings.append(f"{service_name} 目录不存在")
            return False
        
        # 检查 Python
        python_cmd = 'python' if platform.system() == 'Windows' else 'python3'
        try:
            result = subprocess.run(
                [python_cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print(f"{Colors.FAIL}[X] Python 未安装{Colors.ENDC}\n")
                self.errors.append("Python 未安装")
                return False
            print(f"{Colors.OKGREEN}[OK] {result.stdout.strip()}{Colors.ENDC}\n")
        except:
            print(f"{Colors.FAIL}[X] Python 未安装{Colors.ENDC}\n")
            self.errors.append("Python 未安装")
            return False
        
        # 创建虚拟环境
        venv_path = service_path / "venv"
        if not venv_path.exists():
            print(f"{Colors.BOLD}[1/3] 创建虚拟环境...{Colors.ENDC}\n")
            if self.run_command([python_cmd, '-m', 'venv', 'venv'], cwd=service_path):
                print(f"{Colors.OKGREEN}[OK] 虚拟环境创建成功{Colors.ENDC}\n")
            else:
                print(f"{Colors.FAIL}[X] 虚拟环境创建失败{Colors.ENDC}\n")
                self.errors.append(f"{service_name} 虚拟环境创建失败")
                return False
        else:
            print(f"{Colors.OKCYAN}[i] 虚拟环境已存在，跳过创建{Colors.ENDC}\n")
        
        # 激活虚拟环境并安装依赖
        if platform.system() == 'Windows':
            pip_path = venv_path / "Scripts" / "pip.exe"
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"
        
        # 升级 pip
        print(f"{Colors.BOLD}[2/3] 升级 pip...{Colors.ENDC}\n")
        self.run_command([str(python_path), '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        # 安装依赖
        requirements_file = service_path / "requirements.txt"
        if requirements_file.exists():
            print(f"\n{Colors.BOLD}[3/3] 安装 Python 依赖...{Colors.ENDC}\n")
            if self.run_command([str(pip_path), 'install', '-r', 'requirements.txt'], 
                              cwd=service_path):
                print(f"\n{Colors.OKGREEN}[OK] Python 依赖安装成功{Colors.ENDC}\n")
            else:
                print(f"\n{Colors.FAIL}[X] Python 依赖安装失败{Colors.ENDC}\n")
                self.errors.append(f"{service_name} Python 依赖安装失败")
                return False
        else:
            print(f"{Colors.WARNING}[!] requirements.txt 不存在{Colors.ENDC}\n")
            self.warnings.append(f"{service_name} requirements.txt 不存在")
        
        # 验证安装
        print(f"{Colors.BOLD}验证安装...{Colors.ENDC}\n")
        if venv_path.exists():
            print(f"{Colors.OKGREEN}[OK] 虚拟环境存在: {venv_path.relative_to(self.root)}{Colors.ENDC}\n")
            return True
        else:
            print(f"{Colors.FAIL}[X] 虚拟环境不存在{Colors.ENDC}\n")
            return False
    
    def setup_go_gateway(self) -> bool:
        """安装 Go 网关依赖"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   安装 Go 网关依赖{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        gateway_dir = self.root / "backend" / "gateway"
        
        if not gateway_dir.exists():
            print(f"{Colors.WARNING}[!] Go 网关目录不存在（可选）{Colors.ENDC}\n")
            self.warnings.append("Go 网关目录不存在")
            return False
        
        # 检查 Go
        try:
            result = subprocess.run(
                ['go', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                print(f"{Colors.WARNING}[!] Go 未安装（可选）{Colors.ENDC}\n")
                self.warnings.append("Go 未安装")
                return False
            print(f"{Colors.OKGREEN}[OK] {result.stdout.strip()}{Colors.ENDC}\n")
        except:
            print(f"{Colors.WARNING}[!] Go 未安装（可选）{Colors.ENDC}\n")
            self.warnings.append("Go 未安装")
            return False
        
        # 下载依赖
        print(f"{Colors.BOLD}[1/3] 检查Go依赖...{Colors.ENDC}\n")
        if self.run_command(['go', 'mod', 'download'], cwd=gateway_dir):
            print(f"{Colors.OKGREEN}[OK] Go 模块下载成功{Colors.ENDC}\n")
        else:
            print(f"{Colors.FAIL}[X] Go 模块下载失败{Colors.ENDC}\n")
            self.warnings.append("Go 模块下载失败")
            return False
        
        # 编译 Go 程序
        print(f"{Colors.BOLD}[2/3] 编译Go程序...{Colors.ENDC}\n")
        exe_name = "gateway.exe" if platform.system() == 'Windows' else "gateway"
        if self.run_command(['go', 'build', '-o', exe_name, 'cmd/main.go'], cwd=gateway_dir):
            print(f"{Colors.OKGREEN}[OK] Go 网关编译成功{Colors.ENDC}\n")
        else:
            print(f"{Colors.FAIL}[X] Go 网关构建失败{Colors.ENDC}\n")
            self.errors.append("Go 网关构建失败")
            return False
        
        # 验证
        print(f"{Colors.BOLD}[3/3] 验证安装...{Colors.ENDC}\n")
        go_sum = gateway_dir / "go.sum"
        gateway_exe = gateway_dir / exe_name
        
        if gateway_exe.exists():
            file_size = gateway_exe.stat().st_size / (1024 * 1024)  # MB
            print(f"{Colors.OKGREEN}[OK] 网关可执行文件存在: {exe_name} ({file_size:.2f} MB){Colors.ENDC}\n")
            return True
        else:
            print(f"{Colors.FAIL}[X] 网关可执行文件不存在{Colors.ENDC}\n")
            self.errors.append("网关可执行文件不存在")
            return False
    
    def create_directories(self):
        """创建必要的目录"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   创建目录结构{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        dirs_to_create = [
            "database/sqlite",
            "database/chromadb",
            "logs",
            "models/llm",
            "models/embeddings",
            "models/rerankers",
        ]
        
        for dir_path in dirs_to_create:
            full_path = self.root / dir_path
            if not full_path.exists():
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    print(f"{Colors.OKGREEN}[OK] 创建: {dir_path}{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.FAIL}[X] 创建失败: {dir_path} - {e}{Colors.ENDC}")
                    self.errors.append(f"无法创建目录: {dir_path}")
            else:
                print(f"{Colors.OKCYAN}[i] 已存在: {dir_path}{Colors.ENDC}")
        
        print()
    
    def print_summary(self):
        """打印安装总结"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   安装总结{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        if self.errors:
            print(f"{Colors.FAIL}[ERROR] 错误 ({len(self.errors)}):{Colors.ENDC}")
            for error in self.errors:
                print(f"  {Colors.FAIL}- {error}{Colors.ENDC}")
            print()
        
        if self.warnings:
            print(f"{Colors.WARNING}[!]️  警告 ({len(self.warnings)}):{Colors.ENDC}")
            for warning in self.warnings:
                print(f"  {Colors.WARNING}- {warning}{Colors.ENDC}")
            print()
        
        if not self.errors:
            if not self.warnings:
                print(f"{Colors.OKGREEN}[SUCCESS] 所有依赖安装成功！{Colors.ENDC}\n")
            else:
                print(f"{Colors.OKGREEN}[OK] 基础依赖安装成功（有部分可选项未安装）{Colors.ENDC}\n")
            
            print("下一步:")
            print("  1. 下载模型: python scripts/download-models.py")
            print("  2. 启动服务: python scripts/dev.py")
            print("  3. 访问游戏: http://localhost:5173\n")
        else:
            print(f"{Colors.FAIL}[ERROR] 安装未完成，请解决上述错误后重试{Colors.ENDC}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI-RPG Engine 安装脚本')
    parser.add_argument('--skip-frontend', action='store_true',
                       help='跳过前端安装')
    parser.add_argument('--skip-backend', action='store_true',
                       help='跳过后端安装')
    parser.add_argument('--skip-go', action='store_true',
                       help='跳过 Go 网关安装')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"\n{Colors.HEADER}{'═'*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}   AI-RPG Engine 安装向导{Colors.ENDC}")
    print(f"{Colors.HEADER}{'═'*60}{Colors.ENDC}\n")
    
    print(f"安装时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目路径: {project_root}\n")
    
    manager = SetupManager(project_root)
    
    # 创建目录
    manager.create_directories()
    
    # 安装前端
    if not args.skip_frontend:
        manager.setup_frontend()
    
    # 安装后端服务
    if not args.skip_backend:
        manager.setup_backend_service(
            "游戏引擎",
            project_root / "backend" / "services" / "game-engine"
        )
        manager.setup_backend_service(
            "AI引擎",
            project_root / "backend" / "services" / "ai-engine"
        )
    
    # 安装 Go 网关
    if not args.skip_go:
        manager.setup_go_gateway()
    
    # 打印总结
    manager.print_summary()
    
    # 返回退出码
    sys.exit(0 if len(manager.errors) == 0 else 1)


if __name__ == "__main__":
    main()
