import React, { useEffect, useState } from 'react'
import { UserCircle2, MapPin, ChevronLeft, ChevronRight, Calendar } from 'lucide-react'
import { mockTeacherSchedule, Event } from './mockSchedule'
import LoadingSpinner from '../../../components/LoadingSpinner'
import '../../student/schedule/SchedulePage.css'

const TeacherSchedulePage: React.FC = () => {
    const [schedule, setSchedule] = useState<Event[]>([])
    const [teacherName, setTeacherName] = useState<string>('')
    const [loading, setLoading] = useState(true)
    const [selectedWeekParity, setSelectedWeekParity] = useState<'четная' | 'нечетная'>('нечетная')
    const [currentWeek, setCurrentWeek] = useState<Date>(new Date())
    const [selectedDay, setSelectedDay] = useState<string | null>(null)

    // Определение текущей недели (четная/нечетная)
    const getCurrentWeekParity = (): 'четная' | 'нечетная' => {
        const startDate = new Date(2024, 8, 1)
        const today = new Date()
        const diffTime = today.getTime() - startDate.getTime()
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
        const weekNumber = Math.floor(diffDays / 7)
        return weekNumber % 2 === 0 ? 'нечетная' : 'четная'
    }

    useEffect(() => {
        const currentParity = getCurrentWeekParity()
        setSelectedWeekParity(currentParity)
        loadSchedule()
    }, [])

    const loadSchedule = () => {
        try {
            setLoading(true)

            // Используем mock-данные
            const scheduleData = mockTeacherSchedule

            if (!scheduleData.events_by_calname || Object.keys(scheduleData.events_by_calname).length === 0) {
                console.warn('Расписание пустое или не найдено')
                setSchedule([])
                setTeacherName('')
                return
            }

            // Берем первого преподавателя из расписания
            const firstTeacherName = Object.keys(scheduleData.events_by_calname)[0]
            setTeacherName(firstTeacherName)
            setSchedule(scheduleData.events_by_calname[firstTeacherName])
        } catch (error) {
            console.error('Ошибка загрузки расписания:', error)
            setSchedule([])
            setTeacherName('')
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

    const extractGroups = (description: string): string => {
        // Извлекаем группы из описания
        const groups = description.trim().split('\n').filter(line => line.trim())
        return groups.length > 0 ? groups.join(', ') : 'Группы не указаны'
    }

    const cleanSummary = (summary: string): string => {
        return summary.replace(/^(ЛК|ПР|ЛБ)\s+/, '')
    }

    const daysOfWeek = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    const daysOfWeekShort = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    const getWeekStart = (date: Date): Date => {
        const d = new Date(date)
        const day = d.getDay()
        const diff = d.getDate() - day + (day === 0 ? -6 : 1)
        return new Date(d.setDate(diff))
    }

    const getWeekDates = (date: Date): Date[] => {
        const weekStart = getWeekStart(date)
        const dates: Date[] = []
        for (let i = 0; i < 7; i++) {
            const d = new Date(weekStart)
            d.setDate(weekStart.getDate() + i)
            dates.push(d)
        }
        return dates
    }

    const getWeekNumber = (date: Date): number => {
        const currentYear = date.getFullYear()
        const currentMonth = date.getMonth()
        let academicYearStart: Date

        if (currentMonth < 8) {
            academicYearStart = new Date(currentYear - 1, 8, 1)
        } else {
            academicYearStart = new Date(currentYear, 8, 1)
        }

        const diffTime = date.getTime() - academicYearStart.getTime()
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
        return Math.floor(diffDays / 7) + 1
    }

    const getWeekParity = (date: Date): 'четная' | 'нечетная' => {
        const weekNumber = getWeekNumber(date)
        return weekNumber % 2 === 0 ? 'четная' : 'нечетная'
    }

    const getDayOfWeekByDate = (date: Date): string => {
        const dayIndex = date.getDay()
        const dayMap: { [key: number]: string } = {
            1: 'Понедельник',
            2: 'Вторник',
            3: 'Среда',
            4: 'Четверг',
            5: 'Пятница',
            6: 'Суббота',
            0: 'Воскресенье'
        }
        return dayMap[dayIndex] || 'Понедельник'
    }

    const hasEventsOnDay = (dayName: string): boolean => {
        return schedule.some(event =>
            event.day_of_week === dayName &&
            event.week_parity === selectedWeekParity
        )
    }

    const goToPreviousWeek = () => {
        const newDate = new Date(currentWeek)
        newDate.setDate(newDate.getDate() - 7)
        setCurrentWeek(newDate)
    }

    const goToNextWeek = () => {
        const newDate = new Date(currentWeek)
        newDate.setDate(newDate.getDate() + 7)
        setCurrentWeek(newDate)
    }

    const getAvailableWeekParities = (dayName: string): ('четная' | 'нечетная')[] => {
        const dayEvents = schedule.filter(event => event.day_of_week === dayName)
        const parities = new Set<'четная' | 'нечетная'>()

        dayEvents.forEach(event => {
            parities.add(event.week_parity as 'четная' | 'нечетная')
        })

        return Array.from(parities)
    }

    useEffect(() => {
        if (selectedDay) {
            const availableParities = getAvailableWeekParities(selectedDay)
            if (availableParities.length > 0) {
                if (availableParities.length === 1) {
                    setSelectedWeekParity(availableParities[0])
                } else {
                    setSelectedWeekParity(prevParity => {
                        if (availableParities.includes(prevParity)) {
                            return prevParity
                        }
                        return availableParities[0]
                    })
                }
            }
        }
    }, [selectedDay, schedule])

    const groupByDay = () => {
        const grouped: { [key: string]: Event[] } = {}

        let filteredSchedule = schedule

        if (selectedDay) {
            filteredSchedule = schedule.filter(event =>
                event.day_of_week === selectedDay &&
                event.week_parity === selectedWeekParity
            )
        } else {
            filteredSchedule = schedule
        }

        filteredSchedule.forEach(event => {
            if (!grouped[event.day_of_week]) {
                grouped[event.day_of_week] = []
            }
            grouped[event.day_of_week].push(event)
        })

        Object.keys(grouped).forEach(day => {
            grouped[day].sort((a, b) => a.start.localeCompare(b.start))
        })

        return grouped
    }

    const handleDayClick = (dayName: string) => {
        if (selectedDay === dayName) {
            setSelectedDay(null)
        } else {
            setSelectedDay(dayName)
        }
    }

    if (loading) {
        return (
            <div className="schedule-page">
                <LoadingSpinner text="Загрузка расписания..." />
            </div>
        )
    }

    const groupedSchedule = groupByDay()
    const weekDates = getWeekDates(currentWeek)
    const weekNumber = getWeekNumber(currentWeek)
    const weekParity = getWeekParity(currentWeek)
    const currentMonth = months[currentWeek.getMonth()]
    const currentYear = currentWeek.getFullYear()
    const today = new Date()

    return (
        <div className="schedule-page">
            <div className="schedule-header">
                <div className="header-content">
                    <h1>Расписание</h1>
                    <p className="group-name">{teacherName}</p>
                </div>

                <div className="week-calendar">
                    <div className="calendar-header">
                        <button className="calendar-nav-btn" onClick={goToPreviousWeek}>
                            <ChevronLeft size={20} />
                        </button>
                        <div className="calendar-title">
                            {currentMonth} {currentYear} – {weekNumber} неделя ({weekParity})
                        </div>
                        <button className="calendar-nav-btn" onClick={goToNextWeek}>
                            <ChevronRight size={20} />
                        </button>
                    </div>
                    <div className="calendar-week">
                        <div className="calendar-days">
                            {daysOfWeekShort.map((day) => (
                                <div key={day} className="calendar-day-label">{day}</div>
                            ))}
                        </div>
                        <div className="calendar-dates">
                            {weekDates.map((date, index) => {
                                const dayName = getDayOfWeekByDate(date)
                                const isToday = date.toDateString() === today.toDateString()
                                const hasEvents = hasEventsOnDay(dayName)
                                const isSelected = selectedDay === dayName

                                return (
                                    <div
                                        key={index}
                                        className={`calendar-date ${isToday ? 'today' : ''} ${hasEvents ? 'has-events' : ''} ${isSelected ? 'selected' : ''}`}
                                        onClick={() => handleDayClick(dayName)}
                                    >
                                        <span className="date-number">{date.getDate()}</span>
                                        {hasEvents && <span className="event-dot"></span>}
                                    </div>
                                )
                            })}
                        </div>
                    </div>
                    {selectedDay && (
                        <div className="selected-date-display">
                            <Calendar size={16} />
                            <span>{selectedDay}</span>
                            <button
                                className="clear-day-btn"
                                onClick={() => setSelectedDay(null)}
                                title="Показать все дни"
                            >
                                ✕
                            </button>
                        </div>
                    )}
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
                                                <span className="text">{extractGroups(event.description)}</span>
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

export default TeacherSchedulePage

