import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import {
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  User as FirebaseUser,
} from 'firebase/auth'
import { auth, googleProvider } from '@/config/firebase'
import apiClient from '@/services/api'
import { User } from '@/types'
import toast from 'react-hot-toast'

interface AuthContextType {
  currentUser: User | null
  firebaseUser: FirebaseUser | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  loginWithGoogle: () => Promise<void>
  register: (email: string, password: string, displayName: string, role?: string) => Promise<void>
  logout: () => Promise<void>
  isAuthenticated: boolean
  isAdmin: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setFirebaseUser(user)
      
      if (user) {
        try {
          // Get user from local storage or verify with backend
          const storedUser = localStorage.getItem('user_data')
          if (storedUser) {
            setCurrentUser(JSON.parse(storedUser))
          } else {
            const idToken = await user.getIdToken()
            const response: any = await apiClient.login(idToken)
            setCurrentUser(response.user)
            apiClient.setToken(response.token)
            localStorage.setItem('user_data', JSON.stringify(response.user))
          }
        } catch (error) {
          console.error('Auth state change error:', error)
        }
      } else {
        setCurrentUser(null)
        apiClient.removeToken()
      }
      
      setLoading(false)
    })

    return unsubscribe
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password)
      const idToken = await userCredential.user.getIdToken()
      
      const response: any = await apiClient.login(idToken)
      setCurrentUser(response.user)
      apiClient.setToken(response.token)
      localStorage.setItem('user_data', JSON.stringify(response.user))
      
      toast.success('Login successful!')
    } catch (error: any) {
      toast.error(error.message || 'Login failed')
      throw error
    }
  }

  const loginWithGoogle = async () => {
    try {
      const userCredential = await signInWithPopup(auth, googleProvider)
      const idToken = await userCredential.user.getIdToken()
      
      const response: any = await apiClient.login(idToken)
      setCurrentUser(response.user)
      apiClient.setToken(response.token)
      localStorage.setItem('user_data', JSON.stringify(response.user))
      
      toast.success('Login successful!')
    } catch (error: any) {
      toast.error(error.message || 'Google login failed')
      throw error
    }
  }

  const register = async (
    email: string,
    password: string,
    displayName: string,
    role: string = 'student'
  ) => {
    try {
      const response: any = await apiClient.register(email, password, displayName, role)
      setCurrentUser(response.user)
      apiClient.setToken(response.token)
      localStorage.setItem('user_data', JSON.stringify(response.user))
      
      toast.success('Account created successfully!')
    } catch (error: any) {
      toast.error(error.message || 'Registration failed')
      throw error
    }
  }

  const logout = async () => {
    try {
      await firebaseSignOut(auth)
      setCurrentUser(null)
      setFirebaseUser(null)
      apiClient.removeToken()
      toast.success('Logged out successfully')
    } catch (error: any) {
      toast.error('Logout failed')
      throw error
    }
  }

  const value: AuthContextType = {
    currentUser,
    firebaseUser,
    loading,
    login,
    loginWithGoogle,
    register,
    logout,
    isAuthenticated: !!currentUser,
    isAdmin: currentUser?.role === 'admin',
  }

  return <AuthContext.Provider value={value}>{!loading && children}</AuthContext.Provider>
}