import React from 'react'
import { Chat } from '@/types'
import { formatDate } from '@/utils/helpers'
import { User, Bot, FileText, Sparkles, Files } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

interface ChatMessageProps {
  chat: Chat
}

const ChatMessage: React.FC<ChatMessageProps> = ({ chat }) => {
  const metadata = chat.metadata || {}
  const pdfSources = metadata.pdf_sources || []
  const isMultiplePdfs = pdfSources.length > 1

  return (
    <div className="space-y-4 fade-in">
      {/* User Message */}
      <div className="flex justify-end">
        <div className="max-w-3xl bg-gradient-to-br from-cyan-400 to-blue-500 text-dark-bg rounded-2xl rounded-tr-sm p-4 shadow-lg">
          <div className="flex items-start gap-3">
            <div className="flex-1">
              <p className="text-sm font-medium whitespace-pre-wrap">{chat.message}</p>
              <p className="text-xs text-dark-bg/70 mt-2">{formatDate(chat.created_at)}</p>
            </div>
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-dark-bg/20 rounded-full flex items-center justify-center">
                <User className="w-5 h-5" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bot Response */}
      <div className="flex justify-start">
        <div className="max-w-3xl bg-dark-card border border-dark-border rounded-2xl rounded-tl-sm p-4 shadow-xl">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full flex items-center justify-center shadow-glow">
                <Bot className="w-5 h-5 text-dark-bg" />
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm text-gray-100 prose prose-sm prose-invert max-w-none">
                <ReactMarkdown>{chat.response}</ReactMarkdown>
              </div>

              {/* PDF Source Badges */}
              {pdfSources.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {isMultiplePdfs ? (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-purple-500/20 text-purple-400 text-xs rounded-full border border-purple-500/30">
                      <Files className="w-3 h-3" />
                      {pdfSources.length} PDFs
                      <Sparkles className="w-3 h-3" />
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-purple-500/20 text-purple-400 text-xs rounded-full border border-purple-500/30">
                      <FileText className="w-3 h-3" />
                      {pdfSources[0].filename}
                      <Sparkles className="w-3 h-3" />
                    </span>
                  )}
                  {metadata.search_method && (
                    <span className="px-2 py-1 bg-cyan-400/10 text-cyan-400 text-xs rounded-full">
                      {metadata.search_method}
                    </span>
                  )}
                </div>
              )}

              <p className="text-xs text-gray-500 mt-3">{formatDate(chat.created_at)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatMessage