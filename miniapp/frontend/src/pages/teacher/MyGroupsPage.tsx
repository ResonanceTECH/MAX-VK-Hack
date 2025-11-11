import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../../utils/api'
import './MyGroupsPage.css'

interface Group {
  id: number
  name: string
  semester?: number
  year?: number
}

const MyGroupsPage: React.FC = () => {
  const [groups, setGroups] = useState<Group[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadGroups()
  }, [])

  const loadGroups = async () => {
    try {
      setLoading(true)
      const response = await api.get('/groups')
      setGroups(response.data)
    } catch (error) {
      console.error('Ошибка загрузки групп:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Загрузка...</div>
  }

  return (
    <div className="my-groups-page">
      <h1>Мои группы</h1>
      
      <div className="groups-list">
        {groups.length === 0 ? (
          <div className="empty-state">
            <p>У вас нет групп</p>
          </div>
        ) : (
          <div className="groups-grid">
            {groups.map(group => (
              <Link key={group.id} to={`/groups/${group.id}`} className="group-card">
                <h3>{group.name}</h3>
                {group.year && group.semester && (
                  <p>{group.year} год, {group.semester} семестр</p>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default MyGroupsPage

