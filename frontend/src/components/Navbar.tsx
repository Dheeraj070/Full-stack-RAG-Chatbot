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
    <nav className="bg-dark-card border-b border-dark-border shadow-lg">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-4">
            <div className={`h-10 w-10 rounded-xl flex items-center justify-center shadow-glow ${isAdmin
                ? 'bg-gradient-to-br from-purple-500 to-pink-500'
                : 'bg-gradient-to-br from-cyan-400 to-blue-500'
              }`}>
              {isAdmin ? (
                <Settings className="w-6 h-6 text-white" />
              ) : (
                <MessageSquare className="w-6 h-6 text-white" />
              )}
            </div>
            <div>
              <h1 className="text-xl font-bold text-gradient">{title}</h1>
              <p className="text-xs text-gray-500">Powered by Gemini AI</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium text-gray-300">Welcome back!</p>
              <p className="text-xs text-gray-500">{userName}</p>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg font-medium transition-all duration-200 border border-red-600/30"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar