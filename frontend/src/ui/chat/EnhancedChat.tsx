import React, { useState, useRef, useEffect } from 'react'
import useGameStore from '../../store/gameStore'
import { aiAPI } from '../../api/gameApi'

const EnhancedChat: React.FC = () => {
  const { 
    isChatOpen, 
    chatMessages, 
    currentNPC,
    character,
    currentScene,
    addMessage, 
    closeChat 
  } = useGameStore()
  
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [streamingMessage, setStreamingMessage] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages, streamingMessage])

  useEffect(() => {
    if (isChatOpen && currentNPC && chatMessages.length === 0) {
      addMessage({
        role: 'system',
        content: `你开始与${currentNPC.name}交谈。`,
        npcName: currentNPC.name
      })
    }
  }, [isChatOpen, currentNPC])

  if (!isChatOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading || !character || !currentScene) return

    const userMessage = input.trim()
    setInput('')
    
    // 添加玩家消息
    addMessage({ 
      role: 'player', 
      content: userMessage 
    })
    setIsLoading(true)
    setStreamingMessage('')

    try {
      // 使用流式API
      const cleanup = aiAPI.streamChat(
        userMessage,
        character.id,
        currentScene.id,
        (chunk) => {
          setStreamingMessage(prev => prev + chunk)
        },
        () => {
          // 完成时添加完整消息
          const fullResponse = streamingMessage
          if (fullResponse) {
            addMessage({
              role: 'ai',
              content: fullResponse,
              npcName: currentNPC?.name
            })
          }
          setStreamingMessage('')
          setIsLoading(false)
        },
        (error) => {
          console.error('Stream error:', error)
          addMessage({ 
            role: 'system', 
            content: 'AI服务暂时不可用,请稍后再试。' 
          })
          setIsLoading(false)
          setStreamingMessage('')
        },
        currentNPC?.id
      )

      // 设置超时清理
      setTimeout(() => {
        cleanup()
        setIsLoading(false)
      }, 30000)
      
    } catch (error) {
      console.error('Chat error:', error)
      addMessage({ 
        role: 'system', 
        content: '发生错误,请稍后再试。' 
      })
      setIsLoading(false)
    }
  }

  const handleQuickAction = (action: string) => {
    setInput(action)
  }

  const quickActions = [
    { label: '打招呼', text: '你好!' },
    { label: '询问任务', text: '有什么我可以帮忙的吗?' },
    { label: '询问位置', text: '能告诉我这个地方的信息吗?' },
    { label: '交易', text: '我想看看你的商品。' }
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-2xl shadow-2xl w-full max-w-3xl h-[700px] flex flex-col border border-gray-700">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700 bg-gradient-to-r from-purple-900 to-blue-900">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center text-2xl">
              {currentNPC ? '👤' : '🎭'}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">
                {currentNPC?.name || 'AI助手'}
              </h2>
              <p className="text-xs text-gray-300">
                {currentNPC?.type || '游戏主持'}
              </p>
            </div>
          </div>
          <button
            onClick={closeChat}
            className="text-gray-300 hover:text-white transition-colors text-2xl"
          >
            ✕
          </button>
        </div>

        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-950">
          {chatMessages.length === 0 && !isLoading && (
            <div className="text-center text-gray-500 mt-20">
              <span className="text-6xl mb-4 block">💬</span>
              <p className="text-lg">开始对话吧!</p>
              <p className="text-sm mt-2">输入任何内容与AI交互</p>
            </div>
          )}
          
          {chatMessages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.role === 'player' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[75%] rounded-2xl p-4 ${
                  msg.role === 'player'
                    ? 'bg-blue-600 text-white'
                    : msg.role === 'ai'
                    ? 'bg-gray-800 text-gray-100 border border-gray-700'
                    : 'bg-yellow-900 bg-opacity-50 text-yellow-100 border border-yellow-800'
                }`}
              >
                {(msg.role === 'ai' || msg.role === 'system') && msg.npcName && (
                  <div className="text-xs text-gray-400 mb-1 font-semibold">
                    {msg.npcName}
                  </div>
                )}
                <div className="text-sm whitespace-pre-wrap leading-relaxed">
                  {msg.content}
                </div>
                <div className="text-xs text-gray-400 mt-1 opacity-50">
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          
          {/* 流式消息 */}
          {streamingMessage && (
            <div className="flex justify-start">
              <div className="max-w-[75%] rounded-2xl p-4 bg-gray-800 text-gray-100 border border-gray-700">
                {currentNPC && (
                  <div className="text-xs text-gray-400 mb-1 font-semibold">
                    {currentNPC.name}
                  </div>
                )}
                <div className="text-sm whitespace-pre-wrap">
                  {streamingMessage}
                  <span className="animate-pulse">▊</span>
                </div>
              </div>
            </div>
          )}
          
          {/* 加载指示器 */}
          {isLoading && !streamingMessage && (
            <div className="flex justify-start">
              <div className="bg-gray-800 rounded-2xl p-4 border border-gray-700">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* 快捷操作 */}
        {currentNPC && (
          <div className="px-4 py-2 border-t border-gray-800 overflow-x-auto">
            <div className="flex space-x-2">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickAction(action.text)}
                  className="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs rounded-full whitespace-nowrap transition-colors"
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 输入框 */}
        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700 bg-gray-900">
          <div className="flex space-x-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={currentNPC ? `对${currentNPC.name}说...` : "输入你的行动或对话..."}
              className="flex-1 bg-gray-800 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-6 py-3 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              发送
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default EnhancedChat
