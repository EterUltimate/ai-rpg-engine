import { create } from 'zustand'
import Phaser from 'phaser'
import { Character, Scene as GameScene, Quest, NPC } from '../types/game'

interface ChatMessage {
  id: string
  role: 'player' | 'ai' | 'system'
  content: string
  timestamp: Date
  npcName?: string
}

interface GameStore {
  // 游戏实例
  phaserGame: Phaser.Game | null
  setPhaserGame: (game: Phaser.Game) => void

  // 角色信息
  character: Character | null
  setCharacter: (character: Character) => void
  updateCharacterStatus: (status: Partial<Character['status']>) => void

  // 当前场景
  currentScene: GameScene | null
  setCurrentScene: (scene: GameScene) => void
  availableActions: any[]
  setAvailableActions: (actions: any[]) => void

  // 任务系统
  activeQuests: Quest[]
  addQuest: (quest: Quest) => void
  updateQuestProgress: (questId: string, progress: any) => void

  // NPC系统
  npcsInScene: NPC[]
  setNPCsInScene: (npcs: NPC[]) => void

  // 聊天系统
  isChatOpen: boolean
  chatMessages: ChatMessage[]
  currentNPC: NPC | null
  toggleChat: () => void
  openChatWithNPC: (npc: NPC) => void
  closeChat: () => void
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  clearMessages: () => void

  // UI状态
  isInventoryOpen: boolean
  toggleInventory: () => void
  
  isQuestLogOpen: boolean
  toggleQuestLog: () => void

  isCharacterSheetOpen: boolean
  toggleCharacterSheet: () => void

  // 游戏状态
  isLoading: boolean
  setLoading: (loading: boolean) => void
  error: string | null
  setError: (error: string | null) => void

  // 游戏世界状态
  worldTime: string
  worldWeather: string
  updateWorldState: (time: string, weather: string) => void
}

const useGameStore = create<GameStore>((set) => ({
  // 游戏实例
  phaserGame: null,
  setPhaserGame: (game) => set({ phaserGame: game }),

  // 角色信息
  character: null,
  setCharacter: (character) => set({ character }),
  updateCharacterStatus: (status) => set((state) => ({
    character: state.character ? {
      ...state.character,
      status: { ...state.character.status, ...status }
    } : null
  })),

  // 当前场景
  currentScene: null,
  setCurrentScene: (scene) => set({ currentScene: scene }),
  availableActions: [],
  setAvailableActions: (actions) => set({ availableActions: actions }),

  // 任务系统
  activeQuests: [],
  addQuest: (quest) => set((state) => ({
    activeQuests: [...state.activeQuests, quest]
  })),
  updateQuestProgress: (questId, progress) => set((state) => ({
    activeQuests: state.activeQuests.map(q => 
      q.id === questId ? { ...q, progress: { ...q.progress, ...progress } } : q
    )
  })),

  // NPC系统
  npcsInScene: [],
  setNPCsInScene: (npcs) => set({ npcsInScene: npcs }),

  // 聊天系统
  isChatOpen: false,
  chatMessages: [],
  currentNPC: null,
  toggleChat: () => set((state) => ({ isChatOpen: !state.isChatOpen })),
  openChatWithNPC: (npc) => set({ isChatOpen: true, currentNPC: npc }),
  closeChat: () => set({ isChatOpen: false, currentNPC: null }),
  addMessage: (message) =>
    set((state) => ({
      chatMessages: [
        ...state.chatMessages,
        {
          ...message,
          id: Date.now().toString(),
          timestamp: new Date(),
        },
      ],
    })),
  clearMessages: () => set({ chatMessages: [] }),

  // UI状态
  isInventoryOpen: false,
  toggleInventory: () => set((state) => ({ isInventoryOpen: !state.isInventoryOpen })),
  
  isQuestLogOpen: false,
  toggleQuestLog: () => set((state) => ({ isQuestLogOpen: !state.isQuestLogOpen })),

  isCharacterSheetOpen: false,
  toggleCharacterSheet: () => set((state) => ({ 
    isCharacterSheetOpen: !state.isCharacterSheetOpen 
  })),

  // 游戏状态
  isLoading: false,
  setLoading: (loading) => set({ isLoading: loading }),
  error: null,
  setError: (error) => set({ error }),

  // 游戏世界状态
  worldTime: 'morning',
  worldWeather: 'clear',
  updateWorldState: (time, weather) => set({ 
    worldTime: time, 
    worldWeather: weather 
  }),
}))

export default useGameStore
