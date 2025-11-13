import React, { useState } from 'react'
import api from '../../../utils/api'
import './NewsPage.css'

// Иконки в стиле Hugeicons
const NewsIcon = ({ size = 18 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M19 20H5C4.46957 20 3.96086 19.7893 3.58579 19.4142C3.21071 19.0391 3 18.5304 3 18V6C3 5.46957 3.21071 4.96086 3.58579 4.58579C3.96086 4.21071 4.46957 4 5 4H15C15.5304 4 16.0391 4.21071 16.4142 4.58579C16.7893 4.96086 17 5.46957 17 6V18C17 18.5304 16.7893 19.0391 16.4142 19.4142C16.0391 19.7893 15.5304 20 15 20H19M19 20C19.5304 20 20.0391 19.7893 20.4142 19.4142C20.7893 19.0391 21 18.5304 21 18V8C21 7.46957 20.7893 6.96086 20.4142 6.58579C20.0391 6.21071 19.5304 6 19 6M19 20V6M7 8H13M7 12H15M7 16H11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const AdminNewsPage: React.FC = () => {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        hashtags: '',
        target_role: 'all'
    })

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            await api.post('/admin/news', formData)
            alert('Новость создана!')
            setFormData({
                title: '',
                description: '',
                hashtags: '',
                target_role: 'all'
            })
        } catch (error) {
            console.error('Ошибка создания новости:', error)
            alert('Ошибка создания новости')
        }
    }

    return (
        <div className="admin-news-page">
            <h1>Создание новостей</h1>

            <form onSubmit={handleSubmit} className="news-form">
                <div className="form-group">
                    <label>Заголовок:</label>
                    <input
                        type="text"
                        value={formData.title}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                        required
                        placeholder="Введите заголовок новости"
                    />
                </div>

                <div className="form-group">
                    <label>Описание:</label>
                    <textarea
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        required
                        rows={6}
                        placeholder="Введите описание новости"
                    />
                </div>

                <div className="form-group">
                    <label>Хэштеги (через запятую):</label>
                    <input
                        type="text"
                        value={formData.hashtags}
                        onChange={(e) => setFormData({ ...formData, hashtags: e.target.value })}
                        placeholder="например: новости, объявления, важное"
                    />
                </div>

                <div className="form-group">
                    <label>Целевая аудитория:</label>
                    <select
                        value={formData.target_role}
                        onChange={(e) => setFormData({ ...formData, target_role: e.target.value })}
                    >
                        <option value="all">Все</option>
                        <option value="student">Студенты</option>
                        <option value="teacher">Преподаватели</option>
                    </select>
                </div>

                <button type="submit" className="submit-button">
                    <NewsIcon size={18} />
                    Создать новость
                </button>
            </form>
        </div>
    )
}

export default AdminNewsPage

