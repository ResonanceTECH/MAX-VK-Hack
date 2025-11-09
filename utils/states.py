"""Управление состояниями пользователей (FSM)"""
from typing import Dict, Optional
import threading

# Хранилище состояний (в продакшене лучше использовать Redis)
_user_states: Dict[int, Dict] = {}
_lock = threading.Lock()

def set_state(user_id: int, state: str, data: Optional[Dict] = None):
    """Установить состояние пользователя"""
    with _lock:
        _user_states[user_id] = {
            'state': state,
            'data': data or {}
        }

def get_state(user_id: int) -> Optional[Dict]:
    """Получить состояние пользователя"""
    with _lock:
        return _user_states.get(user_id)

def clear_state(user_id: int):
    """Очистить состояние пользователя"""
    with _lock:
        if user_id in _user_states:
            del _user_states[user_id]

def is_in_state(user_id: int, state: str) -> bool:
    """Проверить, находится ли пользователь в определенном состоянии"""
    user_state = get_state(user_id)
    return user_state and user_state.get('state') == state

def get_state_data(user_id: int) -> Dict:
    """Получить данные состояния пользователя"""
    user_state = get_state(user_id)
    return user_state.get('data', {}) if user_state else {}

def update_state_data(user_id: int, **kwargs):
    """Обновить данные состояния пользователя"""
    with _lock:
        if user_id in _user_states:
            if 'data' not in _user_states[user_id]:
                _user_states[user_id]['data'] = {}
            _user_states[user_id]['data'].update(kwargs)

# Хранилище выбранных ролей пользователей
_user_roles: Dict[int, str] = {}
_role_lock = threading.Lock()

def set_user_role(user_id: int, role: str):
    """Сохранить выбранную роль пользователя"""
    with _role_lock:
        _user_roles[user_id] = role

def get_user_role(user_id: int) -> Optional[str]:
    """Получить выбранную роль пользователя"""
    with _role_lock:
        return _user_roles.get(user_id)

def clear_user_role(user_id: int):
    """Очистить выбранную роль пользователя"""
    with _role_lock:
        if user_id in _user_roles:
            del _user_roles[user_id]

