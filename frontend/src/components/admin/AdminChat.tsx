import React, { useState, useEffect, useRef } from 'react'
import { PDFDocument, Chat } from '@/types'
import apiClient from '@/services/api'
import toast from 'react-hot-toast'
import { Send, Loader2, FileText } from 'lucide-react'
import ChatMessage from '@/components/ChatMessage'

const AdminChat: React.FC = () => {
  const [pdfs, setPdfs] = useState<PDFDocument[]>([])
  const [currentPdfId, setCurrentPdfId] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const [chats, setChats] = useState<Chat[]>([])
  const [sendingMessage, setSendingMessage] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadPDFs()
    createAdminSession()
  }, [])

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [chats])

  const loadPDFs = async () => {
    try {
      const response: any = await apiClient.getAllPDFs(1, 100)
      setPdfs(response.pdfs)
    } catch (error: any) {
      console.error('Failed to load PDFs:', error)
    }
  }

  const createAdminSession = async () => {
    try {
      const response: any = await apiClient.createSession('Admin Session')
      setSessionId(response.session.id)
    } catch (error: any) {
      toast.error('Failed to create admin session')
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!message.trim() || !sessionId) return

    const userMessage = message
    setMessage('')
    setSendingMessage(true)

    const tempChat: Chat = {
      id: 'temp-' + Date.now(),
      user_id: 'admin',
      session_id: sessionId,
      message: userMessage,
      response: '',
      context_type: currentPdfId ? 'pdf' : 'direct',
      pdf_id: currentPdfId || undefined,
      created_at: new Date().toISOString(),
    }
    setChats([...chats, tempChat])

    try {
      const response: any = await apiClient.sendMessage(userMessage, sessionId, currentPdfId || undefined)
      
      setChats((prev) => {
        const filtered = prev.filter((c) => c.id !== tempChat.id)
        return [...filtered, response.chat]
      })
    } catch (error: any) {
      toast.error('Failed to send message')
      setChats((prev) => prev.filter((c) => c.id !== tempChat.id))
      setMessage(userMessage)
    } finally {
      setSendingMessage(false)
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Admin Chat Interface</h1>

      <div className="grid grid-cols-3 gap-6">
        {/* Chat Area */}
        <div className="col-span-2 bg-white rounded-lg shadow-md flex flex-col" style={{ height: 'calc(100vh - 250px)' }}>
          <div className="border-b border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900">Admin Chat</h3>
            {currentPdfId && (
              <p className="text-sm text-purple-600 mt-1 flex items-center gap-1">
                <FileText className="w-4 h-4" />
                Chatting with PDF
              </p>
            )}
          </div>

          <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-6 space-y-4">
            {chats.length === 0 ? (
              <div className="text-center text-gray-500 py-12">
                Start chatting with full admin access
              </div>
            ) : (
              chats.map((chat) => <ChatMessage key={chat.id} chat={chat} />)
            )}
            {sendingMessage && (
              <div className="flex justify-start">
                <div className="max-w-3xl bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="border-t border-gray-200 p-4">
            <form onSubmit={handleSendMessage} className="flex items-end space-x-3">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSendMessage(e)
                  }
                }}
                rows={2}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                disabled={sendingMessage}
              />
              <button
                type="submit"
                disabled={sendingMessage || !message.trim()}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors flex items-center justify-center"
              >
                {sendingMessage ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </form>
          </div>
        </div>

        {/* PDF Sidebar */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Available PDFs</h3>
          <div className="space-y-2">
            <button
              onClick={() => setCurrentPdfId(null)}
              className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                !currentPdfId ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 hover:bg-gray-200'
              }`}
            >
              <p className="text-sm font-medium">Direct Chat</p>
              <p className="text-xs text-gray-500">No PDF context</p>
            </button>
            {pdfs.map((pdf) => (
              <button
                key={pdf.id}
                onClick={() => setCurrentPdfId(pdf.id)}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  currentPdfId === pdf.id
                    ? 'bg-purple-100 text-purple-700'
                    : 'bg-gray-100 hover:bg-gray-200'
                }`}
              >
                <p className="text-sm font-medium truncate">{pdf.filename}</p>
                <p className="text-xs text-gray-500">{pdf.page_count} pages</p>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminChat