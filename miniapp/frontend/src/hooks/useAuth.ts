import { useState, useEffect } from 'react'
import axios from 'axios'
import { getInitData } from '../utils/getInitData'

interface User {
  id: number
  max_user_id: number
  fio: string
  role: string
  all_roles: Array<{ role: string; fio: string }>
}

/**
 * Создает мок initData для локального тестирования
 * Использует данные пользователя: max_user_id=96855100
 */
function createMockInitData(): string {
  const userData = {
    id: 96855100,
    first_name: "Петр",
    last_name: "Петров",
    username: "petrov"
  }
  
  const authDate = Math.floor(Date.now() / 1000)
  
  // Создаем query string без hash (бэкенд пропустит проверку если SKIP_INITDATA_VERIFY=true)
  const params = new URLSearchParams({
    user: JSON.stringify(userData),
    auth_date: authDate.toString(),
    hash: 'mock_hash_for_dev' // Мок-хэш, проверка будет пропущена
  })
  
  return params.toString()
}

const SELECTED_ROLE_KEY = 'selected_role'

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedRole, setSelectedRoleState] = useState<string | null>(null)

  const initMaxWebApp = () => {
    // Инициализация Max WebApp
    // Max может передавать данные через window.MaxWebApp или через URL параметры
    if (window.MaxWebApp) {
      if (window.MaxWebApp.ready) {
        window.MaxWebApp.ready()
      }
      if (window.MaxWebApp.expand) {
        window.MaxWebApp.expand()
      }
    }
  }

  const setSelectedRole = (role: string | null) => {
    if (role) {
      localStorage.setItem(SELECTED_ROLE_KEY, role)
    } else {
      localStorage.removeItem(SELECTED_ROLE_KEY)
    }
    setSelectedRoleState(role)
    // Перезагружаем пользователя с новой ролью
    fetchUser(role)
  }

  const fetchUser = async (roleOverride?: string | null) => {
    try {
      // Получаем initData из Max WebApp
      let initData = getInitData()
      
      // В режиме разработки, если нет initData, создаем мок
      if (!initData && import.meta.env.DEV) {
        initData = createMockInitData()
      }
      
      if (!initData) {
        console.warn('initData не найден. Проверьте, что мини-приложение открыто из Max мессенджера.')
        setLoading(false)
        return
      }

      // Определяем роль для запроса
      const roleToUse = roleOverride !== undefined 
        ? roleOverride 
        : selectedRole || localStorage.getItem(SELECTED_ROLE_KEY)

      // Запрос к API с initData в заголовке
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
      const headers: Record<string, string> = {
        'X-Init-Data': initData
      }
      
      if (roleToUse) {
        headers['X-Selected-Role'] = roleToUse
      }

      const response = await axios.get(`${apiUrl}/user/info`, { headers })

      const userData = response.data
      setUser(userData)
      
      // Если роль не была установлена, но у пользователя несколько ролей, выбираем первую
      if (!roleToUse && userData.all_roles && userData.all_roles.length > 1) {
        const firstRole = userData.all_roles[0].role
        setSelectedRoleState(firstRole)
        localStorage.setItem(SELECTED_ROLE_KEY, firstRole)
      } else if (roleToUse) {
        setSelectedRoleState(roleToUse)
      }
    } catch (error: any) {
      console.error('Ошибка загрузки пользователя:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Загружаем сохраненную роль из localStorage
    const savedRole = localStorage.getItem(SELECTED_ROLE_KEY)
    if (savedRole) {
      setSelectedRoleState(savedRole)
    }
    
    fetchUser(savedRole)
  }, [])

  // Функция для получения заголовков с выбранной ролью
  const getAuthHeaders = (): Record<string, string> => {
    let initData = getInitData()
    
    if (!initData && import.meta.env.DEV) {
      initData = createMockInitData()
    }
    
    const headers: Record<string, string> = {}
    if (initData) {
      headers['X-Init-Data'] = initData
    }
    
    const roleToUse = selectedRole || localStorage.getItem(SELECTED_ROLE_KEY)
    if (roleToUse) {
      headers['X-Selected-Role'] = roleToUse
    }
    
    return headers
  }

  return { 
    user, 
    loading, 
    initMaxWebApp, 
    selectedRole: selectedRole || localStorage.getItem(SELECTED_ROLE_KEY),
    setSelectedRole,
    getAuthHeaders
  }
}

