"""Обработка команд бота"""
from typing import Dict, Any
from handlers.base import BaseHandler
from utils.keyboard import create_main_menu_keyboard, create_role_selection_keyboard
from utils.states import get_user_role, set_user_state


class CommandsHandler(BaseHandler):
    """Обработчик команд"""
    
    def can_handle(self, update: Dict[str, Any]) -> bool:
        update_type = update.get('update_type')
        
        # Обрабатываем bot_started (кнопка "Начать" в мессенджере)
        if update_type == 'bot_started':
            return True
        
        # Обрабатываем команды в сообщениях
        if update_type != 'message_created':
            return False
        
        message = update.get('message', {})
        body = message.get('body', {})
        text = body.get('text', '').strip()
        
        # Обрабатываем команды (начинающиеся с /) и пустые сообщения
        return text.startswith('/') or not text
    
    def handle(self, update: Dict[str, Any], api) -> None:
        update_type = update.get('update_type')
        
        # Обработка bot_started (кнопка "Начать" в мессенджере)
        if update_type == 'bot_started':
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Получено обновление bot_started: {update}")
            
            # Пробуем разные варианты структуры обновления
            # Вариант 1: user в корне
            user = update.get('user', {})
            # Вариант 2: sender (как в message_created)
            if not user:
                user = update.get('sender', {})
            # Вариант 3: данные пользователя в корне
            if not user and 'user_id' in update:
                user = update
            
            user_id = user.get('user_id') if user else None
            user_name = user.get('first_name', '') if user else ''
            
            # Пробуем найти chat_id в разных местах
            chat_id = None
            # Вариант 1: chat.chat_id
            if 'chat' in update:
                chat_id = update.get('chat', {}).get('chat_id')
            # Вариант 2: chat_id в корне
            if not chat_id:
                chat_id = update.get('chat_id')
            # Вариант 3: recipient.chat_id (как в message_created)
            if not chat_id and 'recipient' in update:
                chat_id = update.get('recipient', {}).get('chat_id')
            # Вариант 4: для личных сообщений используем user_id как chat_id
            if not chat_id and user_id:
                chat_id = user_id
            
            if not user_id:
                logger.warning(f"Не удалось получить user_id из обновления bot_started. Структура: {update}")
                return
            
            logger.info(f"Обработка bot_started: user_id={user_id}, user_name={user_name}, chat_id={chat_id}")
            self._handle_start(chat_id, user_id, user_name, api)
            return
        
        # Обработка команд в сообщениях
        message = update.get('message', {})
        recipient = message.get('recipient', {})
        chat_id = recipient.get('chat_id')
        body = message.get('body', {})
        text = body.get('text', '').strip()
        sender = message.get('sender', {})
        user_id = sender.get('user_id')
        user_name = sender.get('first_name', '')
        
        command = text.split()[0] if text else ''
        
        # Если сообщение пустое (кнопка "Начать" в мессенджере) или команда /start
        if not text or command == '/start':
            self._handle_start(chat_id, user_id, user_name, api)
        elif command == '/help':
            self._handle_help(chat_id, api)
        elif command == '/menu':
            self._handle_menu(chat_id, api)
        elif command == '/role':
            self._handle_role(chat_id, api)
        else:
            api.send_message(
                chat_id=chat_id,
                text=f"Неизвестная команда: {command}\nИспользуйте /help для списка команд."
            )
    
    def _handle_start(self, chat_id: int, user_id: int, user_name: str, api) -> None:
        """Обработка команды /start или кнопки 'Начать'"""
        from utils.states import get_user_role, set_user_state
        
        role = get_user_role(user_id)
        
        # Персонализированное приветствие
        if user_name:
            greeting = f"👋 Привет, {user_name}!"
        else:
            greeting = "👋 Добро пожаловать!"
        
        welcome_text = (
            f"{greeting}\n\n"
            "Добро пожаловать в бот университета!\n\n"
            "Я помогу вам с:\n"
            "• 📚 Поступлением\n"
            "• 🎓 Обучением\n"
            "• 🚀 Проектной деятельностью\n"
            "• 💼 Карьерой\n"
            "• 📋 Работой деканата\n"
            "• 🏠 Общежитием\n"
            "• 📖 Библиотекой\n\n"
        )
        
        if not role:
            welcome_text += "Для начала выберите вашу роль:"
            keyboard = create_role_selection_keyboard()
        else:
            welcome_text += f"Ваша роль: {self._get_role_name(role)}\n\nВыберите раздел:"
            keyboard = create_main_menu_keyboard()
        
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=welcome_text, attachments=attachments)
        set_user_state(user_id, 'idle')
    
    def _handle_help(self, chat_id: int, api) -> None:
        """Обработка команды /help"""
        help_text = (
            "📖 Доступные команды:\n\n"
            "/start - Начать работу с ботом\n"
            "/menu - Открыть главное меню\n"
            "/role - Выбрать/изменить роль\n"
            "/help - Показать эту справку\n\n"
            "Используйте кнопки меню для навигации по разделам."
        )
        api.send_message(chat_id=chat_id, text=help_text)
    
    def _handle_menu(self, chat_id: int, api) -> None:
        """Обработка команды /menu"""
        keyboard = create_main_menu_keyboard()
        text = "🏠 Главное меню:\n\nВыберите интересующий раздел:"
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments)
    
    def _handle_role(self, chat_id: int, api) -> None:
        """Обработка команды /role"""
        keyboard = create_role_selection_keyboard()
        text = "👤 Выберите вашу роль:"
        attachments = [keyboard]
        api.send_message(chat_id=chat_id, text=text, attachments=attachments)
    
    def _get_role_name(self, role: str) -> str:
        """Возвращает читаемое имя роли"""
        role_names = {
            'applicant': '🎓 Абитуриент',
            'student': '👨‍🎓 Студент',
            'staff': '👔 Сотрудник',
            'admin': '👑 Администрация'
        }
        return role_names.get(role, role)

