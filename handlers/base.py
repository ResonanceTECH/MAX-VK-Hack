"""Базовый класс для обработчиков"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from db.models import User

class BaseHandler(ABC):
    """Базовый класс для обработчиков"""
    
    @abstractmethod
    def can_handle(self, update: Dict[str, Any]) -> bool:
        """Проверить, может ли обработчик обработать обновление"""
        pass
    
    @abstractmethod
    def handle(self, update: Dict[str, Any], api) -> None:
        """Обработать обновление"""
        pass
    
    def get_user_from_update(self, update: Dict[str, Any]) -> Dict:
        """Получить информацию о пользователе из обновления"""
        if 'message' in update:
            return update['message'].get('sender', {})
        elif 'callback' in update:
            return update.get('user', {})
        elif 'user' in update:
            return update['user']
        return {}
    
    def is_user_verified(self, max_user_id: int) -> bool:
        """Проверить, верифицирован ли пользователь"""
        return User.is_verified(max_user_id)

