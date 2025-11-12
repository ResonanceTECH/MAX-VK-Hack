"""Обработчик события bot_started"""
from handlers.base import BaseHandler
from db.models import User
from utils.keyboard import create_role_selection_keyboard, create_main_menu_keyboard
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BotStartedHandler(BaseHandler):
    """Обработчик события запуска бота"""

    def can_handle(self, update: Dict[str, Any]) -> bool:
        return update.get('update_type') == 'bot_started'

    def handle(self, update: Dict[str, Any], api) -> None:
        user = update.get('user', {})
        max_user_id = user.get('user_id')
        first_name = user.get('first_name', 'Unknown')

        if not max_user_id:
            return

        logger.info(f"[USER] user_id={max_user_id}, first_name={first_name}, action=bot_started")

        # Проверка верификации
        if not self.is_user_verified(max_user_id):
            # Показываем приветствие, но без выбора роли
            api.send_message(
                user_id=max_user_id,
                text="Добро пожаловать в Цифровой университет.\n\n❌ Вы не зарегистрированы в системе. Обратитесь к администрации."
            )
            return

        # Получаем все роли пользователя
        all_roles = User.get_all_roles(max_user_id)

        if not all_roles:
            api.send_message(
                user_id=max_user_id,
                text="Добро пожаловать в Цифровой университет.\n\n❌ У вас нет назначенных ролей. Обратитесь к администрации."
            )
            return

        # Показываем приветствие с кнопкой "Начать"
        start_keyboard = {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [[{"type": "callback", "text": "Начать", "payload": "start_after_greeting"}]]
            }
        }
        api.send_message(
            user_id=max_user_id,
            text="Добро пожаловать в Цифровой университет.",
            attachments=[start_keyboard]
        )
