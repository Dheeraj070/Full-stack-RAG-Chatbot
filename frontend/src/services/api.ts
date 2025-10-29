import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { API_BASE_URL, APP_CONFIG } from '@/config/api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.removeToken()
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  getToken(): string | null {
    return localStorage.getItem(APP_CONFIG.STORAGE_KEYS.TOKEN)
  }

  setToken(token: string): void {
    localStorage.setItem(APP_CONFIG.STORAGE_KEYS.TOKEN, token)
  }

  removeToken(): void {
    localStorage.removeItem(APP_CONFIG.STORAGE_KEYS.TOKEN)
    localStorage.removeItem(APP_CONFIG.STORAGE_KEYS.USER)
  }

  async request<T>(config: AxiosRequestConfig): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.client.request(config)
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || error.message)
      }
      throw error
    }
  }

  // Auth endpoints
  async login(firebaseToken: string) {
    return this.request({
      method: 'POST',
      url: '/auth/login',
      data: { firebase_token: firebaseToken },
    })
  }

  async register(email: string, password: string, displayName: string, role: string = 'student') {
    return this.request({
      method: 'POST',
      url: '/auth/register',
      data: { email, password, display_name: displayName, role },
    })
  }

  async verifyToken() {
    return this.request({
      method: 'GET',
      url: '/auth/verify',
    })
  }

  // Chat endpoints
  async sendMessage(message: string, sessionId?: string, pdfId?: string) {
    return this.request({
      method: 'POST',
      url: '/chat/send',
      data: { message, session_id: sessionId, pdf_id: pdfId },
    })
  }

  async getChatHistory(sessionId: string, page: number = 1, limit: number = 50) {
    return this.request({
      method: 'GET',
      url: `/chat/history/${sessionId}`,
      params: { page, limit },
    })
  }

  async getSessions(page: number = 1, limit: number = 20) {
    return this.request({
      method: 'GET',
      url: '/chat/sessions',
      params: { page, limit },
    })
  }

  async createSession(sessionName?: string) {
    return this.request({
      method: 'POST',
      url: '/chat/session',
      data: { session_name: sessionName },
    })
  }

  async deleteSession(sessionId: string) {
    return this.request({
      method: 'DELETE',
      url: `/chat/session/${sessionId}`,
    })
  }

  // Student endpoints
  async uploadPDF(file: File) {
    const formData = new FormData()
    formData.append('file', file)

    return this.request({
      method: 'POST',
      url: '/student/upload-pdf',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  }

  async getPDFs(page: number = 1, limit: number = 20) {
    return this.request({
      method: 'GET',
      url: '/student/pdfs',
      params: { page, limit },
    })
  }

  async deletePDF(pdfId: string) {
    return this.request({
      method: 'DELETE',
      url: `/student/pdf/${pdfId}`,
    })
  }

  // Admin endpoints
  async getUsers(page: number = 1, limit: number = 20) {
    return this.request({
      method: 'GET',
      url: '/admin/users',
      params: { page, limit },
    })
  }

  async updateUser(userId: string, updateData: Partial<any>) {
    return this.request({
      method: 'PUT',
      url: `/admin/user/${userId}`,
      data: updateData,
    })
  }

  async deleteUser(userId: string) {
    return this.request({
      method: 'DELETE',
      url: `/admin/user/${userId}`,
    })
  }

  async getAllSessions(page: number = 1, limit: number = 20) {
    return this.request({
      method: 'GET',
      url: '/admin/sessions',
      params: { page, limit },
    })
  }

  async getAllChats(page: number = 1, limit: number = 20) {
    return this.request({
      method: 'GET',
      url: '/admin/chats',
      params: { page, limit },
    })
  }

  async deleteChat(chatId: string) {
    return this.request({
      method: 'DELETE',
      url: `/admin/chat/${chatId}`,
    })
  }

  async getAllPDFs(page: number = 1, limit: number = 20) {
    return this.request({
      method: 'GET',
      url: '/admin/pdfs',
      params: { page, limit },
    })
  }

  async getVectorStore(page: number = 1, limit: number = 20) {
    return this.request({
      method: 'GET',
      url: '/admin/vectorstore',
      params: { page, limit },
    })
  }

  async getStats() {
    return this.request({
      method: 'GET',
      url: '/admin/stats',
    })
  }
}

const apiClient = new ApiClient()
export default apiClient