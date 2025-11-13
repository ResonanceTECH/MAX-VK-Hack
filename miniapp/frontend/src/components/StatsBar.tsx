import React from 'react'
import './StatsBar.css'

interface Stats {
  unread: number
  read?: number
  awaiting?: number
  replied?: number
  total: number
}

interface StatsBarProps {
  stats: Stats
}

const StatsBar: React.FC<StatsBarProps> = ({ stats }) => {
  return (
    <div className="stats-bar">
      <div className="stat-item unread">
        <div className="stat-value">{stats.unread || 0}</div>
        <div className="stat-label">НЕПРОЧИТАННЫЕ</div>
      </div>
      <div className="stat-item read">
        <div className="stat-value">{stats.read || 0}</div>
        <div className="stat-label">ПРОЧИТАННЫЕ</div>
      </div>
      <div className="stat-item total">
        <div className="stat-value">{stats.total}</div>
        <div className="stat-label">ВСЕГО</div>
      </div>
    </div>
  )
}

export default StatsBar

