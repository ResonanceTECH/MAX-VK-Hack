"""Хранение данных пользователей (заявления, и т.д.)"""
from typing import Dict, List, Optional
from datetime import datetime
import random
import string

# Хранение заявлений пользователей
applications: Dict[int, List[Dict]] = {}

# Данные о факультетах
FACULTIES = {
    'informatics': {
        'name': 'Факультет информатики',
        'passing_score': 245,
        'price': 120000,
        'contacts': '+7(495)123-45-67',
        'description': 'Современное IT-образование с практическим подходом'
    },
    'economics': {
        'name': 'Экономический факультет',
        'passing_score': 220,
        'price': 100000,
        'contacts': '+7(495)123-45-68',
        'description': 'Подготовка экономистов и менеджеров'
    },
    'law': {
        'name': 'Юридический факультет',
        'passing_score': 250,
        'price': 130000,
        'contacts': '+7(495)123-45-69',
        'description': 'Классическое юридическое образование'
    }
}


def generate_application_id() -> str:
    """Генерирует ID заявления"""
    year = datetime.now().year
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"АБ-{year}-{random_part}"


def create_application(user_id: int, faculty: str, method: str) -> Dict:
    """Создает новое заявление"""
    if user_id not in applications:
        applications[user_id] = []
    
    application = {
        'id': generate_application_id(),
        'faculty': faculty,
        'method': method,
        'status': 'На проверке',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    applications[user_id].append(application)
    return application


def get_user_applications(user_id: int) -> List[Dict]:
    """Получает все заявления пользователя"""
    return applications.get(user_id, [])


def get_application_by_id(user_id: int, application_id: str) -> Optional[Dict]:
    """Получает заявление по ID"""
    user_apps = applications.get(user_id, [])
    for app in user_apps:
        if app['id'] == application_id:
            return app
    return None


def get_faculty_info(faculty_key: str) -> Optional[Dict]:
    """Получает информацию о факультете"""
    return FACULTIES.get(faculty_key)

