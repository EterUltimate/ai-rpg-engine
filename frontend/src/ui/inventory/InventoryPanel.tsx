import React from 'react'
import useGameStore from '../../store/gameStore'

const InventoryPanel: React.FC = () => {
  const { 
    character, 
    toggleInventory,
    isInventoryOpen 
  } = useGameStore()

  if (!isInventoryOpen || !character) return null

  const inventory = character.inventory || []

  const itemTypes = {
    consumable: { name: '消耗品', icon: '🧪', color: 'blue' },
    weapon: { name: '武器', icon: '⚔️', color: 'red' },
    armor: { name: '防具', icon: '🛡️', color: 'yellow' },
    misc: { name: '杂项', icon: '📦', color: 'gray' }
  }

  const groupedItems = inventory.reduce((acc, item) => {
    const type = item.type || 'misc'
    if (!acc[type]) acc[type] = []
    acc[type].push(item)
    return acc
  }, {} as Record<string, any[]>)

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-2xl shadow-2xl w-full max-w-4xl h-[600px] flex flex-col border border-gray-700">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">🎒</span>
            <h2 className="text-xl font-bold text-white">背包</h2>
            <span className="text-sm text-gray-400">
              {inventory.length} / 50
            </span>
          </div>
          <button
            onClick={toggleInventory}
            className="text-gray-400 hover:text-white transition-colors text-2xl"
          >
            ✕
          </button>
        </div>

        {/* 内容区域 */}
        <div className="flex-1 overflow-y-auto p-6">
          {inventory.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <span className="text-6xl mb-4">📦</span>
              <p className="text-lg">背包是空的</p>
              <p className="text-sm mt-2">在冒险中收集物品吧!</p>
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(groupedItems).map(([type, items]) => {
                const typeInfo = itemTypes[type as keyof typeof itemTypes] || itemTypes.misc
                return (
                  <div key={type}>
                    <h3 className="text-sm font-bold text-gray-400 mb-3 flex items-center">
                      <span className="mr-2">{typeInfo.icon}</span>
                      {typeInfo.name}
                      <span className="ml-2 text-xs">({items.length})</span>
                    </h3>
                    
                    <div className="grid grid-cols-4 gap-3">
                      {items.map((item: any, index: number) => (
                        <div
                          key={index}
                          className="bg-gray-800 hover:bg-gray-750 rounded-lg p-3 border border-gray-700 hover:border-gray-600 transition-all cursor-pointer group"
                        >
                          <div className="aspect-square bg-gray-900 rounded-lg mb-2 flex items-center justify-center text-4xl">
                            {typeInfo.icon}
                          </div>
                          
                          <h4 className="text-sm font-semibold text-white truncate">
                            {item.name}
                          </h4>
                          
                          {item.quantity > 1 && (
                            <p className="text-xs text-gray-400 mt-1">
                              数量: {item.quantity}
                            </p>
                          )}
                          
                          {item.description && (
                            <p className="text-xs text-gray-500 mt-1 truncate">
                              {item.description}
                            </p>
                          )}
                          
                          {/* 悬停效果 */}
                          <div className="opacity-0 group-hover:opacity-100 transition-opacity mt-2 flex space-x-1">
                            <button className="flex-1 text-xs bg-blue-600 hover:bg-blue-500 text-white px-2 py-1 rounded transition-colors">
                              使用
                            </button>
                            <button className="flex-1 text-xs bg-gray-700 hover:bg-gray-600 text-white px-2 py-1 rounded transition-colors">
                              丢弃
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* 装备栏 */}
        <div className="border-t border-gray-700 p-4">
          <h3 className="text-sm font-bold text-gray-400 mb-3">装备</h3>
          <div className="grid grid-cols-4 gap-3">
            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700 text-center">
              <div className="text-xs text-gray-500 mb-1">武器</div>
              <div className="aspect-square bg-gray-900 rounded flex items-center justify-center text-2xl">
                {character.equipment?.weapon ? '⚔️' : '➕'}
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700 text-center">
              <div className="text-xs text-gray-500 mb-1">防具</div>
              <div className="aspect-square bg-gray-900 rounded flex items-center justify-center text-2xl">
                {character.equipment?.armor ? '🛡️' : '➕'}
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700 text-center">
              <div className="text-xs text-gray-500 mb-1">饰品</div>
              <div className="aspect-square bg-gray-900 rounded flex items-center justify-center text-2xl">
                {character.equipment?.accessory ? '💎' : '➕'}
              </div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700 text-center">
              <div className="text-xs text-gray-500 mb-1">统计</div>
              <div className="text-xs text-gray-400 mt-3">
                攻击力: {character.attributes.strength}<br/>
                防御力: {character.attributes.agility}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default InventoryPanel
