import React, { useEffect, useState } from 'react'
import api from '../../../utils/api'
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
                            + Создать
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
                                        ✏️
                                    </button>
                                    <button
                                        className="btn-delete"
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            handleDeleteGroup(group.id)
                                        }}
                                        title="Удалить"
                                    >
                                        🗑️
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
                                <h3>Студенты в группе</h3>
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
                                                        <button onClick={() => handleSetHeadman(student.id)}>
                                                            Назначить старостой
                                                        </button>
                                                    )}
                                                    <button onClick={() => handleRemoveStudent(student.id)}>
                                                        Удалить
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
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

