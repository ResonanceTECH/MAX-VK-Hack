"""Конфигурация бота"""
import os

# Токен бота
TOKEN = os.getenv('MAX_BOT_TOKEN')

# Настройки API
API_BASE_URL = 'https://platform-api.max.ru'

# Настройки polling
POLLING_TIMEOUT = 30
POLLING_LIMIT = 100

# Роли пользователей
ROLES = {
    'applicant': 'Абитуриент',
    'student': 'Студент',
    'staff': 'Сотрудник',
    'admin': 'Администрация'
}

