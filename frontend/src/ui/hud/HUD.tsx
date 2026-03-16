import React from 'react'
import useGameStore from '../../store/gameStore'

const HUD: React.FC = () => {
  const { 
    character, 
    toggleInventory, 
    toggleQuestLog,
    isInventoryOpen,
    isQuestLogOpen 
  } = useGameStore()

  if (!character) return null

  return (
    <>
      {/* 角色状态栏 */}
      <div className="absolute top-4 left-4 bg-gray-900 bg-opacity-90 rounded-lg p-4 min-w-[250px]">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-bold text-white">{character.name}</h3>
          <span className="text-sm text-gray-400">Lv.{character.level}</span>
        </div>

        {/* 生命值 */}
        <div className="mb-2">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>HP</span>
            <span>{character.status.hp}/{character.status.maxHp}</span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-red-500 transition-all duration-300"
              style={{ width: `${(character.status.hp / character.status.maxHp) * 100}%` }}
            />
          </div>
        </div>

        {/* 魔法值 */}
        <div className="mb-3">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>MP</span>
            <span>{character.status.mp}/{character.status.maxMp}</span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-300"
              style={{ width: `${(character.status.mp / character.status.maxMp) * 100}%` }}
            />
          </div>
        </div>

        {/* 属性 */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="text-gray-400">
            力量: <span className="text-white">{character.attributes.strength}</span>
          </div>
          <div className="text-gray-400">
            敏捷: <span className="text-white">{character.attributes.agility}</span>
          </div>
          <div className="text-gray-400">
            智力: <span className="text-white">{character.attributes.intelligence}</span>
          </div>
          <div className="text-gray-400">
            魅力: <span className="text-white">{character.attributes.charisma}</span>
          </div>
        </div>
      </div>

      {/* 快捷菜单 */}
      <div className="absolute bottom-4 left-4 flex space-x-2">
        <button
          onClick={toggleInventory}
          className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
            isInventoryOpen
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
          }`}
        >
          背包
        </button>
        <button
          onClick={toggleQuestLog}
          className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
            isQuestLogOpen
              ? 'bg-blue-600 text-white'
              : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
          }`}
        >
          任务
        </button>
      </div>

      {/* 小地图占位 */}
      <div className="absolute top-4 right-4 bg-gray-900 bg-opacity-90 rounded-lg p-2">
        <div className="w-32 h-32 bg-gray-800 rounded flex items-center justify-center text-gray-600 text-xs">
          小地图
        </div>
      </div>
    </>
  )
}

export default HUD
