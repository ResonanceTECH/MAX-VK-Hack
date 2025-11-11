import React, { useEffect, useState } from 'react'
import api from '../../utils/api'
import './StatsPage.css'

interface Stats {
  total: number
  new: number
  in_progress: number
  resolved: number
  avg_response_time?: number
}

const StatsPage: React.FC = () => {
  const [stats, setStats] = useState<Stats>({ total: 0, new: 0, in_progress: 0, resolved: 0 })

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const response = await api.get('/support/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error)
    }
  }

  return (
    <div className="stats-page">
      <h1>Статистика</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Всего обращений</h3>
          <p className="stat-value">{stats.total}</p>
        </div>
        <div className="stat-card">
          <h3>Новых</h3>
          <p className="stat-value">{stats.new}</p>
        </div>
        <div className="stat-card">
          <h3>В работе</h3>
          <p className="stat-value">{stats.in_progress}</p>
        </div>
        <div className="stat-card">
          <h3>Решено</h3>
          <p className="stat-value">{stats.resolved}</p>
        </div>
        {stats.avg_response_time !== undefined && (
          <div className="stat-card">
            <h3>Среднее время реакции</h3>
            <p className="stat-value">{stats.avg_response_time.toFixed(1)} мин</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default StatsPage

