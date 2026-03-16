import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 发送消息到AI
 */
export async function sendMessage(message: string): Promise<string> {
  try {
    const response = await apiClient.post('/api/v1/ai/chat', {
      message,
      character_id: '1',
      scene_id: 'main',
    })
    
    return response.data.response
  } catch (error) {
    console.error('Send message error:', error)
    throw error
  }
}

/**
 * 流式对话 (SSE)
 */
export function streamMessage(
  message: string,
  onChunk: (chunk: string) => void,
  onComplete: () => void,
  onError: (error: Error) => void
): void {
  const eventSource = new EventSource(
    `${API_BASE_URL}/api/v1/ai/chat/stream?message=${encodeURIComponent(message)}&character_id=1&scene_id=main`
  )

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.chunk) {
      onChunk(data.chunk)
    }
  }

  eventSource.onerror = (_error) => {
    eventSource.close()
    onError(new Error('Stream connection error'))
  }

  eventSource.addEventListener('complete', () => {
    eventSource.close()
    onComplete()
  })
}

/**
 * 获取游戏状态
 */
export async function getGameState(characterId: string) {
  const response = await apiClient.get(`/api/v1/game/state/${characterId}`)
  return response.data
}

/**
 * 保存游戏
 */
export async function saveGame(characterId: string, state: any) {
  const response = await apiClient.post('/api/v1/game/save', {
    character_id: characterId,
    state,
  })
  return response.data
}

/**
 * 加载游戏
 */
export async function loadGame(saveId: string) {
  const response = await apiClient.get(`/api/v1/game/load/${saveId}`)
  return response.data
}

/**
 * 执行游戏动作
 */
export async function performAction(action: string, target?: string) {
  const response = await apiClient.post('/api/v1/game/action', {
    action,
    target,
  })
  return response.data
}
