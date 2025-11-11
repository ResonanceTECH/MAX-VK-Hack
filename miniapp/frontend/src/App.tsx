import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import MessagesPage from './pages/MessagesPage'
import Layout from './components/Layout'
import RoleSelector from './components/RoleSelector'
import { useAuth } from './hooks/useAuth'
import './App.css'

// Импорты страниц для студентов
import MyGroupPage from './pages/student/MyGroupPage'
import SchedulePage from './pages/student/SchedulePage'
import TeachersPage from './pages/student/TeachersPage'
import NewsPage from './pages/student/NewsPage'

// Импорты страниц для преподавателей
import MyGroupsPage from './pages/teacher/MyGroupsPage'

// Импорты страниц для поддержки
import SupportTicketsPage from './pages/support/SupportTicketsPage'
import StatsPage from './pages/support/StatsPage'

// Импорты страниц для администрации
import AdminStudentsPage from './pages/admin/AdminStudentsPage'
import AdminTeachersPage from './pages/admin/AdminTeachersPage'
import AdminGroupsPage from './pages/admin/AdminGroupsPage'
import AdminNewsPage from './pages/admin/AdminNewsPage'

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

function App() {
  const { user, loading, initMaxWebApp, selectedRole, setSelectedRole } = useAuth()

  useEffect(() => {
    initMaxWebApp()
  }, [])

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

  // Если у пользователя несколько ролей, показываем селектор
  const hasMultipleRoles = user.all_roles && user.all_roles.length > 1

  return (
    <Router>
      <div className="app-container">
        {hasMultipleRoles && (
          <RoleSelector
            roles={user.all_roles}
            currentRole={user.role}
            onRoleChange={setSelectedRole}
          />
        )}
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
    </Router>
  )
}

export default App

