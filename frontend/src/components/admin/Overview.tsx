import React from 'react'
import { Stats } from '@/types'
import { Users, MessageSquare, MessageCircle, FileText, RefreshCw } from 'lucide-react'

interface OverviewProps {
  stats: Stats
  onRefresh: () => void
}

const Overview: React.FC<OverviewProps> = ({ stats, onRefresh }) => {
  const statCards = [
    {
      title: 'Total Users',
      value: stats.total_users,
      icon: Users,
      bgColor: 'bg-blue-100',
      iconColor: 'text-blue-600',
    },
    {
      title: 'Total Sessions',
      value: stats.total_sessions,
      icon: MessageSquare,
      bgColor: 'bg-green-100',
      iconColor: 'text-green-600',
    },
    {
      title: 'Total Messages',
      value: stats.total_chats,
      icon: MessageCircle,
      bgColor: 'bg-purple-100',
      iconColor: 'text-purple-600',
    },
    {
      title: 'Total PDFs',
      value: stats.total_pdfs,
      icon: FileText,
      bgColor: 'bg-yellow-100',
      iconColor: 'text-yellow-600',
    },
  ]

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
        <button
          onClick={onRefresh}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card) => {
          const Icon = card.icon
          return (
            <div key={card.title} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{card.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{card.value}</p>
                </div>
                <div className={`${card.bgColor} rounded-full p-3`}>
                  <Icon className={`w-8 h-8 ${card.iconColor}`} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">System Status</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-700">API Status</span>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
              Operational
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-700">Database</span>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
              Connected
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-700">Gemini API</span>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
              Active
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-700">Vector Store</span>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
              {stats.total_vectors} vectors
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Overview