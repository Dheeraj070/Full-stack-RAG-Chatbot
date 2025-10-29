export interface User {
  id: string
  firebase_uid: string
  email: string
  display_name: string
  role: 'student' | 'admin'
  is_active: boolean
  created_at: string
  last_login: string
}

export interface Session {
  id: string
  user_id: string
  session_name: string
  message_count: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Chat {
  id: string
  user_id: string
  session_id: string
  message: string
  response: string
  context_type: 'direct' | 'pdf'
  pdf_id?: string
  metadata?: Record<string, any>
  created_at: string
}

export interface PDFDocument {
  id: string
  user_id: string
  filename: string
  file_size: number
  page_count: number
  processed: boolean
  created_at: string
  text_content?: string
}

export interface VectorData {
  id: string
  pdf_id: string
  chunk_text: string
  chunk_index: number
  created_at: string
}

export interface Stats {
  total_users: number
  total_sessions: number
  total_chats: number
  total_pdfs: number
  total_vectors: number
}

export interface ApiResponse<T> {
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
}