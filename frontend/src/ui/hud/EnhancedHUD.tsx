import React, { useState } from 'react'
import useGameStore from '../../store/gameStore'
import { actionAPI } from '../../api/gameApi'

const EnhancedHUD: React.FC = () => {
  const { 
    character, 
    currentScene,
    availableActions,
    npcsInScene,
    worldTime,
    worldWeather,
    toggleInventory,
    toggleQuestLog,
    toggleCharacterSheet,
    isInventoryOpen,
    isQuestLogOpen,
    isCharacterSheetOpen: _isCharacterSheetOpen,
    setLoading,
    openChatWithNPC
  } = useGameStore()

  const [showActions, setShowActions] = useState(false)

  if (!character) return null

  const handleAction = async (action: any) => {
    if (!character) return
    
    setLoading(true)
    try {
      const result = await actionAPI.perform(
        character.id,
        action.type,
        action.target
      )
      
      if (result.success) {
        console.log('Action performed:', result)
      }
    } catch (error) {
      console.error('Action error:', error)
    } finally {
      setLoading(false)
      setShowActions(false)
    }
  }

  const handleNPCClick = (npc: any) => {
    openChatWithNPC(npc)
  }

  return (
    <>
      {/* 角色状态栏 */}
      <div className="absolute top-4 left-4 bg-gray-900 bg-opacity-95 rounded-lg shadow-2xl p-4 min-w-[280px] border border-gray-700">
        {/* 角色名称和等级 */}
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-xl font-bold text-white">{character.name}</h3>
            <p className="text-sm text-gray-400">Lv.{character.level} 冒险者</p>
          </div>
          <button
            onClick={toggleCharacterSheet}
            className="text-gray-400 hover:text-white transition-colors"
            title="角色详情"
          >
            👤
          </button>
        </div>

        {/* 生命值 */}
        <div className="mb-3">
          <div className="flex justify-between text-xs text-gray-300 mb-1">
            <span className="flex items-center">
              <span className="mr-1">❤️</span> HP
            </span>
            <span className="font-mono">
              {character.status.hp} / {character.status.maxHp}
            </span>
          </div>
          <div className="h-3 bg-gray-800 rounded-full overflow-hidden border border-gray-700">
            <div
              className="h-full bg-gradient-to-r from-red-600 to-red-500 transition-all duration-500 relative"
              style={{ width: `${(character.status.hp / character.status.maxHp) * 100}%` }}
            >
              <div className="absolute inset-0 bg-white opacity-20 animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* 魔法值 */}
        <div className="mb-3">
          <div className="flex justify-between text-xs text-gray-300 mb-1">
            <span className="flex items-center">
              <span className="mr-1">💧</span> MP
            </span>
            <span className="font-mono">
              {character.status.mp} / {character.status.maxMp}
            </span>
          </div>
          <div className="h-3 bg-gray-800 rounded-full overflow-hidden border border-gray-700">
            <div
              className="h-full bg-gradient-to-r from-blue-600 to-blue-500 transition-all duration-500"
              style={{ width: `${(character.status.mp / character.status.maxMp) * 100}%` }}
            />
          </div>
        </div>

        {/* 体力 */}
        <div className="mb-4">
          <div className="flex justify-between text-xs text-gray-300 mb-1">
            <span className="flex items-center">
              <span className="mr-1">⚡</span> 体力
            </span>
            <span className="font-mono">
              {character.status.stamina} / {character.status.maxStamina}
            </span>
          </div>
          <div className="h-2 bg-gray-800 rounded-full overflow-hidden border border-gray-700">
            <div
              className="h-full bg-gradient-to-r from-yellow-600 to-yellow-500 transition-all duration-500"
              style={{ width: `${(character.status.stamina / character.status.maxStamina) * 100}%` }}
            />
          </div>
        </div>

        {/* 属性 */}
        <div className="grid grid-cols-2 gap-2 text-xs border-t border-gray-700 pt-3">
          <div className="flex justify-between text-gray-300">
            <span>💪 力量</span>
            <span className="font-bold text-white">{character.attributes.strength}</span>
          </div>
          <div className="flex justify-between text-gray-300">
            <span>🏃 敏捷</span>
            <span className="font-bold text-white">{character.attributes.agility}</span>
          </div>
          <div className="flex justify-between text-gray-300">
            <span>📚 智力</span>
            <span className="font-bold text-white">{character.attributes.intelligence}</span>
          </div>
          <div className="flex justify-between text-gray-300">
            <span>🎭 魅力</span>
            <span className="font-bold text-white">{character.attributes.charisma}</span>
          </div>
        </div>
      </div>

      {/* 场景信息 */}
      {currentScene && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-gray-900 bg-opacity-95 rounded-lg shadow-2xl px-6 py-3 border border-gray-700">
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <h4 className="text-lg font-bold text-white">{currentScene.name}</h4>
              <p className="text-xs text-gray-400">{currentScene.type}</p>
            </div>
            <div className="border-l border-gray-700 pl-4">
              <p className="text-sm text-gray-300">
                {worldTime === 'morning' && '🌅 早晨'}
                {worldTime === 'afternoon' && '☀️ 下午'}
                {worldTime === 'evening' && '🌆 傍晚'}
                {worldTime === 'night' && '🌙 夜晚'}
              </p>
              <p className="text-xs text-gray-400">
                {worldWeather === 'clear' && '晴朗'}
                {worldWeather === 'cloudy' && '多云'}
                {worldWeather === 'rainy' && '下雨'}
                {worldWeather === 'stormy' && '暴风雨'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* NPC列表 */}
      {npcsInScene.length > 0 && (
        <div className="absolute top-32 left-4 bg-gray-900 bg-opacity-95 rounded-lg shadow-2xl p-3 border border-gray-700">
          <h4 className="text-sm font-bold text-gray-300 mb-2">附近的NPC</h4>
          <div className="space-y-1">
            {npcsInScene.map((npc: any) => (
              <button
                key={npc.id}
                onClick={() => handleNPCClick(npc)}
                className="w-full text-left px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm text-white transition-colors flex items-center justify-between"
              >
                <span>👤 {npc.name}</span>
                <span className="text-xs text-gray-400">{npc.type}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 快捷菜单 */}
      <div className="absolute bottom-4 left-4 flex space-x-2">
        <button
          onClick={toggleInventory}
          className={`px-5 py-3 rounded-lg font-semibold transition-all ${
            isInventoryOpen
              ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/50'
              : 'bg-gray-800 text-gray-300 hover:bg-gray-700 hover:shadow-lg'
          }`}
        >
          🎒 背包
        </button>
        <button
          onClick={toggleQuestLog}
          className={`px-5 py-3 rounded-lg font-semibold transition-all ${
            isQuestLogOpen
              ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/50'
              : 'bg-gray-800 text-gray-300 hover:bg-gray-700 hover:shadow-lg'
          }`}
        >
          📜 任务
        </button>
        <button
          onClick={() => setShowActions(!showActions)}
          className={`px-5 py-3 rounded-lg font-semibold transition-all ${
            showActions
              ? 'bg-green-600 text-white shadow-lg shadow-green-600/50'
              : 'bg-gray-800 text-gray-300 hover:bg-gray-700 hover:shadow-lg'
          }`}
        >
          ⚔️ 行动
        </button>
      </div>

      {/* 可用动作面板 */}
      {showActions && availableActions.length > 0 && (
        <div className="absolute bottom-20 left-4 bg-gray-900 bg-opacity-95 rounded-lg shadow-2xl p-4 border border-gray-700 min-w-[300px]">
          <h4 className="text-sm font-bold text-gray-300 mb-3">可用行动</h4>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {availableActions.map((action: any, index: number) => (
              <button
                key={index}
                onClick={() => handleAction(action)}
                className="w-full text-left px-4 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm text-white transition-all hover:shadow-lg flex items-center justify-between"
              >
                <span>{action.label}</span>
                <span className="text-xs text-gray-400">{action.type}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 小地图 */}
      <div className="absolute top-4 right-4 bg-gray-900 bg-opacity-95 rounded-lg shadow-2xl p-2 border border-gray-700">
        <div className="w-36 h-36 bg-gray-800 rounded-lg flex items-center justify-center border border-gray-700">
          <div className="text-center">
            <div className="text-3xl mb-2">🗺️</div>
            <p className="text-xs text-gray-500">小地图</p>
            {currentScene && (
              <p className="text-xs text-gray-400 mt-1">{currentScene.name}</p>
            )}
          </div>
        </div>
      </div>

      {/* 快捷键提示 */}
      <div className="absolute bottom-4 right-4 bg-gray-900 bg-opacity-90 rounded-lg shadow-xl px-4 py-2 border border-gray-700">
        <div className="text-xs text-gray-400 space-y-1">
          <p><span className="text-white font-mono bg-gray-800 px-1 rounded">↑↓←→</span> 移动</p>
          <p><span className="text-white font-mono bg-gray-800 px-1 rounded">Space</span> 对话</p>
          <p><span className="text-white font-mono bg-gray-800 px-1 rounded">I</span> 背包</p>
          <p><span className="text-white font-mono bg-gray-800 px-1 rounded">Q</span> 任务</p>
        </div>
      </div>
    </>
  )
}

export default EnhancedHUD
