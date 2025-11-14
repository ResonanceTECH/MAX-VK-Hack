import React, { useEffect, useState } from 'react'
import api from '../../../utils/api'
import LoadingSpinner from '../../../components/LoadingSpinner'
import './StudentsPage.css'

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
        return (
            <div className="admin-students-page">
                <LoadingSpinner text="Загрузка..." />
            </div>
        )
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
                    <PlusIcon size={16} />
                    Добавить студента
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

            {/* Таблица для десктопа */}
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
                                <button onClick={() => handleEdit(student)}>
                                    <EditIcon size={16} />
                                </button>
                                <button onClick={() => handleDelete(student.id)}>
                                    <DeleteIcon size={16} />
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Карточки для мобильных устройств */}
            <div className="students-cards">
                {students.map(student => (
                    <div key={student.id} className="student-card">
                        <div className="student-card-header">
                            <div className="student-card-id">ID: {student.id}</div>
                            <h3 className="student-card-name">{student.fio}</h3>
                        </div>
                        <div className="student-card-body">
                            <div className="student-card-field">
                                <span className="field-label">Max User ID:</span>
                                <span className="field-value">{student.max_user_id || '-'}</span>
                            </div>
                            <div className="student-card-field">
                                <span className="field-label">Телефон:</span>
                                <span className="field-value">{student.phone || '-'}</span>
                            </div>
                            <div className="student-card-field">
                                <span className="field-label">Email:</span>
                                <span className="field-value">{student.email || '-'}</span>
                            </div>
                        </div>
                        <div className="student-card-actions">
                            <button 
                                className="btn-edit-card"
                                onClick={() => handleEdit(student)}
                            >
                                <EditIcon size={16} />
                                Редактировать
                            </button>
                            <button 
                                className="btn-delete-card"
                                onClick={() => handleDelete(student.id)}
                            >
                                <DeleteIcon size={16} />
                                Удалить
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default AdminStudentsPage

