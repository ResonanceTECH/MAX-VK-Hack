import React, { useEffect, useState } from 'react'
import { UserCircle2, MapPin, ChevronLeft, ChevronRight, Calendar } from 'lucide-react'
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
    const [currentWeek, setCurrentWeek] = useState<Date>(new Date())
    const [selectedDay, setSelectedDay] = useState<string | null>(null)

    // Определение текущей недели (четная/нечетная)
    const getCurrentWeekParity = (): 'четная' | 'нечетная' => {
        // Дата начала учебного года (1 сентября 2024)
        const startDate = new Date(2024, 8, 1) // месяц 8 = сентябрь (0-indexed)
        const today = new Date()

        // Разница в днях
        const diffTime = today.getTime() - startDate.getTime()
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

        // Номер недели с начала учебного года
        const weekNumber = Math.floor(diffDays / 7)

        // Четная или нечетная неделя
        return weekNumber % 2 === 0 ? 'нечетная' : 'четная'
    }

    useEffect(() => {
        const currentParity = getCurrentWeekParity()
        setSelectedWeekParity(currentParity)
        loadSchedule()
    }, [])

    const loadSchedule = async () => {
        try {
            setLoading(true)
            // Данные расписания
            const scheduleData: ScheduleData = {
                "events_by_calname": {
                    "ИКБО-16-22": [
                        { "summary": "ПР Информационный менеджмент программных продуктов и систем", "start": "09:00", "end": "10:30", "day_of_week": "Понедельник", "description": "Преподаватель: Братусь Надежда Валерьевна\n", "location": "И-205-а (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Информационный менеджмент программных продуктов и систем", "start": "10:40", "end": "12:10", "day_of_week": "Понедельник", "description": "Преподаватель: Братусь Надежда Валерьевна\n", "location": "И-205-а (В-78)", "week_parity": "нечетная" },
                        { "summary": "ЛК Управление информационно-технологическими проектами", "start": "18:00", "end": "19:30", "day_of_week": "Понедельник", "description": "Преподаватель: Потапова Ксения Александровна\n\nГруппы:\nИКБО-01-22\nИКБО-02-22\nИКБО-16-22\nИКБО-20-22\nИКБО-30-22\nИКБО-36-22\n", "location": "Дистанционно (СДО)", "week_parity": "нечетная" },
                        { "summary": "ЛК Управление информационно-технологическими проектами", "start": "18:00", "end": "19:30", "day_of_week": "Понедельник", "description": "Преподаватель: Потапова Ксения Александровна\n\nГруппы:\nИКБО-01-22\nИКБО-02-22\nИКБО-16-22\nИКБО-20-22\nИКБО-30-22\nИКБО-36-22\n", "location": "Дистанционно (СДО)", "week_parity": "четная" },
                        { "summary": "ПР Информационный менеджмент программных продуктов и систем", "start": "09:00", "end": "10:30", "day_of_week": "Вторник", "description": "Преподаватель: Братусь Надежда Валерьевна\n", "location": "И-205-а (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Информационный менеджмент программных продуктов и систем", "start": "10:40", "end": "12:10", "day_of_week": "Вторник", "description": "Преподаватель: Братусь Надежда Валерьевна\n", "location": "И-205-а (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Имитационное моделирование клиент-серверных приложений", "start": "09:00", "end": "10:30", "day_of_week": "Среда", "description": "Преподаватель: Коваленко Михаил Андреевич\n", "location": "Г-227-1 (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Имитационное моделирование клиент-серверных приложений", "start": "09:00", "end": "10:30", "day_of_week": "Среда", "description": "Преподаватель: Коваленко Михаил Андреевич\n", "location": "Г-227-1 (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Имитационное моделирование клиент-серверных приложений", "start": "10:40", "end": "12:10", "day_of_week": "Среда", "description": "Преподаватель: Коваленко Михаил Андреевич\n", "location": "Г-227-1 (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Имитационное моделирование клиент-серверных приложений", "start": "10:40", "end": "12:10", "day_of_week": "Среда", "description": "Преподаватель: Коваленко Михаил Андреевич\n", "location": "Г-227-1 (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Проектирование клиент-серверных систем", "start": "09:00", "end": "10:30", "day_of_week": "Четверг", "description": "Преподаватель: Мельников Денис Александрович\n", "location": "И-203-б (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Проектирование клиент-серверных систем", "start": "09:00", "end": "10:30", "day_of_week": "Четверг", "description": "Преподаватель: Мельников Денис Александрович\n", "location": "И-203-б (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Проектирование клиент-серверных систем", "start": "10:40", "end": "12:10", "day_of_week": "Четверг", "description": "Преподаватель: Мельников Денис Александрович\n", "location": "И-203-б (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Информационный менеджмент программных продуктов и систем", "start": "10:40", "end": "12:10", "day_of_week": "Четверг", "description": "Преподаватель: Братусь Надежда Валерьевна\n", "location": "Г-226-2 (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Информационный менеджмент программных продуктов и систем", "start": "12:40", "end": "14:10", "day_of_week": "Четверг", "description": "Преподаватель: Братусь Надежда Валерьевна\n", "location": "Г-226-2 (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Управление информационно-технологическими проектами", "start": "12:40", "end": "14:10", "day_of_week": "Четверг", "description": "Преподаватель: Габриелян Гайк Ашотович\n", "location": "Д-313 (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Информационный менеджмент программных продуктов и систем", "start": "12:40", "end": "14:10", "day_of_week": "Четверг", "description": "Преподаватель: Братусь Надежда Валерьевна\n", "location": "Г-226-2 (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Управление информационно-технологическими проектами", "start": "12:40", "end": "14:10", "day_of_week": "Четверг", "description": "Преподаватель: Габриелян Гайк Ашотович\n", "location": "Д-313 (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Управление информационно-технологическими проектами", "start": "14:20", "end": "15:50", "day_of_week": "Четверг", "description": "Преподаватель: Габриелян Гайк Ашотович\n", "location": "И-202-а (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Управление информационно-технологическими проектами", "start": "14:20", "end": "15:50", "day_of_week": "Четверг", "description": "Преподаватель: Габриелян Гайк Ашотович\n", "location": "И-202-а (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Разработка клиент-серверных приложений", "start": "09:00", "end": "10:30", "day_of_week": "Пятница", "description": "Преподаватель: Романченко Алексей Евгеньевич\n", "location": "Г-226-2 (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Разработка клиент-серверных приложений", "start": "09:00", "end": "10:30", "day_of_week": "Пятница", "description": "Преподаватель: Романченко Алексей Евгеньевич\n", "location": "Г-226-2 (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Разработка клиент-серверных приложений", "start": "10:40", "end": "12:10", "day_of_week": "Пятница", "description": "Преподаватель: Романченко Алексей Евгеньевич\n", "location": "Г-226-2 (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Разработка клиент-серверных приложений", "start": "10:40", "end": "12:10", "day_of_week": "Пятница", "description": "Преподаватель: Романченко Алексей Евгеньевич\n", "location": "Г-226-2 (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Технологии виртуализации клиент-серверных приложений", "start": "12:40", "end": "14:10", "day_of_week": "Пятница", "description": "Преподаватель: Волков Михаил Юрьевич\n", "location": "Г-226-2 (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Технологии виртуализации клиент-серверных приложений", "start": "12:40", "end": "14:10", "day_of_week": "Пятница", "description": "Преподаватель: Волков Михаил Юрьевич\n", "location": "Г-226-2 (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Технологии виртуализации клиент-серверных приложений", "start": "14:20", "end": "15:50", "day_of_week": "Пятница", "description": "Преподаватель: Волков Михаил Юрьевич\n", "location": "Г-226-2 (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Технологии виртуализации клиент-серверных приложений", "start": "14:20", "end": "15:50", "day_of_week": "Пятница", "description": "Преподаватель: Волков Михаил Юрьевич\n", "location": "Г-226-2 (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Технологии и инструментарий анализа больших данных", "start": "16:20", "end": "17:50", "day_of_week": "Пятница", "description": "Преподаватель: Тетерин Николай Николаевич\n", "location": "А-421 (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Технологии и инструментарий анализа больших данных", "start": "16:20", "end": "17:50", "day_of_week": "Пятница", "description": "Преподаватель: Тетерин Николай Николаевич\n", "location": "Г-413 (В-78)", "week_parity": "нечетная" },
                        { "summary": "ПР Технологии и инструментарий анализа больших данных", "start": "16:20", "end": "17:50", "day_of_week": "Пятница", "description": "Преподаватель: Тетерин Николай Николаевич\n", "location": "А-421 (В-78)", "week_parity": "четная" },
                        { "summary": "ПР Технологии и инструментарий анализа больших данных", "start": "16:20", "end": "17:50", "day_of_week": "Пятница", "description": "Преподаватель: Тетерин Николай Николаевич\n", "location": "Г-413 (В-78)", "week_parity": "четная" },
                        { "summary": "ЛК Разработка клиент-серверных приложений", "start": "10:40", "end": "12:10", "day_of_week": "Суббота", "description": "Преподаватель: Коваленко Михаил Андреевич\n\nГруппы:\nИКБО-01-22\nИКБО-02-22\nИКБО-16-22\nИКБО-20-22\nИКБО-30-22\nИКБО-36-22\n", "location": "Дистанционно (СДО)", "week_parity": "нечетная" },
                        { "summary": "ЛК Технологии и инструментарий анализа больших данных", "start": "10:40", "end": "12:10", "day_of_week": "Суббота", "description": "Преподаватель: Юрченков Иван Александрович\n\nГруппы:\nИКБО-01-22\nИКБО-02-22\nИКБО-16-22\nИКБО-20-22\nИКБО-30-22\nИКБО-36-22\n", "location": "Дистанционно (СДО)", "week_parity": "четная" },
                        { "summary": "ЛК Имитационное моделирование клиент-серверных приложений", "start": "12:40", "end": "14:10", "day_of_week": "Суббота", "description": "Преподаватель: Акопов Андраник Сумбатович\n\nГруппы:\nИКБО-01-22\nИКБО-16-22\nИКБО-20-22\nИКБО-30-22\nИКБО-36-22\n", "location": "Дистанционно (СДО)", "week_parity": "нечетная" },
                        { "summary": "ЛК Проектирование клиент-серверных систем", "start": "12:40", "end": "14:10", "day_of_week": "Суббота", "description": "Преподаватель: Лобанов Александр Анатольевич\n\nГруппы:\nИКБО-01-22\nИКБО-16-22\nИКБО-20-22\nИКБО-30-22\nИКБО-36-22\n", "location": "Дистанционно (СДО)", "week_parity": "четная" },
                        { "summary": "ЛК Информационный менеджмент программных продуктов и систем", "start": "14:20", "end": "15:50", "day_of_week": "Суббота", "description": "Преподаватель: Лобанов Александр Анатольевич\n\nГруппы:\nИКБО-01-22\nИКБО-16-22\nИКБО-20-22\nИКБО-30-22\nИКБО-36-22\n", "location": "Дистанционно (СДО)", "week_parity": "нечетная" },
                        { "summary": "ЛК Информационный менеджмент программных продуктов и систем", "start": "14:20", "end": "15:50", "day_of_week": "Суббота", "description": "Преподаватель: Лобанов Александр Анатольевич\n\nГруппы:\nИКБО-01-22\nИКБО-16-22\nИКБО-20-22\nИКБО-30-22\nИКБО-36-22\n", "location": "Дистанционно (СДО)", "week_parity": "четная" },
                        { "summary": "ЛК Технологии виртуализации клиент-серверных приложений", "start": "16:20", "end": "17:50", "day_of_week": "Суббота", "description": "Преподаватель: Волков Михаил Юрьевич\n\nГруппы:\nИКБО-01-22\nИКБО-16-22\nИКБО-20-22\nИКБО-30-22\nИКБО-36-22\n", "location": "Дистанционно (СДО)", "week_parity": "нечетная" }
                    ]
                }
            }

            const firstGroupName = Object.keys(scheduleData.events_by_calname)[0]
            setGroupName(firstGroupName)
            setSchedule(scheduleData.events_by_calname[firstGroupName])
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
    const daysOfWeekShort = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    // Получить начало недели (понедельник)
    const getWeekStart = (date: Date): Date => {
        const d = new Date(date)
        const day = d.getDay()
        const diff = d.getDate() - day + (day === 0 ? -6 : 1) // Понедельник = 1
        return new Date(d.setDate(diff))
    }

    // Получить даты недели
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

    // Получить номер недели с начала учебного года (1 сентября)
    const getWeekNumber = (date: Date): number => {
        // Определяем год начала учебного года
        const currentYear = date.getFullYear()
        const currentMonth = date.getMonth() // 0-11
        let academicYearStart: Date

        // Если текущая дата до сентября, то учебный год начался в прошлом году
        if (currentMonth < 8) { // 8 = сентябрь (0-indexed)
            academicYearStart = new Date(currentYear - 1, 8, 1) // 1 сентября прошлого года
        } else {
            academicYearStart = new Date(currentYear, 8, 1) // 1 сентября текущего года
        }

        // Разница в днях
        const diffTime = date.getTime() - academicYearStart.getTime()
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

        // Номер недели с начала учебного года (начинаем с 1)
        return Math.floor(diffDays / 7) + 1
    }

    // Получить четность недели по дате
    const getWeekParity = (date: Date): 'четная' | 'нечетная' => {
        const weekNumber = getWeekNumber(date)
        return weekNumber % 2 === 0 ? 'четная' : 'нечетная'
    }

    // Получить русское название дня недели по дате
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

    // Проверить, есть ли события в день
    const hasEventsOnDay = (dayName: string): boolean => {
        return schedule.some(event =>
            event.day_of_week === dayName &&
            event.week_parity === selectedWeekParity
        )
    }

    // Навигация по неделям
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

    // Определить доступные недели для выбранного дня
    const getAvailableWeekParities = (dayName: string): ('четная' | 'нечетная')[] => {
        const dayEvents = schedule.filter(event => event.day_of_week === dayName)
        const parities = new Set<'четная' | 'нечетная'>()

        dayEvents.forEach(event => {
            parities.add(event.week_parity as 'четная' | 'нечетная')
        })

        return Array.from(parities)
    }

    // Автоматически определить неделю для выбранного дня
    useEffect(() => {
        if (selectedDay) {
            const availableParities = getAvailableWeekParities(selectedDay)
            if (availableParities.length > 0) {
                // Если есть занятия только на одну неделю, автоматически выбрать её
                if (availableParities.length === 1) {
                    setSelectedWeekParity(availableParities[0])
                } else {
                    // Если есть на обе недели, использовать текущую выбранную или первую доступную
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

        // Если выбран конкретный день, фильтруем по дню и неделе
        if (selectedDay) {
            filteredSchedule = schedule.filter(event =>
                event.day_of_week === selectedDay &&
                event.week_parity === selectedWeekParity
            )
        } else {
            // Если день не выбран, показываем все расписание без фильтрации по неделе
            filteredSchedule = schedule
        }

        filteredSchedule.forEach(event => {
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

    // Обработчик клика по дню в календаре
    const handleDayClick = (dayName: string) => {
        if (selectedDay === dayName) {
            // Если кликнули по уже выбранному дню, снимаем выбор
            setSelectedDay(null)
        } else {
            // Выбираем новый день
            setSelectedDay(dayName)
        }
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
                    <h1>
                        Расписание
                    </h1>
                    <p className="group-name">{groupName}</p>
                </div>

                {/* Календарь недели */}
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
