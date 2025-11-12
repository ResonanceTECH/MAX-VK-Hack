import React, { useEffect, useState } from 'react'
import api from '../../utils/api'
import './TeachersPage.css'

interface Teacher {
  id: number
  fio: string
  max_user_id?: number
  phone?: string
  email?: string
}

const TeachersPage: React.FC = () => {
  const [teachers, setTeachers] = useState<Teacher[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTeachers()
  }, [])

  const loadTeachers = async () => {
    try {
      setLoading(true)
      const response = await api.get('/teachers')
      setTeachers(response.data)
    } catch (error) {
      console.error('Ошибка загрузки преподавателей:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Загрузка...</div>
  }

  return (
    <div className="teachers-page">
      <h1>Преподаватели</h1>
      
      <div className="teachers-list">
        {teachers.length === 0 ? (
          <div className="empty-state">
            <p>Нет преподавателей</p>
          </div>
        ) : (
          <div className="teachers-grid">
            {teachers.map(teacher => (
              <div key={teacher.id} className="teacher-card">
                <h3>{teacher.fio}</h3>
                {teacher.phone && <p>📞 {teacher.phone}</p>}
                {teacher.email && <p>📧 {teacher.email}</p>}
                {teacher.max_user_id && (
                  <p>
                    <a 
                      href={`max://user/${teacher.max_user_id}`}
                      className="max-profile-link"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      👤 Профиль в Max
                    </a>
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default TeachersPage

