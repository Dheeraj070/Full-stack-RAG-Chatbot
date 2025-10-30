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
        <MessageSquare className="w-12 h-12 text-gray-600 mx-auto mb-3" />
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
            'p-3 rounded-xl border transition-all duration-200 cursor-pointer group',
            currentSessionId === session.id
              ? 'bg-dark-hover border-cyan-400 shadow-glow'
              : 'border-dark-border hover:bg-dark-hover hover:border-cyan-400/50'
          )}
          onClick={() => onSelectSession(session.id)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h4 className={clsx(
                "text-sm font-medium truncate",
                currentSessionId === session.id ? 'text-cyan-400' : 'text-gray-300'
              )}>
                {session.session_name}
              </h4>
              <p className="text-xs text-gray-500 mt-1">{session.message_count} messages</p>
              <p className="text-xs text-gray-600 mt-1">{formatDate(session.updated_at)}</p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onDeleteSession(session.id)
              }}
              className="ml-2 p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all opacity-0 group-hover:opacity-100"
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