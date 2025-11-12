"""Обработчики для преподавателей"""
from typing import Dict, Any
from db.models import User, Group, Teacher
from utils.keyboard import (
    create_group_menu_teacher_keyboard, create_groups_keyboard,
    create_students_keyboard, create_headmen_menu_keyboard,
    create_headmen_keyboard, create_teachers_teacher_keyboard,
    create_back_keyboard, create_cancel_keyboard
)
from utils.states import set_state
import logging

logger = logging.getLogger(__name__)


class TeacherHandler:
    """Обработчики для преподавателей"""

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

    def show_group_members(self, group_id: int, user: Dict, max_user_id: int, api):
        """Показать участников группы (для преподавателя)"""
        members = Group.get_group_members(group_id)
        group = Group.get_by_id(group_id)

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

    def show_help_notifications(self, user: Dict, max_user_id: int, api):
        """Показать настройки уведомлений"""
        from utils.keyboard import create_back_keyboard
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
