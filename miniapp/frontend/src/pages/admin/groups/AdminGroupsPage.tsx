import React, { useEffect, useState } from 'react'
import api from '../../../utils/api'
import './GroupsPage.css'

// Иконки в стиле Hugeicons
const PlusIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const EditIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13M18.5 2.5C18.8978 2.10217 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10217 21.5 2.5C21.8978 2.89782 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.10217 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const DeleteIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 6H5H21M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const UsersIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88M13 7C13 9.20914 11.2091 11 9 11C6.79086 11 5 9.20914 5 7C5 4.79086 6.79086 3 9 3C11.2091 3 13 4.79086 13 7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

interface Group {
    id: number
    name: string
    semester?: number
    year?: number
}

interface Student {
    id: number
    fio: string
    is_headman: boolean
}

const AdminGroupsPage: React.FC = () => {
    const [groups, setGroups] = useState<Group[]>([])
    const [selectedGroup, setSelectedGroup] = useState<Group | null>(null)
    const [students, setStudents] = useState<Student[]>([])
    const [allStudents, setAllStudents] = useState<Student[]>([])
    const [loading, setLoading] = useState(true)
    const [showCreateForm, setShowCreateForm] = useState(false)
    const [showEditForm, setShowEditForm] = useState(false)
    const [formData, setFormData] = useState({ name: '', semester: '', year: '' })
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

    useEffect(() => {
        loadGroups()
        loadAllStudents()
    }, [])

    useEffect(() => {
        if (selectedGroup) {
            loadGroupStudents(selectedGroup.id)
        }
    }, [selectedGroup])

    const loadGroups = async () => {
        try {
            setLoading(true)
            const response = await api.get('/admin/groups')
            setGroups(response.data)
            if (response.data.length > 0 && !selectedGroup) {
                setSelectedGroup(response.data[0])
            }
        } catch (error) {
            console.error('Ошибка загрузки групп:', error)
        } finally {
            setLoading(false)
        }
    }

    const loadAllStudents = async () => {
        try {
            const response = await api.get('/admin/students')
            setAllStudents(response.data)
        } catch (error) {
            console.error('Ошибка загрузки студентов:', error)
        }
    }

    const loadGroupStudents = async (groupId: number) => {
        try {
            const response = await api.get(`/groups/${groupId}/students`)
            setStudents(response.data)
        } catch (error) {
            console.error('Ошибка загрузки студентов группы:', error)
        }
    }

    const showToast = (message: string, type: 'success' | 'error' = 'success') => {
        setToast({ message, type })
        setTimeout(() => setToast(null), 3000)
    }

    const handleAddStudent = async (studentId: number) => {
        if (!selectedGroup) return
        try {
            await api.post(`/admin/groups/${selectedGroup.id}/students/${studentId}`)
            loadGroupStudents(selectedGroup.id)
            showToast('Студент успешно добавлен в группу')
        } catch (error) {
            console.error('Ошибка добавления студента:', error)
            showToast('Ошибка добавления студента', 'error')
        }
    }

    const handleRemoveStudent = async (studentId: number) => {
        if (!selectedGroup) return
        if (!confirm('Удалить студента из группы?')) return
        try {
            await api.delete(`/admin/groups/${selectedGroup.id}/students/${studentId}`)
            loadGroupStudents(selectedGroup.id)
            showToast('Студент удален из группы')
        } catch (error) {
            console.error('Ошибка удаления студента:', error)
            showToast('Ошибка удаления студента', 'error')
        }
    }

    const handleSetHeadman = async (studentId: number) => {
        if (!selectedGroup) return
        try {
            await api.put(`/admin/groups/${selectedGroup.id}/headman/${studentId}`)
            loadGroupStudents(selectedGroup.id)
            showToast('Староста успешно назначен')
        } catch (error) {
            console.error('Ошибка назначения старосты:', error)
            showToast('Ошибка назначения старосты', 'error')
        }
    }

    const handleCreateGroup = async () => {
        try {
            const data: any = { name: formData.name }
            if (formData.semester) data.semester = parseInt(formData.semester)
            if (formData.year) data.year = parseInt(formData.year)

            await api.post('/admin/groups', data)
            setShowCreateForm(false)
            setFormData({ name: '', semester: '', year: '' })
            loadGroups()
            showToast('Группа успешно создана')
        } catch (error: any) {
            console.error('Ошибка создания группы:', error)
            showToast(error.response?.data?.detail || 'Ошибка создания группы', 'error')
        }
    }

    const handleEditGroup = async () => {
        if (!selectedGroup) return
        try {
            const data: any = {}
            if (formData.name) data.name = formData.name
            if (formData.semester) data.semester = parseInt(formData.semester)
            if (formData.year) data.year = parseInt(formData.year)

            await api.put(`/admin/groups/${selectedGroup.id}`, data)
            setShowEditForm(false)
            setFormData({ name: '', semester: '', year: '' })
            loadGroups()
            // Обновляем выбранную группу
            const updatedGroups = await api.get('/admin/groups')
            const updated = updatedGroups.data.find((g: Group) => g.id === selectedGroup.id)
            if (updated) setSelectedGroup(updated)
            showToast('Группа успешно обновлена')
        } catch (error: any) {
            console.error('Ошибка обновления группы:', error)
            showToast(error.response?.data?.detail || 'Ошибка обновления группы', 'error')
        }
    }

    const handleDeleteGroup = async (groupId: number) => {
        if (!confirm('Удалить группу? Это действие нельзя отменить.')) return
        try {
            await api.delete(`/admin/groups/${groupId}`)
            if (selectedGroup?.id === groupId) {
                setSelectedGroup(null)
            }
            loadGroups()
            showToast('Группа успешно удалена')
        } catch (error: any) {
            console.error('Ошибка удаления группы:', error)
            showToast(error.response?.data?.detail || 'Ошибка удаления группы', 'error')
        }
    }

    const openEditForm = (group: Group) => {
        setFormData({
            name: group.name || '',
            semester: group.semester?.toString() || '',
            year: group.year?.toString() || ''
        })
        setShowEditForm(true)
    }

    const availableStudents = allStudents.filter(
        s => !students.some(gs => gs.id === s.id)
    )

    if (loading) {
        return <div className="loading">Загрузка данных...</div>
    }

    return (
        <div className="admin-groups-page">
            {toast && (
                <div className={`toast ${toast.type}`}>
                    {toast.message}
                </div>
            )}

            <h1>Управление группами</h1>

            <div className="groups-layout">
                <div className="groups-sidebar">
                    <div className="groups-header">
                        <h2>Группы</h2>
                        <button
                            className="btn-create"
                            onClick={() => {
                                setShowCreateForm(true)
                                setFormData({ name: '', semester: '', year: '' })
                            }}
                        >
                            <PlusIcon size={16} />
                            Создать
                        </button>
                    </div>
                    <div className="groups-list">
                        {groups.map(group => (
                            <div
                                key={group.id}
                                className={`group-item ${selectedGroup?.id === group.id ? 'active' : ''}`}
                            >
                                <div
                                    className="group-item-content"
                                    onClick={() => setSelectedGroup(group)}
                                >
                                    {group.name}
                                </div>
                                <div className="group-item-actions">
                                    <button
                                        className="btn-edit"
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            setSelectedGroup(group)
                                            openEditForm(group)
                                        }}
                                        title="Редактировать"
                                    >
                                        <EditIcon size={16} />
                                    </button>
                                    <button
                                        className="btn-delete"
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            handleDeleteGroup(group.id)
                                        }}
                                        title="Удалить"
                                    >
                                        <DeleteIcon size={16} />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="groups-content">
                    {selectedGroup ? (
                        <>
                            <h2>Группа: {selectedGroup.name}</h2>

                            <div className="students-section">
                                <h3>
                                    <UsersIcon size={20} />
                                    Студенты в группе
                                </h3>
                                <table className="students-table">
                                    <thead>
                                        <tr>
                                            <th>ФИО</th>
                                            <th>Статус</th>
                                            <th>Действия</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {students.map(student => (
                                            <tr key={student.id}>
                                                <td>{student.fio}</td>
                                                <td>{student.is_headman ? '⭐ Староста' : 'Студент'}</td>                                                       
                                                <td>
                                                    {!student.is_headman && (   
                                                        <button
                                                            className="btn-set-headman"                                                                         
                                                            onClick={() => handleSetHeadman(student.id)}                                                        
                                                        >
                                                            Назначить старостой
                                                        </button>
                                                    )}
                                                    <button
                                                        className="btn-delete-student"                                                                          
                                                        onClick={() => handleRemoveStudent(student.id)}                                                         
                                                    >
                                                        Удалить
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                
                                {/* Карточки студентов для мобильных */}
                                <div className="students-cards">
                                    {students.map(student => (
                                        <div key={student.id} className="student-card">
                                            <div className="student-card-header">
                                                <div className="student-card-name">{student.fio}</div>
                                            </div>
                                            <div className="student-card-body">
                                                <div className="student-card-field">
                                                    <span className="field-label">Статус:</span>
                                                    <span className="field-value">
                                                        {student.is_headman ? '⭐ Староста' : 'Студент'}
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="student-card-actions">
                                                {!student.is_headman && (
                                                    <button
                                                        className="btn-set-headman-card"
                                                        onClick={() => handleSetHeadman(student.id)}
                                                    >
                                                        Назначить старостой
                                                    </button>
                                                )}
                                                <button
                                                    className="btn-delete-student-card"
                                                    onClick={() => handleRemoveStudent(student.id)}
                                                >
                                                    Удалить
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="add-student-section">
                                <h3>Добавить студента</h3>
                                <select
                                    onChange={(e) => {
                                        if (e.target.value) {
                                            handleAddStudent(parseInt(e.target.value))
                                            e.target.value = ''
                                        }
                                    }}
                                >
                                    <option value="">Выберите студента...</option>
                                    {availableStudents.map(student => (
                                        <option key={student.id} value={student.id}>
                                            {student.fio}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </>
                    ) : (
                        <p>Выберите группу</p>
                    )}
                </div>
            </div>

            {/* Модальное окно создания группы */}
            {showCreateForm && (
                <div className="modal-overlay" onClick={() => setShowCreateForm(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Создать группу</h2>
                        <div className="form-group">
                            <label>Название группы *</label>
                            <input
                                type="text"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                placeholder="Например: ИС-21"
                            />
                        </div>
                        <div className="form-group">
                            <label>Семестр</label>
                            <input
                                type="number"
                                value={formData.semester}
                                onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                                placeholder="Например: 1"
                                min="1"
                                max="12"
                            />
                        </div>
                        <div className="form-group">
                            <label>Год</label>
                            <input
                                type="number"
                                value={formData.year}
                                onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                                placeholder="Например: 2024"
                                min="2000"
                                max="2100"
                            />
                        </div>
                        <div className="modal-actions">
                            <button className="btn-cancel" onClick={() => setShowCreateForm(false)}>
                                Отмена
                            </button>
                            <button className="btn-save" onClick={handleCreateGroup}>
                                Создать
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Модальное окно редактирования группы */}
            {showEditForm && selectedGroup && (
                <div className="modal-overlay" onClick={() => setShowEditForm(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Редактировать группу</h2>
                        <div className="form-group">
                            <label>Название группы</label>
                            <input
                                type="text"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                placeholder={selectedGroup.name}
                            />
                        </div>
                        <div className="form-group">
                            <label>Семестр</label>
                            <input
                                type="number"
                                value={formData.semester}
                                onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                                placeholder={selectedGroup.semester?.toString() || ''}
                                min="1"
                                max="12"
                            />
                        </div>
                        <div className="form-group">
                            <label>Год</label>
                            <input
                                type="number"
                                value={formData.year}
                                onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                                placeholder={selectedGroup.year?.toString() || ''}
                                min="2000"
                                max="2100"
                            />
                        </div>
                        <div className="modal-actions">
                            <button className="btn-cancel" onClick={() => setShowEditForm(false)}>
                                Отмена
                            </button>
                            <button className="btn-save" onClick={handleEditGroup}>
                                Сохранить
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default AdminGroupsPage

