"""Хранение данных пользователей (заявления, и т.д.)"""
from typing import Dict, List, Optional
from datetime import datetime
import random
import string

# Хранение заявлений пользователей (абитуриенты)
applications: Dict[int, List[Dict]] = {}

# Хранение заявок студентов
student_requests: Dict[int, List[Dict]] = {}

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


# Расписание студентов (примерные данные)
STUDENT_SCHEDULE = {
    'today': [
        {'time': '09:00', 'subject': 'Математика', 'room': '310'},
        {'time': '11:00', 'subject': 'Программирование', 'room': '415'},
        {'time': '13:00', 'subject': 'База данных', 'room': '201'}
    ],
    'week': [
        {'day': 'Понедельник', 'lessons': [
            {'time': '09:00', 'subject': 'Математика', 'room': '310'},
            {'time': '11:00', 'subject': 'Программирование', 'room': '415'}
        ]},
        {'day': 'Вторник', 'lessons': [
            {'time': '09:00', 'subject': 'Физика', 'room': '205'},
            {'time': '13:00', 'subject': 'База данных', 'room': '201'}
        ]},
        {'day': 'Среда', 'lessons': [
            {'time': '09:00', 'subject': 'Математика', 'room': '310'},
            {'time': '11:00', 'subject': 'Программирование', 'room': '415'}
        ]},
        {'day': 'Четверг', 'lessons': [
            {'time': '09:00', 'subject': 'Алгоритмы', 'room': '415'},
            {'time': '13:00', 'subject': 'База данных', 'room': '201'}
        ]},
        {'day': 'Пятница', 'lessons': [
            {'time': '09:00', 'subject': 'Математика', 'room': '310'},
            {'time': '11:00', 'subject': 'Программирование', 'room': '415'}
        ]}
    ]
}

# Типы справок для студентов
REQUEST_TYPES = {
    'study': {
        'name': 'Об обучении',
        'processing_days': 2
    },
    'scholarship': {
        'name': 'О стипендии',
        'processing_days': 3
    },
    'enrollment': {
        'name': 'С места учебы',
        'processing_days': 2
    }
}


def generate_student_request_id() -> str:
    """Генерирует ID заявки студента"""
    year = datetime.now().year
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"СТ-{year}-{random_part}"


def create_student_request(user_id: int, request_type: str, request_category: str = 'certificate') -> Dict:
    """Создает новую заявку студента"""
    if user_id not in student_requests:
        student_requests[user_id] = []
    
    request_info = REQUEST_TYPES.get(request_type, {})
    
    request = {
        'id': generate_student_request_id(),
        'type': request_type,
        'category': request_category,
        'name': request_info.get('name', request_type),
        'status': 'В обработке',
        'processing_days': request_info.get('processing_days', 2),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    student_requests[user_id].append(request)
    return request


def get_student_requests(user_id: int) -> List[Dict]:
    """Получает все заявки студента"""
    return student_requests.get(user_id, [])


def get_active_student_requests(user_id: int) -> List[Dict]:
    """Получает активные заявки студента (не завершенные)"""
    all_requests = get_student_requests(user_id)
    return [req for req in all_requests if req['status'] not in ['Завершено', 'Отклонено']]

