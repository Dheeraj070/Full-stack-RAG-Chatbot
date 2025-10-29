import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Stats } from '@/types'
import apiClient from '@/services/api'
import toast from 'react-hot-toast'
import {
  Settings,
  Users,
  MessageSquare,
  FileText,
  Database,
  MessageCircle,
  BarChart3,
} from 'lucide-react'
import Navbar from '@/components/Navbar'
import Sidebar from '@/components/admin/Sidebar'
import Overview from '@/components/admin/Overview'
import UsersManagement from '@/components/admin/UsersManagement'
import SessionsManagement from '@/components/admin/SessionsManagement'
import ChatsManagement from '@/components/admin/ChatsManagement'
import FilesManagement from '@/components/admin/FilesManagement'
import VectorStoreManagement from '@/components/admin/VectorStoreManagement'
import AdminChat from '@/components/admin/AdminChat'

type Section = 'overview' | 'users' | 'sessions' | 'chats' | 'files' | 'vectorstore' | 'chat'

const AdminDashboard: React.FC = () => {
  const { currentUser, logout } = useAuth()
  const [currentSection, setCurrentSection] = useState<Section>('overview')
  const [stats, setStats] = useState<Stats>({
    total_users: 0,
    total_sessions: 0,
    total_chats: 0,
    total_pdfs: 0,
    total_vectors: 0,
  })

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const response: any = await apiClient.getStats()
      setStats(response)
    } catch (error: any) {
      console.error('Failed to load stats:', error)
    }
  }

  const menuItems = [
    { id: 'overview' as Section, label: 'Overview', icon: BarChart3 },
    { id: 'users' as Section, label: 'Users', icon: Users },
    { id: 'sessions' as Section, label: 'Sessions', icon: MessageSquare },
    { id: 'chats' as Section, label: 'Chat History', icon: MessageCircle },
    { id: 'files' as Section, label: 'PDF Files', icon: FileText },
    { id: 'vectorstore' as Section, label: 'Vector Store', icon: Database },
    { id: 'chat' as Section, label: 'Admin Chat', icon: MessageSquare },
  ]

  const renderSection = () => {
    switch (currentSection) {
      case 'overview':
        return <Overview stats={stats} onRefresh={loadStats} />
      case 'users':
        return <UsersManagement />
      case 'sessions':
        return <SessionsManagement />
      case 'chats':
        return <ChatsManagement />
      case 'files':
        return <FilesManagement />
      case 'vectorstore':
        return <VectorStoreManagement />
      case 'chat':
        return <AdminChat />
      default:
        return <Overview stats={stats} onRefresh={loadStats} />
    }
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Navbar
        title="Admin Dashboard"
        userName={currentUser?.display_name || 'Admin'}
        onLogout={logout}
        isAdmin
      />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          menuItems={menuItems}
          currentSection={currentSection}
          onSectionChange={setCurrentSection}
        />

        <div className="flex-1 overflow-y-auto">
          {renderSection()}
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard