"""Генерация клавиатур для сообщений"""
from typing import List, Dict, Any, Optional


def create_inline_keyboard(buttons: List[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Создает inline клавиатуру"""
    return {
        'type': 'inline_keyboard',
        'payload': {
            'buttons': buttons
        }
    }


def create_callback_button(
    text: str,
    payload: str,
    intent: Optional[str] = None
) -> Dict[str, Any]:
    """Создает callback кнопку"""
    button = {
        'type': 'callback',
        'text': text,
        'payload': payload
    }
    # Intent опционален, добавляем только если указан
    if intent:
        button['intent'] = intent
    return button


def create_link_button(text: str, url: str) -> Dict[str, Any]:
    """Создает кнопку-ссылку"""
    return {
        'type': 'link',
        'text': text,
        'url': url
    }


def create_main_menu_keyboard() -> Dict[str, Any]:
    """Создает главное меню"""
    buttons = [
        [
            create_callback_button('📚 Поступление', 'menu_admission'),
            create_callback_button('🎓 Обучение', 'menu_education')
        ],
        [
            create_callback_button('🚀 Проекты', 'menu_projects'),
            create_callback_button('💼 Карьера', 'menu_career')
        ],
        [
            create_callback_button('📋 Деканат', 'menu_deanery'),
            create_callback_button('🏠 Общежитие', 'menu_dormitory')
        ],
        [
            create_callback_button('📖 Библиотека', 'menu_library'),
            create_callback_button('⚙️ Настройки', 'menu_settings')
        ]
    ]
    return create_inline_keyboard(buttons)


def create_role_selection_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру выбора роли"""
    buttons = [
        [create_callback_button('🎓 Абитуриент', 'role_applicant')],
        [create_callback_button('👨‍🎓 Студент', 'role_student')],
        [create_callback_button('👔 Сотрудник', 'role_staff')],
        [create_callback_button('👑 Администрация', 'role_admin')]
    ]
    return create_inline_keyboard(buttons)


def create_back_to_menu_button() -> List[Dict[str, Any]]:
    """Создает кнопку возврата в меню"""
    return [[create_callback_button('🔙 Главное меню', 'menu_main')]]


def create_admission_main_keyboard() -> Dict[str, Any]:
    """Создает главное меню модуля Поступление"""
    buttons = [
        [create_callback_button('📋 Информация о вузе', 'admission_info')],
        [create_callback_button('📝 Подать документы', 'admission_apply')],
        [create_callback_button('📄 Мои заявления', 'admission_my_applications')],
        [create_callback_button('📅 Ближайшие мероприятия', 'admission_events')],
        [create_callback_button('🔙 Вернуться', 'menu_main')]
    ]
    return create_inline_keyboard(buttons)


def create_faculties_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру выбора факультета"""
    buttons = [
        [create_callback_button('💻 Факультет информатики', 'faculty_informatics')],
        [create_callback_button('💰 Экономический', 'faculty_economics')],
        [create_callback_button('⚖️ Юридический', 'faculty_law')],
        [create_callback_button('📚 Все факультеты', 'faculty_all')],
        [create_callback_button('🔙 Назад', 'menu_admission')]
    ]
    return create_inline_keyboard(buttons)


def create_faculty_info_keyboard(faculty_key: str) -> Dict[str, Any]:
    """Создает клавиатуру для информации о факультете"""
    buttons = [
        [create_callback_button('📝 Подать документы', 'admission_apply')],
        [
            create_callback_button('🔙 Назад', 'admission_info'),
            create_callback_button('🏠 Главное меню', 'menu_main')
        ]
    ]
    return create_inline_keyboard(buttons)


def create_application_method_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру выбора способа подачи документов"""
    buttons = [
        [create_callback_button('💻 Онлайн-заявление', 'apply_online')],
        [create_callback_button('📅 Запись на очную подачу', 'apply_offline')],
        [create_callback_button('💬 Консультация', 'apply_consultation')],
        [create_callback_button('🔙 Назад', 'menu_admission')]
    ]
    return create_inline_keyboard(buttons)


def create_application_created_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру после создания заявления"""
    buttons = [
        [create_callback_button('📄 Мои заявления', 'admission_my_applications')],
        [create_callback_button('➕ Новое заявление', 'admission_apply')],
        [
            create_callback_button('🔙 Назад', 'menu_admission'),
            create_callback_button('🏠 Главное меню', 'menu_main')
        ]
    ]
    return create_inline_keyboard(buttons)


# ========== Клавиатуры для студентов ==========

def create_student_main_keyboard() -> Dict[str, Any]:
    """Создает главное меню для студентов"""
    buttons = [
        [create_callback_button('📅 Расписание', 'student_schedule')],
        [create_callback_button('📋 Заявки', 'student_requests')],
        [create_callback_button('🏠 Общежитие', 'student_dormitory')],
        [create_callback_button('🚀 Проекты', 'student_projects')],
        [create_callback_button('📖 Библиотека', 'student_library')],
        [create_callback_button('🎉 Мероприятия', 'student_events')],
        [create_callback_button('🔙 Вернуться', 'menu_main')]
    ]
    return create_inline_keyboard(buttons)


def create_schedule_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру для расписания"""
    buttons = [
        [create_callback_button('📆 На неделю', 'schedule_week')],
        [create_callback_button('🔔 Изменения', 'schedule_changes')],
        [create_callback_button('⚙️ Настройка напоминаний', 'schedule_notifications')],
        [create_callback_button('🔙 Назад', 'student_main')]
    ]
    return create_inline_keyboard(buttons)


def create_requests_main_keyboard() -> Dict[str, Any]:
    """Создает главное меню заявок студентов"""
    buttons = [
        [create_callback_button('📄 Заказать справку', 'request_certificate')],
        [create_callback_button('📝 Академический отпуск', 'request_academic_leave')],
        [create_callback_button('📋 Мои заявки', 'request_my_requests')],
        [create_callback_button('🔙 Назад', 'student_main')]
    ]
    return create_inline_keyboard(buttons)


def create_certificate_types_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру выбора типа справки"""
    buttons = [
        [create_callback_button('📚 Об обучении', 'certificate_study')],
        [create_callback_button('💰 О стипендии', 'certificate_scholarship')],
        [create_callback_button('🏫 С места учебы', 'certificate_enrollment')],
        [create_callback_button('🔙 Назад', 'student_requests')]
    ]
    return create_inline_keyboard(buttons)


def create_request_created_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру после создания заявки"""
    buttons = [
        [create_callback_button('📋 Мои заявки', 'request_my_requests')],
        [create_callback_button('➕ Новая заявка', 'request_certificate')],
        [create_callback_button('🔙 Главное меню', 'menu_main')]
    ]
    return create_inline_keyboard(buttons)


def create_my_requests_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру для просмотра заявок"""
    buttons = [
        [create_callback_button('🔄 Обновить', 'request_my_requests')],
        [create_callback_button('🔙 Главное меню', 'menu_main')]
    ]
    return create_inline_keyboard(buttons)


# ========== Клавиатуры для сотрудников ==========

def create_staff_main_keyboard() -> Dict[str, Any]:
    """Создает главное меню для сотрудников"""
    buttons = [
        [create_callback_button('✈️ Командировки', 'staff_business_trips')],
        [create_callback_button('🏖️ Отпуск', 'staff_vacation')],
        [create_callback_button('📋 Служебные запросы', 'staff_requests')],
        [create_callback_button('📅 Расписание', 'staff_schedule')],
        [create_callback_button('🔙 Вернуться', 'menu_main')]
    ]
    return create_inline_keyboard(buttons)


def create_business_trips_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру управления командировками"""
    buttons = [
        [create_callback_button('📝 Подать заявку', 'trip_create')],
        [create_callback_button('📋 Мои командировки', 'trip_my_trips')],
        [create_callback_button('📄 Отчет по командировке', 'trip_report')],
        [create_callback_button('🔙 Назад', 'staff_main')]
    ]
    return create_inline_keyboard(buttons)


def create_trip_dates_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру выбора дат командировки"""
    buttons = [
        [create_callback_button('📅 15.04.2025 - 18.04.2025', 'trip_date_15-18')],
        [create_callback_button('📅 Выбрать другие даты', 'trip_date_custom')],
        [create_callback_button('❌ Отмена', 'trip_cancel')]
    ]
    return create_inline_keyboard(buttons)


def create_trip_created_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру после создания заявки на командировку"""
    buttons = [
        [create_callback_button('📋 Мои заявки', 'trip_my_trips')],
        [create_callback_button('🔙 Главное меню', 'menu_main')]
    ]
    return create_inline_keyboard(buttons)


def create_my_trips_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру для просмотра командировок"""
    buttons = [
        [create_callback_button('🔄 Обновить', 'trip_my_trips')],
        [create_callback_button('🔙 Назад', 'staff_business_trips')]
    ]
    return create_inline_keyboard(buttons)


# ========== Клавиатуры для администраторов ==========

def create_admin_main_keyboard() -> Dict[str, Any]:
    """Создает главное меню для администраторов"""
    buttons = [
        [create_callback_button('📊 Дашборд', 'admin_dashboard')],
        [create_callback_button('📈 Аналитика', 'admin_analytics')],
        [create_callback_button('👁️ Мониторинг', 'admin_monitoring')],
        [create_callback_button('📰 Новости', 'admin_news')],
        [create_callback_button('🔙 Вернуться', 'menu_main')]
    ]
    return create_inline_keyboard(buttons)


def create_dashboard_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру для дашборда"""
    buttons = [
        [create_callback_button('📈 Подробная аналитика', 'admin_analytics')],
        [create_callback_button('📥 Экспорт данных', 'admin_export')],
        [create_callback_button('🔙 Главное меню', 'menu_main')]
    ]
    return create_inline_keyboard(buttons)


def create_analytics_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру выбора метрик для анализа"""
    buttons = [
        [create_callback_button('👥 Посещаемость по факультетам', 'analytics_attendance')],
        [create_callback_button('📚 Успеваемость', 'analytics_performance')],
        [create_callback_button('📋 Заявки и обращения', 'analytics_requests')],
        [create_callback_button('💰 Финансовые показатели', 'analytics_financial')],
        [create_callback_button('🔙 Назад', 'admin_main')]
    ]
    return create_inline_keyboard(buttons)


def create_attendance_analytics_keyboard() -> Dict[str, Any]:
    """Создает клавиатуру для аналитики посещаемости"""
    buttons = [
        [create_callback_button('📊 График', 'analytics_attendance_chart')],
        [create_callback_button('📈 Сравнение с прошлым месяцем', 'analytics_attendance_comparison')],
        [create_callback_button('🔙 Главное меню', 'menu_main')]
    ]
    return create_inline_keyboard(buttons)

