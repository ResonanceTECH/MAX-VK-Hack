"""Генерация клавиатур для бота"""
from typing import List, Dict, Optional
import os

def create_main_menu_keyboard(role: str, has_multiple_roles: bool = False) -> Dict:
    """Создать главное меню в зависимости от роли"""
    buttons = []
    
    # Если у пользователя несколько ролей, добавляем кнопку выбора роли
    if has_multiple_roles:
        buttons.append([{"type": "callback", "text": "🔄 Выбрать роль", "payload": "select_role"}])
        buttons.append([])  # Разделитель
    
    if role == 'student':
        buttons.extend([
            [{"type": "callback", "text": "👥 Моя группа", "payload": "menu_group"}],
            [{"type": "callback", "text": "👨‍🏫 Преподаватели", "payload": "menu_teachers"}],
            [{"type": "callback", "text": "📅 Расписание", "payload": "menu_schedule"}],
            [{"type": "callback", "text": "📢 Новости", "payload": "menu_news"}],
            [{"type": "callback", "text": "❓ Помощь", "payload": "help"}]
        ])
    elif role == 'teacher':
        buttons.extend([
            [{"type": "callback", "text": "👥 Мои группы", "payload": "menu_my_groups"}],
            [{"type": "callback", "text": "⭐ Старосты", "payload": "menu_headmen"}],
            [{"type": "callback", "text": "👨‍🏫 Преподаватели", "payload": "menu_teachers_teacher"}],
            [{"type": "callback", "text": "📅 Расписание", "payload": "menu_schedule"}],
            [{"type": "callback", "text": "📢 Новости", "payload": "menu_news_teacher"}],
            [{"type": "callback", "text": "❓ Помощь", "payload": "help"}]
        ])
    elif role == 'admin':
        buttons.extend([
            [{"type": "callback", "text": "👨‍🎓 Управление студентами", "payload": "admin_students"}],
            [{"type": "callback", "text": "👨‍🏫 Управление преподавателями", "payload": "admin_teachers"}],
            [{"type": "callback", "text": "👥 Группы", "payload": "admin_groups"}],
            [{"type": "callback", "text": "📢 Рассылки", "payload": "admin_broadcasts"}],
            [{"type": "callback", "text": "💬 Поддержка", "payload": "admin_support"}],
            [{"type": "callback", "text": "📊 Отчеты", "payload": "admin_reports"}],
            [{"type": "callback", "text": "❓ Помощь", "payload": "help"}]
        ])
    elif role == 'support':
        buttons.extend([
            [{"type": "callback", "text": "📋 Запросы в поддержку", "payload": "support_tickets"}],
            [{"type": "callback", "text": "📢 Сообщения", "payload": "support_messages"}],
            [{"type": "callback", "text": "❓ FAQ", "payload": "support_faq"}],
            [{"type": "callback", "text": "📊 Статистика", "payload": "support_stats"}],
            [{"type": "callback", "text": "❓ Помощь", "payload": "help"}]
        ])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_role_selection_keyboard(roles: List[Dict]) -> Dict:
    """Создать клавиатуру для выбора роли"""
    buttons = []
    role_names = {
        'student': '👨‍🎓 Студент',
        'teacher': '👨‍🏫 Преподаватель',
        'admin': '👑 Администратор'
    }
    
    for role_data in roles:
        role = role_data.get('role')
        role_name = role_names.get(role, role)
        buttons.append([{
            "type": "callback",
            "text": role_name,
            "payload": f"select_role_{role}"
        }])
    
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_groups_keyboard(groups: List[Dict], prefix: str = "group") -> Dict:
    """Создать клавиатуру со списком групп"""
    buttons = []
    for group in groups:
        buttons.append([{
            "type": "callback",
            "text": f"📚 {group['name']}",
            "payload": f"{prefix}_{group['id']}"
        }])
    
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_students_keyboard(students: List[Dict], group_id: int, for_student: bool = False) -> Dict:
    """Создать клавиатуру со списком студентов группы
    
    Args:
        students: Список студентов
        group_id: ID группы
        for_student: Если True, создает клавиатуру для студента (написать сокурснику)
    """
    buttons = []
    for student in students:
        headman_mark = "⭐ " if student.get('is_headman') else ""
        if for_student:
            # Для студента - кнопка написать сокурснику
            payload = f"write_student_{student['id']}_group_{group_id}"
        else:
            # Для преподавателя - обычная кнопка выбора
            payload = f"student_{student['id']}_group_{group_id}"
        buttons.append([{
            "type": "callback",
            "text": f"{headman_mark}{student['fio']}",
            "payload": payload
        }])
    
    back_payload = "menu_group" if for_student else "menu_my_groups"
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": back_payload}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_teachers_keyboard(teachers: List[Dict], for_student: bool = False, group_id: Optional[int] = None) -> Dict:
    """Создать клавиатуру со списком преподавателей
    
    Args:
        teachers: Список преподавателей
        for_student: Если True, создает клавиатуру для студента
        group_id: ID группы (для отправки сообщения от группы)
    """
    buttons = []
    for teacher in teachers:
        if for_student and group_id:
            # Для студента - кнопка написать преподавателю (от группы или лично)
            buttons.append([{
                "type": "callback",
                "text": f"👨‍🏫 {teacher['fio']}",
                "payload": f"teacher_{teacher['id']}"
            }])
        else:
            buttons.append([{
                "type": "callback",
                "text": f"👨‍🏫 {teacher['fio']}",
                "payload": f"teacher_{teacher['id']}"
            }])
    
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_back_keyboard(payload: str = "main_menu") -> Dict:
    """Создать кнопку 'Назад'"""
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": [[{"type": "callback", "text": "◀️ Назад", "payload": payload}]]
        }
    }

def create_cancel_keyboard() -> Dict:
    """Создать кнопку 'Отмена'"""
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": [[{"type": "callback", "text": "❌ Отмена", "payload": "cancel"}]]
        }
    }

def create_group_menu_keyboard(is_headman: bool = False) -> Dict:
    """Создать меню для группы студента"""
    buttons = [
        [{"type": "callback", "text": "👥 Список студентов", "payload": "group_students_list"}],
        [{"type": "callback", "text": "💬 Написать сокурснику", "payload": "group_write_student"}],
    ]
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_teachers_menu_keyboard(is_headman: bool = False) -> Dict:
    """Создать меню преподавателей для студента"""
    buttons = [
        [{"type": "callback", "text": "👨‍🏫 Список преподавателей", "payload": "teachers_list"}],
        [{"type": "callback", "text": "💬 Написать преподавателю", "payload": "write_teacher"}],
    ]
    if is_headman:
        buttons.append([{"type": "callback", "text": "💬 Написать от группы", "payload": "write_teacher_group"}])
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_schedule_menu_keyboard() -> Dict:
    """Создать меню расписания"""
    buttons = [
        [{"type": "callback", "text": "📅 На сегодня", "payload": "schedule_today"}],
        [{"type": "callback", "text": "📆 На неделю", "payload": "schedule_week"}],
        [{"type": "callback", "text": "⬇️ Скачать расписание", "payload": "schedule_download"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_news_menu_keyboard() -> Dict:
    """Создать меню новостей"""
    buttons = [
        [{"type": "callback", "text": "🏛️ Новости вуза", "payload": "news_university"}],
        [{"type": "callback", "text": "👥 Объявления группы", "payload": "news_group"}],
        [{"type": "callback", "text": "⚠️ Уведомления администрации", "payload": "news_admin"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_help_menu_keyboard(role: str = 'student') -> Dict:
    """Создать меню помощи"""
    buttons = [
        [{"type": "callback", "text": "❓ FAQ", "payload": "help_faq"}],
        [{"type": "callback", "text": "💬 Связь с поддержкой", "payload": "help_support"}],
    ]
    
    if role == 'student':
        buttons.append([{"type": "callback", "text": "📋 Частые вопросы", "payload": "help_common"}])
    elif role == 'teacher':
        buttons.append([{"type": "callback", "text": "⚙️ Настройки уведомлений", "payload": "help_notifications"}])
    
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_group_menu_teacher_keyboard() -> Dict:
    """Создать меню группы для преподавателя"""
    buttons = [
        [{"type": "callback", "text": "👥 Список студентов", "payload": "group_students_list_teacher"}],
        [{"type": "callback", "text": "💬 Написать студенту", "payload": "write_student"}],
        [{"type": "callback", "text": "📢 Рассылка группе", "payload": "broadcast_group"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "menu_my_groups"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_headmen_menu_keyboard() -> Dict:
    """Создать меню старост для преподавателя"""
    buttons = [
        [{"type": "callback", "text": "⭐ Список старост", "payload": "headmen_list"}],
        [{"type": "callback", "text": "📢 Рассылка старостам", "payload": "broadcast_headmen"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_headmen_keyboard(headmen: List[Dict]) -> Dict:
    """Создать клавиатуру со списком старост"""
    buttons = []
    for headman in headmen:
        group_name = headman.get('group_name', '')
        buttons.append([{
            "type": "callback",
            "text": f"⭐ {headman['fio']} ({group_name})",
            "payload": f"headman_{headman['id']}"
        }])
    
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "menu_headmen"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_teachers_teacher_keyboard(teachers: List[Dict]) -> Dict:
    """Создать клавиатуру со списком преподавателей для преподавателя"""
    buttons = []
    for teacher in teachers:
        buttons.append([{
            "type": "callback",
            "text": f"👨‍🏫 {teacher['fio']}",
            "payload": f"teacher_teacher_{teacher['id']}"
        }])
    
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_news_teacher_menu_keyboard() -> Dict:
    """Создать меню новостей для преподавателя"""
    buttons = [
        [{"type": "callback", "text": "🏛️ Новости кафедры", "payload": "news_department"}],
        [{"type": "callback", "text": "🏢 Новости института", "payload": "news_institute"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_admin_students_menu_keyboard() -> Dict:
    """Создать меню управления студентами для администратора"""
    buttons = [
        [{"type": "callback", "text": "➕ Добавить студента", "payload": "admin_student_add"}],
        [{"type": "callback", "text": "✏️ Редактировать студента", "payload": "admin_student_edit"}],
        [{"type": "callback", "text": "🗑️ Удалить студента", "payload": "admin_student_delete"}],
        [{"type": "callback", "text": "👥 Присвоить группу", "payload": "admin_student_assign_group"}],
        [{"type": "callback", "text": "📋 Просмотр контактов", "payload": "admin_student_contacts"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_admin_teachers_menu_keyboard() -> Dict:
    """Создать меню управления преподавателями для администратора"""
    buttons = [
        [{"type": "callback", "text": "➕ Добавить преподавателя", "payload": "admin_teacher_add"}],
        [{"type": "callback", "text": "✏️ Редактировать преподавателя", "payload": "admin_teacher_edit"}],
        [{"type": "callback", "text": "👥 Назначить группы", "payload": "admin_teacher_assign_groups"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_admin_groups_menu_keyboard() -> Dict:
    """Создать меню управления группами для администратора"""
    buttons = [
        [{"type": "callback", "text": "👥 Просмотр состава", "payload": "admin_group_view"}],
        [{"type": "callback", "text": "➕ Добавить студента в группу", "payload": "admin_group_add_student"}],
        [{"type": "callback", "text": "➖ Удалить студента из группы", "payload": "admin_group_remove_student"}],
        [{"type": "callback", "text": "👨‍🏫 Привязать преподавателя", "payload": "admin_group_assign_teacher"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_admin_broadcasts_menu_keyboard() -> Dict:
    """Создать меню рассылок для администратора"""
    buttons = [
        [{"type": "callback", "text": "📢 Массовая рассылка", "payload": "admin_broadcast_mass"}],
        [{"type": "callback", "text": "📝 Шаблоны сообщений", "payload": "admin_broadcast_templates"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_admin_reports_menu_keyboard() -> Dict:
    """Создать меню отчетов для администратора"""
    buttons = [
        [{"type": "callback", "text": "📊 Статистика активности", "payload": "admin_report_activity"}],
        [{"type": "callback", "text": "💬 Отчеты по сообщениям", "payload": "admin_report_messages"}],
        [{"type": "callback", "text": "👥 Отчеты по пользователям", "payload": "admin_report_users"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_admin_help_menu_keyboard() -> Dict:
    """Создать меню помощи для администратора"""
    buttons = [
        [{"type": "callback", "text": "📖 Инструкции", "payload": "admin_help_instructions"}],
        [{"type": "callback", "text": "💬 Связь с поддержкой", "payload": "help_support"}],
        [{"type": "callback", "text": "⚙️ Настройки уведомлений", "payload": "help_notifications"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_admin_support_menu_keyboard() -> Dict:
    """Создать меню поддержки для администратора"""
    buttons = [
        [{"type": "callback", "text": "📋 Запросы в поддержку", "payload": "admin_support_tickets"}],
        [{"type": "callback", "text": "📢 Сообщения", "payload": "admin_support_messages"}],
        [{"type": "callback", "text": "❓ FAQ", "payload": "admin_support_faq"}],
        [{"type": "callback", "text": "📊 Статистика", "payload": "admin_support_stats"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": "main_menu"}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_support_tickets_status_keyboard(role: str = 'admin') -> Dict:
    """Создать клавиатуру для фильтрации обращений по статусу"""
    prefix = 'admin_support' if role == 'admin' else 'support'
    back_payload = 'admin_support' if role == 'admin' else 'main_menu'
    
    buttons = [
        [{"type": "callback", "text": "🆕 Новые", "payload": f"{prefix}_tickets_new"}],
        [{"type": "callback", "text": "🔄 В работе", "payload": f"{prefix}_tickets_in_progress"}],
        [{"type": "callback", "text": "✅ Решено", "payload": f"{prefix}_tickets_resolved"}],
        [{"type": "callback", "text": "📋 Все обращения", "payload": f"{prefix}_tickets_all"}],
        [{"type": "callback", "text": "◀️ Назад", "payload": back_payload}]
    ]
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_support_tickets_list_keyboard(tickets: List[Dict], prefix: str = "admin_support_ticket", back_payload: str = "admin_support_tickets") -> Dict:
    """Создать клавиатуру со списком обращений"""
    buttons = []
    for ticket in tickets[:20]:  # Ограничиваем 20 записями
        ticket_id = ticket.get('id')
        subject = ticket.get('subject', 'Без темы')[:30]  # Обрезаем длинные темы
        status_emoji = {
            'new': '🆕',
            'in_progress': '🔄',
            'resolved': '✅'
        }.get(ticket.get('status', 'new'), '📋')
        
        buttons.append([{
            "type": "callback",
            "text": f"{status_emoji} {subject}",
            "payload": f"{prefix}_{ticket_id}"
        }])
    
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "admin_support_tickets"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_support_ticket_actions_keyboard(ticket_id: int, status: str, role: str = 'admin') -> Dict:
    """Создать клавиатуру действий для обращения"""
    prefix = 'admin_support' if role == 'admin' else 'support'
    back_payload = f"{prefix}_tickets"
    
    buttons = []
    
    if status == 'new':
        buttons.append([{"type": "callback", "text": "🔄 Взять в работу", "payload": f"{prefix}_ticket_take_{ticket_id}"}])
    elif status == 'in_progress':
        buttons.append([{"type": "callback", "text": "✅ Решить", "payload": f"{prefix}_ticket_resolve_{ticket_id}"}])
    
    buttons.append([{"type": "callback", "text": "💬 Написать пользователю", "payload": f"{prefix}_ticket_contact_{ticket_id}"}])
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": back_payload}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_faq_list_keyboard(faq_list: List[Dict], prefix: str = "admin_support_faq") -> Dict:
    """Создать клавиатуру со списком FAQ"""
    buttons = []
    for faq in faq_list[:20]:  # Ограничиваем 20 записями
        faq_id = faq.get('id')
        question = faq.get('question', 'Без вопроса')[:40]  # Обрезаем длинные вопросы
        
        buttons.append([{
            "type": "callback",
            "text": f"❓ {question}",
            "payload": f"{prefix}_view_{faq_id}"
        }])
    
    buttons.append([{"type": "callback", "text": "➕ Добавить FAQ", "payload": "admin_support_faq_add"}])
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "admin_support"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_students_list_keyboard(students: List[Dict], prefix: str = "admin_student") -> Dict:
    """Создать клавиатуру со списком студентов"""
    buttons = []
    for student in students[:20]:  # Ограничиваем 20 записями
        buttons.append([{
            "type": "callback",
            "text": f"👨‍🎓 {student['fio']}",
            "payload": f"{prefix}_{student['id']}"
        }])
    
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "admin_students"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_teachers_list_keyboard(teachers: List[Dict], prefix: str = "admin_teacher") -> Dict:
    """Создать клавиатуру со списком преподавателей"""
    buttons = []
    for teacher in teachers[:20]:  # Ограничиваем 20 записями
        buttons.append([{
            "type": "callback",
            "text": f"👨‍🏫 {teacher['fio']}",
            "payload": f"{prefix}_{teacher['id']}"
        }])
    
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "admin_teachers"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_groups_list_keyboard(groups: List[Dict], prefix: str = "admin_group") -> Dict:
    """Создать клавиатуру со списком групп"""
    buttons = []
    for group in groups[:20]:  # Ограничиваем 20 записями
        buttons.append([{
            "type": "callback",
            "text": f"👥 {group['name']}",
            "payload": f"{prefix}_{group['id']}"
        }])
    
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "admin_groups"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

