"""
AI Engine 客户端 - game-engine 调用 ai-engine 的轻量 HTTP 客户端

职责：
- 封装对 ai-engine /api/v1/ai/chat 的异步 HTTP 调用
- 支持同步返回和流式 SSE 两种模式
- 网络异常时降级到本地兜底回复，保证游戏不中断
"""
from __future__ import annotations

import os
import json
import logging
from typing import Optional, AsyncIterator, Dict, Any

import httpx

logger = logging.getLogger(__name__)

# ai-engine 地址，优先读环境变量；本地开发默认 :8002
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://localhost:8002")
# HTTP 超时（秒）：connect=5s，read=120s（LLM 推理可能较慢）
_TIMEOUT = httpx.Timeout(connect=5.0, read=120.0, write=10.0, pool=5.0)


def _build_system_prompt(npc: Optional[Dict[str, Any]], scene_name: str, world_time: str) -> str:
    """根据 NPC 属性构造 system prompt"""
    if npc:
        return (
            f"你正在扮演RPG游戏中的NPC角色「{npc.get('name', '神秘人')}」。\n"
            f"性格特征：{npc.get('personality', '沉稳')}。\n"
            f"对话风格：{npc.get('dialogue_style', '简洁')}。\n"
            f"当前位置：{scene_name}（{world_time}）。\n"
            "请以该角色的身份用中文回应玩家，语气自然，契合角色设定，不超过150字。"
        )
    return (
        f"你是RPG游戏「艾尔德兰」的故事叙述者。\n"
        f"当前场景：{scene_name}，时间：{world_time}。\n"
        "请用沉浸式叙述风格描述玩家的周围发生的事情，不超过150字。"
    )


async def chat(
    message: str,
    character_id: str,
    scene_id: str,
    history: Optional[list] = None,
    npc: Optional[Dict[str, Any]] = None,
    scene_name: str = "未知场景",
    world_time: str = "白天",
) -> Dict[str, Any]:
    """
    调用 ai-engine /api/v1/ai/chat，返回 AI 回复。

    返回格式：
        {
            "response": str,          # NPC/叙述者的回复文本
            "ai_used": bool,          # 是否真正调用了 ai-engine
            "fallback": bool,         # 是否触发了本地兜底
            "tokens_used": int
        }
    """
    system_prompt = _build_system_prompt(npc, scene_name, world_time)

    payload = {
        "message": message,
        "character_id": character_id,
        "scene_id": scene_id,
        "history": history or [],
        # 把 system_prompt 放进 parameters 字段，mock 和真实引擎都忽略未知字段
        "system_prompt": system_prompt,
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT, trust_env=False) as client:
            resp = await client.post(
                f"{AI_ENGINE_URL}/api/v1/ai/chat",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "response": data.get("response", ""),
                "ai_used": True,
                "fallback": False,
                "tokens_used": data.get("tokens_used", 0),
            }

    except httpx.TimeoutException:
        logger.warning("ai-engine request timed out, using fallback response")
        return _fallback(message, npc, reason="timeout")

    except httpx.HTTPStatusError as exc:
        logger.warning("ai-engine HTTP error %s, using fallback", exc.response.status_code)
        return _fallback(message, npc, reason=f"http_{exc.response.status_code}")

    except Exception as exc:  # noqa: BLE001
        logger.warning("ai-engine unreachable (%s), using fallback", exc)
        return _fallback(message, npc, reason="unreachable")


async def chat_stream(
    message: str,
    character_id: str,
    scene_id: str,
    npc: Optional[Dict[str, Any]] = None,
    scene_name: str = "未知场景",
    world_time: str = "白天",
) -> AsyncIterator[str]:
    """
    流式调用 ai-engine /api/v1/ai/chat/stream。
    每次 yield 一个 SSE data 行（字符串，已含 'data: ' 前缀）。
    异常时降级为逐词兜底流。
    """
    system_prompt = _build_system_prompt(npc, scene_name, world_time)
    payload = {
        "message": message,
        "character_id": character_id,
        "scene_id": scene_id,
        "system_prompt": system_prompt,
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT, trust_env=False) as client:
            async with client.stream(
                "POST",
                f"{AI_ENGINE_URL}/api/v1/ai/chat/stream",
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        yield line + "\n\n"
        return

    except Exception as exc:  # noqa: BLE001
        logger.warning("ai-engine stream failed (%s), using fallback stream", exc)

    # 兜底：把本地文字拆词流式输出
    fallback_text = _fallback_text(npc)
    for word in fallback_text.split():
        chunk = {"delta": word + " ", "done": False}
        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
    yield f"data: {json.dumps({'delta': '', 'done': True})}\n\n"


# ── 本地兜底 ───────────────────────────────────────────────────────────────

def _fallback_text(npc: Optional[Dict[str, Any]]) -> str:
    if npc:
        return f"{npc.get('name', 'NPC')}若有所思地看着你，暂时没有回应。"
    return "四周一片寂静，故事在此暂停了一瞬。"


def _fallback(
    message: str,
    npc: Optional[Dict[str, Any]],
    reason: str = "unknown",
) -> Dict[str, Any]:
    return {
        "response": _fallback_text(npc),
        "ai_used": False,
        "fallback": True,
        "fallback_reason": reason,
        "tokens_used": 0,
    }
