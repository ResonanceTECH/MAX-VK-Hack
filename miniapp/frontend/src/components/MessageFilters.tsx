import React, { useEffect, useState } from 'react'
import api from '../utils/api'
import './MessageFilters.css'

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
        <label>Статус:</label>
        <select
          value={statusFilter || ''}
          onChange={(e) => onStatusChange(e.target.value || null)}
        >
          <option value="">Все</option>
          <option value="unread">Непрочитанные</option>
          <option value="awaiting">Ожидают ответа</option>
          <option value="replied">Отвечено</option>
        </select>
      </div>

      <div className="filter-group">
        <label>Группа:</label>
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
          Сбросить фильтры
        </button>
      )}
    </div>
  )
}

export default MessageFilters

