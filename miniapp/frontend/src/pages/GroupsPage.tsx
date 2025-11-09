import React, { useEffect, useState } from 'react'
import api from '../utils/api'
import './GroupsPage.css'

interface Group {
  id: number
  name: string
  semester?: number
  year?: number
}

interface Student {
  id: number
  fio: string
  max_user_id?: number
  is_headman: boolean
}

const GroupsPage: React.FC = () => {
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null)
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadGroups()
  }, [])

  useEffect(() => {
    if (selectedGroup) {
      loadStudents(selectedGroup)
    } else {
      setStudents([])
    }
  }, [selectedGroup])

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

  const loadStudents = async (groupId: number) => {
    try {
      const response = await api.get(`/groups/${groupId}/students`)
      setStudents(response.data)
    } catch (error) {
      console.error('Ошибка загрузки студентов:', error)
    }
  }

  if (loading) {
    return <div className="loading">Загрузка групп...</div>
  }

  return (
    <div className="groups-page">
      <h1>Мои группы</h1>

      <div className="groups-container">
        <div className="groups-list">
          <h2>Группы</h2>
          {groups.length === 0 ? (
            <div className="empty-state">Нет групп</div>
          ) : (
            <div className="groups-grid">
              {groups.map(group => (
                <div
                  key={group.id}
                  className={`group-card ${selectedGroup === group.id ? 'active' : ''}`}
                  onClick={() => setSelectedGroup(group.id)}
                >
                  <div className="group-name">{group.name}</div>
                  {group.semester && group.year && (
                    <div className="group-info">
                      {group.semester} семестр, {group.year}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedGroup && (
          <div className="students-list">
            <h2>Студенты</h2>
            {students.length === 0 ? (
              <div className="empty-state">Нет студентов в группе</div>
            ) : (
              <div className="students-grid">
                {students.map(student => (
                  <div key={student.id} className="student-card">
                    {student.is_headman && <span className="headman-badge">⭐</span>}
                    <div className="student-name">{student.fio}</div>
                    {student.max_user_id && (
                      <a
                        href={`max://user/${student.max_user_id}`}
                        className="student-link"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Профиль в Max
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default GroupsPage

