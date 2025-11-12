import React from 'react'
import './MessageCard.css'

// Иконки в стиле Hugeicons
const UserIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const UsersIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88M13 7C13 9.20914 11.2091 11 9 11C6.79086 11 5 9.20914 5 7C5 4.79086 6.79086 3 9 3C11.2091 3 13 4.79086 13 7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const ClockIcon = ({ size = 16 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const CheckIcon = ({ size = 16 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

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
  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'unread':
        return 'Непрочитанное'
      case 'read':
        return 'Прочитанное'
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
    <div className={`message-card ${message.status === 'unread' ? 'unread' : 'read'}`}>
      <div className="message-header">
        <div className="message-sender">
          <div className="sender-info">
            <UserIcon size={18} />
            <strong>{message.from_user_fio}</strong>
          </div>
          {message.group_name && (
            <div className="message-group">
              <UsersIcon size={16} />
              <span>Группа: {message.group_name}</span>
            </div>
          )}
        </div>
        <div className="message-date">
          <ClockIcon size={16} />
          <span>{formatDate(message.created_at)}</span>
        </div>
      </div>
      
      <div className="message-text">{message.text}</div>
      
      <div className="message-footer">
        <div className={`message-status ${message.status}`}>
          <CheckIcon size={16} />
          <span>{getStatusLabel(message.status)}</span>
        </div>
        <div className="message-actions">
          <button
            className={`status-btn ${message.status === 'unread' ? 'active' : ''}`}
            onClick={() => onStatusChange(message.id, 'unread')}
          >
            Непрочитанное
          </button>
          <button
            className={`status-btn ${message.status === 'read' ? 'active' : ''}`}
            onClick={() => onStatusChange(message.id, 'read')}
          >
            Прочитанное
          </button>
        </div>
      </div>
    </div>
  )
}

export default MessageCard

