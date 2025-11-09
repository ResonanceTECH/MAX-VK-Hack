import React, { useEffect, useState } from 'react'
import api from '../utils/api'
import MessageCard from '../components/MessageCard'
import MessageFilters from '../components/MessageFilters'
import StatsBar from '../components/StatsBar'
import './MessagesPage.css'

interface Message {
  id: number
  from_user_id: number
  from_user_fio: string
  to_user_id: number
  to_user_fio: string
  group_id?: number
  group_name?: string
  text: string
  status: string
  created_at: string
}

interface Stats {
  unread: number
  awaiting: number
  replied: number
  total: number
}

const MessagesPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [stats, setStats] = useState<Stats>({ unread: 0, awaiting: 0, replied: 0, total: 0 })
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string | null>(null)
  const [groupFilter, setGroupFilter] = useState<number | null>(null)

  useEffect(() => {
    loadMessages()
    loadStats()
  }, [statusFilter, groupFilter])

  const loadMessages = async () => {
    try {
      setLoading(true)
      const params: any = {}
      if (statusFilter) params.status = statusFilter
      if (groupFilter) params.group_id = groupFilter

      const response = await api.get('/messages', { params })
      setMessages(response.data)
    } catch (error) {
      console.error('Ошибка загрузки сообщений:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await api.get('/messages/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error)
    }
  }

  const handleStatusChange = async (messageId: number, newStatus: string) => {
    try {
      await api.put(`/messages/${messageId}/status`, { status: newStatus })
      // Обновляем локальное состояние
      setMessages(messages.map(msg => 
        msg.id === messageId ? { ...msg, status: newStatus } : msg
      ))
      // Обновляем статистику
      loadStats()
    } catch (error) {
      console.error('Ошибка обновления статуса:', error)
    }
  }

  if (loading && messages.length === 0) {
    return <div className="loading">Загрузка сообщений...</div>
  }

  return (
    <div className="messages-page">
      <h1>Сообщения студентов</h1>
      
      <StatsBar stats={stats} />
      
      <MessageFilters
        statusFilter={statusFilter}
        groupFilter={groupFilter}
        onStatusChange={setStatusFilter}
        onGroupChange={setGroupFilter}
      />

      <div className="messages-list">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>Нет сообщений</p>
          </div>
        ) : (
          messages.map(message => (
            <MessageCard
              key={message.id}
              message={message}
              onStatusChange={handleStatusChange}
            />
          ))
        )}
      </div>
    </div>
  )
}

export default MessagesPage

