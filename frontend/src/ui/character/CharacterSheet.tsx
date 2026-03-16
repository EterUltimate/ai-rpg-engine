import React from 'react'
import useGameStore from '../../store/gameStore'

const CharacterSheet: React.FC = () => {
  const { 
    character,
    isCharacterSheetOpen,
    toggleCharacterSheet
  } = useGameStore()

  if (!isCharacterSheetOpen || !character) return null

  const expForNextLevel = character.level * 100
  const expProgress = (character.experience / expForNextLevel) * 100

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-2xl shadow-2xl w-full max-w-2xl border border-gray-700 overflow-hidden">
        {/* 头部 */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center text-5xl border-4 border-white">
                🧙
              </div>
              <div>
                <h2 className="text-3xl font-bold text-white">{character.name}</h2>
                <p className="text-blue-100">Lv.{character.level} 冒险者</p>
              </div>
            </div>
            <button
              onClick={toggleCharacterSheet}
              className="text-white hover:text-gray-200 transition-colors text-2xl"
            >
              ✕
            </button>
          </div>

          {/* 经验条 */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-blue-100 mb-1">
              <span>经验值</span>
              <span>{character.experience} / {expForNextLevel}</span>
            </div>
            <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-green-400 to-green-500"
                style={{ width: `${expProgress}%` }}
              />
            </div>
          </div>
        </div>

        {/* 内容区域 */}
        <div className="p-6">
          {/* 状态 */}
          <div className="mb-6">
            <h3 className="text-lg font-bold text-white mb-3 flex items-center">
              <span className="mr-2">❤️</span> 状态
            </h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                <div className="text-xs text-gray-400 mb-1">生命值</div>
                <div className="text-2xl font-bold text-red-400">
                  {character.status.hp} / {character.status.maxHp}
                </div>
              </div>
              <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                <div className="text-xs text-gray-400 mb-1">魔法值</div>
                <div className="text-2xl font-bold text-blue-400">
                  {character.status.mp} / {character.status.maxMp}
                </div>
              </div>
              <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                <div className="text-xs text-gray-400 mb-1">体力</div>
                <div className="text-2xl font-bold text-yellow-400">
                  {character.status.stamina} / {character.status.maxStamina}
                </div>
              </div>
            </div>
          </div>

          {/* 属性 */}
          <div className="mb-6">
            <h3 className="text-lg font-bold text-white mb-3 flex items-center">
              <span className="mr-2">📊</span> 属性
            </h3>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(character.attributes).map(([key, value]) => {
                const attrNames: Record<string, { name: string; icon: string }> = {
                  strength: { name: '力量', icon: '💪' },
                  agility: { name: '敏捷', icon: '🏃' },
                  intelligence: { name: '智力', icon: '📚' },
                  charisma: { name: '魅力', icon: '🎭' }
                }
                const attr = attrNames[key] || { name: key, icon: '❓' }
                
                return (
                  <div key={key} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-400 flex items-center">
                        <span className="mr-2">{attr.icon}</span>
                        {attr.name}
                      </span>
                      <span className="text-2xl font-bold text-white">{value}</span>
                    </div>
                    <div className="h-1 bg-gray-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                        style={{ width: `${(value / 20) * 100}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* 统计信息 */}
          <div className="grid grid-cols-3 gap-3 text-sm">
            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700 text-center">
              <div className="text-gray-400 mb-1">金币</div>
              <div className="text-xl font-bold text-yellow-400">💰 0</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700 text-center">
              <div className="text-gray-400 mb-1">完成任务</div>
              <div className="text-xl font-bold text-green-400">0</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700 text-center">
              <div className="text-gray-400 mb-1">游戏时长</div>
              <div className="text-xl font-bold text-purple-400">0h</div>
            </div>
          </div>
        </div>

        {/* 底部 */}
        <div className="border-t border-gray-700 p-4 flex justify-between items-center text-xs text-gray-500">
          <span>创建于: {new Date(character.createdAt).toLocaleDateString()}</span>
          <span>角色ID: {character.id}</span>
        </div>
      </div>
    </div>
  )
}

export default CharacterSheet
