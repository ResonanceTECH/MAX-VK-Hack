import React, { useEffect, useState } from 'react'
import api from '../../utils/api'
import './MyGroupPage.css'

interface GroupMember {
  id: number
  fio: string
  max_user_id?: number
  phone?: string
  email?: string
  is_headman: boolean
}

const MyGroupPage: React.FC = () => {
  const [members, setMembers] = useState<GroupMember[]>([])
  const [groupName, setGroupName] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadGroupData()
  }, [])

  const loadGroupData = async () => {
    try {
      setLoading(true)
      // Получаем группы студента
      const groupsResponse = await api.get('/groups')
      const groups = groupsResponse.data
      
      if (groups && groups.length > 0) {
        const group = groups[0]
        setGroupName(group.name)
        
        // Получаем участников группы
        const membersResponse = await api.get(`/groups/${group.id}/students`)
        setMembers(membersResponse.data)
      }
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
    <div className="my-group-page">
      <h1>Моя группа: {groupName}</h1>
      
      <div className="members-list">
        {members.length === 0 ? (
          <div className="empty-state">
            <p>В группе нет участников</p>
          </div>
        ) : (
          <table className="members-table">
            <thead>
              <tr>
                <th>ФИО</th>
                <th>Телефон</th>
                <th>Email</th>
                <th>Статус</th>
              </tr>
            </thead>
            <tbody>
              {members.map(member => (
                <tr key={member.id}>
                  <td>{member.fio}</td>
                  <td>{member.phone || '-'}</td>
                  <td>{member.email || '-'}</td>
                  <td>{member.is_headman ? '⭐ Староста' : 'Студент'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default MyGroupPage

