import React, { useEffect, useState } from 'react'
import api from '../../../utils/api'
import './NewsPage.css'

const CalendarIcon = ({ size = 16 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 2V6M16 2V6M3 10H21M5 4H19C20.1046 4 21 4.89543 21 6V20C21 21.1046 20.1046 22 19 22H5C3.89543 22 3 21.1046 3 20V6C3 4.89543 3.89543 4 5 4Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
        <rect x="6" y="13" width="3" height="3" rx="0.5" fill="currentColor" opacity="0.3"/>
    </svg>
)

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
        return (
            <div className="news-page">
                <h1>Новости</h1>
                <div className="loading">
                    <div className="loading-spinner"></div>
                    <p>Загрузка новостей...</p>
                </div>
            </div>
        )
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
                                <CalendarIcon size={16} />
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

