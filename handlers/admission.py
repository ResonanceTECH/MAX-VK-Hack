"""Обработчик модуля Поступление"""
from typing import Dict, Any
from handlers.base import BaseHandler
from utils.keyboard import (
    create_admission_main_keyboard,
    create_faculties_keyboard,
    create_faculty_info_keyboard,
    create_application_method_keyboard,
    create_application_created_keyboard,
    create_inline_keyboard,
    create_callback_button
)
from utils.states import get_user_role, set_user_state, get_user_state
from utils.storage import (
    get_faculty_info,
    create_application,
    get_user_applications,
    FACULTIES
)


class AdmissionHandler(BaseHandler):
    """Обработчик модуля Поступление"""
    
    def can_handle(self, update: Dict[str, Any]) -> bool:
        """Проверяет, относится ли обновление к модулю Поступление"""
        if update.get('update_type') == 'message_callback':
            payload = update.get('callback', {}).get('payload', '')
            return payload.startswith(('admission_', 'faculty_', 'apply_'))
        return False
    
    def handle(self, update: Dict[str, Any], api) -> None:
        """Обрабатывает обновление модуля Поступление"""
        callback = update.get('callback', {})
        payload = callback.get('payload', '')
        user = callback.get('user', {})
        user_id = user.get('user_id')
        user_name = user.get('first_name', 'Пользователь')
        message = update.get('message', {})
        recipient = message.get('recipient', {})
        chat_id = recipient.get('chat_id')
        
        role = get_user_role(user_id)
        
        # Проверка роли
        if role != 'applicant':
            api.send_message(
                chat_id=chat_id,
                text="⚠️ Этот раздел доступен только для абитуриентов.\nИспользуйте /role для смены роли."
            )
            return
        
        # Главное меню модуля Поступление
        if payload == 'menu_admission':
            self._show_admission_main(chat_id, user_name, api)
        
        # Информация о вузе - показываем список факультетов
        elif payload == 'admission_info':
            self._show_faculties(chat_id, api)
        
        # Выбор факультета (назад из информации о факультете или из "Все факультеты")
        elif payload == 'admission_faculties':
            self._show_faculties(chat_id, api)
        
        # Информация о конкретном факультете
        elif payload.startswith('faculty_'):
            faculty_key = payload.replace('faculty_', '')
            if faculty_key == 'all':
                self._show_all_faculties(chat_id, api)
            else:
                self._show_faculty_info(chat_id, faculty_key, api)
        
        # Подача документов
        elif payload == 'admission_apply':
            self._show_application_methods(chat_id, api)
        
        # Выбор способа подачи
        elif payload.startswith('apply_'):
            method_type = payload.replace('apply_', '')
            self._handle_application_method(chat_id, user_id, method_type, api)
        
        # Мои заявления
        elif payload == 'admission_my_applications':
            self._show_user_applications(chat_id, user_id, api)
        
        # Запись на мероприятия
        elif payload == 'admission_events':
            self._show_events(chat_id, api)
    
    def _show_admission_main(self, chat_id: int, user_name: str, api) -> None:
        """Показывает главное меню модуля Поступление"""
        text = (
            f"{user_name}, раздел для абитуриентов:\n\n"
            "Выберите интересующий раздел:"
        )
        keyboard = create_admission_main_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments)
    
    def _show_faculties(self, chat_id: int, api) -> None:
        """Показывает список факультетов"""
        text = "Выберите факультет:"
        keyboard = create_faculties_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments)
    
    def _show_faculty_info(self, chat_id: int, faculty_key: str, api) -> None:
        """Показывает информацию о факультете"""
        faculty = get_faculty_info(faculty_key)
        
        if not faculty:
            api.send_message(chat_id=chat_id, text="❌ Факультет не найден")
            return
        
        text = (
            f"**{faculty['name']}:**\n\n"
            f"• Проходной балл: {faculty['passing_score']}\n"
            f"• Стоимость: {faculty['price']:,} руб/год\n"
            f"• Контакты: {faculty['contacts']}\n\n"
            f"_{faculty['description']}_"
        )
        
        keyboard = create_faculty_info_keyboard(faculty_key)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_all_faculties(self, chat_id: int, api) -> None:
        """Показывает информацию о всех факультетах"""
        text = "**Все факультеты:**\n\n"
        
        for key, faculty in FACULTIES.items():
            text += (
                f"**{faculty['name']}**\n"
                f"• Проходной балл: {faculty['passing_score']}\n"
                f"• Стоимость: {faculty['price']:,} руб/год\n"
                f"• Контакты: {faculty['contacts']}\n\n"
            )
        
        buttons = [
            [create_callback_button('🔙 Назад', 'admission_faculties')],
            [create_callback_button('🏠 Главное меню', 'menu_main')]
        ]
        keyboard = create_inline_keyboard(buttons)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_application_methods(self, chat_id: int, api) -> None:
        """Показывает способы подачи документов"""
        text = (
            "Начинаем процесс подачи документов.\n\n"
            "Выберите способ:"
        )
        keyboard = create_application_method_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments)
    
    def _handle_application_method(self, chat_id: int, user_id: int, method_type: str, api) -> None:
        """Обрабатывает выбор способа подачи документов"""
        method_names = {
            'online': 'Онлайн-заявление',
            'offline': 'Запись на очную подачу',
            'consultation': 'Консультация'
        }
        
        method_name = method_names.get(method_type, method_type)
        
        # Для упрощения создаем заявление с первым факультетом
        # В реальности здесь должна быть форма выбора факультета
        faculty_key = 'informatics'  # По умолчанию
        
        application = create_application(user_id, faculty_key, method_name)
        
        faculty = get_faculty_info(faculty_key)
        faculty_name = faculty['name'] if faculty else 'Не указан'
        
        text = (
            f"✅ Заявление #{application['id']} создано!\n\n"
            f"**Факультет:** {faculty_name}\n"
            f"**Способ подачи:** {method_name}\n"
            f"**Статус:** {application['status']}\n\n"
            "Мы уведомим вас о результате."
        )
        
        keyboard = create_application_created_keyboard()
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_user_applications(self, chat_id: int, user_id: int, api) -> None:
        """Показывает заявления пользователя"""
        applications_list = get_user_applications(user_id)
        
        if not applications_list:
            text = (
                "📄 У вас пока нет заявлений.\n\n"
                "Хотите подать новое заявление?"
            )
            buttons = [
                [create_callback_button('📝 Подать документы', 'admission_apply')],
                [
                    create_callback_button('🔙 Назад', 'menu_admission'),
                    create_callback_button('🏠 Главное меню', 'menu_main')
                ]
            ]
            keyboard = create_inline_keyboard(buttons)
            attachments = [keyboard]
            api.send_message(chat_id=chat_id, text=text, attachments=attachments)
            return
        
        text = "📄 **Ваши заявления:**\n\n"
        
        for i, app in enumerate(applications_list, 1):
            faculty = get_faculty_info(app['faculty'])
            faculty_name = faculty['name'] if faculty else app['faculty']
            
            text += (
                f"**{i}. {app['id']}**\n"
                f"Факультет: {faculty_name}\n"
                f"Способ: {app['method']}\n"
                f"Статус: {app['status']}\n\n"
            )
        
        buttons = [
            [create_callback_button('🔙 Назад', 'menu_admission')],
            [create_callback_button('🏠 Главное меню', 'menu_main')]
        ]
        keyboard = create_inline_keyboard(buttons)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')
    
    def _show_events(self, chat_id: int, api) -> None:
        """Показывает информацию о мероприятиях"""
        text = (
            "📅 **Запись на мероприятия**\n\n"
            "• Дни открытых дверей\n"
            "• Мастер-классы\n"
            "• Экскурсии по кампусу\n\n"
            "Функционал в разработке 🚧"
        )
        buttons = [
            [create_callback_button('🔙 Назад', 'menu_admission')],
            [create_callback_button('🏠 Главное меню', 'menu_main')]
        ]
        keyboard = create_inline_keyboard(buttons)
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments, format_type='markdown')

