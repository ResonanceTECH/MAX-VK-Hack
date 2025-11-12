import React, { useEffect, useState } from 'react'
import api from '../../../utils/api'
import './TeachersPage.css'

// Иконки в стиле Hugeicons
const PhoneIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 5C3 3.89543 3.89543 3 5 3H8.27924C8.70967 3 9.09181 3.27543 9.22792 3.68377L10.7257 8.17721C10.8831 8.64932 10.6694 9.16531 10.2243 9.38787L7.96701 10.5165C9.06925 12.9612 11.0388 14.9308 13.4835 16.033L14.6121 13.7757C14.8347 13.3306 15.3507 13.1169 15.8228 13.2743L20.3162 14.7721C20.7246 14.9082 21 15.2903 21 15.7208V19C21 20.1046 20.1046 21 19 21H18C9.71573 21 3 14.2843 3 6V5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const MailIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 8L10.89 13.26C11.2187 13.4793 11.6049 13.5963 12 13.5963C12.3951 13.5963 12.7813 13.4793 13.11 13.26L21 8M5 19H19C20.1046 19 21 18.1046 21 17V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V17C3 18.1046 3.89543 19 5 19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const UserIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

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
        return (
            <div className="teachers-page">
                <h1>Преподаватели</h1>
                <div className="loading">
                    <div className="loading-spinner"></div>
                    <p>Загрузка преподавателей...</p>
                </div>
            </div>
        )
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
                                <div className="teacher-contacts">
                                    {teacher.phone && (
                                        <div className="contact-item">
                                            <PhoneIcon size={18} />
                                            <span>{teacher.phone}</span>
                                        </div>
                                    )}
                                    {teacher.email && (
                                        <div className="contact-item">
                                            <MailIcon size={18} />
                                            <span>{teacher.email}</span>
                                        </div>
                                    )}
                                    {teacher.max_user_id && (
                                        <div className="contact-item">
                                            <UserIcon size={18} />
                                            <a
                                                href={`max://user/${teacher.max_user_id}`}
                                                className="max-profile-link"
                                                target="_blank"
                                                rel="noopener noreferrer"
                                            >
                                                Профиль в Max
                                            </a>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}

export default TeachersPage

