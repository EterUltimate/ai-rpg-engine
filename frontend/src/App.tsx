import { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom'
import GameCanvas from './game/GameCanvas'
import EnhancedHUD from './ui/hud/EnhancedHUD'
import EnhancedChat from './ui/chat/EnhancedChat'
import InventoryPanel from './ui/inventory/InventoryPanel'
import QuestLog from './ui/quest/QuestLog'
import CharacterCreation from './ui/character/CharacterCreation'
import CharacterSheet from './ui/character/CharacterSheet'
import useGameStore from './store/gameStore'
import { gameAPI, actionAPI, healthCheck } from './api/gameApi'

function App() {
  const [isLoading, setIsLoading] = useState(true)
  const [showCharacterCreation, setShowCharacterCreation] = useState(false)
  // API状态监控(可用于UI显示或调试)
  const [_apiStatus, setApiStatus] = useState({
    gateway: false,
    gameEngine: false,
    aiEngine: false
  })

  useEffect(() => {
    // 检查API状态
    checkAPIs()
    
    // 尝试加载已有角色
    loadExistingCharacter()
  }, [])

  const checkAPIs = async () => {
    const status = {
      gateway: false,
      gameEngine: false,
      aiEngine: false
    }

    try {
      const gateway = await healthCheck()
      status.gateway = !!gateway
    } catch (error) {
      console.warn('Gateway not available')
    }

    try {
      const gameEngine = await fetch('http://localhost:8001/health').then(r => r.json())
      status.gameEngine = !!gameEngine
    } catch (error) {
      console.warn('Game Engine not available')
    }

    try {
      const aiEngine = await fetch('http://localhost:8002/health').then(r => r.json())
      status.aiEngine = !!aiEngine
    } catch (error) {
      console.warn('AI Engine not available')
    }

    setApiStatus(status)
  }

  const loadExistingCharacter = async () => {
    // TODO: 从本地存储或后端加载角色
    setIsLoading(false)
    setShowCharacterCreation(true)
  }

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <Router>
      <div className="game-container">
        <Routes>
          <Route 
            path="/" 
            element={
              <GamePage 
                showCharacterCreation={showCharacterCreation}
                onCharacterCreated={() => setShowCharacterCreation(false)}
              />
            } 
          />
          <Route path="/menu" element={<MenuPage onStartGame={() => setShowCharacterCreation(true)} />} />
        </Routes>
      </div>
    </Router>
  )
}

function LoadingScreen() {
  return (
    <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="text-6xl mb-4 animate-bounce">🎮</div>
        <h1 className="text-3xl font-bold text-white mb-4">AI-RPG Engine</h1>
        <div className="flex items-center justify-center space-x-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-3 h-3 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
        <p className="text-gray-400 mt-4">正在加载游戏...</p>
      </div>
    </div>
  )
}

function GamePage({ showCharacterCreation, onCharacterCreated }: { showCharacterCreation: boolean, onCharacterCreated: () => void }) {
  const { 
    character, 
    setCharacter,
    setCurrentScene,
    setAvailableActions,
    setNPCsInScene,
    setLoading
  } = useGameStore()

  useEffect(() => {
    if (character) {
      loadGameState()
    }
  }, [character])

  const loadGameState = async () => {
    if (!character) return
    
    setLoading(true)
    try {
      // 加载游戏状态
      const gameState = await gameAPI.getState(character.id)
      
      if (gameState.scene) {
        setCurrentScene(gameState.scene)
      }

      // 加载可用动作
      const actions = await actionAPI.getAvailable(character.id)
      setAvailableActions(actions)

      // 加载NPC
      if (gameState.scene?.npcs) {
        // npcs是NPC ID数组,需要转换为NPC对象
        const npcs = gameState.scene.npcs.map(npcId => ({
          id: npcId,
          name: npcId,
          type: 'neutral' as const,
          description: '',
          personality: '',
          dialogueStyle: '',
          location: gameState.scene.id,
          relationships: {},
          inventory: []
        }))
        setNPCsInScene(npcs)
      }
    } catch (error) {
      console.error('Failed to load game state:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCharacterCreated = (newCharacter: any) => {
    setCharacter(newCharacter)
    onCharacterCreated()
  }

  return (
    <>
      {/* 游戏画布 */}
      <GameCanvas />
      
      {/* HUD界面 */}
      {character && <EnhancedHUD />}
      
      {/* AI对话界面 */}
      <EnhancedChat />
      
      {/* 背包界面 */}
      <InventoryPanel />
      
      {/* 任务日志 */}
      <QuestLog />
      
      {/* 角色详情 */}
      <CharacterSheet />
      
      {/* 角色创建 */}
      {showCharacterCreation && !character && (
        <CharacterCreation 
          onComplete={handleCharacterCreated}
          onCancel={() => {}} 
        />
      )}
    </>
  )
}

function MenuPage({ onStartGame }: { onStartGame: () => void }) {
  const navigate = useNavigate()
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-8">
      <div className="text-center max-w-2xl">
        <div className="mb-8">
          <h1 className="text-7xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 mb-4">
            AI-RPG Engine
          </h1>
          <div className="w-32 h-1 bg-gradient-to-r from-blue-500 to-purple-500 mx-auto mb-6"></div>
          <p className="text-xl text-gray-300 mb-2">
            AI驱动的角色扮演游戏
          </p>
          <p className="text-sm text-gray-500">
            由大语言模型和RAG系统支持
          </p>
        </div>

        <div className="space-y-4 mb-12">
          <div className="flex items-center justify-center space-x-8 text-sm text-gray-400">
            <span className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              RAG记忆系统
            </span>
            <span className="flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
              动态剧情生成
            </span>
            <span className="flex items-center">
              <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
              智能NPC交互
            </span>
          </div>
        </div>

        <div className="space-y-3">
          <button 
            onClick={onStartGame}
            className="w-full px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white text-lg font-semibold rounded-xl shadow-lg shadow-purple-500/50 transition-all transform hover:scale-105"
          >
            🎮 开始新游戏
          </button>
          
          <button 
            onClick={() => navigate('/')}
            className="w-full px-8 py-4 bg-gray-800 hover:bg-gray-700 text-gray-300 text-lg font-semibold rounded-xl transition-colors"
          >
            📂 继续游戏
          </button>
        </div>

        <div className="mt-12 text-xs text-gray-500">
          <p>按 Enter 快速开始 | 访问 GitHub 查看源码</p>
        </div>
      </div>
    </div>
  )
}

export default App
