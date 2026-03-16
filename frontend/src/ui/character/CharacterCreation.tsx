import React, { useState } from 'react'
import { characterAPI } from '../../api/gameApi'
import useGameStore from '../../store/gameStore'

interface CharacterCreationProps {
  onComplete: (character: any) => void
  onCancel?: () => void
}

const CharacterCreation: React.FC<CharacterCreationProps> = ({ onComplete, onCancel }) => {
  const { setLoading, setError } = useGameStore()
  
  const [name, setName] = useState('')
  const [points, setPoints] = useState(10)
  const [attributes, setAttributes] = useState({
    strength: 10,
    agility: 10,
    intelligence: 10,
    charisma: 10
  })

  const attributeInfo = {
    strength: {
      name: '力量',
      icon: '💪',
      description: '影响物理攻击力和负重能力',
      color: 'red'
    },
    agility: {
      name: '敏捷',
      icon: '🏃',
      description: '影响闪避率和行动速度',
      color: 'green'
    },
    intelligence: {
      name: '智力',
      icon: '📚',
      description: '影响魔法攻击力和魔法值',
      color: 'blue'
    },
    charisma: {
      name: '魅力',
      icon: '🎭',
      description: '影响NPC互动和交易价格',
      color: 'purple'
    }
  }

  const handleAttributeChange = (attr: string, delta: number) => {
    const newValue = attributes[attr as keyof typeof attributes] + delta
    
    // 检查是否有效
    if (newValue < 5 || newValue > 20) return
    if (delta > 0 && points <= 0) return
    
    setAttributes(prev => ({
      ...prev,
      [attr]: newValue
    }))
    setPoints(prev => prev - delta)
  }

  const handleCreate = async () => {
    if (!name.trim()) {
      setError('请输入角色名称')
      return
    }

    setLoading(true)
    try {
      const character = await characterAPI.create(name, attributes)
      onComplete(character)
    } catch (error) {
      console.error('Create character error:', error)
      setError('创建角色失败,请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const getTotalPoints = () => {
    return Object.values(attributes).reduce((sum, val) => sum + val, 0)
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 bg-opacity-95 rounded-2xl shadow-2xl w-full max-w-2xl border border-gray-700 overflow-hidden">
        {/* 头部 */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
          <h2 className="text-3xl font-bold text-white text-center">创建角色</h2>
          <p className="text-center text-blue-100 mt-2">开始你的冒险之旅</p>
        </div>

        <div className="p-8">
          {/* 角色名称 */}
          <div className="mb-8">
            <label className="block text-sm font-bold text-gray-300 mb-2">
              角色名称
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="输入你的角色名称..."
              className="w-full bg-gray-800 text-white text-lg rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700"
              maxLength={20}
            />
          </div>

          {/* 剩余点数 */}
          <div className="mb-6 bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">可分配点数</span>
              <span className={`text-2xl font-bold ${points > 0 ? 'text-green-400' : 'text-gray-400'}`}>
                {points}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              总属性点: {getTotalPoints()} / 50
            </p>
          </div>

          {/* 属性分配 */}
          <div className="space-y-4 mb-8">
            {Object.entries(attributes).map(([key, value]) => {
              const info = attributeInfo[key as keyof typeof attributeInfo]
              return (
                <div key={key} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{info.icon}</span>
                      <div>
                        <h4 className="font-bold text-white">{info.name}</h4>
                        <p className="text-xs text-gray-400">{info.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleAttributeChange(key, -1)}
                        disabled={value <= 5}
                        className="w-8 h-8 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed rounded text-white font-bold transition-colors"
                      >
                        -
                      </button>
                      <span className="text-2xl font-bold text-white w-12 text-center">
                        {value}
                      </span>
                      <button
                        onClick={() => handleAttributeChange(key, 1)}
                        disabled={value >= 20 || points <= 0}
                        className="w-8 h-8 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed rounded text-white font-bold transition-colors"
                      >
                        +
                      </button>
                    </div>
                  </div>
                  
                  {/* 属性条 */}
                  <div className="h-2 bg-gray-900 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-${info.color}-500 transition-all duration-300`}
                      style={{ width: `${(value / 20) * 100}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>

          {/* 预览 */}
          <div className="mb-6 bg-gradient-to-r from-gray-800 to-gray-700 rounded-lg p-4 border border-gray-600">
            <h4 className="font-bold text-white mb-2">角色预览</h4>
            <div className="text-sm text-gray-300">
              <p className="mb-1">
                <span className="text-gray-400">名称:</span> {name || '未命名'}
              </p>
              <div className="flex space-x-4 mt-2">
                <span>💪 {attributes.strength}</span>
                <span>🏃 {attributes.agility}</span>
                <span>📚 {attributes.intelligence}</span>
                <span>🎭 {attributes.charisma}</span>
              </div>
            </div>
          </div>

          {/* 按钮 */}
          <div className="flex space-x-4">
            {onCancel && (
              <button
                onClick={onCancel}
                className="flex-1 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold transition-colors"
              >
                取消
              </button>
            )}
            <button
              onClick={handleCreate}
              disabled={!name.trim() || points > 0}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white rounded-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              开始冒险
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CharacterCreation
