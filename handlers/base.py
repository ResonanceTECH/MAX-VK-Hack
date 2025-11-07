"""Базовый класс для обработчиков"""
from typing import Dict, Any


class BaseHandler:
    """Базовый класс для всех обработчиков"""
    
    def can_handle(self, update: Dict[str, Any]) -> bool:
        """Проверяет, может ли обработчик обработать это обновление"""
        raise NotImplementedError
    
    def handle(self, update: Dict[str, Any], api) -> None:
        """Обрабатывает обновление"""
        raise NotImplementedError

