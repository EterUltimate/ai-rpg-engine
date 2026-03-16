"""
项目完整性检查脚本
"""
import os
import json
from pathlib import Path
from typing import List, Dict

class ProjectChecker:
    """项目完整性检查器"""
    
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.results = []
    
    def check_file_exists(self, file_path: str, description: str) -> bool:
        """检查文件是否存在"""
        full_path = self.root / file_path
        exists = full_path.exists()
        self.results.append({
            "type": "file",
            "path": file_path,
            "description": description,
            "exists": exists,
            "status": "✅" if exists else "❌"
        })
        return exists
    
    def check_directory_exists(self, dir_path: str, description: str) -> bool:
        """检查目录是否存在"""
        full_path = self.root / dir_path
        exists = full_path.exists() and full_path.is_dir()
        self.results.append({
            "type": "directory",
            "path": dir_path,
            "description": description,
            "exists": exists,
            "status": "✅" if exists else "❌"
        })
        return exists
    
    def check_json_file(self, file_path: str, required_keys: List[str]) -> bool:
        """检查JSON文件是否有效"""
        full_path = self.root / file_path
        if not full_path.exists():
            self.results.append({
                "type": "json",
                "path": file_path,
                "description": "JSON文件检查",
                "exists": False,
                "status": "❌ 文件不存在"
            })
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                self.results.append({
                    "type": "json",
                    "path": file_path,
                    "description": "JSON文件检查",
                    "exists": True,
                    "status": f"⚠️ 缺少字段: {', '.join(missing_keys)}"
                })
                return False
            
            self.results.append({
                "type": "json",
                "path": file_path,
                "description": "JSON文件检查",
                "exists": True,
                "status": "✅ 有效"
            })
            return True
        except Exception as e:
            self.results.append({
                "type": "json",
                "path": file_path,
                "description": "JSON文件检查",
                "exists": True,
                "status": f"❌ 解析错误: {str(e)}"
            })
            return False
    
    def run_all_checks(self) -> Dict:
        """运行所有检查"""
        print("=" * 70)
        print("AI-RPG Engine 项目完整性检查")
        print("=" * 70)
        print()
        
        # 1. 根目录文件
        print("📁 检查根目录文件...")
        self.check_file_exists("README.md", "项目说明文档")
        self.check_file_exists("package.json", "根package.json (可选)", )
        self.check_file_exists(".gitignore", "Git忽略配置")
        self.check_file_exists("docker-compose.yml", "Docker编排文件")
        self.check_file_exists(".env.example", "环境变量示例")
        print()
        
        # 2. 前端项目
        print("🎨 检查前端项目...")
        self.check_directory_exists("frontend", "前端目录")
        self.check_file_exists("frontend/package.json", "前端依赖配置")
        self.check_json_file("frontend/package.json", ["name", "dependencies", "scripts"])
        self.check_file_exists("frontend/tsconfig.json", "TypeScript配置")
        self.check_file_exists("frontend/vite.config.ts", "Vite配置")
        self.check_file_exists("frontend/index.html", "HTML入口")
        self.check_file_exists("frontend/src/main.tsx", "React入口")
        self.check_file_exists("frontend/src/App.tsx", "主应用组件")
        self.check_directory_exists("frontend/src/game", "游戏引擎目录")
        self.check_directory_exists("frontend/src/ui", "UI组件目录")
        self.check_directory_exists("frontend/src/api", "API客户端目录")
        self.check_directory_exists("frontend/src/store", "状态管理目录")
        print()
        
        # 3. 后端Go网关
        print("🐹 检查Go网关...")
        self.check_directory_exists("backend/gateway", "网关目录")
        self.check_file_exists("backend/gateway/go.mod", "Go模块配置")
        self.check_file_exists("backend/gateway/cmd/main.go", "主程序入口")
        self.check_directory_exists("backend/gateway/internal/handlers", "处理器目录")
        self.check_directory_exists("backend/gateway/internal/middleware", "中间件目录")
        print()
        
        # 4. 后端游戏引擎
        print("🎮 检查游戏引擎服务...")
        self.check_directory_exists("backend/services/game-engine", "游戏引擎目录")
        self.check_file_exists("backend/services/game-engine/requirements.txt", "Python依赖")
        self.check_file_exists("backend/services/game-engine/app/main.py", "FastAPI入口")
        self.check_directory_exists("backend/services/game-engine/app/routers", "路由目录")
        self.check_directory_exists("backend/services/game-engine/app/models", "模型目录")
        self.check_directory_exists("backend/services/game-engine/app/game_logic", "游戏逻辑目录")
        print()
        
        # 5. 后端AI引擎
        print("🤖 检查AI引擎服务...")
        self.check_directory_exists("backend/services/ai-engine", "AI引擎目录")
        self.check_file_exists("backend/services/ai-engine/requirements.txt", "Python依赖")
        self.check_file_exists("backend/services/ai-engine/main.py", "FastAPI入口")
        self.check_directory_exists("backend/services/ai-engine/rag", "RAG系统目录")
        self.check_directory_exists("backend/services/ai-engine/llm", "LLM接口目录")
        self.check_directory_exists("backend/services/ai-engine/roleplay", "角色扮演引擎目录")
        self.check_directory_exists("backend/services/ai-engine/routers", "路由目录")
        print()
        
        # 6. 文档
        print("📚 检查文档...")
        self.check_directory_exists("docs", "文档目录")
        self.check_file_exists("docs/architecture.md", "架构文档")
        self.check_file_exists("docs/api-spec.md", "API文档")
        self.check_file_exists("docs/deployment.md", "部署文档")
        self.check_file_exists("QUICKSTART.md", "快速启动指南")
        self.check_file_exists("CONTRIBUTING.md", "贡献指南")
        print()
        
        # 7. 脚本
        print("🛠️ 检查脚本...")
        self.check_directory_exists("scripts", "脚本目录")
        self.check_file_exists("scripts/setup.bat", "Windows安装脚本")
        self.check_file_exists("scripts/setup.sh", "Linux/Mac安装脚本")
        print()
        
        # 8. 测试
        print("🧪 检查测试...")
        self.check_directory_exists("tests", "测试目录")
        self.check_file_exists("tests/integration_test.py", "集成测试脚本")
        self.check_file_exists("tests/integration_test.bat", "测试启动脚本")
        print()
        
        # 生成报告
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """生成检查报告"""
        total = len(self.results)
        passed = sum(1 for r in self.results if "✅" in r["status"])
        failed = total - passed
        
        print("=" * 70)
        print("检查结果汇总")
        print("=" * 70)
        print()
        
        for result in self.results:
            print(f"{result['status']} {result['description']}: {result['path']}")
        
        print()
        print(f"总计: {total} 项检查")
        print(f"通过: {passed} 项")
        print(f"失败: {failed} 项")
        print(f"完整度: {(passed/total*100):.1f}%")
        print()
        
        if failed == 0:
            print("🎉 项目结构完整,所有文件都存在!")
        elif failed < 5:
            print("⚠️  项目基本完整,有少量文件缺失")
        else:
            print("❌ 项目不完整,请检查缺失的文件")
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "completeness": f"{(passed/total*100):.1f}%",
            "results": self.results
        }


if __name__ == "__main__":
    checker = ProjectChecker(".")
    report = checker.run_all_checks()
    
    # 保存报告
    with open("project_check_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n📄 详细报告已保存到: project_check_report.json")
