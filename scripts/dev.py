#!/usr/bin/env python3
"""
统一开发启动脚本 - AI-RPG Engine

功能:
- 检查环境依赖
- 检查模型文件
- 检查数据库文件
- 启动所有服务（game-engine, ai-engine, gateway, frontend）
- 输出日志和访问地址
- 支持跨平台运行（Windows/Linux/macOS）

用法:
    python scripts/dev.py
    python scripts/dev.py --check-only  # 仅检查环境
    python scripts/dev.py --skip-checks # 跳过检查直接启动
"""

import os
import sys
import subprocess
import platform
import time
import argparse
import signal
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import threading
import queue

# 颜色输出（跨平台）
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
                # 启用虚拟终端处理
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass

# 启用颜色支持
Colors.enable_windows_colors()


class ServiceProcess:
    """服务进程管理器"""
    
    def __init__(self, name: str, command: List[str], cwd: Path, port: int):
        self.name = name
        self.command = command
        self.cwd = cwd
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        self.log_queue = queue.Queue()
        self.is_running = False
        
    def start(self):
        """启动服务"""
        try:
            # 创建日志目录
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # 启动进程
            self.process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )
            self.is_running = True
            
            # 启动日志读取线程
            thread = threading.Thread(target=self._read_output, daemon=True)
            thread.start()
            
            return True
        except Exception as e:
            print(f"{Colors.FAIL}✗ 启动 {self.name} 失败: {e}{Colors.ENDC}")
            return False
    
    def _read_output(self):
        """读取进程输出"""
        if not self.process:
            return
            
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.log_queue.put(f"[{self.name}] {line.rstrip()}")
        except:
            pass
        finally:
            self.is_running = False
    
    def stop(self):
        """停止服务"""
        if self.process:
            try:
                # Windows下需要特殊处理
                if platform.system() == 'Windows':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.process.pid)],
                                 capture_output=True)
                else:
                    self.process.terminate()
                    self.process.wait(timeout=5)
            except:
                pass
            finally:
                self.is_running = False
    
    def check_health(self) -> bool:
        """检查服务健康状态"""
        import urllib.request
        import urllib.error
        
        try:
            url = f"http://localhost:{self.port}/health"
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except:
            return False


class EnvironmentChecker:
    """环境检查器"""
    
    def __init__(self, project_root: Path):
        self.root = project_root
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.infos: List[str] = []
    
    def check_all(self) -> bool:
        """执行所有检查"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   AI-RPG Engine 环境检查{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        checks = [
            ("基础环境", self.check_basic_environment),
            ("依赖状态", self.check_dependencies),
            ("模型状态", self.check_models),
            ("数据库状态", self.check_database),
            ("端口状态", self.check_ports),
            ("目录权限", self.check_permissions),
            ("配置一致性", self.check_config_consistency),
        ]
        
        for check_name, check_func in checks:
            print(f"{Colors.BOLD}[检查] {check_name}{Colors.ENDC}")
            try:
                check_func()
            except Exception as e:
                self.errors.append(f"{check_name}: {e}")
            print()
        
        # 输出总结
        self.print_summary()
        
        return len(self.errors) == 0
    
    def check_basic_environment(self):
        """检查基础环境"""
        # Node.js
        node_version = self._get_command_version('node')
        if node_version:
            major = int(node_version.split('.')[0].replace('v', ''))
            if major >= 18:
                print(f"  {Colors.OKGREEN}✓ Node.js {node_version}{Colors.ENDC}")
            else:
                self.warnings.append(f"Node.js 版本过低 ({node_version})，建议 18+")
                print(f"  {Colors.WARNING}⚠ Node.js {node_version} (建议 18+){Colors.ENDC}")
        else:
            self.errors.append("Node.js 未安装")
            print(f"  {Colors.FAIL}✗ Node.js 未安装{Colors.ENDC}")
        
        # Python
        python_version = self._get_command_version('python') or self._get_command_version('python3')
        if python_version:
            major, minor = map(int, python_version.split('.')[:2])
            if major == 3 and minor >= 10:
                print(f"  {Colors.OKGREEN}✓ Python {python_version}{Colors.ENDC}")
            else:
                self.warnings.append(f"Python 版本过低 ({python_version})，建议 3.10+")
                print(f"  {Colors.WARNING}⚠ Python {python_version} (建议 3.10+){Colors.ENDC}")
        else:
            self.errors.append("Python 未安装")
            print(f"  {Colors.FAIL}✗ Python 未安装{Colors.ENDC}")
        
        # Go
        go_version = self._get_command_version('go')
        if go_version:
            print(f"  {Colors.OKGREEN}✓ Go {go_version}{Colors.ENDC}")
        else:
            self.warnings.append("Go 未安装（可选，如需网关功能）")
            print(f"  {Colors.WARNING}⚠ Go 未安装 (可选){Colors.ENDC}")
    
    def check_dependencies(self):
        """检查依赖安装状态"""
        # 前端依赖
        node_modules = self.root / "frontend" / "node_modules"
        if node_modules.exists():
            print(f"  {Colors.OKGREEN}✓ 前端依赖已安装{Colors.ENDC}")
        else:
            self.errors.append("前端依赖未安装")
            print(f"  {Colors.FAIL}✗ 前端依赖未安装 (运行: cd frontend && npm install){Colors.ENDC}")
        
        # 游戏引擎虚拟环境
        game_venv = self.root / "backend" / "services" / "game-engine" / "venv"
        if game_venv.exists():
            print(f"  {Colors.OKGREEN}✓ 游戏引擎虚拟环境已创建{Colors.ENDC}")
        else:
            self.warnings.append("游戏引擎虚拟环境未创建")
            print(f"  {Colors.WARNING}⚠ 游戏引擎虚拟环境未创建{Colors.ENDC}")
        
        # AI引擎虚拟环境
        ai_venv = self.root / "backend" / "services" / "ai-engine" / "venv"
        if ai_venv.exists():
            print(f"  {Colors.OKGREEN}✓ AI引擎虚拟环境已创建{Colors.ENDC}")
        else:
            self.warnings.append("AI引擎虚拟环境未创建")
            print(f"  {Colors.WARNING}⚠ AI引擎虚拟环境未创建{Colors.ENDC}")
    
    def check_models(self):
        """检查模型文件"""
        models_dir = self.root / "models"
        
        # 嵌入模型
        embeddings_dir = models_dir / "embeddings"
        if embeddings_dir.exists() and any(embeddings_dir.iterdir()):
            print(f"  {Colors.OKGREEN}✓ 嵌入模型已存在{Colors.ENDC}")
        else:
            self.warnings.append("嵌入模型未下载")
            print(f"  {Colors.WARNING}⚠ 嵌入模型未下载 (运行: scripts/download-models.bat){Colors.ENDC}")
        
        # 重排序模型
        rerankers_dir = models_dir / "rerankers"
        if rerankers_dir.exists() and any(rerankers_dir.iterdir()):
            print(f"  {Colors.OKGREEN}✓ 重排序模型已存在{Colors.ENDC}")
        else:
            self.warnings.append("重排序模型未下载")
            print(f"  {Colors.WARNING}⚠ 重排序模型未下载 (运行: scripts/download-models.bat){Colors.ENDC}")
        
        # LLM模型
        llm_dir = models_dir / "llm"
        if llm_dir.exists() and any(llm_dir.iterdir()):
            files = list(llm_dir.glob("*.gguf"))
            if files:
                total_size = sum(f.stat().st_size for f in files) / (1024**3)
                print(f"  {Colors.OKGREEN}✓ LLM模型已存在 ({len(files)} 个文件, {total_size:.2f} GB){Colors.ENDC}")
            else:
                self.warnings.append("LLM模型目录为空")
                print(f"  {Colors.WARNING}⚠ LLM模型目录为空{Colors.ENDC}")
        else:
            self.warnings.append("LLM模型未下载")
            print(f"  {Colors.WARNING}⚠ LLM模型未下载{Colors.ENDC}")
    
    def check_database(self):
        """检查数据库"""
        database_dir = self.root / "database"
        
        # SQLite
        sqlite_dir = database_dir / "sqlite"
        if sqlite_dir.exists():
            db_file = sqlite_dir / "game.db"
            if db_file.exists():
                size_mb = db_file.stat().st_size / (1024**2)
                print(f"  {Colors.OKGREEN}✓ SQLite数据库存在 ({size_mb:.2f} MB){Colors.ENDC}")
            else:
                print(f"  {Colors.OKCYAN}ℹ SQLite数据库文件不存在（首次运行时创建）{Colors.ENDC}")
        else:
            print(f"  {Colors.WARNING}⚠ SQLite数据库目录不存在{Colors.ENDC}")
        
        # ChromaDB
        chromadb_dir = database_dir / "chromadb"
        if chromadb_dir.exists():
            print(f"  {Colors.OKGREEN}✓ ChromaDB目录存在{Colors.ENDC}")
        else:
            print(f"  {Colors.OKCYAN}ℹ ChromaDB目录不存在（首次运行时创建）{Colors.ENDC}")
    
    def check_ports(self):
        """检查端口占用"""
        ports = {
            8000: "API网关",
            8001: "游戏引擎",
            8002: "AI引擎",
            5173: "前端开发服务器"
        }
        
        for port, service in ports.items():
            if self._is_port_in_use(port):
                self.warnings.append(f"端口 {port} 已被占用 ({service})")
                print(f"  {Colors.WARNING}⚠ 端口 {port} 已被占用 ({service}){Colors.ENDC}")
            else:
                print(f"  {Colors.OKGREEN}✓ 端口 {port} 可用 ({service}){Colors.ENDC}")
    
    def check_permissions(self):
        """检查目录权限"""
        dirs_to_check = [
            self.root / "database",
            self.root / "logs",
        ]
        
        for dir_path in dirs_to_check:
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print(f"  {Colors.OKGREEN}✓ 创建目录: {dir_path.relative_to(self.root)}{Colors.ENDC}")
                except PermissionError:
                    self.errors.append(f"无法创建目录: {dir_path}")
                    print(f"  {Colors.FAIL}✗ 无权限创建目录: {dir_path.relative_to(self.root)}{Colors.ENDC}")
            else:
                # 测试写权限
                test_file = dir_path / ".write_test"
                try:
                    test_file.write_text("test")
                    test_file.unlink()
                    print(f"  {Colors.OKGREEN}✓ 目录可写: {dir_path.relative_to(self.root)}{Colors.ENDC}")
                except:
                    self.errors.append(f"目录无写权限: {dir_path}")
                    print(f"  {Colors.FAIL}✗ 目录无写权限: {dir_path.relative_to(self.root)}{Colors.ENDC}")
    
    def check_config_consistency(self):
        """检查配置一致性"""
        env_example = self.root / ".env.example"
        env_file = self.root / ".env"
        
        if not env_example.exists():
            self.warnings.append(".env.example 文件不存在")
            print(f"  {Colors.WARNING}⚠ .env.example 文件不存在{Colors.ENDC}")
            return
        
        if not env_file.exists():
            print(f"  {Colors.OKCYAN}ℹ .env 文件不存在（使用默认配置）{Colors.ENDC}")
            print(f"  {Colors.OKCYAN}  提示: 复制 .env.example 为 .env 并修改配置{Colors.ENDC}")
        else:
            print(f"  {Colors.OKGREEN}✓ .env 配置文件存在{Colors.ENDC}")
            
            # 检查关键配置项
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    env_content = f.read()
                
                # 检查数据库路径
                if 'DATABASE_URL' in env_content:
                    if 'sqlite+aiosqlite:///' in env_content:
                        print(f"  {Colors.OKGREEN}  ✓ 数据库路径配置正确{Colors.ENDC}")
                    else:
                        self.warnings.append("数据库路径格式可能不正确")
                        print(f"  {Colors.WARNING}  ⚠ 数据库路径格式可能不正确{Colors.ENDC}")
            except:
                pass
    
    def print_summary(self):
        """输出检查总结"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   检查结果{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        if self.errors:
            print(f"{Colors.FAIL}❌ 错误 ({len(self.errors)}):{Colors.ENDC}")
            for error in self.errors:
                print(f"  {Colors.FAIL}• {error}{Colors.ENDC}")
            print()
        
        if self.warnings:
            print(f"{Colors.WARNING}⚠️  警告 ({len(self.warnings)}):{Colors.ENDC}")
            for warning in self.warnings:
                print(f"  {Colors.WARNING}• {warning}{Colors.ENDC}")
            print()
        
        if not self.errors and not self.warnings:
            print(f"{Colors.OKGREEN}✅ 所有检查通过！环境配置完整{Colors.ENDC}\n")
        elif not self.errors:
            print(f"{Colors.OKCYAN}✓ 基础环境完整，但有部分可选功能缺失{Colors.ENDC}\n")
        else:
            print(f"{Colors.FAIL}❌ 环境不完整，请先解决上述错误{Colors.ENDC}\n")
    
    def _get_command_version(self, command: str) -> Optional[str]:
        """获取命令版本"""
        try:
            result = subprocess.run(
                [command, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # 取第一行
                return result.stdout.split('\n')[0].strip()
        except:
            pass
        return None
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return False
        except:
            return True


class DevServerManager:
    """开发服务器管理器"""
    
    def __init__(self, project_root: Path):
        self.root = project_root
        self.services: List[ServiceProcess] = []
        self.log_file = None
        self.log_writer = None
        self.running = True
        
    def setup(self):
        """设置日志文件"""
        log_dir = self.root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"dev_{timestamp}.log"
        self.log_file = open(log_file, 'w', encoding='utf-8')
        
        print(f"{Colors.OKCYAN}日志文件: {log_file}{Colors.ENDC}\n")
    
    def start_all_services(self):
        """启动所有服务"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   启动服务{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        # 定义服务
        services_config = [
            {
                "name": "游戏引擎",
                "emoji": "🎮",
                "port": 8001,
                "cwd": self.root / "backend" / "services" / "game-engine",
                "command": self._get_python_command("main.py")
            },
            {
                "name": "AI引擎",
                "emoji": "🤖",
                "port": 8002,
                "cwd": self.root / "backend" / "services" / "ai-engine",
                "command": self._get_python_command("main.py")
            },
            {
                "name": "API网关",
                "emoji": "🌐",
                "port": 8000,
                "cwd": self.root / "backend" / "gateway",
                "command": ["go", "run", "cmd/main.go"]
            },
            {
                "name": "前端服务",
                "emoji": "💻",
                "port": 5173,
                "cwd": self.root / "frontend",
                "command": ["npm", "run", "dev"]
            }
        ]
        
        # 逐个启动服务
        for idx, config in enumerate(services_config, 1):
            print(f"[{idx}/{len(services_config)}] 启动 {config['name']}...")
            
            if not config['cwd'].exists():
                print(f"  {Colors.WARNING}⚠ 目录不存在，跳过: {config['cwd'].relative_to(self.root)}{Colors.ENDC}\n")
                continue
            
            service = ServiceProcess(
                name=config['name'],
                command=config['command'],
                cwd=config['cwd'],
                port=config['port']
            )
            
            if service.start():
                self.services.append(service)
                print(f"  {Colors.OKGREEN}✓ {config['name']} 已启动 (端口 {config['port']}){Colors.ENDC}\n")
            else:
                print(f"  {Colors.FAIL}✗ {config['name']} 启动失败{Colors.ENDC}\n")
            
            # 等待服务初始化
            time.sleep(2)
        
        # 启动日志监控线程
        log_thread = threading.Thread(target=self._monitor_logs, daemon=True)
        log_thread.start()
        
        return len(self.services) > 0
    
    def _get_python_command(self, script: str) -> List[str]:
        """获取Python命令（优先使用虚拟环境）"""
        # 检查虚拟环境
        venv_python = None
        if platform.system() == 'Windows':
            venv_python = Path("venv/Scripts/python.exe")
        else:
            venv_python = Path("venv/bin/python")
        
        if venv_python.exists():
            return [str(venv_python), script]
        else:
            # 使用系统Python
            return ["python", script]
    
    def _monitor_logs(self):
        """监控所有服务的日志"""
        while self.running:
            for service in self.services:
                try:
                    while True:
                        try:
                            line = service.log_queue.get_nowait()
                            # 写入日志文件
                            if self.log_file:
                                self.log_file.write(line + '\n')
                                self.log_file.flush()
                        except queue.Empty:
                            break
                except:
                    pass
            time.sleep(0.1)
    
    def check_services_health(self):
        """检查服务健康状态"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   服务健康检查{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        print("等待服务启动...\n")
        time.sleep(5)
        
        for service in self.services:
            if service.check_health():
                print(f"  {Colors.OKGREEN}✓ {service.name} (端口 {service.port}) - 运行正常{Colors.ENDC}")
            else:
                print(f"  {Colors.WARNING}⚠ {service.name} (端口 {service.port}) - 未响应或正在启动{Colors.ENDC}")
    
    def print_access_info(self):
        """打印访问信息"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}   服务访问地址{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}🌐 前端界面{Colors.ENDC}")
        print(f"   http://localhost:5173\n")
        
        print(f"{Colors.BOLD}🔌 API网关{Colors.ENDC}")
        print(f"   http://localhost:8000")
        print(f"   http://localhost:8000/health (健康检查)\n")
        
        print(f"{Colors.BOLD}🎮 游戏引擎{Colors.ENDC}")
        print(f"   http://localhost:8001")
        print(f"   http://localhost:8001/health (健康检查)\n")
        
        print(f"{Colors.BOLD}🤖 AI引擎{Colors.ENDC}")
        print(f"   http://localhost:8002")
        print(f"   http://localhost:8002/health (健康检查)\n")
        
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✅ 开发环境已启动！{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        print(f"{Colors.OKCYAN}🎮 打开浏览器访问: http://localhost:5173{Colors.ENDC}")
        print(f"{Colors.OKCYAN}📝 按 Ctrl+C 停止所有服务{Colors.ENDC}\n")
    
    def stop_all(self):
        """停止所有服务"""
        print(f"\n{Colors.WARNING}正在停止所有服务...{Colors.ENDC}")
        
        for service in self.services:
            if service.is_running:
                service.stop()
                print(f"  {Colors.OKGREEN}✓ 已停止 {service.name}{Colors.ENDC}")
        
        if self.log_file:
            self.log_file.close()
        
        self.running = False
        print(f"{Colors.OKGREEN}所有服务已停止{Colors.ENDC}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AI-RPG Engine 统一开发启动脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/dev.py              # 检查环境并启动服务
  python scripts/dev.py --check-only # 仅检查环境
  python scripts/dev.py --skip-checks # 跳过检查直接启动
        """
    )
    parser.add_argument('--check-only', action='store_true',
                       help='仅执行环境检查，不启动服务')
    parser.add_argument('--skip-checks', action='store_true',
                       help='跳过环境检查直接启动服务')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 切换到项目根目录
    os.chdir(project_root)
    
    # 环境检查
    if not args.skip_checks:
        checker = EnvironmentChecker(project_root)
        env_ok = checker.check_all()
        
        if args.check_only:
            sys.exit(0 if env_ok else 1)
        
        if not env_ok:
            print(f"\n{Colors.FAIL}❌ 环境检查未通过，请先解决上述问题{Colors.ENDC}")
            print(f"{Colors.OKCYAN}提示: 运行 scripts/setup.bat 安装依赖{Colors.ENDC}\n")
            sys.exit(1)
    
    # 启动服务
    manager = DevServerManager(project_root)
    manager.setup()
    
    # 注册信号处理
    def signal_handler(sig, frame):
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    if platform.system() != 'Windows':
        signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动所有服务
    if not manager.start_all_services():
        print(f"{Colors.FAIL}❌ 没有服务成功启动{Colors.ENDC}\n")
        sys.exit(1)
    
    # 检查服务健康
    manager.check_services_health()
    
    # 打印访问信息
    manager.print_access_info()
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop_all()


if __name__ == "__main__":
    main()
