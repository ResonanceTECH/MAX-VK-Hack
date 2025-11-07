"""Обработчик модуля для студентов"""
from typing import Dict, Any
import logging
from handlers.base import BaseHandler
from utils.keyboard import (
    create_student_main_keyboard,
    create_schedule_keyboard,
    create_requests_main_keyboard,
    create_certificate_types_keyboard,
    create_request_created_keyboard,
    create_my_requests_keyboard,
    create_inline_keyboard,
    create_callback_button
)
from utils.states import get_user_role, set_user_role
from utils.storage import (
    STUDENT_SCHEDULE,
    create_student_request,
    get_active_student_requests
)

logger = logging.getLogger(__name__)


class StudentHandler(BaseHandler):
    """Обработчик модуля для студентов"""
    
    def can_handle(self, update: Dict[str, Any]) -> bool:
        """Проверяет, относится ли обновление к модулю студентов"""
        if update.get('update_type') == 'message_callback':
            payload = update.get('callback', {}).get('payload', '')
            # Обрабатываем payload'ы модуля студентов
            return (payload.startswith(('student_', 'schedule_', 'request_', 'certificate_')) 
                    or payload == 'student_main')
        return False
    
    def handle(self, update: Dict[str, Any], api) -> None:
        """Обрабатывает обновление модуля студентов"""
        callback = update.get('callback', {})
        payload = callback.get('payload', '')
        user = callback.get('user', {})
        user_id = user.get('user_id')
        user_name = user.get('first_name', 'Пользователь')
        message = update.get('message', {})
        recipient = message.get('recipient', {})
        chat_id = recipient.get('chat_id')
        
        logger.debug(f"StudentHandler обрабатывает payload: {payload}")
        
        role = get_user_role(user_id)
        
        # Главное меню студентов - обрабатываем даже если роль не установлена
        if payload == 'student_main' or payload == 'menu_student':
            if role != 'student':
                set_user_role(user_id, 'student')
            self._show_student_main(chat_id, user_name, api)
            return
        
        # Проверка роли для остальных действий
        if role != 'student':
            api.send_message(
                chat_id=chat_id,
                text="⚠️ Этот раздел доступен только для студентов.\nИспользуйте /role для смены роли."
            )
            return
        
        # Расписание
        if payload == 'student_schedule':
            self._show_schedule_today(chat_id, api)
        
        # Расписание на неделю
        elif payload == 'schedule_week':
            self._show_schedule_week(chat_id, api)
        
        # Изменения в расписании
        elif payload == 'schedule_changes':
            self._show_schedule_changes(chat_id, api)
        
        # Настройка напоминаний
        elif payload == 'schedule_notifications':
            self._show_schedule_notifications(chat_id, api)
        
        # Заявки
        elif payload == 'student_requests':
            self._show_requests_main(chat_id, api)
        
        # Заказать справку
        elif payload == 'request_certificate':
            self._show_certificate_types(chat_id, api)
        
        # Создание справки
        elif payload.startswith('certificate_'):
            cert_type = payload.replace('certificate_', '')
            self._create_certificate_request(chat_id, user_id, cert_type, api)
        
        # Академический отпуск
        elif payload == 'request_academic_leave':
            self._show_academic_leave(chat_id, api)
        
        # Мои заявки
        elif payload == 'request_my_requests':
            self._show_my_requests(chat_id, user_id, api)
        
        # Остальные разделы (в разработке)
        elif payload in ['student_dormitory', 'student_projects', 'student_library', 'student_events']:
            api.send_message(
                chat_id=chat_id,
                text="🚧 Функционал в разработке",
                attachments=[self._create_back_button()]
            )
        
        # Неизвестный payload
        else:
            logger.warning(f"Неизвестный payload в StudentHandler: {payload}")
            api.send_message(
                chat_id=chat_id,
                text="❌ Произошла ошибка. Попробуйте использовать /menu для возврата в меню."
            )
    
    def _show_student_main(self, chat_id: int, user_name: str, api) -> None:
        """Показывает главное меню студентов"""
        text = f"{user_name}, главное меню:"
        keyboard = create_student_main_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments)
    
    def _show_schedule_today(self, chat_id: int, api) -> None:
        """Показывает расписание на сегодня"""
        schedule = STUDENT_SCHEDULE.get('today', [])
        
        if not schedule:
            text = "На сегодня занятий нет."
        else:
            text = "**Ваше расписание на сегодня:**\n\n"
            for lesson in schedule:
                text += f"{lesson['time']} - {lesson['subject']} (ауд. {lesson['room']})\n"
        
        keyboard = create_schedule_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_schedule_week(self, chat_id: int, api) -> None:
        """Показывает расписание на неделю"""
        week_schedule = STUDENT_SCHEDULE.get('week', [])
        
        if not week_schedule:
            text = "Расписание на неделю отсутствует."
        else:
            text = "**Ваше расписание на неделю:**\n\n"
            for day_data in week_schedule:
                text += f"**{day_data['day']}:**\n"
                for lesson in day_data['lessons']:
                    text += f"  {lesson['time']} - {lesson['subject']} (ауд. {lesson['room']})\n"
                text += "\n"
        
        keyboard = create_schedule_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_schedule_changes(self, chat_id: int, api) -> None:
        """Показывает изменения в расписании"""
        text = (
            "**Изменения в расписании:**\n\n"
            "На данный момент изменений нет.\n"
            "Все изменения будут отображаться здесь."
        )
        keyboard = create_schedule_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_schedule_notifications(self, chat_id: int, api) -> None:
        """Показывает настройки напоминаний"""
        text = (
            "**Настройка напоминаний:**\n\n"
            "🚧 Функционал в разработке"
        )
        keyboard = create_schedule_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_requests_main(self, chat_id: int, api) -> None:
        """Показывает главное меню заявок"""
        text = "**Раздел заявок:**"
        keyboard = create_requests_main_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_certificate_types(self, chat_id: int, api) -> None:
        """Показывает типы справок"""
        text = "**Выберите тип справки:**"
        keyboard = create_certificate_types_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _create_certificate_request(self, chat_id: int, user_id: int, cert_type: str, api) -> None:
        """Создает заявку на справку"""
        request = create_student_request(user_id, cert_type, 'certificate')
        
        text = (
            f"✅ **Заявка #{request['id']} создана!**\n\n"
            f"**Статус:** \"{request['status']}\"\n"
            f"**Срок выполнения:** {request['processing_days']} рабочих дня"
        )
        
        keyboard = create_request_created_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_academic_leave(self, chat_id: int, api) -> None:
        """Показывает информацию об академическом отпуске"""
        text = (
            "**Академический отпуск:**\n\n"
            "🚧 Функционал в разработке"
        )
        buttons = [
            [create_callback_button('🔙 Назад', 'student_requests')],
            [create_callback_button('🏠 Главное меню', 'menu_main')]
        ]
        keyboard = create_inline_keyboard(buttons)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_my_requests(self, chat_id: int, user_id: int, api) -> None:
        """Показывает заявки пользователя"""
        from utils.storage import get_student_requests
        
        # Получаем все заявки (включая одобренные)
        all_requests = get_student_requests(user_id)
        active_requests = get_active_student_requests(user_id)
        
        # Показываем активные заявки (включая одобренные, но не завершенные)
        if not active_requests and not all_requests:
            text = "У вас нет активных заявок."
        else:
            # Показываем все активные заявки (включая одобренные)
            requests_to_show = [r for r in all_requests if r['status'] not in ['Завершено', 'Отклонено']]
            
            if not requests_to_show:
                text = "У вас нет активных заявок."
            else:
                text = "**Ваши активные заявки:**\n\n"
                for req in requests_to_show:
                    status_emoji = "✅" if req['status'] == 'одобрено' else "⏳" if req['status'] == 'В обработке' else "📋"
                    text += f"{status_emoji} #{req['id']} - {req['name']} ({req['status']})\n"
        
        keyboard = create_my_requests_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _create_back_button(self) -> Dict[str, Any]:
        """Создает кнопку назад"""
        buttons = [[create_callback_button('🔙 Назад', 'student_main')]]
        return create_inline_keyboard(buttons)

