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

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

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

  useEffect(() => {
    const fetchUser = async () => {
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

        // Запрос к API с initData в заголовке
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
        const response = await axios.get(`${apiUrl}/user/info`, {
          headers: {
            'X-Init-Data': initData
          }
        })

        setUser(response.data)
      } catch (error: any) {
        console.error('Ошибка загрузки пользователя:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [])

  return { user, loading, initMaxWebApp }
}

