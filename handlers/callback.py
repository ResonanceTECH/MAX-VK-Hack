"""Обработчик нажатий на кнопки"""
from handlers.base import BaseHandler
from db.models import User, Group, Teacher
from utils.keyboard import (
    create_main_menu_keyboard, create_groups_keyboard, 
    create_students_keyboard, create_teachers_keyboard,
    create_back_keyboard, create_cancel_keyboard,
    create_role_selection_keyboard
)
from utils.states import set_state, clear_state
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
        
        user_data = User.get_by_max_id(max_user_id)
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
        if payload.startswith('group_') and not payload.startswith('group_message'):
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
        elif payload == 'select_role':
            self.show_role_selection(max_user_id, api)
        elif payload.startswith('select_role_'):
            role = payload.split('_')[2]
            self.switch_role(max_user_id, role, api)
        elif payload == 'menu_group':
            self.show_user_groups(user_data, max_user_id, api)
        elif payload == 'menu_teachers':
            self.show_teachers(user_data, max_user_id, api)
        elif payload == 'menu_my_groups':
            self.show_teacher_groups(user_data, max_user_id, api)
        elif payload.startswith('group_') and not payload.startswith('group_message'):
            group_id = int(payload.split('_')[1])
            self.show_group_members(group_id, user_data, max_user_id, api)
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
    
    def show_user_groups(self, user: Dict, max_user_id: int, api):
        """Показать группы студента"""
        groups = Group.get_user_groups(user['id'])
        if not groups:
            api.send_message(
                user_id=max_user_id,
                text="❌ Вы не состоите ни в одной группе",
                attachments=[create_back_keyboard()]
            )
            return
        
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
    
    def show_teachers(self, user: Dict, max_user_id: int, api):
        """Показать список преподавателей студента"""
        teachers = Teacher.get_student_teachers(user['id'])
        if not teachers:
            api.send_message(
                user_id=max_user_id,
                text="❌ У вас нет назначенных преподавателей",
                attachments=[create_back_keyboard()]
            )
            return
        
        text = "👨‍🏫 Ваши преподаватели:\n\n"
        for teacher in teachers:
            text += f"• {teacher['fio']}\n"
        
        keyboard = create_teachers_keyboard(teachers)
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
    
    def show_help(self, role: str, max_user_id: int, api):
        """Показать справку"""
        help_text = {
            'student': (
                "📖 Справка для студентов:\n\n"
                "• Моя группа - просмотр участников группы с контактами\n"
                "• Преподаватели - список ваших преподавателей\n"
                "• Написать преподавателю - отправить сообщение\n\n"
                "Команды:\n"
                "/start - главное меню\n"
                "/help - эта справка"
            ),
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

