import React, { useEffect, useState } from 'react'
import api from '../../utils/api'
import './SupportTicketsPage.css'

interface Ticket {
  id: number
  user_id: number
  user_fio: string
  subject: string
  message: string
  status: string
  created_at: string
}

const SupportTicketsPage: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>('all')

  useEffect(() => {
    loadTickets()
  }, [statusFilter])

  const loadTickets = async () => {
    try {
      setLoading(true)
      const params: any = {}
      if (statusFilter !== 'all') {
        params.status = statusFilter
      }
      const response = await api.get('/support/tickets', { params })
      setTickets(response.data)
    } catch (error) {
      console.error('Ошибка загрузки обращений:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (ticketId: number, newStatus: string) => {
    try {
      await api.put(`/support/tickets/${ticketId}/status`, { status: newStatus })
      loadTickets()
    } catch (error) {
      console.error('Ошибка обновления статуса:', error)
    }
  }

  if (loading) {
    return <div className="loading">Загрузка...</div>
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'new': return '🆕 Новое'
      case 'in_progress': return '🔄 В работе'
      case 'resolved': return '✅ Решено'
      default: return status
    }
  }

  return (
    <div className="support-tickets-page">
      <h1>Запросы в поддержку</h1>
      
      <div className="filters">
        <button 
          className={statusFilter === 'all' ? 'active' : ''}
          onClick={() => setStatusFilter('all')}
        >
          Все
        </button>
        <button 
          className={statusFilter === 'new' ? 'active' : ''}
          onClick={() => setStatusFilter('new')}
        >
          Новые
        </button>
        <button 
          className={statusFilter === 'in_progress' ? 'active' : ''}
          onClick={() => setStatusFilter('in_progress')}
        >
          В работе
        </button>
        <button 
          className={statusFilter === 'resolved' ? 'active' : ''}
          onClick={() => setStatusFilter('resolved')}
        >
          Решено
        </button>
      </div>

      <div className="tickets-list">
        {tickets.length === 0 ? (
          <div className="empty-state">
            <p>Нет обращений</p>
          </div>
        ) : (
          tickets.map(ticket => (
            <div key={ticket.id} className="ticket-card">
              <div className="ticket-header">
                <h3>{ticket.subject}</h3>
                <span className={`status status-${ticket.status}`}>
                  {getStatusLabel(ticket.status)}
                </span>
              </div>
              <p className="ticket-user">От: {ticket.user_fio}</p>
              <p className="ticket-message">{ticket.message}</p>
              <div className="ticket-footer">
                <span className="ticket-date">
                  {new Date(ticket.created_at).toLocaleString('ru-RU')}
                </span>
                <div className="ticket-actions">
                  {ticket.status === 'new' && (
                    <button onClick={() => handleStatusChange(ticket.id, 'in_progress')}>
                      Взять в работу
                    </button>
                  )}
                  {ticket.status === 'in_progress' && (
                    <button onClick={() => handleStatusChange(ticket.id, 'resolved')}>
                      Решить
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default SupportTicketsPage

