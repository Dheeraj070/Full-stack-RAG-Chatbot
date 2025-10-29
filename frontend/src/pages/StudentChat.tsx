import React, { useState, useEffect, useRef } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Session, Chat, PDFDocument } from '@/types'
import apiClient from '@/services/api'
import toast from 'react-hot-toast'
import { formatDate, formatFileSize } from '@/utils/helpers'
import {
  MessageSquare,
  LogOut,
  Plus,
  Trash2,
  Upload,
  Send,
  Loader2,
  FileText,
  X,
} from 'lucide-react'
import Navbar from '@/components/Navbar'
import ChatMessage from '@/components/ChatMessage'
import SessionList from '@/components/SessionList'
import PDFList from '@/components/PDFList'

const StudentChat: React.FC = () => {
  const { currentUser, logout } = useAuth()
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [chats, setChats] = useState<Chat[]>([])
  const [pdfs, setPdfs] = useState<PDFDocument[]>([])
  const [currentPdfId, setCurrentPdfId] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [sendingMessage, setSendingMessage] = useState(false)
  const [uploadingPdf, setUploadingPdf] = useState(false)
  
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadSessions()
    loadPDFs()
  }, [])

  useEffect(() => {
    if (currentSessionId) {
      loadChatHistory(currentSessionId)
    }
  }, [currentSessionId])

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [chats])

  const loadSessions = async () => {
    try {
      const response: any = await apiClient.getSessions()
      setSessions(response.sessions)
    } catch (error: any) {
      toast.error('Failed to load sessions')
    }
  }

  const loadPDFs = async () => {
    try {
      const response: any = await apiClient.getPDFs()
      setPdfs(response.pdfs)
    } catch (error: any) {
      toast.error('Failed to load PDFs')
    }
  }

  const loadChatHistory = async (sessionId: string) => {
    setLoading(true)
    try {
      const response: any = await apiClient.getChatHistory(sessionId)
      setChats(response.chats)
    } catch (error: any) {
      toast.error('Failed to load chat history')
      setChats([])
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSession = async () => {
    try {
      const response: any = await apiClient.createSession()
      setSessions([response.session, ...sessions])
      setCurrentSessionId(response.session.id)
      setChats([])
      toast.success('New session created')
    } catch (error: any) {
      toast.error('Failed to create session')
    }
  }

  const handleDeleteSession = async (sessionId: string) => {
    if (!confirm('Are you sure you want to delete this session?')) return

    try {
      await apiClient.deleteSession(sessionId)
      setSessions(sessions.filter((s) => s.id !== sessionId))
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null)
        setChats([])
      }
      toast.success('Session deleted')
    } catch (error: any) {
      toast.error('Failed to delete session')
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!message.trim()) return

    let sessionId = currentSessionId

    // Create session if none exists
    if (!sessionId) {
      try {
        const response: any = await apiClient.createSession()
        sessionId = response.session.id
        setSessions([response.session, ...sessions])
        setCurrentSessionId(sessionId)
      } catch (error: any) {
        toast.error('Failed to create session')
        return
      }
    }

    const userMessage = message
    setMessage('')
    setSendingMessage(true)

    // Optimistically add user message to UI
    const tempChat: Chat = {
      id: 'temp-' + Date.now(),
      user_id: currentUser?.id || '',
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
      
      // Replace temp message with actual response
      setChats((prev) => {
        const filtered = prev.filter((c) => c.id !== tempChat.id)
        return [...filtered, response.chat]
      })

      // Update session message count
      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId
            ? { ...s, message_count: s.message_count + 1, updated_at: new Date().toISOString() }
            : s
        )
      )
    } catch (error: any) {
      toast.error('Failed to send message')
      // Remove temp message on error
      setChats((prev) => prev.filter((c) => c.id !== tempChat.id))
      setMessage(userMessage) // Restore message
    } finally {
      setSendingMessage(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.type !== 'application/pdf') {
      toast.error('Please select a PDF file')
      return
    }

    if (file.size > 16 * 1024 * 1024) {
      toast.error('File size must be less than 16MB')
      return
    }

    setUploadingPdf(true)
    toast.loading('Uploading and processing PDF...', { id: 'pdf-upload' })

    try {
      const response: any = await apiClient.uploadPDF(file)
      setPdfs([response.pdf, ...pdfs])
      toast.success(`PDF uploaded! ${response.chunks_created} chunks created`, { id: 'pdf-upload' })
    } catch (error: any) {
      toast.error('Failed to upload PDF', { id: 'pdf-upload' })
    } finally {
      setUploadingPdf(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleDeletePDF = async (pdfId: string) => {
    if (!confirm('Are you sure you want to delete this PDF?')) return

    try {
      await apiClient.deletePDF(pdfId)
      setPdfs(pdfs.filter((p) => p.id !== pdfId))
      if (currentPdfId === pdfId) {
        setCurrentPdfId(null)
      }
      toast.success('PDF deleted')
    } catch (error: any) {
      toast.error('Failed to delete PDF')
    }
  }

  const currentSession = sessions.find((s) => s.id === currentSessionId)
  const currentPdf = pdfs.find((p) => p.id === currentPdfId)

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Navbar
        title="Engineering Chatbot"
        userName={currentUser?.display_name || 'Student'}
        onLogout={logout}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          {/* Sessions Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Chat Sessions</h2>
              <button
                onClick={handleCreateSession}
                className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                title="New Session"
              >
                <Plus className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Sessions List */}
          <div className="flex-1 overflow-y-auto p-4">
            <SessionList
              sessions={sessions}
              currentSessionId={currentSessionId}
              onSelectSession={setCurrentSessionId}
              onDeleteSession={handleDeleteSession}
            />
          </div>

          {/* PDF Section */}
          <div className="border-t border-gray-200 p-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">My PDFs</h3>
            <div className="space-y-2 max-h-48 overflow-y-auto mb-3">
              <PDFList pdfs={pdfs} onDelete={handleDeletePDF} />
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              className="hidden"
              disabled={uploadingPdf}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadingPdf}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white text-sm font-medium rounded-lg transition-colors"
            >
              {uploadingPdf ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  Upload PDF
                </>
              )}
            </button>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Chat Header */}
          <div className="bg-white border-b border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {currentSession?.session_name || 'Select or create a session'}
                </h3>
                {currentPdf ? (
                  <p className="text-sm text-purple-600 mt-1 flex items-center gap-1">
                    <FileText className="w-4 h-4" />
                    Chatting with: {currentPdf.filename}
                  </p>
                ) : (
                  <p className="text-sm text-gray-500 mt-1">Direct chat mode</p>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <select
                  value={currentPdfId || ''}
                  onChange={(e) => setCurrentPdfId(e.target.value || null)}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Direct Chat</option>
                  {pdfs.map((pdf) => (
                    <option key={pdf.id} value={pdf.id}>
                      Chat with: {pdf.filename}
                    </option>
                  ))}
                </select>
                {currentSessionId && (
                  <button
                    onClick={() => {
                      setChats([])
                      toast.success('Chat cleared')
                    }}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 font-medium"
                  >
                    Clear Chat
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Chat Messages */}
          <div
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50"
          >
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              </div>
            ) : chats.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">
                    {currentSessionId
                      ? 'No messages yet. Start the conversation!'
                      : 'Start a conversation or select a session'}
                  </p>
                </div>
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

          {/* Chat Input */}
          <div className="bg-white border-t border-gray-200 p-4">
            <form onSubmit={handleSendMessage} className="flex items-end space-x-3">
              <div className="flex-1">
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSendMessage(e)
                    }
                  }}
                  rows={3}
                  placeholder="Type your engineering question here..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  disabled={sendingMessage}
                />
              </div>
              <button
                type="submit"
                disabled={sendingMessage || !message.trim()}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors h-[60px] flex items-center justify-center"
              >
                {sendingMessage ? (
                  <Loader2 className="w-6 h-6 animate-spin" />
                ) : (
                  <Send className="w-6 h-6" />
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StudentChat