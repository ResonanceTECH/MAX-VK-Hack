import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../../utils/api'
import './GroupStudentsPage.css'

interface Student {
  id: number
  fio: string
  max_user_id?: number
  phone?: string
  email?: string
  is_headman: boolean
}

const GroupStudentsPage: React.FC = () => {
  const { groupId } = useParams<{ groupId: string }>()
  const navigate = useNavigate()
  const [students, setStudents] = useState<Student[]>([])
  const [groupName, setGroupName] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (groupId) {
      loadGroupData(parseInt(groupId))
    }
  }, [groupId])

  const loadGroupData = async (id: number) => {
    try {
      setLoading(true)
      // Получаем группы преподавателя для получения названия
      const groupsResponse = await api.get('/groups')
      const groups = groupsResponse.data
      const group = groups.find((g: any) => g.id === id)
      
      if (group) {
        setGroupName(group.name)
      }
      
      // Получаем студентов группы
      const studentsResponse = await api.get(`/groups/${id}/students`)
      setStudents(studentsResponse.data)
    } catch (error) {
      console.error('Ошибка загрузки данных группы:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Загрузка...</div>
  }

  return (
    <div className="group-students-page">
      <button className="back-button" onClick={() => navigate('/my-groups')}>
        ← Назад к группам
      </button>
      <h1>Группа: {groupName}</h1>
      
      <div className="students-list">
        {students.length === 0 ? (
          <div className="empty-state">
            <p>В группе нет студентов</p>
          </div>
        ) : (
          <table className="students-table">
            <thead>
              <tr>
                <th>ФИО</th>
                <th>Телефон</th>
                <th>Email</th>
                <th>Статус</th>
                <th>Профиль</th>
              </tr>
            </thead>
            <tbody>
              {students.map(student => (
                <tr key={student.id}>
                  <td>{student.fio}</td>
                  <td>{student.phone || '-'}</td>
                  <td>{student.email || '-'}</td>
                  <td>{student.is_headman ? '⭐ Староста' : 'Студент'}</td>
                  <td>
                    {student.max_user_id ? (
                      <a 
                        href={`max://user/${student.max_user_id}`}
                        className="max-profile-link"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        👤 Профиль
                      </a>
                    ) : (
                      '-'
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default GroupStudentsPage

