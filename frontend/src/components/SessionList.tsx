import React from 'react'
import { Session } from '@/types'
import { formatDate } from '@/utils/helpers'
import { Trash2, MessageSquare } from 'lucide-react'
import clsx from 'clsx'

interface SessionListProps {
  sessions: Session[]
  currentSessionId: string | null
  onSelectSession: (sessionId: string) => void
  onDeleteSession: (sessionId: string) => void
}

const SessionList: React.FC<SessionListProps> = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onDeleteSession,
}) => {
  if (sessions.length === 0) {
    return (
      <div className="text-center py-8">
        <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <p className="text-sm text-gray-500">No sessions yet. Create one to start!</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {sessions.map((session) => (
        <div
          key={session.id}
          className={clsx(
            'p-3 rounded-lg border transition-colors cursor-pointer',
            currentSessionId === session.id
              ? 'bg-blue-50 border-blue-500'
              : 'border-gray-200 hover:bg-gray-50'
          )}
          onClick={() => onSelectSession(session.id)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-medium text-gray-900 truncate">
                {session.session_name}
              </h4>
              <p className="text-xs text-gray-500 mt-1">{session.message_count} messages</p>
              <p className="text-xs text-gray-400 mt-1">{formatDate(session.updated_at)}</p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onDeleteSession(session.id)
              }}
              className="ml-2 p-1 text-red-600 hover:text-red-700 transition-colors"
              title="Delete session"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

export default SessionList