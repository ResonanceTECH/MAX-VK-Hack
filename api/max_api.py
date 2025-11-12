"""Обертка над Max Bot API"""
import requests
import os
import logging
import io
import json
import base64
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
    ) -> Optional[Dict[str, Any]]:
        """Отправляет сообщение в чат или пользователю. Возвращает данные сообщения или None"""
        if not chat_id and not user_id:
            print("Ошибка: нужно указать chat_id или user_id")
            return None

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

        try:
            response = requests.post(
                f'{self.base_url}/messages',
                params=params,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при отправке сообщения: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"  Детали ошибки: {error_data}")
                except:
                    pass
            return None

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

    def answer_callback(self, callback_id: str, notification: Optional[str] = None,
                        message: Optional[Dict] = None) -> bool:
        """Ответить на callback (убрать индикатор загрузки)"""
        try:
            data = {}
            if notification:
                data['notification'] = notification
            if message:
                data['message'] = message

            # Если data пустой, отправляем пустой объект
            if not data:
                data = {}

            response = requests.post(
                f'{self.base_url}/answers',
                params=self._get_params(callback_id=callback_id),
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            # Игнорируем ошибку 400 - callback уже обработан или недействителен
            if e.response.status_code == 400:
                return False
            logger = logging.getLogger(__name__)
            logger.warning(f"Ошибка при ответе на callback (HTTP {e.response.status_code}): {e}")
            return False
        except requests.exceptions.RequestException as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Ошибка при ответе на callback: {e}")
            return False

    def send_photo(
            self,
            chat_id: Optional[int] = None,
            user_id: Optional[int] = None,
            photo: Optional[io.BytesIO] = None,
            caption: Optional[str] = None,
            attachments: Optional[list] = None
    ) -> Optional[Dict[str, Any]]:
        """Отправляет фото пользователю или в чат"""
        if not chat_id and not user_id:
            print("Ошибка: нужно указать chat_id или user_id")
            return None

        params = self._get_params()
        if chat_id:
            params['chat_id'] = chat_id
        if user_id:
            params['user_id'] = user_id

        try:
            # Max API требует JSON формат, поэтому используем base64 для изображения
            if photo:
                photo.seek(0)  # Убеждаемся, что указатель в начале

                # Читаем байты изображения
                photo_bytes = photo.read()

                # Кодируем в base64
                photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')

                # Формируем JSON payload в том же формате, что и send_message
                # Max API может не поддерживать прямую отправку изображений через attachments
                # Попробуем использовать формат, аналогичный send_message
                data = {
                    'text': caption or '',
                    'attachments': attachments or [],
                    'link': None
                }

                # Добавляем фото в attachments в формате base64
                # Формат может быть: {'type': 'photo', 'payload': {'data': base64}}
                photo_attachment = {
                    'type': 'photo',
                    'payload': {
                        'data': photo_base64,
                        'filename': 'schedule.png'
                    }
                }
                data['attachments'].append(photo_attachment)

                # Отправляем как JSON (как в send_message)
                response = requests.post(
                    f'{self.base_url}/messages',
                    params=params,
                    json=data,
                    timeout=30
                )
            else:
                # Если нет фото, отправляем обычное сообщение
                data = {
                    'text': caption or '',
                }
                if attachments:
                    data['attachments'] = attachments

                response = requests.post(
                    f'{self.base_url}/messages',
                    params=params,
                    json=data,
                    timeout=30
                )

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при отправке фото: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"  Детали ошибки: {error_data}")
                except:
                    print(f"  Статус код: {e.response.status_code}")
                    print(f"  Текст ответа: {e.response.text[:500]}")
            return None

    def set_webapp(self, webapp_url: str) -> bool:
        """Настраивает URL миниприложения для бота"""
        try:
            response = requests.post(
                f'{self.base_url}/setWebApp',
                params=self._get_params(),
                json={'url': webapp_url},
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка при настройке миниприложения: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"  Детали ошибки: {error_data}")
                except:
                    logger.error(f"  Статус код: {e.response.status_code}")
            return False
