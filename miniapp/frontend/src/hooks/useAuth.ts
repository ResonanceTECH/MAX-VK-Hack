import { useState, useEffect } from 'react'
import axios from 'axios'
import { getInitData, getCurrentUserId } from '../utils/getInitData'

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
      
      // Подписываемся на события, если Max их поддерживает
      // Это может помочь получить данные, если они приходят асинхронно
      if (window.MaxWebApp.onEvent) {
        try {
          window.MaxWebApp.onEvent('initData', () => {
            console.log('[initMaxWebApp] Получено событие initData от Max')
            // Перезагружаем пользователя при получении новых данных
            const savedRole = localStorage.getItem(SELECTED_ROLE_KEY)
            fetchUser(savedRole)
          })
        } catch (e) {
          // Игнорируем ошибки, если события не поддерживаются
          console.debug('[initMaxWebApp] События не поддерживаются:', e)
        }
      }
      
      console.log('[initMaxWebApp] Max WebApp инициализирован:', {
        hasInitData: !!window.MaxWebApp.initData,
        hasInitDataUnsafe: !!window.MaxWebApp.initDataUnsafe,
        version: window.MaxWebApp.version,
        platform: window.MaxWebApp.platform
      })
    } else {
      console.warn('[initMaxWebApp] window.MaxWebApp не найден - возможно, приложение запущено не из Max мессенджера')
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
    setLoading(true)
    fetchUser(role)
  }

  const fetchUser = async (roleOverride?: string | null) => {
    try {
      // Получаем initData из Max WebApp
      let initData = getInitData()
      
      // Пытаемся извлечь user_id из реального initData от Max
      const realUserId = getCurrentUserId()
      if (realUserId) {
        console.log('[useAuth] Обнаружен пользователь Max с ID:', realUserId)
      } else {
        console.warn('[useAuth] Не удалось получить user_id из Max WebApp')
        // Дополнительная диагностика
        console.log('[useAuth] Диагностика Max WebApp:', {
          hasMaxWebApp: !!window.MaxWebApp,
          hasInitData: !!window.MaxWebApp?.initData,
          hasInitDataUnsafe: !!window.MaxWebApp?.initDataUnsafe,
          hasUser: !!window.MaxWebApp?.initDataUnsafe?.user,
          userObject: window.MaxWebApp?.initDataUnsafe?.user,
          initDataPreview: initData ? initData.substring(0, 200) : 'нет'
        })
      }
      
      // Если нет initData, создаем мок (для работы в контейнере/без Max мессенджера)
      // Бэкенд пропустит проверку если SKIP_AUTH=true и SKIP_INITDATA_VERIFY=true
      if (!initData) {
        initData = createMockInitData()
        console.log('[useAuth] Используется мок initData для локальной разработки')
      }

      // Определяем роль для запроса
      const roleToUse = roleOverride !== undefined 
        ? roleOverride 
        : selectedRole || localStorage.getItem(SELECTED_ROLE_KEY)

      // Запрос к API с initData в заголовке
      const apiUrl = import.meta.env.VITE_API_URL || '/api'
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
    
    // Пытаемся получить данные сразу
    fetchUser(savedRole)
    
    // Если Max WebApp еще не инициализирован, ждем немного и пробуем снова
    // Это нужно, так как Max может загружать данные асинхронно
    if (!window.MaxWebApp?.initData && !window.MaxWebApp?.initDataUnsafe) {
      const retryTimeout = setTimeout(() => {
        console.log('[useAuth] Повторная попытка получения данных от Max WebApp')
        fetchUser(savedRole)
      }, 500) // Ждем 500мс и пробуем снова
      
      return () => clearTimeout(retryTimeout)
    }
  }, [])

  // Функция для получения заголовков с выбранной ролью
  const getAuthHeaders = (): Record<string, string> => {
    let initData = getInitData()
    
    // Если нет initData, создаем мок (для работы в контейнере/без Max мессенджера)
    if (!initData) {
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

