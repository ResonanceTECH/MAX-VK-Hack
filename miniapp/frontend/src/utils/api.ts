import axios from 'axios'
import { getInitData } from './getInitData'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Функция для создания мок initData (для разработки)
function createMockInitData(): string {
  const userData = {
    id: 96855100,
    first_name: "Петр",
    last_name: "Петров",
    username: "petrov"
  }
  
  const authDate = Math.floor(Date.now() / 1000)
  
  const params = new URLSearchParams({
    user: JSON.stringify(userData),
    auth_date: authDate.toString(),
    hash: 'mock_hash_for_dev'
  })
  
  return params.toString()
}

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Интерцептор для добавления initData и выбранной роли в каждый запрос
api.interceptors.request.use((config) => {
  let initData = getInitData()
  
  // В режиме разработки, если нет initData, создаем мок
  if (!initData && import.meta.env.DEV) {
    initData = createMockInitData()
  }
  
  if (initData) {
    config.headers['X-Init-Data'] = initData
  }
  
  // Добавляем выбранную роль из localStorage
  const selectedRole = localStorage.getItem('selected_role')
  if (selectedRole) {
    config.headers['X-Selected-Role'] = selectedRole
  }
  
  return config
})

export default api

