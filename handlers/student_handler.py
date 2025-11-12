"""Обработчики для студентов"""
from typing import Dict, Any
from db.models import User, Group, Teacher
from utils.keyboard import (
    create_group_menu_keyboard, create_groups_keyboard,
    create_students_keyboard, create_teachers_menu_keyboard,
    create_teachers_keyboard, create_back_keyboard, create_cancel_keyboard
)
from utils.states import set_state
import logging

logger = logging.getLogger(__name__)


class StudentHandler:
    """Обработчики для студентов"""

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
        """Показать участников группы (для студентов)"""
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

        # Если пользователь - староста, добавляем кнопку отправки сообщения от группы
        buttons = []
        if Group.is_headman(user['id'], group_id):
            # Получаем преподавателей группы
            teachers = Teacher.get_student_teachers(user['id'])
            if teachers:
                buttons.append([{
                    "type": "callback",
                    "text": "💬 Написать преподавателю от группы",
                    "payload": f"group_message_select_{group_id}"
                }])

        buttons.append([{"type": "callback", "text": "◀️ Назад", "payload": "menu_group"}])

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

    def select_teacher_for_group_message(self, group_id: int, user: Dict, max_user_id: int, api):
        """Выбрать преподавателя для сообщения от группы"""
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
                "payload": f"group_message_{group_id}_{teacher['id']}"
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

    def start_group_message(self, group_id: int, teacher_id: int, user: Dict, max_user_id: int, api):
        """Начать отправку сообщения от группы"""
        teacher = User.get_by_id(teacher_id)
        group = Group.get_by_id(group_id)

        if not teacher or not group:
            api.send_message(
                user_id=max_user_id,
                text="❌ Преподаватель или группа не найдены",
                attachments=[create_back_keyboard("menu_teachers")]
            )
            return

        set_state(max_user_id, 'waiting_group_message', {
            'group_id': group_id,
            'teacher_id': teacher_id
        })
        api.send_message(
            user_id=max_user_id,
            text=f"💬 Напишите сообщение от группы {group['name']} для преподавателя {teacher['fio']}:\n\n(Отправьте текст сообщения или напишите 'отмена' для отмены)",
            attachments=[create_cancel_keyboard()]
        )

    def start_teacher_chat(self, teacher_id: int, user: Dict, max_user_id: int, api):
        """Начать диалог с преподавателем"""
        teacher = User.get_by_id(teacher_id)
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
