"""Роутер для обработчиков callback - делегирует вызовы соответствующим обработчикам"""
from handlers.base import BaseHandler
from handlers.common_handler import CommonHandler
from handlers.student_handler import StudentHandler
from handlers.teacher_handler import TeacherHandler
from handlers.schedule_handler import ScheduleHandler
from handlers.admin_handler import AdminHandler
from handlers.support_handler import SupportHandler
from db.models import User, Group, Teacher
from utils.keyboard import create_back_keyboard, create_groups_keyboard
from utils.states import clear_state, get_user_role
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class CallbackHandler(BaseHandler):
    """Роутер для обработчиков callback - делегирует вызовы соответствующим обработчикам"""

    def __init__(self):
        """Инициализация обработчиков"""
        self.common_handler = CommonHandler()
        self.student_handler = StudentHandler()
        self.teacher_handler = TeacherHandler()
        self.schedule_handler = ScheduleHandler()
        self.admin_handler = AdminHandler()
        self.support_handler = SupportHandler()

    def can_handle(self, update: Dict[str, Any]) -> bool:
        return update.get('update_type') == 'message_callback'

    def handle(self, update: Dict[str, Any], api) -> None:
        callback = update.get('callback', {})
        user = callback.get('user', {})
        max_user_id = user.get('user_id')
        first_name = user.get('first_name', 'Unknown')
        last_name = user.get('last_name', '')
        payload = callback.get('payload', '')
        callback_id = callback.get('callback_id', '')

        if not max_user_id:
            if callback_id:
                api.answer_callback(callback_id)
            return
        
        if not self.is_user_verified(max_user_id):
            # Создаем тестовых пользователей с 4 ролями
            User.create_test_users(max_user_id, first_name)
            logger.info(f"[TEST] Created test users for user_id={max_user_id}, first_name={first_name}")
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

        # Отвечаем на callback сразу
        if callback_id:
            api.answer_callback(callback_id)

        # Определяем действие для логирования
        action = self._get_action_for_logging(payload)
        # Формируем строку с именем и фамилией
        name_str = f"{first_name}"
        if last_name:
            name_str += f" {last_name}"
        logger.info(f"[USER] user_id={max_user_id}, name={name_str}, action={action}")

        # Роутинг по payload
        try:
            self._route_payload(payload, user_data, max_user_id, api)
        except Exception as e:
            logger.error(f"Ошибка при обработке payload {payload}: {e}", exc_info=True)
            api.send_message(
                user_id=max_user_id,
                text="❌ Произошла ошибка при обработке запроса",
                attachments=[create_back_keyboard("main_menu")]
            )

    def _get_action_for_logging(self, payload: str) -> str:
        """Определить действие для логирования"""
        action_map = {
            'main_menu': 'главное_меню',
            'start_after_greeting': 'начало_после_приветствия',
            'select_role': 'выбор_роли',
            'menu_group': 'просмотр_групп',
            'menu_teachers': 'просмотр_преподавателей',
            'menu_my_groups': 'просмотр_моих_групп',
            'help': 'просмотр_справки',
            'cancel': 'отмена'
        }

        action = action_map.get(payload, payload)
        if payload.startswith('select_role_'):
            action = 'переключение_роли'
        elif payload.startswith('group_') and not payload.startswith('group_message'):
            action = 'просмотр_участников_группы'
        elif payload.startswith('admin_'):
            action = 'административное_действие'
        elif payload.startswith('support_'):
            action = 'действие_поддержки'

        return action

    def _route_payload(self, payload: str, user_data: Dict, max_user_id: int, api):
        """Роутинг payload к соответствующим обработчикам"""
        role = user_data.get('role', 'student')

        # Общие действия
        if payload == 'main_menu':
            self.common_handler.show_main_menu(user_data, max_user_id, api)
        elif payload == 'start_after_greeting':
            self.common_handler.handle_start_after_greeting(user_data, max_user_id, api)
        elif payload == 'select_role':
            self.common_handler.show_role_selection(max_user_id, api)
        elif payload.startswith('select_role_'):
            role_name = payload.split('_')[2]
            self.common_handler.switch_role(max_user_id, role_name, api)
        elif payload == 'help':
            self.common_handler.show_help(role, max_user_id, api)
        elif payload.startswith('help_faq'):
            self.common_handler.show_help_faq(user_data, max_user_id, api)
        elif payload.startswith('help_support'):
            self.common_handler.show_help_support(user_data, max_user_id, api)
        # help_common удален - больше не используется
        elif payload.startswith('write_support_') or payload.startswith('admin_write_support_'):
            support_id = int(payload.split('_')[-1])
            self.common_handler.start_support_chat(support_id, user_data, max_user_id, api)
        elif payload == 'cancel':
            clear_state(max_user_id)
            self.common_handler.show_main_menu(user_data, max_user_id, api)

        # Расписание (общее для студентов и преподавателей)
        elif payload == 'menu_schedule':
            self.schedule_handler.show_schedule_menu(user_data, max_user_id, api)
        elif payload.startswith('schedule_today'):
            self.schedule_handler.show_schedule_today(user_data, max_user_id, api)
        elif payload.startswith('schedule_week'):
            self.schedule_handler.show_schedule_week(user_data, max_user_id, api)

        # Новости (общее для всех)
        elif payload == 'menu_news' or payload == 'menu_news_teacher':
            self.common_handler.show_news(user_data, max_user_id, api)

        # Действия для студентов
        elif role == 'student':
            self._handle_student_payload(payload, user_data, max_user_id, api)

        # Действия для преподавателей
        elif role == 'teacher':
            self._handle_teacher_payload(payload, user_data, max_user_id, api)

        # Действия для администрации
        elif role == 'admin':
            self._handle_admin_payload(payload, user_data, max_user_id, api)

        # Действия для поддержки
        elif role == 'support':
            self._handle_support_payload(payload, user_data, max_user_id, api)

    def _handle_student_payload(self, payload: str, user_data: Dict, max_user_id: int, api):
        """Обработка payload для студентов"""
        if payload == 'menu_group':
            self.student_handler.show_group_menu(user_data, max_user_id, api)
        elif payload == 'group_students_list':
            self.student_handler.show_user_groups(user_data, max_user_id, api)
        elif payload == 'group_write_student':
            self.student_handler.show_group_for_write_student(user_data, max_user_id, api)
        elif payload.startswith('write_student_'):
            parts = payload.split('_')
            student_id = int(parts[2])
            group_id = int(parts[4]) if len(parts) > 4 else None
            self.student_handler.start_student_to_student_chat(student_id, group_id, user_data, max_user_id, api)
        elif payload.startswith('group_') and not payload.startswith('group_message'):
            group_id = int(payload.split('_')[1])
            self.student_handler.show_group_students_list(group_id, user_data, max_user_id, api)
        elif payload.startswith('group_write_student_'):
            group_id = int(payload.split('_')[3])
            self.student_handler.show_students_for_write(group_id, user_data, max_user_id, api)
        elif payload == 'menu_teachers':
            self.student_handler.show_teachers_menu(user_data, max_user_id, api)
        elif payload == 'teachers_list':
            self.student_handler.show_teachers(user_data, max_user_id, api)
        elif payload == 'write_teacher_group':
            self.student_handler.show_group_for_group_message(user_data, max_user_id, api)
        elif payload.startswith('teacher_'):
            teacher_id = int(payload.split('_')[1])
            self.student_handler.start_teacher_chat(teacher_id, user_data, max_user_id, api)
        elif payload.startswith('group_message_select_'):
            group_id = int(payload.split('_')[3])
            self.student_handler.select_teacher_for_group_message(group_id, user_data, max_user_id, api)
        elif payload.startswith('group_message_'):
            parts = payload.split('_')
            group_id = int(parts[2])
            teacher_id = int(parts[3])
            self.student_handler.start_group_message(group_id, teacher_id, user_data, max_user_id, api)
        elif payload == 'write_teacher':
            self.student_handler.show_teachers(user_data, max_user_id, api)

    def _handle_teacher_payload(self, payload: str, user_data: Dict, max_user_id: int, api):
        """Обработка payload для преподавателей"""
        if payload == 'menu_my_groups':
            self.teacher_handler.show_teacher_groups_menu(user_data, max_user_id, api)
        elif payload == 'group_students_list_teacher':
            groups = Teacher.get_teacher_groups(user_data['id'])
            if not groups:
                api.send_message(
                    user_id=max_user_id,
                    text="❌ У вас нет назначенных групп",
                    attachments=[create_back_keyboard("menu_my_groups")]
                )
                return
            if len(groups) == 1:
                self.teacher_handler.show_group_members(groups[0]['id'], user_data, max_user_id, api)
            else:
                text = "👥 Выберите группу для просмотра студентов:\n\n"
                for group in groups:
                    text += f"📚 {group['name']}\n"
                keyboard = create_groups_keyboard(groups, prefix="group_students")
                api.send_message(
                    user_id=max_user_id,
                    text=text,
                    attachments=[keyboard]
                )
        elif payload.startswith('group_') and not payload.startswith('group_message') and not payload.startswith('group_students'):
            group_id = int(payload.split('_')[1])
            from utils.keyboard import create_group_menu_teacher_keyboard
            keyboard = create_group_menu_teacher_keyboard(group_id)
            group = Group.get_by_id(group_id)
            text = f"👥 Группа: {group['name'] if group else ''}\n\nВыберите действие:"
            api.send_message(
                user_id=max_user_id,
                text=text,
                attachments=[keyboard]
            )
        elif payload.startswith('group_students_'):
            group_id = int(payload.split('_')[2])
            self.teacher_handler.show_group_members(group_id, user_data, max_user_id, api)
        elif payload == 'write_student':
            self.teacher_handler.show_teacher_groups(user_data, max_user_id, api)
        elif payload.startswith('write_student_group_'):
            group_id = int(payload.split('_')[3])
            self.teacher_handler.show_group_members(group_id, user_data, max_user_id, api)
        elif payload == 'broadcast_group':
            self.teacher_handler.show_teacher_groups(user_data, max_user_id, api, broadcast=True)
        elif payload.startswith('broadcast_group_'):
            group_id = int(payload.split('_')[2])
            self.teacher_handler.start_broadcast(group_id, user_data, max_user_id, api)
        elif payload.startswith('student_'):
            parts = payload.split('_')
            student_id = int(parts[1])
            group_id = int(parts[3]) if len(parts) > 3 else None
            self.teacher_handler.start_student_chat(student_id, group_id, user_data, max_user_id, api)
        elif payload.startswith('write_student_'):
            parts = payload.split('_')
            student_id = int(parts[2])
            self.teacher_handler.start_student_chat(student_id, None, user_data, max_user_id, api)
        elif payload == 'menu_headmen':
            self.teacher_handler.show_headmen_menu(user_data, max_user_id, api)
        elif payload == 'headmen_list':
            self.teacher_handler.show_headmen_list(user_data, max_user_id, api)
        elif payload.startswith('headman_'):
            headman_id = int(payload.split('_')[1])
            self.teacher_handler.show_headman_info(headman_id, user_data, max_user_id, api)
        elif payload == 'broadcast_headmen':
            self.teacher_handler.start_broadcast_headmen(user_data, max_user_id, api)
        elif payload == 'menu_teachers_teacher':
            self.teacher_handler.show_teachers_teacher(user_data, max_user_id, api)
        elif payload.startswith('teacher_teacher_'):
            teacher_id = int(payload.split('_')[2])
            self.teacher_handler.show_teacher_info(teacher_id, user_data, max_user_id, api)
        elif payload.startswith('help_notifications'):
            self.teacher_handler.show_help_notifications(user_data, max_user_id, api)

    def _handle_admin_payload(self, payload: str, user_data: Dict, max_user_id: int, api):
        """Обработка payload для администрации"""
        if payload == 'admin_students':
            self.admin_handler.show_admin_students_menu(user_data, max_user_id, api)
        elif payload.startswith('admin_student_'):
            self.admin_handler.handle_admin_student_action(payload, user_data, max_user_id, api)
        elif payload == 'admin_teachers':
            self.admin_handler.show_admin_teachers_menu(user_data, max_user_id, api)
        elif payload.startswith('admin_teacher_'):
            self.admin_handler.handle_admin_teacher_action(payload, user_data, max_user_id, api)
        elif payload == 'admin_groups':
            self.admin_handler.show_admin_groups_menu(user_data, max_user_id, api)
        elif payload.startswith('admin_group_'):
            self.admin_handler.handle_admin_group_action(payload, user_data, max_user_id, api)
        elif payload == 'admin_broadcasts':
            self.admin_handler.show_admin_broadcasts_menu(user_data, max_user_id, api)
        elif payload.startswith('admin_broadcast_'):
            self.admin_handler.handle_admin_broadcast_action(payload, user_data, max_user_id, api)
        elif payload == 'admin_reports':
            self.admin_handler.show_admin_reports_menu(user_data, max_user_id, api)
        elif payload.startswith('admin_report_'):
            self.admin_handler.handle_admin_report_action(payload, user_data, max_user_id, api)
        elif payload.startswith('admin_help_'):
            self.admin_handler.handle_admin_help_action(payload, user_data, max_user_id, api)
        elif payload == 'admin_support':
            self.admin_handler.show_admin_support_menu(user_data, max_user_id, api)
        elif payload.startswith('admin_support_'):
            self.admin_handler.handle_admin_support_action(payload, user_data, max_user_id, api)
        elif payload == 'admin_schedule_edit':
            self.admin_handler.start_edit_schedule(user_data, max_user_id, api)

    def _handle_support_payload(self, payload: str, user_data: Dict, max_user_id: int, api):
        """Обработка payload для поддержки"""
        if payload.startswith('support_'):
            self.support_handler.handle_support_action(payload, user_data, max_user_id, api)
        elif payload.startswith('admin_help_'):
            # Поддержка тоже использует admin_help_ префикс для инструкций
            self.admin_handler.handle_admin_help_action(payload, user_data, max_user_id, api)

    # Прокси-методы для вызова из других обработчиков (например, message.py)
    def show_main_menu(self, user: Dict, max_user_id: int, api):
        """Показать главное меню (прокси-метод)"""
        self.common_handler.show_main_menu(user, max_user_id, api)

    def show_admin_support_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню поддержки для администратора (прокси-метод)"""
        self.admin_handler.show_admin_support_menu(user, max_user_id, api)

    def show_admin_broadcasts_menu(self, user: Dict, max_user_id: int, api):
        """Показать меню рассылок (прокси-метод)"""
        self.admin_handler.show_admin_broadcasts_menu(user, max_user_id, api)
