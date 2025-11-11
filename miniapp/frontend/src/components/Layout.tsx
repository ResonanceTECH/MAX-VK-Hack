import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import './Layout.css'

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
  const studentMenu = [
    { path: '/messages', label: '📨 Сообщения' },
    { path: '/my-group', label: '👥 Моя группа' },
    { path: '/schedule', label: '📅 Расписание' },
    { path: '/teachers', label: '👨‍🏫 Преподаватели' },
    { path: '/news', label: '📢 Новости' }
  ]

  // Меню для преподавателей
  const teacherMenu = [
    { path: '/messages', label: '📨 Сообщения' },
    { path: '/my-groups', label: '👥 Мои группы' },
    { path: '/schedule', label: '📅 Расписание' },
    { path: '/teachers', label: '👨‍🏫 Преподаватели' },
    { path: '/news', label: '📢 Новости' }
  ]

  // Меню для поддержки
  const supportMenu = [
    { path: '/support-tickets', label: '📋 Запросы в поддержку' },
    { path: '/messages', label: '📨 Сообщения' },
    { path: '/stats', label: '📊 Статистика' }
  ]

  // Меню для администрации
  const adminMenu = [
    { path: '/admin/students', label: '👨‍🎓 Управление студентами' },
    { path: '/admin/teachers', label: '👨‍🏫 Управление преподавателями' },
    { path: '/admin/groups', label: '👥 Управление группами' },
    { path: '/admin/news', label: '📢 Создание новостей' },
    { path: '/messages', label: '📨 Сообщения' }
  ]

  let menuItems: Array<{ path: string; label: string }> = []

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
        {menuItems.map(item => (
          <Link
            key={item.path}
            to={item.path}
            className={location.pathname === item.path ? 'active' : ''}
          >
            {item.label}
          </Link>
        ))}
      </nav>
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

export default Layout

