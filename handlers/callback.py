"""Обработчик нажатий на кнопки"""
from handlers.base import BaseHandler
from db.models import User, Group, Teacher
from utils.keyboard import (
    create_main_menu_keyboard, create_groups_keyboard, 
    create_students_keyboard, create_teachers_keyboard,
    create_back_keyboard, create_cancel_keyboard,
    create_role_selection_keyboard, create_group_menu_keyboard,
    create_teachers_menu_keyboard, create_schedule_menu_keyboard,
    create_news_menu_keyboard, create_help_menu_keyboard
)
from utils.states import set_state, clear_state, set_user_role, get_user_role
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

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
            self.show_teacher_groups(user_data, max_user_id, api)
        elif payload.startswith('group_') and not payload.startswith('group_message'):
            group_id = int(payload.split('_')[1])
            # Проверяем, откуда пришел запрос
            if user_data['role'] == 'student':
                # Если студент - показываем список студентов группы
                self.show_group_students_list(group_id, user_data, max_user_id, api)
            else:
                # Если преподаватель - показываем список студентов для выбора
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
                'admin': f"👋 Администратор {role_data['fio']}\n\nВыберите действие:"
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
            'admin': f"👋 Администратор {user['fio']}\n\nВыберите действие:"
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
    
    def show_teacher_groups(self, user: Dict, max_user_id: int, api, broadcast=False):
        """Показать группы преподавателя"""
        groups = Teacher.get_teacher_groups(user['id'])
        if not groups:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет назначенных групп",
                attachments=[create_back_keyboard()]
            )
            return
        
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
        today = datetime.now().strftime("%d.%m.%Y")
        weekday = datetime.now().strftime("%A")
        weekday_ru = {
            'Monday': 'Понедельник',
            'Tuesday': 'Вторник',
            'Wednesday': 'Среда',
            'Thursday': 'Четверг',
            'Friday': 'Пятница',
            'Saturday': 'Суббота',
            'Sunday': 'Воскресенье'
        }
        
        # TODO: Получить расписание из БД
        text = f"📅 Расписание на сегодня ({weekday_ru.get(weekday, weekday)}, {today}):\n\n"
        text += "⚠️ Расписание пока не настроено.\n"
        text += "Обратитесь к администратору для настройки расписания."
        
        keyboard = create_back_keyboard("menu_schedule")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def show_schedule_week(self, user: Dict, max_user_id: int, api):
        """Показать расписание на неделю"""
        # TODO: Получить расписание из БД
        text = "📆 Расписание на неделю:\n\n"
        text += "⚠️ Расписание пока не настроено.\n"
        text += "Обратитесь к администратору для настройки расписания."
        
        keyboard = create_back_keyboard("menu_schedule")
        api.send_message(
            user_id=max_user_id,
            text=text,
            attachments=[keyboard]
        )
    
    def download_schedule(self, user: Dict, max_user_id: int, api):
        """Скачать расписание"""
        # TODO: Генерация файла расписания
        text = "⬇️ Скачать расписание\n\n"
        text += "⚠️ Функция скачивания расписания пока не реализована.\n"
        text += "Обратитесь к администратору."
        
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
            keyboard = create_help_menu_keyboard()
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

