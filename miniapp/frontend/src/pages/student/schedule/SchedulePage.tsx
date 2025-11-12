import React, { useEffect, useState } from 'react'
import { Calendar, UserCircle2, MapPin } from 'lucide-react'
import './SchedulePage.css'

interface Event {
    summary: string
    start: string
    end: string
    day_of_week: string
    description: string
    location: string
    week_parity: string
}

interface ScheduleData {
    events_by_calname: {
        [key: string]: Event[]
    }
}

const SchedulePage: React.FC = () => {
    const [schedule, setSchedule] = useState<Event[]>([])
    const [groupName, setGroupName] = useState<string>('')
    const [loading, setLoading] = useState(true)
    const [selectedWeekParity, setSelectedWeekParity] = useState<'четная' | 'нечетная'>('нечетная')

    useEffect(() => {
        loadSchedule()
    }, [])

    const loadSchedule = async () => {
        try {
            setLoading(true)
            // Моковые данные для демонстрации
            const mockData: ScheduleData = {
                events_by_calname: {
                    'ИКБО-16-22': [
                        {
                            summary: 'ПР Информационный менеджмент программных продуктов и систем',
                            start: '09:00',
                            end: '10:30',
                            day_of_week: 'Понедельник',
                            description: 'Преподаватель: Братусь Надежда Валерьевна\n',
                            location: 'И-205-а (В-78)',
                            week_parity: 'нечетная'
                        },
                        {
                            summary: 'ПР Информационный менеджмент программных продуктов и систем',
                            start: '10:40',
                            end: '12:10',
                            day_of_week: 'Понедельник',
                            description: 'Преподаватель: Братусь Надежда Валерьевна\n',
                            location: 'И-205-а (В-78)',
                            week_parity: 'нечетная'
                        },
                        {
                            summary: 'ЛК Управление информационно-технологическими проектами',
                            start: '18:00',
                            end: '19:30',
                            day_of_week: 'Понедельник',
                            description: 'Преподаватель: Потапова Ксения Александровна\n',
                            location: 'Дистанционно (СДО)',
                            week_parity: 'нечетная'
                        },
                        {
                            summary: 'ПР Имитационное моделирование клиент-серверных приложений',
                            start: '09:00',
                            end: '10:30',
                            day_of_week: 'Среда',
                            description: 'Преподаватель: Коваленко Михаил Андреевич\n',
                            location: 'Г-227-1 (В-78)',
                            week_parity: 'нечетная'
                        },
                        {
                            summary: 'ПР Имитационное моделирование клиент-серверных приложений',
                            start: '10:40',
                            end: '12:10',
                            day_of_week: 'Среда',
                            description: 'Преподаватель: Коваленко Михаил Андреевич\n',
                            location: 'Г-227-1 (В-78)',
                            week_parity: 'нечетная'
                        },
                        {
                            summary: 'ПР Проектирование клиент-серверных систем',
                            start: '09:00',
                            end: '10:30',
                            day_of_week: 'Четверг',
                            description: 'Преподаватель: Мельников Денис Александрович\n',
                            location: 'И-203-б (В-78)',
                            week_parity: 'нечетная'
                        },
                        {
                            summary: 'ПР Проектирование клиент-серверных систем',
                            start: '10:40',
                            end: '12:10',
                            day_of_week: 'Четверг',
                            description: 'Преподаватель: Мельников Денис Александрович\n',
                            location: 'И-203-б (В-78)',
                            week_parity: 'нечетная'
                        },
                        {
                            summary: 'ПР Информационный менеджмент программных продуктов и систем',
                            start: '12:40',
                            end: '14:10',
                            day_of_week: 'Четверг',
                            description: 'Преподаватель: Братусь Надежда Валерьевна\n',
                            location: 'Г-226-2 (В-78)',
                            week_parity: 'нечетная'
                        },
                        {
                            summary: 'ПР Управление информационно-технологическими проектами',
                            start: '12:40',
                            end: '14:10',
                            day_of_week: 'Четверг',
                            description: 'Преподаватель: Габриелян Гайк Ашотович\n',
                            location: 'Д-313 (В-78)',
                            week_parity: 'нечетная'
                        },
                        {
                            summary: 'ПР Разработка клиент-серверных приложений',
                            start: '09:00',
                            end: '10:30',
                            day_of_week: 'Пятница',
                            description: 'Преподаватель: Романченко Алексей Евгеньевич\n',
                            location: 'Г-226-2 (В-78)',
                            week_parity: 'нечетная'
                        },
                        {
                            summary: 'ПР Разработка клиент-серверных приложений',
                            start: '10:40',
                            end: '12:10',
                            day_of_week: 'Пятница',
                            description: 'Преподаватель: Романченко Алексей Евгеньевич\n',
                            location: 'Г-226-2 (В-78)',
                            week_parity: 'нечетная'
                        }
                    ]
                }
            }

            const firstGroupName = Object.keys(mockData.events_by_calname)[0]
            setGroupName(firstGroupName)
            setSchedule(mockData.events_by_calname[firstGroupName])
        } catch (error) {
            console.error('Ошибка загрузки расписания:', error)
        } finally {
            setLoading(false)
        }
    }

    const getClassType = (summary: string): string => {
        if (summary.startsWith('ЛК')) return 'lecture'
        if (summary.startsWith('ПР')) return 'practice'
        if (summary.startsWith('ЛБ')) return 'lab'
        return 'other'
    }

    const getClassTypeLabel = (summary: string): string => {
        if (summary.startsWith('ЛК')) return 'Лекция'
        if (summary.startsWith('ПР')) return 'Практика'
        if (summary.startsWith('ЛБ')) return 'Лабораторная'
        return 'Занятие'
    }

    const extractTeacher = (description: string): string => {
        const match = description.match(/Преподаватель: (.+)/);
        return match ? match[1].trim() : 'Не указан'
    }

    const cleanSummary = (summary: string): string => {
        return summary.replace(/^(ЛК|ПР|ЛБ)\s+/, '')
    }

    const daysOfWeek = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

    const groupByDay = () => {
        const grouped: { [key: string]: Event[] } = {}

        schedule
            .filter(event => event.week_parity === selectedWeekParity)
            .forEach(event => {
                if (!grouped[event.day_of_week]) {
                    grouped[event.day_of_week] = []
                }
                grouped[event.day_of_week].push(event)
            })

        // Сортируем по времени внутри каждого дня
        Object.keys(grouped).forEach(day => {
            grouped[day].sort((a, b) => a.start.localeCompare(b.start))
        })

        return grouped
    }

    if (loading) {
        return (
            <div className="schedule-page">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Загрузка расписания...</p>
                </div>
            </div>
        )
    }

    const groupedSchedule = groupByDay()

    return (
        <div className="schedule-page">
            <div className="schedule-header">
                <div className="header-content">
                    <h1>
                        <Calendar className="header-icon" size={32} strokeWidth={2.5} />
                        Расписание
                    </h1>
                    <p className="group-name">{groupName}</p>
                </div>

                <div className="week-selector">
                    <button
                        className={`week-btn ${selectedWeekParity === 'нечетная' ? 'active' : ''}`}
                        onClick={() => setSelectedWeekParity('нечетная')}
                    >
                        Нечетная неделя
                    </button>
                    <button
                        className={`week-btn ${selectedWeekParity === 'четная' ? 'active' : ''}`}
                        onClick={() => setSelectedWeekParity('четная')}
                    >
                        Четная неделя
                    </button>
                </div>
            </div>

            <div className="schedule-content">
                {daysOfWeek.map(day => {
                    const dayEvents = groupedSchedule[day]

                    if (!dayEvents || dayEvents.length === 0) {
                        return null
                    }

                    return (
                        <div key={day} className="day-section">
                            <div className="day-header">
                                <h2>{day}</h2>
                                <span className="lessons-count">{dayEvents.length} пар</span>
                            </div>

                            <div className="lessons-list">
                                {dayEvents.map((event, index) => (
                                    <div
                                        key={index}
                                        className={`schedule-card ${getClassType(event.summary)}`}
                                    >
                                        <div className="card-header">
                                            <div className="time-block">
                                                <span className="time-start">{event.start}</span>
                                                <span className="time-separator">—</span>
                                                <span className="time-end">{event.end}</span>
                                            </div>
                                            <span className={`class-type-badge ${getClassType(event.summary)}`}>
                                                {getClassTypeLabel(event.summary)}
                                            </span>
                                        </div>

                                        <h3 className="lesson-title">{cleanSummary(event.summary)}</h3>

                                        <div className="lesson-details">
                                            <div className="detail-item">
                                                <UserCircle2 className="icon" size={18} strokeWidth={2} />
                                                <span className="text">{extractTeacher(event.description)}</span>
                                            </div>
                                            <div className="detail-item">
                                                <MapPin className="icon" size={18} strokeWidth={2} />
                                                <span className="text">{event.location}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )
                })}

                {Object.keys(groupedSchedule).length === 0 && (
                    <div className="empty-state">
                        <div className="empty-icon">📭</div>
                        <h3>Нет занятий</h3>
                        <p>На {selectedWeekParity} неделе занятий не найдено</p>
                    </div>
                )}
            </div>
        </div>
    )
}

export default SchedulePage
