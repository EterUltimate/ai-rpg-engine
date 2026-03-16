import React, { useState, useRef, useEffect } from 'react'
import useGameStore from '../../store/gameStore'
import { sendMessage } from '../../api/chat'

const ChatInterface: React.FC = () => {
  const { chatMessages, addMessage, toggleChat } = useGameStore()
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    
    // 添加玩家消息
    addMessage({ role: 'player', content: userMessage })
    setIsLoading(true)

    try {
      // 调用AI API
      const response = await sendMessage(userMessage)
      
      // 添加AI回复
      addMessage({ role: 'ai', content: response })
    } catch (error) {
      console.error('Chat error:', error)
      addMessage({ 
        role: 'system', 
        content: 'AI服务暂时不可用,请稍后再试。' 
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg shadow-2xl w-full max-w-2xl h-[600px] flex flex-col">
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h2 className="text-xl font-bold text-white">AI对话</h2>
          <button
            onClick={toggleChat}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {chatMessages.length === 0 ? (
            <div className="text-center text-gray-500 mt-20">
              <p className="text-lg">开始你的冒险吧!</p>
              <p className="text-sm mt-2">输入任何内容与AI交互</p>
            </div>
          ) : (
            chatMessages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.role === 'player' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-3 ${
                    msg.role === 'player'
                      ? 'bg-blue-600 text-white'
                      : msg.role === 'ai'
                      ? 'bg-gray-700 text-gray-100'
                      : 'bg-yellow-600 text-white'
                  }`}
                >
                  <div className="text-xs text-gray-300 mb-1">
                    {msg.role === 'player' ? '你' : msg.role === 'ai' ? 'AI' : '系统'}
                  </div>
                  <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* 输入框 */}
        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入你的行动或对话..."
              className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              发送
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ChatInterface
