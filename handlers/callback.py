"""Обработчик нажатий на кнопки"""
from handlers.base import BaseHandler
from db.models import User, Group, Teacher, SupportTicket, FAQ, AdminMessage
from db.connection import execute_query
from utils.keyboard import (
    create_main_menu_keyboard, create_groups_keyboard, 
    create_students_keyboard, create_teachers_keyboard,
    create_back_keyboard, create_cancel_keyboard,
    create_role_selection_keyboard, create_group_menu_keyboard,
    create_teachers_menu_keyboard, create_schedule_menu_keyboard,
    create_news_menu_keyboard, create_help_menu_keyboard,
    create_group_menu_teacher_keyboard, create_headmen_menu_keyboard,
    create_headmen_keyboard, create_teachers_teacher_keyboard,
    create_news_teacher_menu_keyboard,
    create_admin_students_menu_keyboard, create_admin_teachers_menu_keyboard,
    create_admin_groups_menu_keyboard, create_admin_broadcasts_menu_keyboard,
    create_admin_reports_menu_keyboard, create_admin_help_menu_keyboard,
    create_students_list_keyboard, create_teachers_list_keyboard,
    create_groups_list_keyboard,
    create_admin_support_menu_keyboard, create_support_tickets_status_keyboard,
    create_support_tickets_list_keyboard, create_support_ticket_actions_keyboard,
    create_faq_list_keyboard
)
from utils.states import set_state, clear_state, set_user_role, get_user_role, get_state
from typing import Dict, Any
import logging
import httpx
import os

logger = logging.getLogger(__name__)

# URL для API расписания
SCHEDULE_API_URL = os.getenv("SCHEDULE_API_URL", "http://schedule:8001/schedule_1")


def get_schedule_from_api(query: str) -> Dict:
    """Получить расписание из API"""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(SCHEDULE_API_URL, params={"query": query})
            # Если 404 - значит расписание не найдено (нет пар)
            if response.status_code == 404:
                return {}
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        # Если 404 - значит расписание не найдено (нет пар)
        if e.response.status_code == 404:
            return {}
        logger.error(f"Ошибка при получении расписания: {e}")
        return {}
    except Exception as e:
        logger.error(f"Ошибка при получении расписания: {e}")
        return {}


def format_teacher_name_for_schedule(fio: str) -> str:
    """Преобразовать ФИО в формат для расписания (Фамилия И. О.)
    
    Входной формат: "Фамилия Имя Отчество" или "Фамилия Имя"
    Выходной формат: "Фамилия И. О." или "Фамилия И."
    """
    if not fio:
        return ""
    
    # Убираем лишние пробелы и разбиваем на части
    parts = [p.strip() for p in fio.strip().split() if p.strip()]
    
    if len(parts) >= 2:
        last_name = parts[0]
        first_name = parts[1]
        middle_name = parts[2] if len(parts) > 2 else None
        
        # Берем первую букву имени (в верхнем регистре)
        first_initial = first_name[0].upper() if first_name else ""
        
        # Берем первую букву отчества (в верхнем регистре), если есть
        if middle_name:
            middle_initial = middle_name[0].upper()
            return f"{last_name} {first_initial}. {middle_initial}."
        else:
            return f"{last_name} {first_initial}."
    elif len(parts) == 1:
        # Если только фамилия, возвращаем как есть
        return parts[0]
    
    return fio


class CallbackHandler(BaseHandler):
    """Обработчик нажатий на кнопки"""
    
    def can_handle(self, update: Dict[str, Any]) -> bool:
        return update.get('update_type') == 'message_callback'
    
    def handle(self, update: Dict[str, Any], api) -> None:
        callback = update.get('callback', {})
        user = callback.get('user', {})
        max_user_id = user.get('user_id')
        first_name = user.get('first_name', 'Unknown')
        payload = callback.get('payload', '')
        callback_id = callback.get('callback_id', '')
        
        if not max_user_id or not self.is_user_verified(max_user_id):
            # Отвечаем на callback, чтобы убрать индикатор загрузки
            if callback_id:
                api.answer_callback(callback_id)
            return
        
        # Получаем сохраненную роль или используем приоритетную
        saved_role = get_user_role(max_user_id)
        user_data = User.get_by_max_id(max_user_id, saved_role) if saved_role else User.get_by_max_id(max_user_id)
        if not user_data:
            if callback_id:
                api.answer_callback(callback_id)
            return
        
        # Отвечаем на callback сразу, чтобы убрать индикатор загрузки
        if callback_id:
            api.answer_callback(callback_id)
        
        # Определяем действие для логирования
        action_map = {
            'main_menu': 'главное_меню',
            'start_after_greeting': 'начало_после_приветствия',
            'select_role': 'выбор_роли',
            'menu_group': 'просмотр_групп',
            'menu_teachers': 'просмотр_преподавателей',
            'menu_my_groups': 'просмотр_моих_групп',
            'write_teacher': 'выбор_преподавателя_для_сообщения',
            'write_student': 'выбор_студента_для_сообщения',
            'broadcast_group': 'выбор_группы_для_рассылки',
            'help': 'просмотр_справки',
            'cancel': 'отмена'
        }
        
        action = action_map.get(payload, payload)
        if payload.startswith('select_role_'):
            action = 'переключение_роли'
        elif payload.startswith('group_') and not payload.startswith('group_message'):
            action = 'просмотр_участников_группы'
        elif payload.startswith('broadcast_group_'):
            action = 'начало_рассылки_группе'
        elif payload.startswith('teacher_'):
            action = 'начало_диалога_с_преподавателем'
        elif payload.startswith('student_'):
            action = 'начало_диалога_со_студентом'
        elif payload.startswith('group_message_select_'):
            action = 'выбор_преподавателя_для_сообщения_от_группы'
        elif payload.startswith('group_message_'):
            action = 'начало_отправки_сообщения_от_группы'
        
        logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action={action}")
        
        # Обработка payload
        if payload == 'main_menu':
            self.show_main_menu(user_data, max_user_id, api)
        elif payload == 'start_after_greeting':
            self.handle_start_after_greeting(user_data, max_user_id, api)
        elif payload == 'select_role':
            self.show_role_selection(max_user_id, api)
        elif payload.startswith('select_role_'):
            role = payload.split('_')[2]
            self.switch_role(max_user_id, role, api)
        elif payload == 'menu_group':
            self.show_group_menu(user_data, max_user_id, api)
        elif payload == 'menu_teachers':
            self.show_teachers_menu(user_data, max_user_id, api)
        elif payload == 'menu_schedule':
            self.show_schedule_menu(user_data, max_user_id, api)
        elif payload == 'menu_news':
            self.show_news_menu(user_data, max_user_id, api)
        elif payload == 'group_students_list':
            self.show_user_groups(user_data, max_user_id, api)
        elif payload == 'group_write_student':
            self.show_group_for_write_student(user_data, max_user_id, api)
        elif payload.startswith('write_student_'):
            # Написать сокурснику
            parts = payload.split('_')
            student_id = int(parts[2])
            group_id = int(parts[4]) if len(parts) > 4 else None
            self.start_student_to_student_chat(student_id, group_id, user_data, max_user_id, api)
        elif payload == 'teachers_list':
            self.show_teachers(user_data, max_user_id, api)
        elif payload == 'write_teacher_group':
            self.show_group_for_group_message(user_data, max_user_id, api)
        elif payload.startswith('schedule_today'):
            self.show_schedule_today(user_data, max_user_id, api)
        elif payload.startswith('schedule_week'):
            self.show_schedule_week(user_data, max_user_id, api)
        elif payload.startswith('schedule_download'):
            self.download_schedule(user_data, max_user_id, api)
        elif payload.startswith('news_university'):
            self.show_news_university(user_data, max_user_id, api)
        elif payload.startswith('news_group'):
            self.show_news_group(user_data, max_user_id, api)
        elif payload.startswith('news_admin'):
            self.show_news_admin(user_data, max_user_id, api)
        elif payload.startswith('help_faq'):
            self.show_help_faq(user_data, max_user_id, api)
        elif payload.startswith('help_support'):
            self.show_help_support(user_data, max_user_id, api)
        elif payload.startswith('help_common'):
            self.show_help_common(user_data, max_user_id, api)
        elif payload == 'menu_my_groups':
            self.show_teacher_groups_menu(user_data, max_user_id, api)
        elif payload == 'menu_headmen':
            self.show_headmen_menu(user_data, max_user_id, api)
        elif payload == 'menu_teachers_teacher':
            self.show_teachers_teacher(user_data, max_user_id, api)
        elif payload == 'menu_news_teacher':
            self.show_news_teacher_menu(user_data, max_user_id, api)
        elif payload == 'group_students_list_teacher':
            # Показываем выбор группы для просмотра студентов
            groups = Teacher.get_teacher_groups(user_data['id'])
            if not groups:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ У вас нет назначенных групп",
                    attachments=[create_back_keyboard("menu_my_groups")]
                )
                return
            
            if len(groups) == 1:
                # Если одна группа - показываем список студентов сразу
                self.show_group_members(groups[0]['id'], user_data, max_user_id, api)
            else:
                # Если несколько групп - показываем выбор
                text = "👥 Выберите группу для просмотра студентов:\n\n"
                for group in groups:
                    text += f"📚 {group['name']}\n"
                
                keyboard = create_groups_keyboard(groups, prefix="group_students")
                api.send_message(
                    user_id=max_user_id,
                    text=text,
                    attachments=[keyboard]
                )
        elif payload == 'headmen_list':
            self.show_headmen_list(user_data, max_user_id, api)
        elif payload.startswith('headman_'):
            headman_id = int(payload.split('_')[1])
            self.show_headman_info(headman_id, user_data, max_user_id, api)
        elif payload == 'broadcast_headmen':
            self.start_broadcast_headmen(user_data, max_user_id, api)
        elif payload.startswith('teacher_teacher_'):
            teacher_id = int(payload.split('_')[2])
            self.show_teacher_info(teacher_id, user_data, max_user_id, api)
        elif payload.startswith('news_department'):
            self.show_news_department(user_data, max_user_id, api)
        elif payload.startswith('news_institute'):
            self.show_news_institute(user_data, max_user_id, api)
        elif payload.startswith('help_notifications'):
            self.show_help_notifications(user_data, max_user_id, api)
        elif payload.startswith('group_') and not payload.startswith('group_message'):
            group_id = int(payload.split('_')[1])
            # Проверяем, откуда пришел запрос
            if user_data['role'] == 'student':
                # Если студент - показываем список студентов группы
                self.show_group_students_list(group_id, user_data, max_user_id, api)
            elif user_data['role'] == 'teacher':
                # Если преподаватель - показываем меню группы
                keyboard = create_group_menu_teacher_keyboard()
                group = Group.get_by_id(group_id)
                text = f"👥 Группа: {group['name'] if group else ''}\n\nВыберите действие:"
                api.send_message(
                    user_id=max_user_id,
                    text=text,
                    attachments=[keyboard]
                )
            else:
                # Если преподаватель - показываем список студентов для выбора
                self.show_group_members(group_id, user_data, max_user_id, api)
        elif payload.startswith('group_students_'):
            # Просмотр студентов группы (для преподавателя)
            group_id = int(payload.split('_')[2])
            self.show_group_members(group_id, user_data, max_user_id, api)
        elif payload.startswith('group_write_student_'):
            group_id = int(payload.split('_')[3])
            self.show_students_for_write(group_id, user_data, max_user_id, api)
        elif payload.startswith('broadcast_group_'):
            group_id = int(payload.split('_')[2])
            self.start_broadcast(group_id, user_data, max_user_id, api)
        elif payload.startswith('teacher_'):
            teacher_id = int(payload.split('_')[1])
            self.start_teacher_chat(teacher_id, user_data, max_user_id, api)
        elif payload.startswith('student_'):
            parts = payload.split('_')
            student_id = int(parts[1])
            group_id = int(parts[3]) if len(parts) > 3 else None
            self.start_student_chat(student_id, group_id, user_data, max_user_id, api)
        elif payload.startswith('group_message_select_'):
            group_id = int(payload.split('_')[3])
            self.select_teacher_for_group_message(group_id, user_data, max_user_id, api)
        elif payload.startswith('group_message_'):
            parts = payload.split('_')
            group_id = int(parts[2])
            teacher_id = int(parts[3])
            self.start_group_message(group_id, teacher_id, user_data, max_user_id, api)
        elif payload == 'write_teacher':
            self.show_teachers(user_data, max_user_id, api)
        elif payload == 'write_student':
            self.show_teacher_groups(user_data, max_user_id, api)
        elif payload == 'broadcast_group':
            self.show_teacher_groups(user_data, max_user_id, api, broadcast=True)
        elif payload.startswith('write_student_'):
            # Написать студенту (может быть из разных мест)
            parts = payload.split('_')
            student_id = int(parts[2])
            self.start_student_chat(student_id, None, user_data, max_user_id, api)
        elif payload == 'admin_students':
            self.show_admin_students_menu(user_data, max_user_id, api)
        elif payload == 'admin_teachers':
            self.show_admin_teachers_menu(user_data, max_user_id, api)
        elif payload == 'admin_groups':
            self.show_admin_groups_menu(user_data, max_user_id, api)
        elif payload == 'admin_broadcasts':
            self.show_admin_broadcasts_menu(user_data, max_user_id, api)
        elif payload == 'admin_reports':
            self.show_admin_reports_menu(user_data, max_user_id, api)
        elif payload.startswith('admin_student_'):
            self.handle_admin_student_action(payload, user_data, max_user_id, api)
        elif payload.startswith('admin_teacher_'):
            self.handle_admin_teacher_action(payload, user_data, max_user_id, api)
        elif payload.startswith('admin_group_'):
            self.handle_admin_group_action(payload, user_data, max_user_id, api)
        elif payload.startswith('admin_broadcast_'):
            self.handle_admin_broadcast_action(payload, user_data, max_user_id, api)
        elif payload.startswith('admin_report_'):
            self.handle_admin_report_action(payload, user_data, max_user_id, api)
        elif payload.startswith('admin_help_'):
            self.handle_admin_help_action(payload, user_data, max_user_id, api)
        elif payload == 'admin_support':
            self.show_admin_support_menu(user_data, max_user_id, api)
        elif payload.startswith('admin_support_'):
            self.handle_admin_support_action(payload, user_data, max_user_id, api)
        elif payload.startswith('support_'):
            self.handle_support_action(payload, user_data, max_user_id, api)
        elif payload == 'help':
            self.show_help(user_data['role'], max_user_id, api)
        elif payload == 'cancel':
            clear_state(max_user_id)
            self.show_main_menu(user_data, max_user_id, api)
    
    def handle_start_after_greeting(self, user: Dict, max_user_id: int, api):
        """Обработать нажатие кнопки 'Начать' после приветствия"""
        # Получаем все роли пользователя
        all_roles = User.get_all_roles(max_user_id)
        
        if not all_roles:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет назначенных ролей. Обратитесь к администрации."
            )
            return
        
        # Если одна роль - показываем главное меню с этой ролью
        if len(all_roles) == 1:
            role_data = all_roles[0]
            role = role_data.get('role')
            # Сохраняем роль
            set_user_role(max_user_id, role)
            
            greeting = {
                'student': f"👋 Привет, {role_data['fio']}!\n\nВыберите действие:",
                'teacher': f"👋 Здравствуйте, {role_data['fio']}!\n\nВыберите действие:",
                'admin': f"👋 Администратор {role_data['fio']}\n\nВыберите действие:",
                'support': f"👋 Поддержка {role_data['fio']}\n\nВыберите действие:"
            }
            
            keyboard = create_main_menu_keyboard(role, has_multiple_roles=False)
            api.send_message(
                user_id=max_user_id,
                text=greeting.get(role, "Выберите действие:"),
                attachments=[keyboard]
            )
        else:
            # Если несколько ролей - показываем выбор роли
            keyboard = create_role_selection_keyboard(all_roles)
            api.send_message(
                user_id=max_user_id,
                text="Выберите роль:",
                attachments=[keyboard]
            )
    
    def show_main_menu(self, user: Dict, max_user_id: int, api):
        """Показать главное меню"""
        # Проверяем, есть ли у пользователя несколько ролей
        all_roles = User.get_all_roles(max_user_id)
        has_multiple_roles = len(all_roles) > 1
        
        keyboard = create_main_menu_keyboard(user['role'], has_multiple_roles)
        api.send_message(
            user_id=max_user_id,
            text="Главное меню:",
            attachments=[keyboard]
        )
    
    def show_role_selection(self, max_user_id: int, api):
        """Показать выбор роли"""
        all_roles = User.get_all_roles(max_user_id)
        if len(all_roles) <= 1:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас только одна роль",
                attachments=[create_back_keyboard()]
            )
            return
        
        keyboard = create_role_selection_keyboard(all_roles)
        api.send_message(
            user_id=max_user_id,
            text="🔄 Выберите роль:",
            attachments=[keyboard]
        )
    
    def switch_role(self, max_user_id: int, role: str, api):
        """Переключиться на другую роль"""
        user = User.get_by_max_id(max_user_id, role)
        if not user:
            api.send_message(
                user_id=max_user_id,
                text="❌ Роль не найдена",
                attachments=[create_back_keyboard()]
            )
            return
        
        # Сохраняем выбранную роль
        set_user_role(max_user_id, role)
        
        # Показываем главное меню с новой ролью
        all_roles = User.get_all_roles(max_user_id)
        has_multiple_roles = len(all_roles) > 1
        
        greeting = {
            'student': f"👋 Привет, {user['fio']}!\n\nВыберите действие:",
            'teacher': f"👋 Здравствуйте, {user['fio']}!\n\nВыберите действие:",
            'admin': f"👋 Администратор {user['fio']}\n\nВыберите действие:",
            'support': f"👋 Поддержка {user['fio']}\n\nВыберите действие:"
        }
        
        keyboard = create_main_menu_keyboard(role, has_multiple_roles)
        api.send_message(
            user_id=max_user_id,
            text=f"✅ Роль изменена на: {role}\n\n{greeting.get(role, 'Выберите действие:')}",
            attachments=[keyboard]
        )
    
    def show_group_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню группы студента"""
        groups = Group.get_user_groups(user['id'])
        if not groups:
            api.send_message(
                user_id=max_user_id,
                text="❌ Вы не состоите ни в одной группе",
                attachments=[create_back_keyboard()]
            )
            return
        
        # Если одна группа - показываем меню сразу
        if len(groups) == 1:
            group = groups[0]
            is_headman = group.get('is_headman', False)
            keyboard = create_group_menu_keyboard(is_headman)
            text = f"👥 Группа: {group['name']}\n\nВыберите действие:"
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
        else:
            # Если несколько групп - показываем выбор
            text = "👥 Ваши группы:\n\n"
            for group in groups:
                headman = "⭐ Вы староста в " if group.get('is_headman') else ""
                text += f"{headman}📚 {group['name']}\n"
            
            keyboard = create_groups_keyboard(groups, prefix="group")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
    
    def show_user_groups(self, user: Dict, max_user_id: int, api):
        """Показать группы студента (для выбора группы)"""
        groups = Group.get_user_groups(user['id'])
        if not groups:
            api.send_message(
                user_id=max_user_id,
                text="❌ Вы не состоите ни в одной группе",
                attachments=[create_back_keyboard("menu_group")]
            )
            return
        
        # Если одна группа - показываем список студентов сразу
        if len(groups) == 1:
            group = groups[0]
            self.show_group_students_list(group['id'], user, max_user_id, api)
        else:
            text = "👥 Выберите группу:\n\n"
            for group in groups:
                headman = "⭐ Вы староста в " if group.get('is_headman') else ""
                text += f"{headman}📚 {group['name']}\n"
            
            keyboard = create_groups_keyboard(groups, prefix="group")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
    
    def show_group_students_list(self, group_id: int, user: Dict, max_user_id: int, api):
        """Показать список студентов группы"""
        members = Group.get_group_members(group_id)
        group = Group.get_by_id(group_id)
        
        if not members:
            api.send_message(
                user_id=max_user_id,
                text="❌ В группе нет участников",
                attachments=[create_back_keyboard("menu_group")]
            )
            return
        
        text = f"👥 Участники группы {group['name'] if group else ''}:\n\n"
        for member in members:
            headman = "⭐ Староста: " if member.get('is_headman') else ""
            text += f"{headman}{member['fio']}\n"
            if member.get('max_user_id'):
                text += f"   👤 [Профиль](max://user/{member['max_user_id']})\n"
            text += "\n"
        
        keyboard = {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [[{"type": "callback", "text": "◀️ Назад", "payload": "menu_group"}]]
            }
        }
        
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard],
            format_type="markdown"
        )
    
    def show_group_for_write_student(self, user: Dict, max_user_id: int, api):
        """Показать выбор группы для написания сокурснику"""
        groups = Group.get_user_groups(user['id'])
        if not groups:
            api.send_message(
                user_id=max_user_id,
                text="❌ Вы не состоите ни в одной группе",
                attachments=[create_back_keyboard("menu_group")]
            )
            return
        
        if len(groups) == 1:
            group = groups[0]
            self.show_students_for_write(group['id'], user, max_user_id, api)
        else:
            text = "👥 Выберите группу:\n\n"
            for group in groups:
                text += f"📚 {group['name']}\n"
            
            keyboard = create_groups_keyboard(groups, prefix="group_write_student")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
    
    def show_students_for_write(self, group_id: int, user: Dict, max_user_id: int, api):
        """Показать список студентов для написания"""
        members = Group.get_group_members(group_id)
        group = Group.get_by_id(group_id)
        
        # Исключаем самого пользователя из списка
        members = [m for m in members if m['id'] != user['id']]
        
        if not members:
            api.send_message(
                user_id=max_user_id,
                text="❌ В группе нет других студентов",
                attachments=[create_back_keyboard("menu_group")]
            )
            return
        
        keyboard = create_students_keyboard(members, group_id, for_student=True)
        text = f"💬 Выберите сокурсника для отправки сообщения:\n\nГруппа: {group['name'] if group else ''}"
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def start_student_to_student_chat(self, student_id: int, group_id: int, user: Dict, max_user_id: int, api):
        """Начать диалог студента со студентом"""
        student = User.get_by_id(student_id)
        if not student:
            api.send_message(
                user_id=max_user_id,
                text="❌ Студент не найден",
                attachments=[create_back_keyboard("menu_group")]
            )
            return
        
        set_state(max_user_id, 'waiting_message_to_student_student', {'student_id': student_id})
        api.send_message(
            user_id=max_user_id,
            text=f"💬 Напишите сообщение для {student['fio']}:\n\n(Отправьте текст сообщения или напишите 'отмена' для отмены)",
            attachments=[create_cancel_keyboard()]
        )
    
    def show_group_members(self, group_id: int, user: Dict, max_user_id: int, api):
        """Показать участников группы"""
        members = Group.get_group_members(group_id)
        group = Group.get_by_id(group_id)
        
        if not members:
            api.send_message(
                user_id=max_user_id,
                text="❌ В группе нет участников",
                attachments=[create_back_keyboard("menu_group" if user['role'] == 'student' else "menu_my_groups")]
            )
            return
        
        # Если преподаватель - показываем список студентов с кнопками для выбора
        if user['role'] == 'teacher':
            # get_group_members уже возвращает только студентов
            if not members:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ В группе нет студентов",
                    attachments=[create_back_keyboard("menu_my_groups")]
                )
                return
            
            keyboard = create_students_keyboard(members, group_id)
            text = f"👥 Студенты группы {group['name'] if group else ''}:\n\nВыберите студента для отправки сообщения:"
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
            return
        
        # Для студентов - показываем список участников
        text = f"👥 Участники группы {group['name'] if group else ''}:\n\n"
        for member in members:
            headman = "⭐ Староста: " if member.get('is_headman') else ""
            text += f"{headman}{member['fio']}\n"
            if member.get('max_user_id'):
                text += f"   👤 [Профиль](max://user/{member['max_user_id']})\n"
            text += "\n"
        
        # Если пользователь - староста, добавляем кнопку отправки сообщения от группы
        buttons = []
        if user['role'] == 'student' and Group.is_headman(user['id'], group_id):
            # Получаем преподавателей группы
            teachers = Teacher.get_student_teachers(user['id'])
            if teachers:
                buttons.append([{
                    "type": "callback",
                    "text": "💬 Написать преподавателю от группы",
                    "payload": f"group_message_select_{group_id}"
                }])
        
        buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "menu_group" if user['role'] == 'student' else "menu_my_groups"}])
        
        keyboard = {
            "type": "inline_keyboard",
            "payload": {"buttons": buttons}
        }
        
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard],
            format_type="markdown"
        )
    
    def show_teachers_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню преподавателей для студента"""
        groups = Group.get_user_groups(user['id'])
        is_headman = any(g.get('is_headman', False) for g in groups)
        
        keyboard = create_teachers_menu_keyboard(is_headman)
        api.send_message(
            user_id=max_user_id,
            text="👨‍🏫 Преподаватели\n\nВыберите действие:",
            attachments=[keyboard]
        )
    
    def show_teachers(self, user: Dict, max_user_id: int, api):
        """Показать список преподавателей студента"""
        teachers = Teacher.get_student_teachers(user['id'])
        if not teachers:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет назначенных преподавателей",
                attachments=[create_back_keyboard("menu_teachers")]
            )
            return
        
        text = "👨‍🏫 Ваши преподаватели:\n\n"
        for teacher in teachers:
            text += f"• {teacher['fio']}\n"
            if teacher.get('phone'):
                text += f"  📞 {teacher['phone']}\n"
            if teacher.get('email'):
                text += f"  📧 {teacher['email']}\n"
            if teacher.get('max_user_id'):
                text += f"  👤 [Профиль](max://user/{teacher['max_user_id']})\n"
            text += "\n"
        
        keyboard = create_teachers_keyboard(teachers, for_student=True)
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard],
            format_type="markdown"
        )
    
    def show_group_for_group_message(self, user: Dict, max_user_id: int, api):
        """Показать выбор группы для отправки сообщения от группы"""
        groups = Group.get_user_groups(user['id'])
        headman_groups = [g for g in groups if g.get('is_headman', False)]
        
        if not headman_groups:
            api.send_message(
                user_id=max_user_id,
                text="❌ Вы не являетесь старостой ни в одной группе",
                attachments=[create_back_keyboard("menu_teachers")]
            )
            return
        
        if len(headman_groups) == 1:
            group = headman_groups[0]
            teachers = Teacher.get_student_teachers(user['id'])
            if not teachers:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ У вас нет назначенных преподавателей",
                    attachments=[create_back_keyboard("menu_teachers")]
                )
                return
            
            text = "👨‍🏫 Выберите преподавателя для отправки сообщения от группы:\n\n"
            buttons = []
            for teacher in teachers:
                buttons.append([{
                    "type": "callback",
                    "text": f"👨‍🏫 {teacher['fio']}",
                    "payload": f"group_message_{group['id']}_{teacher['id']}"
                }])
            buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "menu_teachers"}])
            
            keyboard = {
                "type": "inline_keyboard",
                "payload": {"buttons": buttons}
            }
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
        else:
            text = "👥 Выберите группу:\n\n"
            for group in headman_groups:
                text += f"📚 {group['name']}\n"
            
            buttons = []
            for group in headman_groups:
                buttons.append([{
                    "type": "callback",
                    "text": f"📚 {group['name']}",
                    "payload": f"group_message_select_{group['id']}"
                }])
            buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "menu_teachers"}])
            
            keyboard = {
                "type": "inline_keyboard",
                "payload": {"buttons": buttons}
            }
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
    
    def show_teacher_groups_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню групп преподавателя"""
        groups = Teacher.get_teacher_groups(user['id'])
        if not groups:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет назначенных групп",
                attachments=[create_back_keyboard()]
            )
            return
        
        # Всегда показываем список групп, чтобы кнопка "Назад" работала корректно
        text = "👥 Ваши группы:\n\n"
        for group in groups:
            text += f"📚 {group['name']}\n"
        
        keyboard = create_groups_keyboard(groups, prefix="group")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_teacher_groups(self, user: Dict, max_user_id: int, api, broadcast=False):
        """Показать группы преподавателя (для выбора)"""
        groups = Teacher.get_teacher_groups(user['id'])
        if not groups:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет назначенных групп",
                attachments=[create_back_keyboard("menu_my_groups")]
            )
            return
        
        # Если одна группа - показываем список студентов сразу
        if len(groups) == 1:
            group = groups[0]
            if broadcast:
                self.start_broadcast(group['id'], user, max_user_id, api)
            else:
                self.show_group_members(group['id'], user, max_user_id, api)
        else:
            text = "📚 Ваши группы:\n\n" if not broadcast else "📚 Выберите группу для рассылки:\n\n"
            for group in groups:
                text += f"• {group['name']}\n"
            
            prefix = "broadcast_group" if broadcast else "group"
            keyboard = create_groups_keyboard(groups, prefix=prefix)
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
    
    def start_teacher_chat(self, teacher_id: int, user: Dict, max_user_id: int, api):
        """Начать диалог с преподавателем"""
        teacher = Teacher.get_teacher_by_id(teacher_id)
        if not teacher:
            api.send_message(
                user_id=max_user_id,
                text="❌ Преподаватель не найден",
                attachments=[create_back_keyboard("menu_teachers")]
            )
            return
        
        set_state(max_user_id, 'waiting_message_to_teacher', {'teacher_id': teacher_id})
        api.send_message(
            user_id=max_user_id,
            text=f"💬 Напишите сообщение для преподавателя {teacher['fio']}:\n\n(Отправьте текст сообщения или напишите 'отмена' для отмены)",
            attachments=[create_cancel_keyboard()]
        )
    
    def start_student_chat(self, student_id: int, group_id: int, user: Dict, max_user_id: int, api):
        """Начать диалог со студентом"""
        student = User.get_by_id(student_id)
        if not student:
            api.send_message(
                user_id=max_user_id,
                text="❌ Студент не найден",
                attachments=[create_back_keyboard()]
            )
            return
        
        set_state(max_user_id, 'waiting_message_to_student', {'student_id': student_id})
        api.send_message(
            user_id=max_user_id,
            text=f"💬 Напишите сообщение для студента {student['fio']}:\n\n(Отправьте текст сообщения или напишите 'отмена' для отмены)",
            attachments=[create_cancel_keyboard()]
        )
    
    def start_broadcast(self, group_id: int, user: Dict, max_user_id: int, api):
        """Начать рассылку группе"""
        group = Group.get_by_id(group_id)
        if not group:
            api.send_message(
                user_id=max_user_id,
                text="❌ Группа не найдена",
                attachments=[create_back_keyboard()]
            )
            return
        
        set_state(max_user_id, 'waiting_broadcast_message', {'group_id': group_id})
        api.send_message(
            user_id=max_user_id,
            text=f"📢 Напишите сообщение для рассылки группе {group['name']}:\n\n(Отправьте текст сообщения или напишите 'отмена' для отмены)",
            attachments=[create_cancel_keyboard()]
        )
    
    def select_teacher_for_group_message(self, group_id: int, user: Dict, max_user_id: int, api):
        """Выбрать преподавателя для отправки сообщения от группы"""
        teachers = Teacher.get_student_teachers(user['id'])
        if not teachers:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет назначенных преподавателей",
                attachments=[create_back_keyboard()]
            )
            return
        
        text = "👨‍🏫 Выберите преподавателя для отправки сообщения от группы:\n\n"
        buttons = []
        for teacher in teachers:
            buttons.append([{
                "type": "callback",
                "text": f"👨‍🏫 {teacher['fio']}",
                "payload": f"group_message_{group_id}_{teacher['id']}"
            }])
        buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "menu_group"}])
        
        keyboard = {
            "type": "inline_keyboard",
            "payload": {"buttons": buttons}
        }
        
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def start_group_message(self, group_id: int, teacher_id: int, user: Dict, max_user_id: int, api):
        """Начать отправку сообщения от имени группы"""
        group = Group.get_by_id(group_id)
        teacher = User.get_by_id(teacher_id)
        
        if not group or not teacher:
            api.send_message(
                user_id=max_user_id,
                text="❌ Ошибка: группа или преподаватель не найдены",
                attachments=[create_back_keyboard()]
            )
            return
        
        set_state(max_user_id, 'waiting_group_message', {
            'group_id': group_id,
            'teacher_id': teacher_id
        })
        api.send_message(
            user_id=max_user_id,
            text=f"💬 Напишите сообщение от имени группы {group['name']} для преподавателя {teacher['fio']}:\n\n(Отправьте текст сообщения или напишите 'отмена' для отмены)",
            attachments=[create_cancel_keyboard()]
        )
    
    def show_schedule_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню расписания"""
        keyboard = create_schedule_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="📅 Расписание\n\nВыберите действие:",
            attachments=[keyboard]
        )
    
    def show_schedule_today(self, user: Dict, max_user_id: int, api):
        """Показать расписание на сегодня"""
        from datetime import datetime
        today = datetime.now()
        today_str = today.strftime("%d.%m.%Y")
        weekday = today.strftime("%A")
        weekday_ru = {
            'Monday': 'Понедельник',
            'Tuesday': 'Вторник',
            'Wednesday': 'Среда',
            'Thursday': 'Четверг',
            'Friday': 'Пятница',
            'Saturday': 'Суббота',
            'Sunday': 'Воскресенье'
        }
        weekday_name = weekday_ru.get(weekday, weekday)
        
        # Определяем запрос для расписания
        query = None
        if user['role'] == 'student':
            # Для студентов - получаем группу
            groups = Group.get_user_groups(user['id'])
            if groups:
                query = groups[0]['name']  # Берем первую группу
        elif user['role'] == 'teacher':
            # Для преподавателей - преобразуем ФИО
            query = format_teacher_name_for_schedule(user.get('fio', ''))
        
        if not query:
            text = f"📅 Расписание на сегодня ({weekday_name}, {today_str}):\n\n"
            text += "⚠️ Не удалось определить запрос для расписания.\n"
            text += "Обратитесь к администратору."
            keyboard = create_back_keyboard("menu_schedule")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
            return
        
        # Получаем расписание из API
        schedule_data = get_schedule_from_api(query)
        events_by_calname = schedule_data.get('events_by_calname', {})
        
        text = f"📅 Расписание на сегодня ({weekday_name}, {today_str}):\n\n"
        
        if not events_by_calname:
            text += f"✅ На {weekday_name} занятий нет."
        else:
            # Фильтруем события на сегодня
            today_events = []
            for calname, events in events_by_calname.items():
                for event in events:
                    if event.get('day_of_week') == weekday_name:
                        today_events.append((calname, event))
            
            if not today_events:
                text += f"✅ На {weekday_name} занятий нет.\n"
            else:
                # Группируем по календарям
                events_by_cal = {}
                for calname, event in today_events:
                    if calname not in events_by_cal:
                        events_by_cal[calname] = []
                    events_by_cal[calname].append(event)
                
                for calname, events in events_by_cal.items():
                    text += f"📚 {calname}:\n\n"
                    # Сортируем по времени начала
                    events.sort(key=lambda e: e.get('start', ''))
                    for event in events:
                        text += f"🕐 {event.get('start', '')} - {event.get('end', '')}\n"
                        text += f"📖 {event.get('summary', '')}\n"
                        if event.get('location'):
                            text += f"📍 {event.get('location', '')}\n"
                        if event.get('description'):
                            text += f"👤 {event.get('description', '').strip()}\n"
                        text += f"📆 {event.get('week_parity', '')}\n\n"
        
        keyboard = create_back_keyboard("menu_schedule")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_schedule_week(self, user: Dict, max_user_id: int, api):
        """Показать расписание на неделю"""
        text = "📆 Расписание на неделю\n\n"
        text += "📱 Данный функционал доступен в мини-приложении.\n"
        text += "Мини-приложение находится в разработке."
        
        keyboard = create_back_keyboard("menu_schedule")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def download_schedule(self, user: Dict, max_user_id: int, api):
        """Скачать расписание"""
        text = "⬇️ Скачать расписание\n\n"
        text += "📱 Данный функционал доступен в мини-приложении.\n"
        text += "Мини-приложение находится в разработке."
        
        keyboard = create_back_keyboard("menu_schedule")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_news_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню новостей"""
        keyboard = create_news_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="📢 Новости\n\nВыберите раздел:",
            attachments=[keyboard]
        )
    
    def show_news_university(self, user: Dict, max_user_id: int, api):
        """Показать новости вуза"""
        # TODO: Получить новости из БД
        text = "🏛️ Новости вуза:\n\n"
        text += "⚠️ Новости пока не добавлены.\n"
        text += "Следите за обновлениями!"
        
        keyboard = create_back_keyboard("menu_news")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_news_group(self, user: Dict, max_user_id: int, api):
        """Показать объявления группы"""
        groups = Group.get_user_groups(user['id'])
        if not groups:
            api.send_message(
                user_id=max_user_id,
                text="❌ Вы не состоите ни в одной группе",
                attachments=[create_back_keyboard("menu_news")]
            )
            return
        
        # TODO: Получить объявления группы из БД
        group_names = ", ".join([g['name'] for g in groups])
        text = f"👥 Объявления группы ({group_names}):\n\n"
        text += "⚠️ Объявления пока не добавлены.\n"
        text += "Следите за обновлениями!"
        
        keyboard = create_back_keyboard("menu_news")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_news_admin(self, user: Dict, max_user_id: int, api):
        """Показать уведомления администрации"""
        # TODO: Получить уведомления из БД
        text = "⚠️ Уведомления администрации:\n\n"
        text += "⚠️ Уведомления пока не добавлены.\n"
        text += "Следите за обновлениями!"
        
        keyboard = create_back_keyboard("menu_news")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_help(self, role: str, max_user_id: int, api):
        """Показать справку"""
        if role == 'student':
            keyboard = create_help_menu_keyboard('student')
            api.send_message(
                user_id=max_user_id,
                text="❓ Помощь\n\nВыберите раздел:",
                attachments=[keyboard]
            )
        elif role == 'teacher':
            keyboard = create_help_menu_keyboard('teacher')
            api.send_message(
                user_id=max_user_id,
                text="❓ Помощь\n\nВыберите раздел:",
                attachments=[keyboard]
            )
        elif role == 'admin':
            keyboard = create_admin_help_menu_keyboard()
            api.send_message(
                user_id=max_user_id,
                text="❓ Помощь\n\nВыберите раздел:",
                attachments=[keyboard]
            )
        elif role == 'support':
            keyboard = create_admin_help_menu_keyboard()
            api.send_message(
                user_id=max_user_id,
                text="❓ Помощь\n\nВыберите раздел:",
                attachments=[keyboard]
            )
        else:
            help_text = {
                'teacher': (
                    "📖 Справка для преподавателей:\n\n"
                    "• Мои группы - просмотр ваших групп и студентов\n"
                    "• Написать студенту - отправить личное сообщение\n"
                    "• Рассылка группе - отправить сообщение всем студентам группы\n\n"
                    "Команды:\n"
                    "/start - главное меню\n"
                    "/help - эта справка"
                ),
                'admin': (
                    "📖 Справка для администратора:\n\n"
                    "• Написать пользователю - отправить сообщение любому пользователю\n\n"
                    "Команды:\n"
                    "/start - главное меню\n"
                    "/help - эта справка"
                )
            }
            
            text = help_text.get(role, "Справка")
            keyboard = create_main_menu_keyboard(role)
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
    
    def show_help_faq(self, user: Dict, max_user_id: int, api):
        """Показать FAQ"""
        text = "❓ Часто задаваемые вопросы (FAQ):\n\n"
        text += "1. Как написать преподавателю?\n"
        text += "   → Выберите 'Преподаватели' → 'Написать преподавателю'\n\n"
        text += "2. Как посмотреть список группы?\n"
        text += "   → Выберите 'Моя группа' → 'Список студентов'\n\n"
        text += "3. Как написать сокурснику?\n"
        text += "   → Выберите 'Моя группа' → 'Написать сокурснику'\n\n"
        text += "4. Как посмотреть расписание?\n"
        text += "   → Выберите 'Расписание' → 'На сегодня' или 'На неделю'\n\n"
        text += "5. Как получить помощь?\n"
        text += "   → Выберите 'Помощь' → 'Связь с поддержкой'"
        
        keyboard = create_back_keyboard("help")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_help_support(self, user: Dict, max_user_id: int, api):
        """Показать контакты поддержки"""
        text = "💬 Связь с поддержкой:\n\n"
        text += "Если у вас возникли вопросы или проблемы:\n\n"
        text += "📧 Email: support@university.ru\n"
        text += "📞 Телефон: +7 (XXX) XXX-XX-XX\n"
        text += "🕐 Время работы: Пн-Пт, 9:00-18:00\n\n"
        text += "Или обратитесь к администратору через бота."
        
        keyboard = create_back_keyboard("help")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_help_common(self, user: Dict, max_user_id: int, api):
        """Показать частые вопросы"""
        text = "📋 Частые вопросы:\n\n"
        text += "Q: Как изменить роль?\n"
        text += "A: Используйте кнопку 'Выбрать роль' в главном меню\n\n"
        text += "Q: Как отправить сообщение от группы?\n"
        text += "A: Эта функция доступна только старостам группы\n\n"
        text += "Q: Где посмотреть контакты преподавателей?\n"
        text += "A: 'Преподаватели' → 'Список преподавателей'\n\n"
        text += "Q: Как скачать расписание?\n"
        text += "A: 'Расписание' → 'Скачать расписание'"
        
        keyboard = create_back_keyboard("help")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_headmen_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню старост для преподавателя"""
        keyboard = create_headmen_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="⭐ Старосты\n\nВыберите действие:",
            attachments=[keyboard]
        )
    
    def show_headmen_list(self, user: Dict, max_user_id: int, api):
        """Показать список старост групп преподавателя"""
        headmen = Teacher.get_teacher_headmen(user['id'])
        if not headmen:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет старост в группах",
                attachments=[create_back_keyboard("menu_headmen")]
            )
            return
        
        text = "⭐ Старосты ваших групп:\n\n"
        for headman in headmen:
            text += f"• {headman['fio']} - {headman.get('group_name', '')}\n"
            if headman.get('phone'):
                text += f"  📞 {headman['phone']}\n"
            if headman.get('email'):
                text += f"  📧 {headman['email']}\n"
            if headman.get('max_user_id'):
                text += f"  👤 [Профиль](max://user/{headman['max_user_id']})\n"
            text += "\n"
        
        keyboard = create_headmen_keyboard(headmen)
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard],
            format_type="markdown"
        )
    
    def show_headman_info(self, headman_id: int, user: Dict, max_user_id: int, api):
        """Показать информацию о старосте"""
        headman = User.get_by_id(headman_id)
        if not headman:
            api.send_message(
                user_id=max_user_id,
                text="❌ Староста не найден",
                attachments=[create_back_keyboard("headmen_list")]
            )
            return
        
        text = f"⭐ Информация о старосте:\n\n"
        text += f"👤 {headman['fio']}\n"
        if headman.get('phone'):
            text += f"📞 {headman['phone']}\n"
        if headman.get('email'):
            text += f"📧 {headman['email']}\n"
        if headman.get('max_user_id'):
            text += f"👤 [Профиль в Max](max://user/{headman['max_user_id']})\n"
        
        buttons = [
            [{"type": "callback", "text": "💬 Написать старосте", "payload": f"write_student_{headman_id}"}],
            [{"type": "callback", "text": "◀️ Назад", "payload": "headmen_list"}]
        ]
        
        keyboard = {
            "type": "inline_keyboard",
            "payload": {"buttons": buttons}
        }
        
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard],
            format_type="markdown"
        )
    
    def start_broadcast_headmen(self, user: Dict, max_user_id: int, api):
        """Начать рассылку старостам"""
        headmen = Teacher.get_teacher_headmen(user['id'])
        if not headmen:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет старост в группах",
                attachments=[create_back_keyboard("menu_headmen")]
            )
            return
        
        set_state(max_user_id, 'waiting_broadcast_headmen', {})
        api.send_message(
            user_id=max_user_id,
            text=f"📢 Напишите сообщение для рассылки всем старостам ({len(headmen)} чел.):\n\n(Отправьте текст сообщения или напишите 'отмена' для отмены)",
            attachments=[create_cancel_keyboard()]
        )
    
    def show_teachers_teacher(self, user: Dict, max_user_id: int, api):
        """Показать список преподавателей для преподавателя"""
        teachers = Teacher.get_all_teachers()
        # Исключаем самого себя
        teachers = [t for t in teachers if t['id'] != user['id']]
        
        if not teachers:
            api.send_message(
                user_id=max_user_id,
                text="❌ Нет других преподавателей",
                attachments=[create_back_keyboard()]
            )
            return
        
        text = "👨‍🏫 Преподаватели:\n\n"
        for teacher in teachers:
            text += f"• {teacher['fio']}\n"
            if teacher.get('phone'):
                text += f"  📞 {teacher['phone']}\n"
            if teacher.get('email'):
                text += f"  📧 {teacher['email']}\n"
            if teacher.get('max_user_id'):
                text += f"  👤 [Профиль](max://user/{teacher['max_user_id']})\n"
            text += "\n"
        
        keyboard = create_teachers_teacher_keyboard(teachers)
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard],
            format_type="markdown"
        )
    
    def show_teacher_info(self, teacher_id: int, user: Dict, max_user_id: int, api):
        """Показать информацию о преподавателе"""
        teacher = User.get_by_id(teacher_id)
        if not teacher:
            api.send_message(
                user_id=max_user_id,
                text="❌ Преподаватель не найден",
                attachments=[create_back_keyboard("menu_teachers_teacher")]
            )
            return
        
        text = f"👨‍🏫 Информация о преподавателе:\n\n"
        text += f"👤 {teacher['fio']}\n"
        if teacher.get('phone'):
            text += f"📞 {teacher['phone']}\n"
        if teacher.get('email'):
            text += f"📧 {teacher['email']}\n"
        if teacher.get('max_user_id'):
            text += f"👤 [Профиль в Max](max://user/{teacher['max_user_id']})\n"
        
        keyboard = create_back_keyboard("menu_teachers_teacher")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard],
            format_type="markdown"
        )
    
    def show_news_teacher_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню новостей для преподавателя"""
        keyboard = create_news_teacher_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="📢 Новости\n\nВыберите раздел:",
            attachments=[keyboard]
        )
    
    def show_news_department(self, user: Dict, max_user_id: int, api):
        """Показать новости кафедры"""
        # TODO: Получить новости кафедры из БД
        text = "🏛️ Новости кафедры:\n\n"
        text += "⚠️ Новости пока не добавлены.\n"
        text += "Следите за обновлениями!"
        
        keyboard = create_back_keyboard("menu_news_teacher")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_news_institute(self, user: Dict, max_user_id: int, api):
        """Показать новости института"""
        # TODO: Получить новости института из БД
        text = "🏢 Новости института:\n\n"
        text += "⚠️ Новости пока не добавлены.\n"
        text += "Следите за обновлениями!"
        
        keyboard = create_back_keyboard("menu_news_teacher")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_help_notifications(self, user: Dict, max_user_id: int, api):
        """Показать настройки уведомлений"""
        # TODO: Реализовать настройки уведомлений
        text = "⚙️ Настройки уведомлений:\n\n"
        text += "⚠️ Функция настройки уведомлений пока не реализована.\n"
        text += "В будущем здесь можно будет настроить:\n"
        text += "• Уведомления о новых сообщениях\n"
        text += "• Уведомления о новостях\n"
        text += "• Уведомления о расписании"
        
        keyboard = create_back_keyboard("help")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    # ========== АДМИНИСТРАТОРСКИЕ ОБРАБОТЧИКИ ==========
    
    def show_admin_students_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню управления студентами"""
        text = "👨‍🎓 Управление студентами\n\n"
        text += "📱 Данный функционал доступен в мини-приложении.\n"
        text += "Мини-приложение находится в разработке."
        
        keyboard = create_back_keyboard("main_menu")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_admin_teachers_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню управления преподавателями"""
        text = "👨‍🏫 Управление преподавателями\n\n"
        text += "📱 Данный функционал доступен в мини-приложении.\n"
        text += "Мини-приложение находится в разработке."
        
        keyboard = create_back_keyboard("main_menu")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_admin_groups_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню управления группами"""
        keyboard = create_admin_groups_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="👥 Управление группами\n\nВыберите действие:",
            attachments=[keyboard]
        )
    
    def show_admin_broadcasts_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню рассылок"""
        keyboard = create_admin_broadcasts_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="📢 Рассылки\n\nВыберите действие:",
            attachments=[keyboard]
        )
    
    def show_admin_reports_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню отчетов"""
        keyboard = create_admin_reports_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="📊 Отчеты\n\nВыберите раздел:",
            attachments=[keyboard]
        )
    
    def handle_admin_student_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия со студентами"""
        text = "👨‍🎓 Управление студентами\n\n"
        text += "📱 Данный функционал доступен в мини-приложении.\n"
        text += "Мини-приложение находится в разработке."
        
        keyboard = create_back_keyboard("main_menu")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
        return
        
        # Закомментированный код - функционал перенесен в миниапп
        action = payload.replace('admin_student_', '')
        
        if action == 'add':
            set_state(max_user_id, 'admin_student_add', {})
            api.send_message(
                user_id=max_user_id,
                text="➕ Добавление студента\n\nОтправьте данные в формате:\nmax_user_id, ФИО, телефон, email\n\nПример: 123456789, Иванов Иван Иванович, +79001234567, ivan@example.com",
                attachments=[create_cancel_keyboard()]
            )
        elif action == 'edit':
            students = User.get_all_students()
            if not students:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет студентов в системе",
                    attachments=[create_back_keyboard("admin_students")]
                )
                return
            keyboard = create_students_list_keyboard(students, prefix="admin_student_edit_select")
            api.send_message(
                user_id=max_user_id,
                text="✏️ Выберите студента для редактирования:",
                attachments=[keyboard]
            )
        elif action == 'delete':
            students = User.get_all_students()
            if not students:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет студентов в системе",
                    attachments=[create_back_keyboard("admin_students")]
                )
                return
            keyboard = create_students_list_keyboard(students, prefix="admin_student_delete_select")
            api.send_message(
                user_id=max_user_id,
                text="🗑️ Выберите студента для удаления:",
                attachments=[keyboard]
            )
        elif action == 'assign_group':
            students = User.get_all_students()
            if not students:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет студентов в системе",
                    attachments=[create_back_keyboard("admin_students")]
                )
                return
            keyboard = create_students_list_keyboard(students, prefix="admin_student_assign_group_select")
            api.send_message(
                user_id=max_user_id,
                text="👥 Выберите студента для присвоения группы:",
                attachments=[keyboard]
            )
        elif action == 'contacts':
            students = User.get_all_students()
            if not students:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет студентов в системе",
                    attachments=[create_back_keyboard("admin_students")]
                )
                return
            keyboard = create_students_list_keyboard(students, prefix="admin_student_contacts_select")
            api.send_message(
                user_id=max_user_id,
                text="📋 Выберите студента для просмотра контактов:",
                attachments=[keyboard]
            )
        elif action.startswith('edit_select_'):
            student_id = int(action.replace('edit_select_', ''))
            set_state(max_user_id, 'admin_student_edit', {'student_id': student_id})
            student = User.get_by_id(student_id)
            if student:
                api.send_message(
                    user_id=max_user_id,
                    text=f"✏️ Редактирование студента: {student['fio']}\n\nОтправьте новые данные в формате:\nФИО, телефон, email\n\nТекущие данные:\nФИО: {student.get('fio', 'не указано')}\nТелефон: {student.get('phone', 'не указано')}\nEmail: {student.get('email', 'не указано')}",
                    attachments=[create_cancel_keyboard()]
                )
        elif action.startswith('delete_select_'):
            student_id = int(action.replace('delete_select_', ''))
            student = User.get_by_id(student_id)
            if student:
                User.delete_user(student_id)
                api.send_message(
                    user_id=max_user_id,
                    text=f"✅ Студент {student['fio']} удален",
                    attachments=[create_back_keyboard("admin_students")]
                )
        elif action.startswith('assign_group_select_'):
            student_id = int(action.replace('assign_group_select_', ''))
            groups = Group.get_all_groups()
            if not groups:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет групп в системе",
                    attachments=[create_back_keyboard("admin_students")]
                )
                return
            set_state(max_user_id, 'admin_student_assign_group', {'student_id': student_id})
            keyboard = create_groups_list_keyboard(groups, prefix="admin_student_assign_group_to")
            api.send_message(
                user_id=max_user_id,
                text="👥 Выберите группу:",
                attachments=[keyboard]
            )
        elif action.startswith('contacts_select_'):
            student_id = int(action.replace('contacts_select_', ''))
            student = User.get_by_id(student_id)
            if student:
                text = f"📋 Контакты студента: {student['fio']}\n\n"
                text += f"👤 Max ID: {student.get('max_user_id', 'не указано')}\n"
                if student.get('max_user_id'):
                    text += f"   [Профиль](max://user/{student['max_user_id']})\n"
                text += f"📞 Телефон: {student.get('phone', 'не указано')}\n"
                text += f"📧 Email: {student.get('email', 'не указано')}\n"
                api.send_message(
                    user_id=max_user_id,
                    text=text,
                    attachments=[create_back_keyboard("admin_students")],
                    format_type="markdown"
                )
        elif action.startswith('assign_group_to_'):
            group_id = int(action.replace('assign_group_to_', ''))
            state_data = get_state(max_user_id)
            if state_data and state_data.get('state') == 'admin_student_assign_group':
                student_id = state_data.get('data', {}).get('student_id')
                if student_id:
                    User.assign_user_to_group(student_id, group_id)
                    student = User.get_by_id(student_id)
                    group = Group.get_by_id(group_id)
                    api.send_message(
                        user_id=max_user_id,
                        text=f"✅ Студент {student['fio'] if student else ''} добавлен в группу {group['name'] if group else ''}",
                        attachments=[create_back_keyboard("admin_students")]
                    )
                    clear_state(max_user_id)
    
    def handle_admin_teacher_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия с преподавателями"""
        text = "👨‍🏫 Управление преподавателями\n\n"
        text += "📱 Данный функционал доступен в мини-приложении.\n"
        text += "Мини-приложение находится в разработке."
        
        keyboard = create_back_keyboard("main_menu")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
        return
        
        # Закомментированный код - функционал перенесен в миниапп
        action = payload.replace('admin_teacher_', '')
        
        if action == 'add':
            set_state(max_user_id, 'admin_teacher_add', {})
            api.send_message(
                user_id=max_user_id,
                text="➕ Добавление преподавателя\n\nОтправьте данные в формате:\nmax_user_id, ФИО, телефон, email\n\nПример: 123456789, Петров Петр Петрович, +79001234567, petrov@example.com",
                attachments=[create_cancel_keyboard()]
            )
        elif action == 'edit':
            teachers = Teacher.get_all_teachers()
            if not teachers:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет преподавателей в системе",
                    attachments=[create_back_keyboard("admin_teachers")]
                )
                return
            keyboard = create_teachers_list_keyboard(teachers, prefix="admin_teacher_edit_select")
            api.send_message(
                user_id=max_user_id,
                text="✏️ Выберите преподавателя для редактирования:",
                attachments=[keyboard]
            )
        elif action == 'assign_groups':
            teachers = Teacher.get_all_teachers()
            if not teachers:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет преподавателей в системе",
                    attachments=[create_back_keyboard("admin_teachers")]
                )
                return
            keyboard = create_teachers_list_keyboard(teachers, prefix="admin_teacher_assign_groups_select")
            api.send_message(
                user_id=max_user_id,
                text="👥 Выберите преподавателя для назначения групп:",
                attachments=[keyboard]
            )
        elif action.startswith('edit_select_'):
            teacher_id = int(action.replace('edit_select_', ''))
            set_state(max_user_id, 'admin_teacher_edit', {'teacher_id': teacher_id})
            teacher = User.get_by_id(teacher_id)
            if teacher:
                api.send_message(
                    user_id=max_user_id,
                    text=f"✏️ Редактирование преподавателя: {teacher['fio']}\n\nОтправьте новые данные в формате:\nФИО, телефон, email\n\nТекущие данные:\nФИО: {teacher.get('fio', 'не указано')}\nТелефон: {teacher.get('phone', 'не указано')}\nEmail: {teacher.get('email', 'не указано')}",
                    attachments=[create_cancel_keyboard()]
                )
        elif action.startswith('assign_groups_select_'):
            teacher_id = int(action.replace('assign_groups_select_', ''))
            groups = Group.get_all_groups()
            if not groups:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет групп в системе",
                    attachments=[create_back_keyboard("admin_teachers")]
                )
                return
            set_state(max_user_id, 'admin_teacher_assign_groups', {'teacher_id': teacher_id})
            keyboard = create_groups_list_keyboard(groups, prefix="admin_teacher_assign_group_to")
            api.send_message(
                user_id=max_user_id,
                text="👥 Выберите группу для назначения:",
                attachments=[keyboard]
            )
        elif action.startswith('assign_group_to_'):
            group_id = int(action.replace('assign_group_to_', ''))
            state_data = get_state(max_user_id)
            if state_data and state_data.get('state') == 'admin_teacher_assign_groups':
                teacher_id = state_data.get('data', {}).get('teacher_id')
                if teacher_id:
                    User.assign_teacher_to_group(teacher_id, group_id)
                    teacher = User.get_by_id(teacher_id)
                    group = Group.get_by_id(group_id)
                    api.send_message(
                        user_id=max_user_id,
                        text=f"✅ Преподаватель {teacher['fio'] if teacher else ''} назначен на группу {group['name'] if group else ''}",
                        attachments=[create_back_keyboard("admin_teachers")]
                    )
                    clear_state(max_user_id)
    
    def handle_admin_group_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия с группами"""
        action = payload.replace('admin_group_', '')
        
        if action == 'view':
            # Просмотр состава группы - функционал в миниаппе
            text = "👥 Просмотр состава группы\n\n"
            text += "📱 Данный функционал доступен в мини-приложении.\n"
            text += "Мини-приложение находится в разработке."
            
            keyboard = create_back_keyboard("admin_groups")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
            return
        elif action.startswith('view_select_'):
            # Просмотр состава группы - функционал в миниаппе
            text = "👥 Просмотр состава группы\n\n"
            text += "📱 Данный функционал доступен в мини-приложении.\n"
            text += "Мини-приложение находится в разработке."
            
            keyboard = create_back_keyboard("admin_groups")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
            return
        elif action == 'add_student':
            groups = Group.get_all_groups()
            if not groups:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет групп в системе",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            keyboard = create_groups_list_keyboard(groups, prefix="admin_group_add_student_select")
            api.send_message(
                user_id=max_user_id,
                text="➕ Выберите группу для добавления студента:",
                attachments=[keyboard]
            )
        elif action == 'remove_student':
            groups = Group.get_all_groups()
            if not groups:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет групп в системе",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            keyboard = create_groups_list_keyboard(groups, prefix="admin_group_remove_student_select")
            api.send_message(
                user_id=max_user_id,
                text="➖ Выберите группу для удаления студента:",
                attachments=[keyboard]
            )
        elif action == 'assign_teacher':
            groups = Group.get_all_groups()
            if not groups:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет групп в системе",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            keyboard = create_groups_list_keyboard(groups, prefix="admin_group_assign_teacher_select")
            api.send_message(
                user_id=max_user_id,
                text="👨‍🏫 Выберите группу для привязки преподавателя:",
                attachments=[keyboard]
            )
        elif action.startswith('view_select_'):
            group_id = int(action.replace('view_select_', ''))
            members = Group.get_group_members(group_id)
            group = Group.get_by_id(group_id)
            text = f"👥 Состав группы {group['name'] if group else ''}:\n\n"
            if not members:
                text += "❌ В группе нет студентов"
            else:
                for member in members:
                    headman = "⭐ Староста: " if member.get('is_headman') else ""
                    text += f"{headman}{member['fio']}\n"
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[create_back_keyboard("admin_groups")]
            )
        elif action.startswith('add_student_select_'):
            group_id = int(action.replace('add_student_select_', ''))
            students = User.get_all_students()
            if not students:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет студентов в системе",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            set_state(max_user_id, 'admin_group_add_student', {'group_id': group_id})
            keyboard = create_students_list_keyboard(students, prefix="admin_group_add_student_to")
            api.send_message(
                user_id=max_user_id,
                text="➕ Выберите студента для добавления:",
                attachments=[keyboard]
            )
        elif action.startswith('add_student_to_'):
            student_id = int(action.replace('add_student_to_', ''))
            state_data = get_state(max_user_id)
            if state_data and state_data.get('state') == 'admin_group_add_student':
                group_id = state_data.get('data', {}).get('group_id')
                if group_id:
                    User.assign_user_to_group(student_id, group_id)
                    student = User.get_by_id(student_id)
                    group = Group.get_by_id(group_id)
                    api.send_message(
                        user_id=max_user_id,
                        text=f"✅ Студент {student['fio'] if student else ''} добавлен в группу {group['name'] if group else ''}",
                        attachments=[create_back_keyboard("admin_groups")]
                    )
                    clear_state(max_user_id)
        elif action.startswith('remove_student_select_'):
            group_id = int(action.replace('remove_student_select_', ''))
            members = Group.get_group_members(group_id)
            if not members:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ В группе нет студентов",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            set_state(max_user_id, 'admin_group_remove_student', {'group_id': group_id})
            buttons = []
            for member in members:
                buttons.append([{
                    "type": "callback",
                    "text": f"{'⭐ ' if member.get('is_headman') else ''}{member['fio']}",
                    "payload": f"admin_group_remove_student_from_{member['id']}"
                }])
            buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "admin_groups"}])
            keyboard = {
                "type": "inline_keyboard",
                "payload": {"buttons": buttons}
            }
            api.send_message(
                user_id=max_user_id,
                text="➖ Выберите студента для удаления из группы:",
                attachments=[keyboard]
            )
        elif action.startswith('remove_student_from_'):
            student_id = int(action.replace('remove_student_from_', ''))
            state_data = get_state(max_user_id)
            if state_data and state_data.get('state') == 'admin_group_remove_student':
                group_id = state_data.get('data', {}).get('group_id')
                if group_id:
                    User.remove_user_from_group(student_id, group_id)
                    student = User.get_by_id(student_id)
                    group = Group.get_by_id(group_id)
                    api.send_message(
                        user_id=max_user_id,
                        text=f"✅ Студент {student['fio'] if student else ''} удален из группы {group['name'] if group else ''}",
                        attachments=[create_back_keyboard("admin_groups")]
                    )
                    clear_state(max_user_id)
        elif action.startswith('assign_teacher_select_'):
            group_id = int(action.replace('assign_teacher_select_', ''))
            teachers = Teacher.get_all_teachers()
            if not teachers:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет преподавателей в системе",
                    attachments=[create_back_keyboard("admin_groups")]
                )
                return
            set_state(max_user_id, 'admin_group_assign_teacher', {'group_id': group_id})
            keyboard = create_teachers_list_keyboard(teachers, prefix="admin_group_assign_teacher_to")
            api.send_message(
                user_id=max_user_id,
                text="👨‍🏫 Выберите преподавателя:",
                attachments=[keyboard]
            )
        elif action.startswith('assign_teacher_to_'):
            teacher_id = int(action.replace('assign_teacher_to_', ''))
            state_data = get_state(max_user_id)
            if state_data and state_data.get('state') == 'admin_group_assign_teacher':
                group_id = state_data.get('data', {}).get('group_id')
                if group_id:
                    User.assign_teacher_to_group(teacher_id, group_id)
                    teacher = User.get_by_id(teacher_id)
                    group = Group.get_by_id(group_id)
                    api.send_message(
                        user_id=max_user_id,
                        text=f"✅ Преподаватель {teacher['fio'] if teacher else ''} привязан к группе {group['name'] if group else ''}",
                        attachments=[create_back_keyboard("admin_groups")]
                    )
                    clear_state(max_user_id)
    
    def handle_admin_broadcast_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия с рассылками"""
        action = payload.replace('admin_broadcast_', '')
        
        if action == 'mass':
            set_state(max_user_id, 'admin_broadcast_mass', {})
            api.send_message(
                user_id=max_user_id,
                text="📢 Массовая рассылка\n\nВыберите получателей:\n1. Все студенты\n2. Все преподаватели\n3. Все пользователи\n4. Конкретная группа\n\nОтправьте номер варианта:",
                attachments=[create_cancel_keyboard()]
            )
        elif action == 'templates':
            text = "📝 Шаблоны сообщений\n\n"
            text += "⚠️ Функция шаблонов пока не реализована.\n"
            text += "В будущем здесь можно будет:\n"
            text += "• Создавать шаблоны сообщений\n"
            text += "• Использовать шаблоны для рассылок\n"
            text += "• Управлять шаблонами"
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[create_back_keyboard("admin_broadcasts")]
            )
    
    def handle_admin_report_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия с отчетами"""
        action = payload.replace('admin_report_', '')
        
        if action == 'activity':
            text = "📊 Статистика активности\n\n"
            text += "⚠️ Функция статистики пока не реализована.\n"
            text += "В будущем здесь будет:\n"
            text += "• Активность пользователей\n"
            text += "• Количество сообщений\n"
            text += "• Популярные функции"
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[create_back_keyboard("admin_reports")]
            )
        elif action == 'messages':
            total = execute_query("SELECT COUNT(*) as count FROM messages", (), fetch_one=True)
            total_count = total.get('count', 0) if total else 0
            text = "💬 Отчеты по сообщениям\n\n"
            text += f"📊 Всего сообщений в системе: {total_count}\n"
            text += "⚠️ Детальная статистика пока не реализована."
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[create_back_keyboard("admin_reports")]
            )
        elif action == 'users':
            students = User.get_all_students()
            teachers = Teacher.get_all_teachers()
            text = "👥 Отчеты по пользователям\n\n"
            text += f"👨‍🎓 Студентов: {len(students)}\n"
            text += f"👨‍🏫 Преподавателей: {len(teachers)}\n"
            text += f"📊 Всего пользователей: {len(students) + len(teachers)}"
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[create_back_keyboard("admin_reports")]
            )
    
    def handle_admin_help_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия помощи для администратора"""
        action = payload.replace('admin_help_', '')
        
        if action == 'instructions':
            text = "📖 Инструкции по работе с ботом\n\n"
            text += "👨‍🎓 Управление студентами:\n"
            text += "• Добавление: отправьте данные в формате max_user_id, ФИО, телефон, email\n"
            text += "• Редактирование: выберите студента и отправьте новые данные\n"
            text += "• Удаление: выберите студента для удаления\n\n"
            text += "👨‍🏫 Управление преподавателями:\n"
            text += "• Аналогично управлению студентами\n\n"
            text += "👥 Управление группами:\n"
            text += "• Просмотр состава группы\n"
            text += "• Добавление/удаление студентов\n"
            text += "• Привязка преподавателей\n\n"
            text += "📢 Рассылки:\n"
            text += "• Массовые уведомления всем пользователям или группам"
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[create_back_keyboard("help")]
            )
    
    # ========== ОБРАБОТЧИКИ ПОДДЕРЖКИ ==========
    
    def show_admin_support_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню поддержки для администратора"""
        keyboard = create_admin_support_menu_keyboard()
        api.send_message(
            user_id=max_user_id,
            text="💬 Поддержка\n\nВыберите раздел:",
            attachments=[keyboard]
        )
    
    def handle_admin_support_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия поддержки"""
        action = payload.replace('admin_support_', '')
        
        if action == 'tickets':
            # Показать фильтр по статусам
            keyboard = create_support_tickets_status_keyboard(role='admin')
            api.send_message(
                user_id=max_user_id,
                text="📋 Запросы в поддержку\n\nВыберите статус:",
                attachments=[keyboard]
            )
        elif action in ['tickets_new', 'tickets_in_progress', 'tickets_resolved', 'tickets_all']:
            # Показать список обращений по статусу
            status_map = {
                'tickets_new': 'new',
                'tickets_in_progress': 'in_progress',
                'tickets_resolved': 'resolved',
                'tickets_all': None
            }
            status = status_map.get(action)
            tickets = SupportTicket.get_tickets(status=status)
            
            if not tickets:
                status_text = {
                    'new': 'новых',
                    'in_progress': 'в работе',
                    'resolved': 'решенных',
                    None: ''
                }.get(status, '')
                api.send_message(
                    user_id=max_user_id,
                    text=f"❌ Нет {status_text} обращений",
                    attachments=[create_support_tickets_status_keyboard(role='support')]
                )
                return
            
            keyboard = create_support_tickets_list_keyboard(tickets, prefix="support_ticket", back_payload="support_tickets")
            status_text = {
                'new': '🆕 Новые',
                'in_progress': '🔄 В работе',
                'resolved': '✅ Решено',
                None: '📋 Все'
            }.get(status, '📋')
            api.send_message(
                user_id=max_user_id,
                text=f"{status_text} обращения ({len(tickets)}):",
                attachments=[keyboard]
            )
        elif action.startswith('ticket_'):
            # Обработка конкретного обращения
            ticket_id = int(action.split('_')[-1])
            ticket = SupportTicket.get_ticket_by_id(ticket_id)
            
            if not ticket:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Обращение не найдено",
                    attachments=[create_support_tickets_status_keyboard(role='support')]
                )
                return
            
            # Показать детали обращения
            status_emoji = {
                'new': '🆕',
                'in_progress': '🔄',
                'resolved': '✅'
            }.get(ticket.get('status', 'new'), '📋')
            
            status_text = {
                'new': 'Новое',
                'in_progress': 'В работе',
                'resolved': 'Решено'
            }.get(ticket.get('status', 'new'), 'Неизвестно')
            
            text = f"{status_emoji} Обращение #{ticket['id']}\n\n"
            text += f"👤 Пользователь: {ticket.get('fio', 'Неизвестно')}\n"
            text += f"📋 Статус: {status_text}\n"
            if ticket.get('admin_fio'):
                text += f"👨‍💼 Администратор: {ticket.get('admin_fio')}\n"
            text += f"📅 Создано: {ticket.get('created_at', 'Неизвестно')}\n\n"
            text += f"📝 Тема: {ticket.get('subject', 'Без темы')}\n\n"
            text += f"💬 Сообщение:\n{ticket.get('message', '')}\n"
            
            if ticket.get('response_time'):
                text += f"\n⏱ Время реакции: {ticket['response_time']} мин."
            
            keyboard = create_support_ticket_actions_keyboard(ticket_id, ticket.get('status', 'new'), role='support')
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
        elif action.startswith('ticket_take_'):
            # Взять обращение в работу
            ticket_id = int(action.split('_')[-1])
            admin_user = User.get_by_max_id(max_user_id, role='admin')
            if admin_user:
                SupportTicket.update_status(ticket_id, 'in_progress', admin_user['id'])
                # Вычислить время реакции
                ticket = SupportTicket.get_ticket_by_id(ticket_id)
                if ticket:
                    from datetime import datetime
                    created_at = ticket.get('created_at')
                    if created_at:
                        try:
                            if isinstance(created_at, str):
                                # Пробуем парсить ISO формат
                                try:
                                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                except:
                                    # Если не получилось, пробуем без timezone
                                    created_at = datetime.fromisoformat(created_at.split('+')[0].split('Z')[0])
                            now = datetime.now()
                            if isinstance(created_at, datetime):
                                # Убираем timezone для сравнения
                                if created_at.tzinfo:
                                    from datetime import timezone
                                    created_at = created_at.replace(tzinfo=None)
                                diff = now - created_at
                                response_time = int(diff.total_seconds() / 60)
                                if response_time >= 0:
                                    SupportTicket.set_response_time(ticket_id, response_time)
                        except Exception as e:
                            logger.error(f"Ошибка при вычислении времени реакции: {e}")
                
                api.send_message(
                    user_id=max_user_id,
                    text="✅ Обращение взято в работу",
                    attachments=[create_back_keyboard(f"admin_support_ticket_{ticket_id}")]
                )
        elif action.startswith('ticket_resolve_'):
            # Решить обращение
            ticket_id = int(action.split('_')[-1])
            SupportTicket.update_status(ticket_id, 'resolved')
            api.send_message(
                user_id=max_user_id,
                text="✅ Обращение помечено как решенное",
                attachments=[create_back_keyboard(f"admin_support_ticket_{ticket_id}")]
            )
        elif action.startswith('ticket_contact_'):
            # Связаться с пользователем
            ticket_id = int(action.split('_')[-1])
            ticket = SupportTicket.get_ticket_by_id(ticket_id)
            if ticket:
                user_id = ticket.get('user_id')
                user = User.get_by_id(user_id)
                if user:
                    set_state(max_user_id, 'admin_support_contact', {'ticket_id': ticket_id, 'user_id': user_id})
                    api.send_message(
                        user_id=max_user_id,
                        text=f"💬 Написать пользователю {user.get('fio', '')}\n\nОтправьте сообщение:",
                        attachments=[create_cancel_keyboard()]
                    )
        elif action == 'messages':
            # Показать сообщения администрации
            messages = AdminMessage.get_messages()
            if not messages:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет сообщений администрации",
                    attachments=[create_back_keyboard("admin_support")]
                )
                return
            
            text = "📢 Сообщения администрации:\n\n"
            for msg in messages[:10]:  # Показываем последние 10
                text += f"📋 {msg.get('title', 'Без заголовка')}\n"
                text += f"   {msg.get('message', '')[:100]}...\n"
                if msg.get('target_role'):
                    text += f"   👥 Для: {msg.get('target_role')}\n"
                text += f"   📅 {msg.get('created_at', '')}\n\n"
            
            keyboard = create_back_keyboard("admin_support")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
        elif action == 'faq':
            # Показать список FAQ
            faq_list = FAQ.get_faq()
            if not faq_list:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет FAQ",
                    attachments=[create_back_keyboard("admin_support")]
                )
                return
            
            keyboard = create_faq_list_keyboard(faq_list)
            api.send_message(
                user_id=max_user_id,
                text=f"❓ Часто задаваемые вопросы ({len(faq_list)}):",
                attachments=[keyboard]
            )
        elif action.startswith('faq_view_'):
            # Показать конкретный FAQ
            faq_id = int(action.split('_')[-1])
            faq = FAQ.get_faq_by_id(faq_id)
            if faq:
                text = f"❓ {faq.get('question', '')}\n\n"
                text += f"💬 {faq.get('answer', '')}\n"
                keyboard = create_back_keyboard("admin_support_faq")
                api.send_message(
                    user_id=max_user_id,
                    text=text,
                    attachments=[keyboard]
                )
        elif action == 'faq_add':
            # Добавить новый FAQ
            set_state(max_user_id, 'admin_support_faq_add', {})
            api.send_message(
                user_id=max_user_id,
                text="➕ Добавление FAQ\n\nОтправьте данные в формате:\nВопрос\nОтвет\n\nПример:\nКак написать преподавателю?\nВыберите 'Преподаватели' → 'Написать преподавателю'",
                attachments=[create_cancel_keyboard()]
            )
        elif action == 'stats':
            # Показать статистику
            stats = SupportTicket.get_stats()
            text = "📊 Статистика поддержки:\n\n"
            text += f"📋 Всего обращений: {stats.get('total', 0)}\n"
            text += f"🆕 Новых: {stats.get('new', 0)}\n"
            text += f"🔄 В работе: {stats.get('in_progress', 0)}\n"
            text += f"✅ Решено: {stats.get('resolved', 0)}\n"
            text += f"✅ Всего решено: {stats.get('total_resolved', 0)}\n"
            avg_time = stats.get('avg_response_time', 0)
            if avg_time > 0:
                text += f"⏱ Среднее время реакции: {avg_time:.1f} мин."
            else:
                text += f"⏱ Среднее время реакции: не рассчитано"
            
            keyboard = create_back_keyboard("admin_support")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
    
    # ========== ОБРАБОТЧИКИ ДЛЯ РОЛИ ПОДДЕРЖКИ ==========
    
    def handle_support_action(self, payload: str, user: Dict, max_user_id: int, api):
        """Обработать действия поддержки (для роли support)"""
        action = payload.replace('support_', '')
        
        if action == 'tickets':
            # Показать фильтр по статусам
            keyboard = create_support_tickets_status_keyboard(role='support')
            api.send_message(
                user_id=max_user_id,
                text="📋 Запросы в поддержку\n\nВыберите статус:",
                attachments=[keyboard]
            )
        elif action in ['tickets_new', 'tickets_in_progress', 'tickets_resolved', 'tickets_all']:
            # Показать список обращений по статусу
            status_map = {
                'tickets_new': 'new',
                'tickets_in_progress': 'in_progress',
                'tickets_resolved': 'resolved',
                'tickets_all': None
            }
            status = status_map.get(action)
            tickets = SupportTicket.get_tickets(status=status)
            
            if not tickets:
                status_text = {
                    'new': 'новых',
                    'in_progress': 'в работе',
                    'resolved': 'решенных',
                    None: ''
                }.get(status, '')
                api.send_message(
                    user_id=max_user_id,
                    text=f"❌ Нет {status_text} обращений",
                    attachments=[create_support_tickets_status_keyboard(role='support')]
                )
                return
            
            keyboard = create_support_tickets_list_keyboard(tickets, prefix="support_ticket", back_payload="support_tickets")
            status_text = {
                'new': '🆕 Новые',
                'in_progress': '🔄 В работе',
                'resolved': '✅ Решено',
                None: '📋 Все'
            }.get(status, '📋')
            api.send_message(
                user_id=max_user_id,
                text=f"{status_text} обращения ({len(tickets)}):",
                attachments=[keyboard]
            )
        elif action.startswith('ticket_'):
            # Обработка конкретного обращения
            ticket_id = int(action.split('_')[-1])
            ticket = SupportTicket.get_ticket_by_id(ticket_id)
            
            if not ticket:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Обращение не найдено",
                    attachments=[create_support_tickets_status_keyboard(role='support')]
                )
                return
            
            # Показать детали обращения
            status_emoji = {
                'new': '🆕',
                'in_progress': '🔄',
                'resolved': '✅'
            }.get(ticket.get('status', 'new'), '📋')
            
            status_text = {
                'new': 'Новое',
                'in_progress': 'В работе',
                'resolved': 'Решено'
            }.get(ticket.get('status', 'new'), 'Неизвестно')
            
            text = f"{status_emoji} Обращение #{ticket['id']}\n\n"
            text += f"👤 Пользователь: {ticket.get('fio', 'Неизвестно')}\n"
            text += f"📋 Статус: {status_text}\n"
            if ticket.get('admin_fio'):
                text += f"👨‍💼 Администратор: {ticket.get('admin_fio')}\n"
            text += f"📅 Создано: {ticket.get('created_at', 'Неизвестно')}\n\n"
            text += f"📝 Тема: {ticket.get('subject', 'Без темы')}\n\n"
            text += f"💬 Сообщение:\n{ticket.get('message', '')}\n"
            
            if ticket.get('response_time'):
                text += f"\n⏱ Время реакции: {ticket['response_time']} мин."
            
            keyboard = create_support_ticket_actions_keyboard(ticket_id, ticket.get('status', 'new'), role='support')
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
        elif action.startswith('ticket_take_'):
            # Взять обращение в работу
            ticket_id = int(action.split('_')[-1])
            support_user = User.get_by_max_id(max_user_id, role='support')
            if support_user:
                SupportTicket.update_status(ticket_id, 'in_progress', support_user['id'])
                # Вычислить время реакции
                ticket = SupportTicket.get_ticket_by_id(ticket_id)
                if ticket:
                    from datetime import datetime
                    created_at = ticket.get('created_at')
                    if created_at:
                        try:
                            if isinstance(created_at, str):
                                try:
                                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                except:
                                    created_at = datetime.fromisoformat(created_at.split('+')[0].split('Z')[0])
                            now = datetime.now()
                            if isinstance(created_at, datetime):
                                if created_at.tzinfo:
                                    created_at = created_at.replace(tzinfo=None)
                                diff = now - created_at
                                response_time = int(diff.total_seconds() / 60)
                                if response_time >= 0:
                                    SupportTicket.set_response_time(ticket_id, response_time)
                        except Exception as e:
                            logger.error(f"Ошибка при вычислении времени реакции: {e}")
                
                api.send_message(
                    user_id=max_user_id,
                    text="✅ Обращение взято в работу",
                    attachments=[create_back_keyboard(f"support_ticket_{ticket_id}")]
                )
        elif action.startswith('ticket_resolve_'):
            # Решить обращение
            ticket_id = int(action.split('_')[-1])
            SupportTicket.update_status(ticket_id, 'resolved')
            api.send_message(
                user_id=max_user_id,
                text="✅ Обращение помечено как решенное",
                attachments=[create_back_keyboard(f"support_ticket_{ticket_id}")]
            )
        elif action.startswith('ticket_contact_'):
            # Связаться с пользователем
            ticket_id = int(action.split('_')[-1])
            ticket = SupportTicket.get_ticket_by_id(ticket_id)
            if ticket:
                user_id = ticket.get('user_id')
                target_user = User.get_by_id(user_id)
                if target_user:
                    set_state(max_user_id, 'support_contact', {'ticket_id': ticket_id, 'user_id': user_id})
                    api.send_message(
                        user_id=max_user_id,
                        text=f"💬 Написать пользователю {target_user.get('fio', '')}\n\nОтправьте сообщение:",
                        attachments=[create_cancel_keyboard()]
                    )
        elif action == 'messages':
            # Показать сообщения администрации
            messages = AdminMessage.get_messages()
            if not messages:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет сообщений администрации",
                    attachments=[create_back_keyboard("main_menu")]
                )
                return
            
            text = "📢 Сообщения администрации:\n\n"
            for msg in messages[:10]:
                text += f"📋 {msg.get('title', 'Без заголовка')}\n"
                text += f"   {msg.get('message', '')[:100]}...\n"
                if msg.get('target_role'):
                    text += f"   👥 Для: {msg.get('target_role')}\n"
                text += f"   📅 {msg.get('created_at', '')}\n\n"
            
            keyboard = create_back_keyboard("main_menu")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
        elif action == 'faq':
            # Показать список FAQ
            faq_list = FAQ.get_faq()
            if not faq_list:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ Нет FAQ",
                    attachments=[create_back_keyboard("main_menu")]
                )
                return
            
            keyboard = create_faq_list_keyboard(faq_list)
            api.send_message(
                user_id=max_user_id,
                text=f"❓ Часто задаваемые вопросы ({len(faq_list)}):",
                attachments=[keyboard]
            )
        elif action.startswith('faq_view_'):
            # Показать конкретный FAQ
            faq_id = int(action.split('_')[-1])
            faq = FAQ.get_faq_by_id(faq_id)
            if faq:
                text = f"❓ {faq.get('question', '')}\n\n"
                text += f"💬 {faq.get('answer', '')}\n"
                keyboard = create_back_keyboard("support_faq")
                api.send_message(
                    user_id=max_user_id,
                    text=text,
                    attachments=[keyboard]
                )
        elif action == 'stats':
            # Показать статистику
            stats = SupportTicket.get_stats()
            text = "📊 Статистика поддержки:\n\n"
            text += f"📋 Всего обращений: {stats.get('total', 0)}\n"
            text += f"🆕 Новых: {stats.get('new', 0)}\n"
            text += f"🔄 В работе: {stats.get('in_progress', 0)}\n"
            text += f"✅ Решено: {stats.get('resolved', 0)}\n"
            text += f"✅ Всего решено: {stats.get('total_resolved', 0)}\n"
            avg_time = stats.get('avg_response_time', 0)
            if avg_time > 0:
                text += f"⏱ Среднее время реакции: {avg_time:.1f} мин."
            else:
                text += f"⏱ Среднее время реакции: не рассчитано"
            
            keyboard = create_back_keyboard("main_menu")
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )

