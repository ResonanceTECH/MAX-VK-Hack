import React from 'react'
import './StatsBar.css'

interface Stats {
  unread: number
  awaiting: number
  replied: number
  total: number
}

interface StatsBarProps {
  stats: Stats
}

const StatsBar: React.FC<StatsBarProps> = ({ stats }) => {
  return (
    <div className="stats-bar">
      <div className="stat-item unread">
        <div className="stat-value">{stats.unread}</div>
        <div className="stat-label">Непрочитанные</div>
      </div>
      <div className="stat-item awaiting">
        <div className="stat-value">{stats.awaiting}</div>
        <div className="stat-label">Ожидают ответа</div>
      </div>
      <div className="stat-item replied">
        <div className="stat-value">{stats.replied}</div>
        <div className="stat-label">Отвечено</div>
      </div>
      <div className="stat-item total">
        <div className="stat-value">{stats.total}</div>
        <div className="stat-label">Всего</div>
      </div>
    </div>
  )
}

export default StatsBar

