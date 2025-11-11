import React, { useState } from 'react'
import api from '../../utils/api'
import './AdminNewsPage.css'

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
          Создать новость
        </button>
      </form>
    </div>
  )
}

export default AdminNewsPage

