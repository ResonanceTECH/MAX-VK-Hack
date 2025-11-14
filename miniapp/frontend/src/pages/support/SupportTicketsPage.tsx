import React, { useEffect, useState } from 'react'
import api from '../../utils/api'
import LoadingSpinner from '../../components/LoadingSpinner'
import './SupportTicketsPage.css'

// Иконки в стиле Hugeicons
const NewIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const ClockIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
        <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    </svg>
)

const CheckIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const UserIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const CalendarIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
        <path d="M16 2V6M8 2V6M3 10H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    </svg>
)


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

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'new': return 'Новое'
      case 'in_progress': return 'В работе'
      case 'resolved': return 'Решено'
      default: return status
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'new': return <NewIcon size={16} />
      case 'in_progress': return <ClockIcon size={16} />
      case 'resolved': return <CheckIcon size={16} />
      default: return null
    }
  }

  if (loading) {
    return (
      <div className="support-tickets-page">
        <LoadingSpinner />
      </div>
    )
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
                  {getStatusIcon(ticket.status)}
                  <span>{getStatusLabel(ticket.status)}</span>
                </span>
              </div>
              <p className="ticket-user">
                <UserIcon size={16} />
                <span>От: {ticket.user_fio}</span>
              </p>
              <p className="ticket-message">{ticket.message}</p>
              <div className="ticket-footer">
                <span className="ticket-date">
                  <CalendarIcon size={16} />
                  <span>{new Date(ticket.created_at).toLocaleString('ru-RU')}</span>
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

