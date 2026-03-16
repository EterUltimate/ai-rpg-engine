// 游戏类型定义

export interface Character {
  id: string
  name: string
  level: number
  experience: number
  attributes: {
    strength: number
    agility: number
    intelligence: number
    charisma: number
  }
  status: {
    hp: number
    maxHp: number
    mp: number
    maxMp: number
    stamina: number
    maxStamina: number
  }
  inventory: InventoryItem[]
  skills: Skill[]
  equipment: Equipment
  sceneId: string
  createdAt: string
}

export interface InventoryItem {
  id: string
  name: string
  type: 'consumable' | 'weapon' | 'armor' | 'misc'
  description: string
  quantity: number
  effects?: ItemEffect[]
}

export interface ItemEffect {
  type: 'heal' | 'damage' | 'buff'
  value: number
  duration?: number
}

export interface Skill {
  id: string
  name: string
  description: string
  type: 'active' | 'passive'
  mpCost?: number
  cooldown?: number
  damage?: number
}

export interface Equipment {
  weapon?: InventoryItem
  armor?: InventoryItem
  accessory?: InventoryItem
}

export interface Scene {
  id: string
  name: string
  description: string
  type: 'town' | 'forest' | 'dungeon' | 'building'
  connections: string[]
  npcs: string[]
  items: string[]
  events: string[]
  visitedBy: string[]
}

export interface NPC {
  id: string
  name: string
  type: 'merchant' | 'quest_giver' | 'enemy' | 'neutral'
  personality: string
  dialogueStyle: string
  location: string
  relationships: Record<string, number>
  inventory: string[]
}

export interface Quest {
  id: string
  title: string
  description: string
  type: 'main' | 'side' | 'random'
  objectives: QuestObjective[]
  rewards: QuestReward
  status: 'available' | 'active' | 'completed' | 'failed'
  progress: Record<string, number>
}

export interface QuestObjective {
  id: string
  description: string
  type: 'talk' | 'visit' | 'kill' | 'collect' | 'explore'
  target: string
  required: number
  current: number
}

export interface QuestReward {
  gold?: number
  experience?: number
  items?: string[]
}

export interface GameState {
  character: Character
  scene: Scene
  worldState: WorldState
  availableQuests: Quest[]
}

export interface WorldState {
  timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night'
  weather: 'clear' | 'cloudy' | 'rainy' | 'stormy'
  dayCount: number
  globalEvents: string[]
}

export interface ActionOption {
  type: string
  target?: string
  label: string
  icon?: string
}

export interface ChatMessage {
  id: string
  role: 'player' | 'ai' | 'system'
  content: string
  timestamp: Date
  npcName?: string
}

export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}
