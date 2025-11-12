import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import MessagesPage from './pages/MessagesPage'
import Layout from './components/Layout'
import { useAuth } from './hooks/useAuth'
import './App.css'

// Импорты страниц для студентов
import MyGroupPage from './pages/student/my-group/MyGroupPage'
import SchedulePage from './pages/student/schedule/SchedulePage'
import TeachersPage from './pages/student/teachers/TeachersPage'
import NewsPage from './pages/student/news/NewsPage'

// Импорты страниц для преподавателей
import MyGroupsPage from './pages/teacher/MyGroupsPage'
import GroupStudentsPage from './pages/teacher/GroupStudentsPage'

// Импорты страниц для поддержки
import SupportTicketsPage from './pages/support/SupportTicketsPage'
import StatsPage from './pages/support/StatsPage'

// Импорты страниц для администрации
import AdminStudentsPage from './pages/admin/students/AdminStudentsPage'
import AdminTeachersPage from './pages/admin/teachers/AdminTeachersPage'
import AdminGroupsPage from './pages/admin/groups/AdminGroupsPage'
import AdminNewsPage from './pages/admin/news/AdminNewsPage'

// Функция для определения дефолтного маршрута в зависимости от роли
const getDefaultRoute = (role: string): string => {
  switch (role) {
    case 'student':
      return '/messages'
    case 'teacher':
      return '/messages'
    case 'support':
      return '/support-tickets'
    case 'admin':
      return '/admin/students'
    default:
      return '/messages'
  }
}

// Внутренний компонент для обработки навигации при смене роли
function AppContent() {
  const { user, loading, initMaxWebApp, selectedRole, setSelectedRole } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [prevRole, setPrevRole] = useState<string | null>(null)

  useEffect(() => {
    initMaxWebApp()
  }, [])

  // Отслеживаем изменение роли и перенаправляем на правильный маршрут
  useEffect(() => {
    if (user && user.role && prevRole && prevRole !== user.role) {
      // Роль изменилась, перенаправляем на дефолтный маршрут для новой роли
      const defaultRoute = getDefaultRoute(user.role)
      if (location.pathname !== defaultRoute) {
        navigate(defaultRoute, { replace: true })
      }
    }
    if (user && user.role) {
      setPrevRole(user.role)
    }
  }, [user?.role, navigate, location.pathname, prevRole])

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">Загрузка...</div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="error-container">
        <h2>Ошибка авторизации</h2>
        <p>Не удалось загрузить данные пользователя</p>
      </div>
    )
  }

  return (
    <div className="app-container">
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to={getDefaultRoute(user.role)} replace />} />

          {/* Общие маршруты */}
          <Route path="/messages" element={<MessagesPage />} />

          {/* Маршруты для студентов */}
          <Route path="/my-group" element={<MyGroupPage />} />
          <Route path="/schedule" element={<SchedulePage />} />
          <Route path="/teachers" element={<TeachersPage />} />
          <Route path="/news" element={<NewsPage />} />

          {/* Маршруты для преподавателей */}
          <Route path="/my-groups" element={<MyGroupsPage />} />
          <Route path="/groups/:groupId" element={<GroupStudentsPage />} />

          {/* Маршруты для поддержки */}
          <Route path="/support-tickets" element={<SupportTicketsPage />} />
          <Route path="/stats" element={<StatsPage />} />

          {/* Маршруты для администрации */}
          <Route path="/admin/students" element={<AdminStudentsPage />} />
          <Route path="/admin/teachers" element={<AdminTeachersPage />} />
          <Route path="/admin/groups" element={<AdminGroupsPage />} />
          <Route path="/admin/news" element={<AdminNewsPage />} />
        </Routes>
      </Layout>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App

