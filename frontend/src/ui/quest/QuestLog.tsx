import React from 'react'
import useGameStore from '../../store/gameStore'

const QuestLog: React.FC = () => {
  const { 
    activeQuests, 
    toggleQuestLog,
    isQuestLogOpen 
  } = useGameStore()

  if (!isQuestLogOpen) return null

  const questTypes = {
    main: { name: '主线任务', icon: '⭐', color: 'yellow' },
    side: { name: '支线任务', icon: '📋', color: 'blue' },
    random: { name: '随机任务', icon: '🎲', color: 'purple' }
  }

  const questStatus = {
    available: { name: '可接取', color: 'gray' },
    active: { name: '进行中', color: 'blue' },
    completed: { name: '已完成', color: 'green' },
    failed: { name: '失败', color: 'red' }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-2xl shadow-2xl w-full max-w-3xl h-[600px] flex flex-col border border-gray-700">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">📜</span>
            <h2 className="text-xl font-bold text-white">任务日志</h2>
            <span className="text-sm text-gray-400">
              {activeQuests.length} 个任务
            </span>
          </div>
          <button
            onClick={toggleQuestLog}
            className="text-gray-400 hover:text-white transition-colors text-2xl"
          >
            ✕
          </button>
        </div>

        {/* 内容区域 */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeQuests.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <span className="text-6xl mb-4">📋</span>
              <p className="text-lg">没有进行中的任务</p>
              <p className="text-sm mt-2">与NPC交谈接取任务吧!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {activeQuests.map((quest: any) => {
                const typeInfo = questTypes[quest.type as keyof typeof questTypes] || questTypes.side
                const statusInfo = questStatus[quest.status as keyof typeof questStatus] || questStatus.active
                
                return (
                  <div
                    key={quest.id}
                    className="bg-gray-800 rounded-lg p-5 border border-gray-700 hover:border-gray-600 transition-all"
                  >
                    {/* 任务标题 */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{typeInfo.icon}</span>
                        <div>
                          <h3 className="text-lg font-bold text-white">
                            {quest.title}
                          </h3>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className={`text-xs px-2 py-1 rounded bg-${typeInfo.color}-900 text-${typeInfo.color}-300`}>
                              {typeInfo.name}
                            </span>
                            <span className={`text-xs px-2 py-1 rounded bg-${statusInfo.color}-900 text-${statusInfo.color}-300`}>
                              {statusInfo.name}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* 任务描述 */}
                    <p className="text-sm text-gray-300 mb-4">
                      {quest.description}
                    </p>

                    {/* 任务目标 */}
                    <div className="space-y-2 mb-4">
                      <h4 className="text-sm font-bold text-gray-400">目标:</h4>
                      {quest.objectives.map((objective: any, index: number) => {
                        const progress = quest.progress?.[objective.id] || 0
                        const isComplete = progress >= objective.required
                        
                        return (
                          <div
                            key={index}
                            className={`flex items-center space-x-3 p-2 rounded ${
                              isComplete ? 'bg-green-900 bg-opacity-20' : 'bg-gray-900'
                            }`}
                          >
                            <span className="text-lg">
                              {isComplete ? '✅' : '⬜'}
                            </span>
                            <div className="flex-1">
                              <p className={`text-sm ${isComplete ? 'text-gray-400 line-through' : 'text-gray-300'}`}>
                                {objective.description}
                              </p>
                              {!isComplete && (
                                <div className="flex items-center space-x-2 mt-1">
                                  <div className="flex-1 h-1 bg-gray-800 rounded-full overflow-hidden">
                                    <div
                                      className="h-full bg-blue-500"
                                      style={{ width: `${(progress / objective.required) * 100}%` }}
                                    />
                                  </div>
                                  <span className="text-xs text-gray-500">
                                    {progress} / {objective.required}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        )
                      })}
                    </div>

                    {/* 奖励 */}
                    <div className="border-t border-gray-700 pt-3">
                      <h4 className="text-sm font-bold text-gray-400 mb-2">奖励:</h4>
                      <div className="flex items-center space-x-4 text-sm text-gray-300">
                        {quest.rewards.gold && (
                          <span>💰 {quest.rewards.gold} 金币</span>
                        )}
                        {quest.rewards.experience && (
                          <span>⭐ {quest.rewards.experience} 经验</span>
                        )}
                        {quest.rewards.items && quest.rewards.items.length > 0 && (
                          <span>📦 {quest.rewards.items.length} 件物品</span>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* 底部提示 */}
        <div className="border-t border-gray-700 p-4 text-center text-xs text-gray-500">
          💡 提示: 完成任务目标后返回任务发布者处领取奖励
        </div>
      </div>
    </div>
  )
}

export default QuestLog
