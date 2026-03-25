import axios from 'axios'
import type { Character, GameState, ActionOption, APIResponse } from '../types/game'

// 所有请求统一走 API 网关（:8000）
// 通过 VITE_API_URL 环境变量覆盖，Docker / 生产部署时修改此变量即可
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // 网关默认超时 30s；AI 推理接口使用单独的 aiClient（见下方）
  timeout: 30_000,
})

// AI 推理接口单独设置更长的超时（本地 LLM 可能较慢）
const aiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120_000,
})

// 统一错误拦截：打印详细错误日志，便于调试
const errorInterceptor = (error: any) => {
  if (error.response) {
    console.error(
      `[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}`,
      `→ ${error.response.status}`,
      error.response.data,
    )
  } else {
    console.error('[API Error] Network/Timeout:', error.message)
  }
  return Promise.reject(error)
}
apiClient.interceptors.response.use(undefined, errorInterceptor)
aiClient.interceptors.response.use(undefined, errorInterceptor)

// ── 角色相关 API ─────────────────────────────────────────────────────────────
export const characterAPI = {
  create: async (name: string, attributes?: Partial<Character['attributes']>): Promise<Character> => {
    const response = await apiClient.post('/api/v1/character/create', { name, attributes })
    return response.data
  },

  get: async (characterId: string): Promise<Character> => {
    const response = await apiClient.get(`/api/v1/character/${characterId}`)
    return response.data
  },

  update: async (characterId: string, updates: Partial<Character>): Promise<Character> => {
    const response = await apiClient.put(`/api/v1/character/${characterId}`, updates)
    return response.data
  },

  getInventory: async (characterId: string) => {
    const response = await apiClient.get(`/api/v1/character/${characterId}/inventory`)
    return response.data
  },
}

// ── 游戏状态 API ─────────────────────────────────────────────────────────────
export const gameAPI = {
  getState: async (characterId: string): Promise<GameState> => {
    const response = await apiClient.get(`/api/v1/game/state/${characterId}`)
    return response.data
  },

  save: async (characterId: string, state: any): Promise<{ saveId: string }> => {
    const response = await apiClient.post('/api/v1/game/save', {
      character_id: characterId,
      state,
    })
    return response.data
  },

  load: async (saveId: string): Promise<GameState> => {
    const response = await apiClient.get(`/api/v1/game/load/${saveId}`)
    return response.data
  },

  getSaves: async (_characterId: string) => {
    // TODO: 存档列表接口（game-engine 侧待实现）
    return []
  },
}

// ── 动作 API ─────────────────────────────────────────────────────────────────
export const actionAPI = {
  perform: async (
    characterId: string,
    actionType: string,
    target?: string,
    parameters?: any,
  ): Promise<APIResponse<any>> => {
    const response = await apiClient.post('/api/v1/actions/perform', {
      character_id: characterId,
      action_type: actionType,
      target,
      parameters,
    })
    return response.data
  },

  getAvailable: async (characterId: string): Promise<ActionOption[]> => {
    const response = await apiClient.get(`/api/v1/actions/available/${characterId}`)
    return response.data.available_actions
  },

  move: async (characterId: string, targetScene: string) => {
    const response = await apiClient.post('/api/v1/actions/move', {
      character_id: characterId,
      target_scene: targetScene,
    })
    return response.data
  },

  talk: async (characterId: string, npcId: string) => {
    const response = await apiClient.post('/api/v1/actions/talk', {
      character_id: characterId,
      npc_id: npcId,
    })
    return response.data
  },

  investigate: async (characterId: string) => {
    const response = await apiClient.post('/api/v1/actions/investigate', {
      character_id: characterId,
    })
    return response.data
  },

  rest: async (characterId: string) => {
    const response = await apiClient.post('/api/v1/actions/rest', {
      character_id: characterId,
    })
    return response.data
  },

  acceptQuest: async (characterId: string, questId: string) => {
    const response = await apiClient.post('/api/v1/actions/quest/accept', {
      character_id: characterId,
      quest_id: questId,
    })
    return response.data
  },

  completeQuest: async (characterId: string, questId: string) => {
    const response = await apiClient.post('/api/v1/actions/quest/complete', {
      character_id: characterId,
      quest_id: questId,
    })
    return response.data
  },
}

// ── AI 对话 API ──────────────────────────────────────────────────────────────
export const chatAPI = {
  /**
   * 普通对话（等待完整响应）
   */
  send: async (
    message: string,
    characterId: string,
    sceneId: string,
    npcId?: string,
    gameContext?: Record<string, any>,
  ): Promise<string> => {
    const response = await aiClient.post('/api/v1/ai/chat', {
      message,
      character_id: characterId,
      scene_id: sceneId,
      npc_id: npcId,
      game_context: gameContext,
    })
    return response.data.response
  },

  /**
   * 流式对话（SSE）
   * 返回一个 EventSource 实例，调用方负责 close()
   */
  stream: (
    message: string,
    characterId: string,
    sceneId: string,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void,
    npcId?: string,
  ): EventSource => {
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
        // 非 JSON 数据直接透传
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
  },
}

// ── 健康检查 ─────────────────────────────────────────────────────────────────
export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get('/health', { timeout: 5_000 })
    return response.data?.status === 'ok'
  } catch {
    return false
  }
}
