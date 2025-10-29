import React from 'react'
import { LucideIcon } from 'lucide-react'
import clsx from 'clsx'

interface MenuItem {
  id: string
  label: string
  icon: LucideIcon
}

interface SidebarProps {
  menuItems: MenuItem[]
  currentSection: string
  onSectionChange: (section: string) => void
}

const Sidebar: React.FC<SidebarProps> = ({ menuItems, currentSection, onSectionChange }) => {
  return (
    <div className="w-64 bg-white border-r border-gray-200">
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.id}
              onClick={() => onSectionChange(item.id)}
              className={clsx(
                'w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors duration-200',
                currentSection === item.id
                  ? 'bg-primary-100 text-primary-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              )}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>
    </div>
  )
}

export default Sidebar