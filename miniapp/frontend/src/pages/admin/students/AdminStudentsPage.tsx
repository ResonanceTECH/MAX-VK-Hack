import React, { useEffect, useState } from 'react'
import api from '../../../utils/api'
import './StudentsPage.css'

interface Student {
    id: number
    fio: string
    max_user_id?: number
    phone?: string
    email?: string
}

const AdminStudentsPage: React.FC = () => {
    const [students, setStudents] = useState<Student[]>([])
    const [loading, setLoading] = useState(true)
    const [showForm, setShowForm] = useState(false)
    const [editingStudent, setEditingStudent] = useState<Student | null>(null)
    const [formData, setFormData] = useState({
        max_user_id: '',
        fio: '',
        phone: '',
        email: ''
    })

    useEffect(() => {
        loadStudents()
    }, [])

    const loadStudents = async () => {
        try {
            setLoading(true)
            const response = await api.get('/admin/students')
            setStudents(response.data)
        } catch (error) {
            console.error('Ошибка загрузки студентов:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            if (editingStudent) {
                await api.put(`/admin/students/${editingStudent.id}`, formData)
            } else {
                await api.post('/admin/students', {
                    ...formData,
                    max_user_id: parseInt(formData.max_user_id)
                })
            }
            setShowForm(false)
            setEditingStudent(null)
            setFormData({ max_user_id: '', fio: '', phone: '', email: '' })
            loadStudents()
        } catch (error) {
            console.error('Ошибка сохранения:', error)
            alert('Ошибка сохранения студента')
        }
    }

    const handleEdit = (student: Student) => {
        setEditingStudent(student)
        setFormData({
            max_user_id: student.max_user_id?.toString() || '',
            fio: student.fio,
            phone: student.phone || '',
            email: student.email || ''
        })
        setShowForm(true)
    }

    const handleDelete = async (id: number) => {
        if (!confirm('Удалить студента?')) return
        try {
            await api.delete(`/admin/students/${id}`)
            loadStudents()
        } catch (error) {
            console.error('Ошибка удаления:', error)
            alert('Ошибка удаления студента')
        }
    }

    if (loading) {
        return <div className="loading">Загрузка...</div>
    }

    return (
        <div className="admin-students-page">
            <div className="page-header">
                <h1>Управление студентами</h1>
                <button onClick={() => {
                    setShowForm(true)
                    setEditingStudent(null)
                    setFormData({ max_user_id: '', fio: '', phone: '', email: '' })
                }}>
                    ➕ Добавить студента
                </button>
            </div>

            {showForm && (
                <div className="form-modal">
                    <div className="form-content">
                        <h2>{editingStudent ? 'Редактировать' : 'Добавить'} студента</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label>Max User ID:</label>
                                <input
                                    type="number"
                                    value={formData.max_user_id}
                                    onChange={(e) => setFormData({ ...formData, max_user_id: e.target.value })}
                                    required
                                    disabled={!!editingStudent}
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
                                    setEditingStudent(null)
                                }}>Отмена</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <table className="students-table">
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
                    {students.map(student => (
                        <tr key={student.id}>
                            <td>{student.id}</td>
                            <td>{student.fio}</td>
                            <td>{student.max_user_id || '-'}</td>
                            <td>{student.phone || '-'}</td>
                            <td>{student.email || '-'}</td>
                            <td>
                                <button onClick={() => handleEdit(student)}>✏️</button>
                                <button onClick={() => handleDelete(student.id)}>🗑️</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default AdminStudentsPage

