import React from 'react'
import { Chat } from '@/types'
import { formatDate } from '@/utils/helpers'
import { User, Bot, FileText } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

interface ChatMessageProps {
  chat: Chat
}

const ChatMessage: React.FC<ChatMessageProps> = ({ chat }) => {
  return (
    <div className="space-y-3">
      {/* User Message */}
      <div className="flex justify-end">
        <div className="max-w-3xl bg-blue-600 text-white rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="flex-1">
              <p className="text-sm whitespace-pre-wrap">{chat.message}</p>
              <p className="text-xs text-blue-100 mt-2">{formatDate(chat.created_at)}</p>
            </div>
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <User className="w-5 h-5" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bot Response */}
      <div className="flex justify-start">
        <div className="max-w-3xl bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-green-600" />
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm text-gray-900 prose prose-sm max-w-none">
                <ReactMarkdown>{chat.response}</ReactMarkdown>
              </div>
              {chat.context_type === 'pdf' && (
                <span className="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded">
                  <FileText className="w-3 h-3" />
                  PDF Context
                </span>
              )}
              <p className="text-xs text-gray-500 mt-2">{formatDate(chat.created_at)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatMessage