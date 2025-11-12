import React, { useEffect, useState } from 'react'
import api from '../../../utils/api'
import './TeachersPage.css'

interface Teacher {
    id: number
    fio: string
    max_user_id?: number
    phone?: string
    email?: string
}

const AdminTeachersPage: React.FC = () => {
    const [teachers, setTeachers] = useState<Teacher[]>([])
    const [loading, setLoading] = useState(true)
    const [showForm, setShowForm] = useState(false)
    const [editingTeacher, setEditingTeacher] = useState<Teacher | null>(null)
    const [formData, setFormData] = useState({
        max_user_id: '',
        fio: '',
        phone: '',
        email: ''
    })

    useEffect(() => {
        loadTeachers()
    }, [])

    const loadTeachers = async () => {
        try {
            setLoading(true)
            const response = await api.get('/admin/teachers')
            setTeachers(response.data)
        } catch (error) {
            console.error('Ошибка загрузки преподавателей:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            if (editingTeacher) {
                await api.put(`/admin/teachers/${editingTeacher.id}`, formData)
            } else {
                await api.post('/admin/teachers', {
                    ...formData,
                    max_user_id: parseInt(formData.max_user_id)
                })
            }
            setShowForm(false)
            setEditingTeacher(null)
            setFormData({ max_user_id: '', fio: '', phone: '', email: '' })
            loadTeachers()
        } catch (error) {
            console.error('Ошибка сохранения:', error)
            alert('Ошибка сохранения преподавателя')
        }
    }

    const handleEdit = (teacher: Teacher) => {
        setEditingTeacher(teacher)
        setFormData({
            max_user_id: teacher.max_user_id?.toString() || '',
            fio: teacher.fio,
            phone: teacher.phone || '',
            email: teacher.email || ''
        })
        setShowForm(true)
    }

    const handleDelete = async (id: number) => {
        if (!confirm('Удалить преподавателя?')) return
        try {
            await api.delete(`/admin/teachers/${id}`)
            loadTeachers()
        } catch (error) {
            console.error('Ошибка удаления:', error)
            alert('Ошибка удаления преподавателя')
        }
    }

    if (loading) {
        return <div className="loading">Загрузка...</div>
    }

    return (
        <div className="admin-teachers-page">
            <div className="page-header">
                <h1>Управление преподавателями</h1>
                <button onClick={() => {
                    setShowForm(true)
                    setEditingTeacher(null)
                    setFormData({ max_user_id: '', fio: '', phone: '', email: '' })
                }}>
                    ➕ Добавить преподавателя
                </button>
            </div>

            {showForm && (
                <div className="form-modal">
                    <div className="form-content">
                        <h2>{editingTeacher ? 'Редактировать' : 'Добавить'} преподавателя</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label>Max User ID:</label>
                                <input
                                    type="number"
                                    value={formData.max_user_id}
                                    onChange={(e) => setFormData({ ...formData, max_user_id: e.target.value })}
                                    required
                                    disabled={!!editingTeacher}
                                />
                            </div>
                            <div className="form-group">
                                <label>ФИО:</label>
                                <input
                                    type="text"
                                    value={formData.fio}
                                    onChange={(e) => setFormData({ ...formData, fio: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Телефон:</label>
                                <input
                                    type="text"
                                    value={formData.phone}
                                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label>Email:</label>
                                <input
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                />
                            </div>
                            <div className="form-actions">
                                <button type="submit">Сохранить</button>
                                <button type="button" onClick={() => {
                                    setShowForm(false)
                                    setEditingTeacher(null)
                                }}>Отмена</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <table className="teachers-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>ФИО</th>
                        <th>Max User ID</th>
                        <th>Телефон</th>
                        <th>Email</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {teachers.map(teacher => (
                        <tr key={teacher.id}>
                            <td>{teacher.id}</td>
                            <td>{teacher.fio}</td>
                            <td>{teacher.max_user_id || '-'}</td>
                            <td>{teacher.phone || '-'}</td>
                            <td>{teacher.email || '-'}</td>
                            <td>
                                <button onClick={() => handleEdit(teacher)}>✏️</button>
                                <button onClick={() => handleDelete(teacher.id)}>🗑️</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default AdminTeachersPage

