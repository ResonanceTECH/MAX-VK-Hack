import React from 'react'
import './MessageCard.css'

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

interface MessageCardProps {
  message: Message
  onStatusChange: (messageId: number, newStatus: string) => void
}

const MessageCard: React.FC<MessageCardProps> = ({ message, onStatusChange }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'unread':
        return '#d32f2f' // красный
      case 'awaiting':
        return '#ed6c02' // желтый/оранжевый
      case 'replied':
        return '#2e7d32' // зеленый
      default:
        return '#666'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'unread':
        return 'Непрочитанное'
      case 'awaiting':
        return 'Ожидает ответа'
      case 'replied':
        return 'Отвечено'
      default:
        return status
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="message-card" style={{ borderLeftColor: getStatusColor(message.status) }}>
      <div className="message-header">
        <div className="message-sender">
          <strong>{message.from_user_fio}</strong>
          {message.group_name && (
            <span className="message-group">Группа: {message.group_name}</span>
          )}
        </div>
        <div className="message-date">{formatDate(message.created_at)}</div>
      </div>
      
      <div className="message-text">{message.text}</div>
      
      <div className="message-footer">
        <div className="message-status" style={{ color: getStatusColor(message.status) }}>
          Статус: {getStatusLabel(message.status)}
        </div>
        <div className="message-actions">
          <button
            className={`status-btn ${message.status === 'unread' ? 'active' : ''}`}
            onClick={() => onStatusChange(message.id, 'unread')}
            style={{ backgroundColor: message.status === 'unread' ? '#d32f2f' : '#f5f5f5', color: message.status === 'unread' ? 'white' : '#333' }}
          >
            Непрочитанное
          </button>
          <button
            className={`status-btn ${message.status === 'awaiting' ? 'active' : ''}`}
            onClick={() => onStatusChange(message.id, 'awaiting')}
            style={{ backgroundColor: message.status === 'awaiting' ? '#ed6c02' : '#f5f5f5', color: message.status === 'awaiting' ? 'white' : '#333' }}
          >
            Ожидает ответа
          </button>
          <button
            className={`status-btn ${message.status === 'replied' ? 'active' : ''}`}
            onClick={() => onStatusChange(message.id, 'replied')}
            style={{ backgroundColor: message.status === 'replied' ? '#2e7d32' : '#f5f5f5', color: message.status === 'replied' ? 'white' : '#333' }}
          >
            Отвечено
          </button>
        </div>
      </div>
    </div>
  )
}

export default MessageCard

