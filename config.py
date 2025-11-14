"""Конфигурация бота"""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла (если есть)
# В продакшене можно использовать переменные окружения напрямую
load_dotenv()

# Токен бота (обязателен, но проверяется при запуске)
TOKEN = os.getenv('MAX_BOT_TOKEN')

# Настройки API
API_BASE_URL = os.getenv('API_BASE_URL', 'https://platform-api.max.ru')

# Настройки polling
POLLING_TIMEOUT = int(os.getenv('POLLING_TIMEOUT', '30'))
POLLING_LIMIT = int(os.getenv('POLLING_LIMIT', '100'))

# Настройки PostgreSQL
# В Docker Compose по умолчанию используется 'db', для внешнего подключения - IP
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
POSTGRES_USER = os.getenv('POSTGRES_USER', 'maxbot')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'maxbot123')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'maxbot_db')

# Строка подключения к БД
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Роли пользователей
ROLES = {
    'applicant': 'Абитуриент',
    'student': 'Студент',
    'staff': 'Сотрудник',
    'admin': 'Администрация'
}

