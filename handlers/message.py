"""Обработка обычных сообщений"""
from typing import Dict, Any
from handlers.base import BaseHandler
from utils.states import get_user_state, set_user_state
from utils.keyboard import create_main_menu_keyboard


class MessageHandler(BaseHandler):
    """Обработчик текстовых сообщений"""
    
    def can_handle(self, update: Dict[str, Any]) -> bool:
        if update.get('update_type') != 'message_created':
            return False
        
        message = update.get('message', {})
        body = message.get('body', {})
        text = body.get('text', '').strip()
        
        # Не обрабатываем команды (их обрабатывает CommandsHandler)
        return text and not text.startswith('/')
    
    def handle(self, update: Dict[str, Any], api) -> None:
        message = update.get('message', {})
        recipient = message.get('recipient', {})
        chat_id = recipient.get('chat_id')
        body = message.get('body', {})
        text = body.get('text', '').strip()
        sender = message.get('sender', {})
        user_id = sender.get('user_id')
        
        state = get_user_state(user_id)
        
        # Обработка в зависимости от состояния
        if state == 'idle':
            # Простое эхо или предложение использовать меню
            response = (
                f"Вы написали: {text}\n\n"
                "Используйте /menu для доступа к функциям бота или выберите раздел:"
            )
            keyboard = create_main_menu_keyboard()
            attachments = [keyboard]
            api.send_message(chat_id=chat_id, text=response, attachments=attachments)
        else:
            # Обработка состояний (для будущих форм)
            api.send_message(
                chat_id=chat_id,
                text="Обработка в разработке. Используйте /menu для возврата в главное меню."
            )

