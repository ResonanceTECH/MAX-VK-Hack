"""Управление состояниями пользователей"""
from typing import Dict, Optional

# Хранение состояний пользователей (в будущем можно заменить на БД)
user_states: Dict[int, str] = {}
user_roles: Dict[int, str] = {}
user_data: Dict[int, dict] = {}


def set_user_state(user_id: int, state: str) -> None:
    """Устанавливает состояние пользователя"""
    user_states[user_id] = state


def get_user_state(user_id: int) -> str:
    """Получает состояние пользователя"""
    return user_states.get(user_id, 'idle')


def clear_user_state(user_id: int) -> None:
    """Очищает состояние пользователя"""
    if user_id in user_states:
        del user_states[user_id]


def set_user_role(user_id: int, role: str) -> None:
    """Устанавливает роль пользователя"""
    user_roles[user_id] = role


def get_user_role(user_id: int) -> Optional[str]:
    """Получает роль пользователя"""
    return user_roles.get(user_id)


def set_user_data(user_id: int, key: str, value: any) -> None:
    """Сохраняет данные пользователя"""
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id][key] = value


def get_user_data(user_id: int, key: str, default: any = None) -> any:
    """Получает данные пользователя"""
    return user_data.get(user_id, {}).get(key, default)

