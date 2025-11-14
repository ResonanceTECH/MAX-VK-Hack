import React, { useEffect, useState } from 'react'
import api from '../../../utils/api'
import LoadingSpinner from '../../../components/LoadingSpinner'
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

const CopyIcon = ({ size = 16 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 5.00005C7.01165 5.00005 6.49359 5.00005 6.09202 5.21799C5.71569 5.40973 5.40973 5.71569 5.21799 6.09202C5 6.49359 5 7.01165 5 8.00005V16C5 16.9884 5 17.5065 5.21799 17.908C5.40973 18.2843 5.71569 18.5903 6.09202 18.782C6.49359 19 7.01165 19 8 19H16C16.9884 19 17.5065 19 17.908 18.782C18.2843 18.5903 18.5903 18.2843 18.782 17.908C19 17.5065 19 16.9884 19 16V8.00005C19 7.01165 19 6.49359 18.782 6.09202C18.5903 5.71569 18.2843 5.40973 17.908 5.21799C17.5065 5.00005 16.9884 5.00005 16 5.00005H8Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M9 3C8.01165 3 7.49359 3 7.09202 3.21799C6.71569 3.40973 6.40973 3.71569 6.21799 4.09202C6 4.49359 6 5.01165 6 6V8H16C16.9884 8 17.5065 8 17.908 7.78201C18.2843 7.59027 18.5903 7.28431 18.782 6.90798C19 6.50641 19 5.98835 19 5V3H9Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const CheckIcon = ({ size = 16 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
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
    const [copiedId, setCopiedId] = useState<string | null>(null)

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

    const copyToClipboard = async (text: string, id: string) => {
        try {
            await navigator.clipboard.writeText(text)
            setCopiedId(id)
            setTimeout(() => setCopiedId(null), 2000)
        } catch (error) {
            console.error('Ошибка копирования:', error)
        }
    }

    if (loading) {
        return (
            <div className="teachers-page">
                <h1>Преподаватели</h1>
                <LoadingSpinner text="Загрузка преподавателей..." />
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
                                            <button
                                                className="copy-btn"
                                                onClick={() => copyToClipboard(teacher.phone!, `phone-${teacher.id}`)}
                                                title="Копировать"
                                            >
                                                {copiedId === `phone-${teacher.id}` ? (
                                                    <CheckIcon size={16} />
                                                ) : (
                                                    <CopyIcon size={16} />
                                                )}
                                            </button>
                                        </div>
                                    )}
                                    {teacher.email && (
                                        <div className="contact-item">
                                            <MailIcon size={18} />
                                            <span>{teacher.email}</span>
                                            <button
                                                className="copy-btn"
                                                onClick={() => copyToClipboard(teacher.email!, `email-${teacher.id}`)}
                                                title="Копировать"
                                            >
                                                {copiedId === `email-${teacher.id}` ? (
                                                    <CheckIcon size={16} />
                                                ) : (
                                                    <CopyIcon size={16} />
                                                )}
                                            </button>
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

