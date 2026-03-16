import axios from 'axios'
import type { Character, GameState, ActionOption, APIResponse } from '../types/game'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 角色相关API
export const characterAPI = {
  create: async (name: string, attributes?: Partial<Character['attributes']>): Promise<Character> => {
    const response = await apiClient.post('/api/v1/character/create', {
      name,
      attributes
    })
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
  }
}

// 游戏状态API
export const gameAPI = {
  getState: async (characterId: string): Promise<GameState> => {
    const response = await apiClient.get(`/api/v1/game/state/${characterId}`)
    return response.data
  },

  save: async (characterId: string, state: any): Promise<{ saveId: string }> => {
    const response = await apiClient.post('/api/v1/game/save', {
      character_id: characterId,
      state
    })
    return response.data
  },

  load: async (saveId: string): Promise<GameState> => {
    const response = await apiClient.get(`/api/v1/game/load/${saveId}`)
    return response.data
  },

  getSaves: async (_characterId: string) => {
    // TODO: 实现存档列表接口
    return []
  }
}

// 动作相关API
export const actionAPI = {
  perform: async (
    characterId: string,
    actionType: string,
    target?: string,
    parameters?: any
  ): Promise<APIResponse<any>> => {
    const response = await apiClient.post('/api/v1/actions/perform', {
      character_id: characterId,
      action_type: actionType,
      target,
      parameters
    })
    return response.data
  },

  getAvailable: async (characterId: string): Promise<ActionOption[]> => {
    const response = await apiClient.get(`/api/v1/actions/available/${characterId}`)
    return response.data.available_actions
  },

  move: async (characterId: string, targetScene: string) => {
    const response = await apiClient.post('/api/v1/actions/move', null, {
      params: { character_id: characterId, target_scene: targetScene }
    })
    return response.data
  },

  talk: async (characterId: string, npcId: string) => {
    const response = await apiClient.post('/api/v1/actions/talk', null, {
      params: { character_id: characterId, npc_id: npcId }
    })
    return response.data
  },

  investigate: async (characterId: string) => {
    const response = await apiClient.post('/api/v1/actions/investigate', null, {
      params: { character_id: characterId }
    })
    return response.data
  },

  rest: async (characterId: string) => {
    const response = await apiClient.post('/api/v1/actions/rest', null, {
      params: { character_id: characterId }
    })
    return response.data
  },

  acceptQuest: async (characterId: string, questId: string) => {
    const response = await apiClient.post('/api/v1/actions/quest/accept', null, {
      params: { character_id: characterId, quest_id: questId }
    })
    return response.data
  },

  completeQuest: async (characterId: string, questId: string) => {
    const response = await apiClient.post('/api/v1/actions/quest/complete', null, {
      params: { character_id: characterId, quest_id: questId }
    })
    return response.data
  }
}

// AI相关API
export const aiAPI = {
  chat: async (
    message: string,
    characterId: string,
    sceneId: string,
    npcId?: string,
    gameContext?: any
  ): Promise<string> => {
    const response = await apiClient.post('/api/v1/ai/chat', {
      message,
      character_id: characterId,
      scene_id: sceneId,
      npc_id: npcId,
      game_context: gameContext
    })
    return response.data.response
  },

  streamChat: (
    message: string,
    characterId: string,
    sceneId: string,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void,
    npcId?: string
  ) => {
    const params = new URLSearchParams({
      message,
      character_id: characterId,
      scene_id: sceneId
    })
    
    if (npcId) params.append('npc_id', npcId)

    const eventSource = new EventSource(
      `${API_BASE_URL}/api/v1/ai/chat/stream?${params.toString()}`
    )

    eventSource.onmessage = (event) => {
      const data = event.data
      if (data === '[DONE]') {
        eventSource.close()
        onComplete()
      } else if (data.startsWith('[ERROR]')) {
        eventSource.close()
        onError(new Error(data))
      } else {
        onChunk(data)
      }
    }

    eventSource.onerror = (_error) => {
      eventSource.close()
      onError(new Error('Stream connection error'))
    }

    return () => eventSource.close()
  },

  getMemory: async (characterId: string) => {
    const response = await apiClient.get(`/api/v1/ai/memory/${characterId}`)
    return response.data
  },

  getStats: async () => {
    const response = await apiClient.get('/api/v1/ai/stats')
    return response.data
  }
}

// 健康检查
export const healthCheck = async () => {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error) {
    return null
  }
}

export default apiClient
