import React, { useEffect, useState } from 'react'
import api from '../utils/api'
import './MessageFilters.css'

// Иконки в стиле Hugeicons
const FilterIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 3H2L10 12.46V19L14 21V12.46L22 3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const UsersIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88M13 7C13 9.20914 11.2091 11 9 11C6.79086 11 5 9.20914 5 7C5 4.79086 6.79086 3 9 3C11.2091 3 13 4.79086 13 7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const XIcon = ({ size = 16 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

interface Group {
  id: number
  name: string
}

interface MessageFiltersProps {
  statusFilter: string | null
  groupFilter: number | null
  onStatusChange: (status: string | null) => void
  onGroupChange: (groupId: number | null) => void
}

const MessageFilters: React.FC<MessageFiltersProps> = ({
  statusFilter,
  groupFilter,
  onStatusChange,
  onGroupChange
}) => {
  const [groups, setGroups] = useState<Group[]>([])

  useEffect(() => {
    loadGroups()
  }, [])

  const loadGroups = async () => {
    try {
      const response = await api.get('/groups')
      setGroups(response.data)
    } catch (error) {
      console.error('Ошибка загрузки групп:', error)
    }
  }

  return (
    <div className="message-filters">
      <div className="filter-group">
        <label>
          <FilterIcon size={16} />
          Статус:
        </label>
        <select
          value={statusFilter || ''}
          onChange={(e) => onStatusChange(e.target.value || null)}
        >
          <option value="">Все</option>
          <option value="unread">Непрочитанные</option>
          <option value="read">Прочитанные</option>
        </select>
      </div>

      <div className="filter-group">
        <label>
          <UsersIcon size={16} />
          Группа:
        </label>
        <select
          value={groupFilter || ''}
          onChange={(e) => onGroupChange(e.target.value ? parseInt(e.target.value) : null)}
        >
          <option value="">Все группы</option>
          {groups.map(group => (
            <option key={group.id} value={group.id}>
              {group.name}
            </option>
          ))}
        </select>
      </div>

      {(statusFilter || groupFilter) && (
        <button
          className="clear-filters"
          onClick={() => {
            onStatusChange(null)
            onGroupChange(null)
          }}
        >
          <XIcon size={16} />
          Сбросить фильтры
        </button>
      )}
    </div>
  )
}

export default MessageFilters

