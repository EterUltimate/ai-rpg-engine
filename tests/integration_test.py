"""
集成测试脚本 - 测试所有API端点和服务
"""
import requests
import time
import json
from typing import Dict, Any

# 服务地址
GATEWAY_URL = "http://localhost:8000"
GAME_ENGINE_URL = "http://localhost:8001"
AI_ENGINE_URL = "http://localhost:8002"

class TestResult:
    """测试结果"""
    def __init__(self, name: str, success: bool, message: str = "", data: Any = None):
        self.name = name
        self.success = success
        self.message = message
        self.data = data
    
    def __str__(self):
        status = "✅ PASS" if self.success else "❌ FAIL"
        return f"{status} - {self.name}: {self.message}"


def test_health_check(service_name: str, url: str) -> TestResult:
    """测试健康检查端点"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            return TestResult(f"{service_name} Health Check", True, "Service is healthy")
        else:
            return TestResult(f"{service_name} Health Check", False, f"Status: {response.status_code}")
    except Exception as e:
        return TestResult(f"{service_name} Health Check", False, str(e))


def test_create_character() -> TestResult:
    """测试创建角色"""
    try:
        data = {
            "name": "测试角色",
            "attributes": {
                "strength": 12,
                "agility": 14,
                "intelligence": 16,
                "charisma": 10
            }
        }
        
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/character/create",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200 or response.status_code == 201:
            character = response.json()
            return TestResult(
                "Create Character",
                True,
                f"Character created: {character.get('id')}",
                character
            )
        else:
            return TestResult("Create Character", False, f"Status: {response.status_code}")
    except Exception as e:
        return TestResult("Create Character", False, str(e))


def test_get_game_state(character_id: str) -> TestResult:
    """测试获取游戏状态"""
    try:
        response = requests.get(
            f"{GATEWAY_URL}/api/v1/game/state/{character_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            state = response.json()
            return TestResult(
                "Get Game State",
                True,
                f"Scene: {state.get('scene', 'unknown')}",
                state
            )
        else:
            return TestResult("Get Game State", False, f"Status: {response.status_code}")
    except Exception as e:
        return TestResult("Get Game State", False, str(e))


def test_perform_action(character_id: str) -> TestResult:
    """测试执行动作"""
    try:
        data = {
            "character_id": character_id,
            "action_type": "investigate",
            "parameters": {}
        }
        
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/actions/perform",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return TestResult(
                "Perform Action",
                result.get("success", False),
                result.get("message", "Action executed"),
                result
            )
        else:
            return TestResult("Perform Action", False, f"Status: {response.status_code}")
    except Exception as e:
        return TestResult("Perform Action", False, str(e))


def test_ai_chat(character_id: str, scene_id: str = "village_001") -> TestResult:
    """测试AI对话"""
    try:
        data = {
            "message": "你好,这是一个测试消息",
            "character_id": character_id,
            "scene_id": scene_id
        }
        
        start_time = time.time()
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/ai/chat",
            json=data,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return TestResult(
                "AI Chat",
                True,
                f"Response time: {elapsed:.2f}s",
                result
            )
        else:
            return TestResult("AI Chat", False, f"Status: {response.status_code}")
    except Exception as e:
        return TestResult("AI Chat", False, str(e))


def test_save_game(character_id: str) -> TestResult:
    """测试保存游戏"""
    try:
        data = {
            "character_id": character_id,
            "state": {
                "test": "integration_test"
            }
        }
        
        response = requests.post(
            f"{GATEWAY_URL}/api/v1/game/save",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return TestResult(
                "Save Game",
                True,
                f"Save ID: {result.get('save_id')}",
                result
            )
        else:
            return TestResult("Save Game", False, f"Status: {response.status_code}")
    except Exception as e:
        return TestResult("Save Game", False, str(e))


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("AI-RPG Engine 集成测试")
    print("=" * 60)
    print()
    
    results = []
    
    # 1. 健康检查
    print("📋 测试服务健康状态...")
    results.append(test_health_check("Gateway", GATEWAY_URL))
    results.append(test_health_check("Game Engine", GAME_ENGINE_URL))
    results.append(test_health_check("AI Engine", AI_ENGINE_URL))
    print()
    
    # 2. 创建角色
    print("👤 测试创建角色...")
    create_result = test_create_character()
    results.append(create_result)
    
    if create_result.success and create_result.data:
        character_id = create_result.data.get("id")
        
        # 3. 获取游戏状态
        print("\n🎮 测试获取游戏状态...")
        results.append(test_get_game_state(character_id))
        
        # 4. 执行动作
        print("\n⚔️  测试执行动作...")
        results.append(test_perform_action(character_id))
        
        # 5. AI对话
        print("\n💬 测试AI对话...")
        results.append(test_ai_chat(character_id))
        
        # 6. 保存游戏
        print("\n💾 测试保存游戏...")
        results.append(test_save_game(character_id))
    
    print()
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    # 统计
    total = len(results)
    passed = sum(1 for r in results if r.success)
    failed = total - passed
    
    for result in results:
        print(result)
    
    print()
    print(f"总计: {total} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print(f"成功率: {(passed/total*100):.1f}%")
    print()
    
    return results


if __name__ == "__main__":
    run_all_tests()
