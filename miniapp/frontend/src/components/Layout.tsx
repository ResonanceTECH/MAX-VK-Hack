import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import './Layout.css'

// Иконки в стиле Hugeicons
const MessageIcon = ({ size = 20 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 8L10.89 13.26C11.2187 13.4793 11.6049 13.5963 12 13.5963C12.3951 13.5963 12.7813 13.4793 13.11 13.26L21 8M5 19H19C20.1046 19 21 18.1046 21 17V7C21 5.89543 20.1046 5 19 5H5C3.89543 5 3 5.89543 3 7V17C3 18.1046 3.89543 19 5 19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const UsersIcon = ({ size = 20 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88M13 7C13 9.20914 11.2091 11 9 11C6.79086 11 5 9.20914 5 7C5 4.79086 6.79086 3 9 3C11.2091 3 13 4.79086 13 7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const CalendarIcon = ({ size = 20 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8 2V6M16 2V6M3 10H21M5 4H19C20.1046 4 21 4.89543 21 6V20C21 21.1046 20.1046 22 19 22H5C3.89543 22 3 21.1046 3 20V6C3 4.89543 3.89543 4 5 4Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const TeacherIcon = ({ size = 20 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const NewsIcon = ({ size = 20 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 22H20C21.1046 22 22 21.1046 22 20V4C22 2.89543 21.1046 2 20 2H4C2.89543 2 2 2.89543 2 4V20C2 21.1046 2.89543 22 4 22Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M7 8H17M7 12H17M7 16H13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const ChecklistIcon = ({ size = 20 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15M9 5C9 6.10457 9.89543 7 11 7H13C14.1046 7 15 6.10457 15 5M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5M9 12L11 14L15 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const ChartIcon = ({ size = 20 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 3V21H21M7 16L12 11L16 15L21 10M21 10H16M21 10V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

const GraduationCapIcon = ({ size = 20 }: { size?: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 10V11C22 13.7614 19.7614 16 17 16H16M22 10L12 5L2 10L12 15L22 10Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M2 10V18C2 19.6569 3.34315 21 5 21H19C20.6569 21 22 19.6569 22 18V11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
)

interface MenuItem {
  path: string
  label: string
  icon: React.ReactNode
}

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()
  const { user } = useAuth()

  if (!user) {
    return <div className="layout"><main className="main-content">{children}</main></div>
  }

  const role = user.role

  // Меню для студентов
  const studentMenu: MenuItem[] = [
    { path: '/messages', label: 'Сообщения', icon: <MessageIcon size={20} /> },
    { path: '/my-group', label: 'Моя группа', icon: <UsersIcon size={20} /> },
    { path: '/schedule', label: 'Расписание', icon: <CalendarIcon size={20} /> },
    { path: '/teachers', label: 'Преподаватели', icon: <TeacherIcon size={20} /> },
    { path: '/news', label: 'Новости', icon: <NewsIcon size={20} /> }
  ]

  // Меню для преподавателей
  const teacherMenu: MenuItem[] = [
    { path: '/messages', label: 'Сообщения', icon: <MessageIcon size={20} /> },
    { path: '/my-groups', label: 'Мои группы', icon: <UsersIcon size={20} /> },
    { path: '/schedule', label: 'Расписание', icon: <CalendarIcon size={20} /> },
    { path: '/teachers', label: 'Преподаватели', icon: <TeacherIcon size={20} /> },
    { path: '/news', label: 'Новости', icon: <NewsIcon size={20} /> }
  ]

  // Меню для поддержки
  const supportMenu: MenuItem[] = [
    { path: '/support-tickets', label: 'Запросы в поддержку', icon: <ChecklistIcon size={20} /> },
    { path: '/messages', label: 'Сообщения', icon: <MessageIcon size={20} /> },
    { path: '/stats', label: 'Статистика', icon: <ChartIcon size={20} /> }
  ]

  // Меню для администрации
  const adminMenu: MenuItem[] = [
    { path: '/admin/students', label: 'Управление студентами', icon: <GraduationCapIcon size={20} /> },
    { path: '/admin/teachers', label: 'Управление преподавателями', icon: <TeacherIcon size={20} /> },
    { path: '/admin/groups', label: 'Управление группами', icon: <UsersIcon size={20} /> },
    { path: '/admin/news', label: 'Создание новостей', icon: <NewsIcon size={20} /> },
    { path: '/messages', label: 'Сообщения', icon: <MessageIcon size={20} /> }
  ]

  let menuItems: MenuItem[] = []

  switch (role) {
    case 'student':
      menuItems = studentMenu
      break
    case 'teacher':
      menuItems = teacherMenu
      break
    case 'support':
      menuItems = supportMenu
      break
    case 'admin':
      menuItems = adminMenu
      break
    default:
      menuItems = []
  }

  return (
    <div className="layout">
      <nav className="navbar">
        {menuItems.map(item => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          )
        })}
      </nav>
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

export default Layout

