import React, { useEffect, useState } from 'react'
import api from '../../utils/api'
import './NewsPage.css'

interface News {
  id: number
  title: string
  description: string
  hashtags?: string
  created_at: string
}

const NewsPage: React.FC = () => {
  const [news, setNews] = useState<News[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadNews()
  }, [])

  const loadNews = async () => {
    try {
      setLoading(true)
      const response = await api.get('/news')
      setNews(response.data)
    } catch (error) {
      console.error('Ошибка загрузки новостей:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Загрузка...</div>
  }

  return (
    <div className="news-page">
      <h1>Новости</h1>
      
      <div className="news-list">
        {news.length === 0 ? (
          <div className="empty-state">
            <p>Нет новостей</p>
          </div>
        ) : (
          news.map(item => (
            <div key={item.id} className="news-card">
              <h3>{item.title}</h3>
              {item.hashtags && (
                <div className="hashtags">
                  {item.hashtags.split(',').map((tag, idx) => (
                    <span key={idx} className="hashtag">#{tag.trim()}</span>
                  ))}
                </div>
              )}
              <p>{item.description}</p>
              <div className="news-date">
                {new Date(item.created_at).toLocaleDateString('ru-RU')}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default NewsPage

