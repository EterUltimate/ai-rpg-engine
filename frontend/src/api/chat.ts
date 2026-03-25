import axios from 'axios'

// 所有请求统一走 API 网关（:8000），由网关转发到 ai-engine
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// AI 推理可能较慢（本地 LLM），单独设置 2 分钟超时
const aiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120_000,
})

/**
 * 普通对话（等待完整响应）
 */
export async function sendMessage(
  message: string,
  characterId = '1',
  sceneId = 'main',
  npcId?: string,
): Promise<string> {
  const response = await aiClient.post('/api/v1/ai/chat', {
    message,
    character_id: characterId,
    scene_id: sceneId,
    ...(npcId ? { npc_id: npcId } : {}),
  })
  return response.data.response
}

/**
 * 流式对话（SSE）
 * 路径：GET /api/v1/ai/chat/stream（经网关 SSE 代理转发到 ai-engine）
 */
export function streamMessage(
  message: string,
  onChunk: (chunk: string) => void,
  onComplete: () => void,
  onError: (error: Error) => void,
  characterId = '1',
  sceneId = 'main',
  npcId?: string,
): EventSource {
  const params = new URLSearchParams({
    message,
    character_id: characterId,
    scene_id: sceneId,
    ...(npcId ? { npc_id: npcId } : {}),
  })
  const es = new EventSource(`${API_BASE_URL}/api/v1/ai/chat/stream?${params}`)

  es.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.chunk) onChunk(data.chunk)
    } catch {
      if (event.data) onChunk(event.data)
    }
  }

  es.addEventListener('complete', () => {
    es.close()
    onComplete()
  })

  es.onerror = () => {
    es.close()
    onError(new Error('Stream connection error'))
  }

  return es
}

/**
 * 获取游戏状态
 */
export async function getGameState(characterId: string) {
  const response = await aiClient.get(`/api/v1/game/state/${characterId}`)
  return response.data
}

/**
 * 保存游戏
 */
export async function saveGame(characterId: string, state: any) {
  const response = await aiClient.post('/api/v1/game/save', {
    character_id: characterId,
    state,
  })
  return response.data
}

/**
 * 加载游戏
 */
export async function loadGame(saveId: string) {
  const response = await aiClient.get(`/api/v1/game/load/${saveId}`)
  return response.data
}

/**
 * 执行游戏动作（旧接口兼容）
 */
export async function performAction(action: string, target?: string) {
  const response = await aiClient.post('/api/v1/game/action', { action, target })
  return response.data
}
