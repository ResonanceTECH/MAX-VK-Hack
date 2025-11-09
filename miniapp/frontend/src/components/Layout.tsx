import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Layout.css'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()

  return (
    <div className="layout">
      <nav className="navbar">
        <Link 
          to="/messages" 
          className={location.pathname === '/messages' ? 'active' : ''}
        >
          📨 Сообщения
        </Link>
        <Link 
          to="/groups" 
          className={location.pathname === '/groups' ? 'active' : ''}
        >
          👥 Группы
        </Link>
      </nav>
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

export default Layout

