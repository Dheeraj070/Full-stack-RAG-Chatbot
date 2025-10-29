import React from 'react'
import { LogOut, MessageSquare, Settings } from 'lucide-react'

interface NavbarProps {
  title: string
  userName: string
  onLogout: () => void
  isAdmin?: boolean
}

const Navbar: React.FC<NavbarProps> = ({ title, userName, onLogout, isAdmin = false }) => {
  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <div className={`h-10 w-10 ${isAdmin ? 'bg-purple-600' : 'bg-blue-600'} rounded-lg flex items-center justify-center`}>
              {isAdmin ? (
                <Settings className="w-6 h-6 text-white" />
              ) : (
                <MessageSquare className="w-6 h-6 text-white" />
              )}
            </div>
            <span className="text-xl font-semibold text-gray-900">{title}</span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">Welcome, {userName}</span>
            <button
              onClick={onLogout}
              className="flex items-center gap-2 text-sm text-red-600 hover:text-red-700 font-medium transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar