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
  CheckSquare,
  Square,
} from 'lucide-react'
import Navbar from '@/components/Navbar'
import ChatMessage from '@/components/ChatMessage'
import SessionList from '@/components/SessionList'

const StudentChat: React.FC = () => {
  const { currentUser, logout } = useAuth()
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [chats, setChats] = useState<Chat[]>([])
  const [pdfs, setPdfs] = useState<PDFDocument[]>([])
  const [selectedPdfIds, setSelectedPdfIds] = useState<string[]>([]) // Changed from single to array
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

  const togglePdfSelection = (pdfId: string) => {
    setSelectedPdfIds(prev => {
      if (prev.includes(pdfId)) {
        return prev.filter(id => id !== pdfId)
      } else {
        return [...prev, pdfId]
      }
    })
  }

  const selectAllPdfs = () => {
    if (selectedPdfIds.length === pdfs.length) {
      setSelectedPdfIds([])
    } else {
      setSelectedPdfIds(pdfs.map(pdf => pdf.id))
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!message.trim()) return

    let sessionId = currentSessionId

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

    const tempChat: Chat = {
      id: 'temp-' + Date.now(),
      user_id: currentUser?.id || '',
      session_id: sessionId,
      message: userMessage,
      response: '',
      context_type: selectedPdfIds.length > 0 ? 'pdf' : 'direct',
      pdf_id: selectedPdfIds[0] || undefined,
      created_at: new Date().toISOString(),
    }
    setChats([...chats, tempChat])

    try {
      // Send with multiple PDF IDs
      const response: any = await apiClient.sendMessage(
        userMessage,
        sessionId,
        selectedPdfIds.length > 0 ? selectedPdfIds : undefined
      )

      setChats((prev) => {
        const filtered = prev.filter((c) => c.id !== tempChat.id)
        return [...filtered, response.chat]
      })

      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId
            ? { ...s, message_count: s.message_count + 1, updated_at: new Date().toISOString() }
            : s
        )
      )
    } catch (error: any) {
      toast.error(error.message || 'Failed to send message')
      setChats((prev) => prev.filter((c) => c.id !== tempChat.id))
      setMessage(userMessage)
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
      setSelectedPdfIds(prev => prev.filter(id => id !== pdfId))
      toast.success('PDF deleted')
    } catch (error: any) {
      toast.error('Failed to delete PDF')
    }
  }

  const currentSession = sessions.find((s) => s.id === currentSessionId)
  const selectedPdfs = pdfs.filter(pdf => selectedPdfIds.includes(pdf.id))

  return (
    <div className="h-screen flex flex-col bg-dark-bg">
      <Navbar
        title="Engineering Chatbot"
        userName={currentUser?.display_name || 'Student'}
        onLogout={logout}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 bg-dark-card border-r border-dark-border flex flex-col shadow-xl">
          {/* Sessions Header */}
          <div className="p-4 border-b border-dark-border">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gradient">Chat Sessions</h2>
              <button
                onClick={handleCreateSession}
                className="p-2 bg-gradient-to-br from-cyan-400 to-blue-500 hover:shadow-glow text-dark-bg rounded-lg transition-all"
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
          <div className="border-t border-dark-border p-4 bg-dark-bg/50">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                My PDFs ({selectedPdfIds.length} selected)
              </h3>
              {pdfs.length > 0 && (
                <button
                  onClick={selectAllPdfs}
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-medium"
                >
                  {selectedPdfIds.length === pdfs.length ? 'Deselect All' : 'Select All'}
                </button>
              )}
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto mb-3">
              {pdfs.length === 0 ? (
                <p className="text-xs text-gray-500 text-center py-4">No PDFs uploaded yet</p>
              ) : (
                pdfs.map((pdf) => (
                  <div
                    key={pdf.id}
                    className={`flex items-center justify-between p-2 rounded-lg border transition-all group cursor-pointer ${selectedPdfIds.includes(pdf.id)
                        ? 'bg-cyan-400/10 border-cyan-400'
                        : 'bg-dark-hover border-dark-border hover:border-cyan-400/50'
                      }`}
                    onClick={() => togglePdfSelection(pdf.id)}
                  >
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <div className="flex-shrink-0">
                        {selectedPdfIds.includes(pdf.id) ? (
                          <CheckSquare className="w-5 h-5 text-cyan-400" />
                        ) : (
                          <Square className="w-5 h-5 text-gray-500" />
                        )}
                      </div>
                      <div className="p-1.5 bg-cyan-400/10 rounded">
                        <FileText className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-gray-300 truncate">{pdf.filename}</p>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(pdf.file_size)} • {pdf.page_count} pages
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeletePDF(pdf.id)
                      }}
                      className="ml-2 p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-all opacity-0 group-hover:opacity-100 flex-shrink-0"
                      title="Delete PDF"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))
              )}
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
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-green-500 to-emerald-500 hover:shadow-glow disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all"
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
        <div className="flex-1 flex flex-col bg-gradient-to-br from-dark-bg to-dark-card">
          {/* Chat Header */}
          <div className="bg-dark-card border-b border-dark-border p-4 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-100">
                  {currentSession?.session_name || 'Select or create a session'}
                </h3>
                {selectedPdfIds.length > 0 ? (
                  <div className="text-sm text-cyan-400 mt-1 flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    <span>
                      Chatting with {selectedPdfIds.length} PDF{selectedPdfIds.length > 1 ? 's' : ''}:
                    </span>
                    <div className="flex gap-1 flex-wrap">
                      {selectedPdfs.slice(0, 2).map(pdf => (
                        <span key={pdf.id} className="px-2 py-0.5 bg-cyan-400/10 rounded text-xs">
                          {pdf.filename.length > 15 ? pdf.filename.substring(0, 15) + '...' : pdf.filename}
                        </span>
                      ))}
                      {selectedPdfs.length > 2 && (
                        <span className="px-2 py-0.5 bg-cyan-400/10 rounded text-xs">
                          +{selectedPdfs.length - 2} more
                        </span>
                      )}
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500 mt-1">Direct chat mode - Select PDFs to enable context</p>
                )}
              </div>
              {currentSessionId && (
                <button
                  onClick={() => {
                    setChats([])
                    toast.success('Chat cleared')
                  }}
                  className="px-4 py-2 text-sm text-gray-400 hover:text-gray-200 font-medium"
                >
                  Clear Chat
                </button>
              )}
            </div>
          </div>

          {/* Chat Messages */}
          <div
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-6 space-y-4"
          >
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
              </div>
            ) : chats.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-2xl flex items-center justify-center shadow-glow">
                    <MessageSquare className="w-12 h-12 text-dark-bg" />
                  </div>
                  <p className="text-gray-400 text-lg mb-2">
                    {currentSessionId
                      ? 'No messages yet. Start the conversation!'
                      : 'Start a conversation or select a session'}
                  </p>
                  {selectedPdfIds.length > 0 && (
                    <p className="text-cyan-400 text-sm">
                      Ask questions about your {selectedPdfIds.length} selected PDF{selectedPdfIds.length > 1 ? 's' : ''}
                    </p>
                  )}
                </div>
              </div>
            ) : (
              chats.map((chat) => <ChatMessage key={chat.id} chat={chat} />)
            )}
            {sendingMessage && (
              <div className="flex justify-start">
                <div className="max-w-3xl bg-dark-card border border-dark-border rounded-2xl p-4">
                  <div className="flex items-center space-x-3">
                    <Loader2 className="w-5 h-5 animate-spin text-cyan-400" />
                    <span className="text-sm text-gray-400">
                      AI is analyzing {selectedPdfIds.length > 0 ? `${selectedPdfIds.length} PDF${selectedPdfIds.length > 1 ? 's' : ''}` : 'your question'}...
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <div className="bg-dark-card border-t border-dark-border p-4 shadow-2xl">
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
                  placeholder={
                    selectedPdfIds.length > 0
                      ? `Ask about your ${selectedPdfIds.length} selected PDF${selectedPdfIds.length > 1 ? 's' : ''}...`
                      : 'Ask me anything about engineering...'
                  }
                  className="w-full px-4 py-3 bg-dark-hover border border-dark-border rounded-xl resize-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent outline-none text-gray-100 placeholder-gray-500"
                  disabled={sendingMessage}
                />
              </div>
              <button
                type="submit"
                disabled={sendingMessage || !message.trim()}
                className="px-6 py-3 bg-gradient-to-r from-cyan-400 to-blue-500 hover:shadow-glow disabled:opacity-50 text-dark-bg font-semibold rounded-xl transition-all h-[60px] flex items-center justify-center"
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