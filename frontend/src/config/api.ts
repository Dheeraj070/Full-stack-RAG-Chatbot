export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export const API_ENDPOINTS = {
  AUTH: {
    REGISTER: '/auth/register',
    LOGIN: '/auth/login',
    VERIFY: '/auth/verify',
    REFRESH: '/auth/refresh',
  },
  CHAT: {
    SEND: '/chat/send',
    HISTORY: '/chat/history',
    SESSIONS: '/chat/sessions',
    CREATE_SESSION: '/chat/session',
    DELETE_SESSION: '/chat/session',
  },
  STUDENT: {
    UPLOAD_PDF: '/student/upload-pdf',
    GET_PDFS: '/student/pdfs',
    DELETE_PDF: '/student/pdf',
  },
  ADMIN: {
    USERS: '/admin/users',
    UPDATE_USER: '/admin/user',
    DELETE_USER: '/admin/user',
    SESSIONS: '/admin/sessions',
    DELETE_SESSION: '/admin/session',
    CHATS: '/admin/chats',
    DELETE_CHAT: '/admin/chat',
    PDFS: '/admin/pdfs',
    DELETE_PDF: '/admin/pdf',
    VECTORSTORE: '/admin/vectorstore',
    STATS: '/admin/stats',
  },
} as const

export const APP_CONFIG = {
  APP_NAME: 'Engineering Chatbot',
  VERSION: '1.0.0',
  STORAGE_KEYS: {
    TOKEN: 'auth_token',
    USER: 'user_data',
  },
  PAGINATION: {
    DEFAULT_LIMIT: 20,
    MAX_LIMIT: 100,
  },
} as const