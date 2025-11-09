import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import MessagesPage from './pages/MessagesPage'
import GroupsPage from './pages/GroupsPage'
import Layout from './components/Layout'
import { useAuth } from './hooks/useAuth'
import './App.css'

function App() {
  const { user, loading, initMaxWebApp } = useAuth()

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

  // Проверяем роль - мини-приложение только для преподавателей
  if (user.role !== 'teacher') {
    return (
      <div className="error-container">
        <h2>Доступ ограничен</h2>
        <p>Мини-приложение доступно только для преподавателей</p>
      </div>
    )
  }

  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/messages" replace />} />
          <Route path="/messages" element={<MessagesPage />} />
          <Route path="/groups" element={<GroupsPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App

