"""Обертка над Max Bot API"""
import requests
import os
from typing import Optional, Dict, Any

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('MAX_BOT_TOKEN')
API_BASE_URL = 'https://platform-api.max.ru'


class MaxAPI:
    """Клиент для работы с Max Bot API"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or TOKEN
        self.base_url = API_BASE_URL
    
    def _get_params(self, **kwargs) -> dict:
        """Добавляет access_token к параметрам"""
        params = {'access_token': self.token}
        params.update(kwargs)
        return params
    
    def get_me(self) -> Dict[str, Any]:
        """Получает информацию о боте"""
        try:
            response = requests.get(
                f'{self.base_url}/me',
                params=self._get_params(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении информации о боте: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"  Детали ошибки: {error_data}")
                except:
                    print(f"  Статус код: {e.response.status_code}")
            return {}
    
    def get_updates(self, marker: Optional[int] = None, timeout: int = 30, limit: int = 100) -> Dict[str, Any]:
        """Получает обновления через long polling"""
        params = self._get_params(timeout=timeout, limit=limit)
        if marker:
            params['marker'] = marker
        
        try:
            response = requests.get(
                f'{self.base_url}/updates',
                params=params,
                timeout=timeout + 5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении обновлений: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"  Детали ошибки: {error_data}")
                except:
                    pass
            return {}
    
    def send_message(
        self,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
        text: str = '',
        attachments: Optional[list] = None,
        format_type: Optional[str] = None
    ) -> bool:
        """Отправляет сообщение в чат или пользователю"""
        if not chat_id and not user_id:
            print("Ошибка: нужно указать chat_id или user_id")
            return False
        
        params = self._get_params()
        if chat_id:
            params['chat_id'] = chat_id
        if user_id:
            params['user_id'] = user_id
        
        data = {
            'text': text,
            'attachments': attachments or [],
            'link': None
        }
        
        if format_type:
            data['format'] = format_type
        
        # Отладочный вывод структуры клавиатуры
        if attachments:
            for att in attachments:
                if att.get('type') == 'inline_keyboard':
                    import json
                    print(f"DEBUG: Отправка клавиатуры: {json.dumps(att, ensure_ascii=False, indent=2)}")
        
        try:
            response = requests.post(
                f'{self.base_url}/messages',
                params=params,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при отправке сообщения: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"  Детали ошибки: {error_data}")
                except:
                    pass
            return False
    
    def send_action(self, chat_id: int, action: str) -> bool:
        """Отправляет действие бота (typing_on, sending_photo, etc.)"""
        try:
            response = requests.post(
                f'{self.base_url}/chats/{chat_id}/actions',
                params=self._get_params(),
                json={'action': action},
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при отправке действия: {e}")
            return False

