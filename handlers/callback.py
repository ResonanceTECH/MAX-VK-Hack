"""Обработка нажатий кнопок"""
from typing import Dict, Any
from handlers.base import BaseHandler
from utils.keyboard import (
    create_main_menu_keyboard,
    create_role_selection_keyboard,
    create_back_to_menu_button
)
from utils.states import set_user_role, get_user_role, set_user_state, clear_user_role


class CallbackHandler(BaseHandler):
    """Обработчик нажатий кнопок"""
    
    def can_handle(self, update: Dict[str, Any]) -> bool:
        return update.get('update_type') == 'message_callback'
    
    def handle(self, update: Dict[str, Any], api) -> None:
        callback = update.get('callback', {})
        payload = callback.get('payload', '')
        user = callback.get('user', {})
        user_id = user.get('user_id')
        user_name = user.get('first_name', 'Пользователь')
        message = update.get('message', {})
        recipient = message.get('recipient', {})
        chat_id = recipient.get('chat_id')
        
        # Обработка выбора роли
        if payload.startswith('role_'):
            self._handle_role_selection(chat_id, user_id, user_name, payload, api)
        # Обработка главного меню
        elif payload.startswith('menu_'):
            self._handle_menu(chat_id, user_id, user_name, payload, api)
        else:
            api.send_message(
                chat_id=chat_id,
                text="Функция в разработке 🚧"
            )
    
    def _handle_role_selection(self, chat_id: int, user_id: int, user_name: str, payload: str, api) -> None:
        """Обработка выбора роли"""
        from utils.keyboard import create_admission_main_keyboard
        
        role_map = {
            'role_applicant': 'applicant',
            'role_student': 'student',
            'role_staff': 'staff',
            'role_admin': 'admin'
        }
        
        role = role_map.get(payload)
        if role:
            set_user_role(user_id, role)
            role_names = {
                'applicant': '🎓 Абитуриент',
                'student': '👨‍🎓 Студент',
                'staff': '👔 Сотрудник',
                'admin': '👑 Администрация'
            }
            
            # Для абитуриента сразу показываем меню модуля Поступление
            if role == 'applicant':
                from utils.keyboard import create_admission_main_keyboard
                text = (
                    f"{user_name}, раздел для абитуриентов:"
                )
                keyboard = create_admission_main_keyboard()
            # Для студента показываем главное меню студентов
            elif role == 'student':
                from handlers.student import StudentHandler
                student_handler = StudentHandler()
                student_handler._show_student_main(chat_id, user_name, api)
                set_user_state(user_id, 'idle')
                return
            # Для сотрудника показываем главное меню сотрудников
            elif role == 'staff':
                from handlers.staff import StaffHandler
                staff_handler = StaffHandler()
                staff_handler._show_staff_main(chat_id, user_name, api)
                set_user_state(user_id, 'idle')
                return
            # Для администратора показываем главное меню администраторов
            elif role == 'admin':
                from handlers.admin import AdminHandler
                admin_handler = AdminHandler()
                admin_handler._show_admin_main(chat_id, user_name, api)
                set_user_state(user_id, 'idle')
                return
            else:
                text = (
                    f"✅ Роль установлена: {role_names[role]}\n\n"
                    "Теперь вы можете использовать все функции бота.\n"
                    "Выберите раздел из меню:"
                )
                keyboard = create_main_menu_keyboard()
            
            attachments = [keyboard]
            api.send_message(chat_id=chat_id, text=text, attachments=attachments)
            set_user_state(user_id, 'idle')
    
    def _handle_menu(self, chat_id: int, user_id: int, user_name: str, payload: str, api) -> None:
        """Обработка выбора пункта меню"""
        role = get_user_role(user_id)
        
        if payload == 'menu_main':
            # Главное меню всегда возвращает к выбору роли
            keyboard = create_role_selection_keyboard()
            text = (
                "👋 Добро пожаловать в бот университета!\n\n"
                "Я помогу вам с:\n"
                "• 📚 Поступлением\n"
                "• 🎓 Обучением\n"
                "• 🚀 Проектной деятельностью\n"
                "• 💼 Карьерой\n"
                "• 📋 Работой деканата\n"
                "• 🏠 Общежитием\n"
                "• 📖 Библиотекой\n\n"
                "Для начала выберите вашу роль:"
            )
            attachments = [keyboard]
            api.send_message(chat_id=chat_id, text=text, attachments=attachments)
            # Сбрасываем роль при возврате в главное меню
            clear_user_role(user_id)
            set_user_state(user_id, 'idle')
            return
        
        # Проверка роли для некоторых разделов
        if payload in ['menu_education', 'menu_deanery', 'menu_dormitory'] and role != 'student':
            api.send_message(
                chat_id=chat_id,
                text="⚠️ Этот раздел доступен только для студентов."
            )
            return
        
        menu_items = {
            'menu_admission': {
                'text': None,  # Обрабатывается AdmissionHandler
                'emoji': '📚'
            },
            'menu_education': {
                'text': (
                    "🎓 Модуль 'Обучение'\n\n"
                    "Здесь вы можете:\n"
                    "• Посмотреть расписание\n"
                    "• Оставить обратную связь\n"
                    "• Записаться на факультативы\n\n"
                    "Функционал в разработке 🚧"
                ),
                'emoji': '🎓'
            },
            'menu_projects': {
                'text': (
                    "🚀 Модуль 'Проектная деятельность'\n\n"
                    "Здесь вы можете:\n"
                    "• Найти проект\n"
                    "• Создать проект\n"
                    "• Найти команду\n\n"
                    "Функционал в разработке 🚧"
                ),
                'emoji': '🚀'
            },
            'menu_career': {
                'text': (
                    "💼 Модуль 'Карьера'\n\n"
                    "Здесь вы можете:\n"
                    "• Посмотреть вакансии\n"
                    "• Записаться на консультацию\n\n"
                    "Функционал в разработке 🚧"
                ),
                'emoji': '💼'
            },
            'menu_deanery': {
                'text': (
                    "📋 Модуль 'Деканат'\n\n"
                    "Здесь вы можете:\n"
                    "• Подать заявку на справку\n"
                    "• Оплатить обучение\n\n"
                    "Функционал в разработке 🚧"
                ),
                'emoji': '📋'
            },
            'menu_dormitory': {
                'text': (
                    "🏠 Модуль 'Общежитие'\n\n"
                    "Здесь вы можете:\n"
                    "• Управлять проживанием\n"
                    "• Подать заявку в техподдержку\n"
                    "• Оформить гостевой пропуск\n\n"
                    "Функционал в разработке 🚧"
                ),
                'emoji': '🏠'
            },
            'menu_library': {
                'text': (
                    "📖 Модуль 'Библиотека'\n\n"
                    "Здесь вы можете:\n"
                    "• Найти литературу\n"
                    "• Заказать книгу\n\n"
                    "Функционал в разработке 🚧"
                ),
                'emoji': '📖'
            },
            'menu_settings': {
                'text': (
                    "⚙️ Настройки\n\n"
                    "Здесь вы можете:\n"
                    "• Изменить профиль\n"
                    "• Настроить уведомления\n"
                    "• Сменить пароль\n\n"
                    "Функционал в разработке 🚧"
                ),
                'emoji': '⚙️'
            }
        }
        
        item = menu_items.get(payload)
        if item:
            # Если текст None, значит обработка передается специализированному handler
            if item['text'] is None:
                # Передаем обработку в AdmissionHandler (он будет вызван после CallbackHandler)
                return
            keyboard = create_back_to_menu_button()
            attachments = [keyboard]
            api.send_message(
                chat_id=chat_id,
                text=item['text'],
                attachments=attachments
            )

