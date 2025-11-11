"""Конфигурация бота"""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота
TOKEN = os.getenv('MAX_BOT_TOKEN')

# Настройки API
API_BASE_URL = os.getenv('API_BASE_URL', 'https://platform-api.max.ru')

# Настройки polling
POLLING_TIMEOUT = int(os.getenv('POLLING_TIMEOUT', '30'))
POLLING_LIMIT = int(os.getenv('POLLING_LIMIT', '100'))

# Настройки PostgreSQL
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5431'))
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'max_bot_db')

# Строка подключения к БД
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Роли пользователей
ROLES = {
    'applicant': 'Абитуриент',
    'student': 'Студент',
    'staff': 'Сотрудник',
    'admin': 'Администрация'
}

