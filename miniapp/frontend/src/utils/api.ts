import axios from 'axios'
import { getInitData } from './getInitData'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Интерцептор для добавления initData в каждый запрос
api.interceptors.request.use((config) => {
  const initData = getInitData()
  if (initData) {
    config.headers['X-Init-Data'] = initData
  }
  return config
})

export default api

