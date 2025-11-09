"""Генерация клавиатур для бота"""
from typing import List, Dict, Optional

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
            [{"type": "callback", "text": "💬 Написать преподавателю", "payload": "write_teacher"}],
            [{"type": "callback", "text": "❓ Помощь", "payload": "help"}]
        ])
    elif role == 'teacher':
        buttons.extend([
            [{"type": "callback", "text": "👥 Мои группы", "payload": "menu_my_groups"}],
            [{"type": "callback", "text": "💬 Написать студенту", "payload": "write_student"}],
            [{"type": "callback", "text": "📢 Рассылка группе", "payload": "broadcast_group"}],
            [{"type": "callback", "text": "❓ Помощь", "payload": "help"}]
        ])
    elif role == 'admin':
        buttons.extend([
            [{"type": "callback", "text": "💬 Написать пользователю", "payload": "admin_write"}],
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

def create_students_keyboard(students: List[Dict], group_id: int) -> Dict:
    """Создать клавиатуру со списком студентов группы"""
    buttons = []
    for student in students:
        headman_mark = "⭐ " if student.get('is_headman') else ""
        buttons.append([{
            "type": "callback",
            "text": f"{headman_mark}{student['fio']}",
            "payload": f"student_{student['id']}_group_{group_id}"
        }])
    
    buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "menu_my_groups"}])
    
    return {
        "type": "inline_keyboard",
        "payload": {
            "buttons": buttons
        }
    }

def create_teachers_keyboard(teachers: List[Dict]) -> Dict:
    """Создать клавиатуру со списком преподавателей"""
    buttons = []
    for teacher in teachers:
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

