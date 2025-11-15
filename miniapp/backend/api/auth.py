"""Аутентификация через Max initData"""
from fastapi import Depends, HTTPException, Header
from typing import Optional, Dict, Any
import hmac
import hashlib
import json
from urllib.parse import parse_qs, unquote
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from db.models import User
from config import TOKEN


def verify_init_data(init_data: str) -> Dict[str, Any]:
    """
    Проверить и распарсить initData от Max
    
    initData имеет формат: hash=xxx&user=xxx&auth_date=xxx&...
    Алгоритм проверки подписи аналогичен Telegram WebApp
    """
    try:
        # Парсим initData
        parsed = parse_qs(init_data)

        # Извлекаем данные
        hash_value = parsed.get('hash', [None])[0]
        user_str = parsed.get('user', [None])[0]
        auth_date = parsed.get('auth_date', [None])[0]

        # В режиме разработки hash может быть моковым
        import os
        skip_verify = os.getenv('SKIP_INITDATA_VERIFY', 'true').lower() == 'true'

        if not user_str:
            raise ValueError("Отсутствует user в initData")

        # auth_date не обязателен в режиме разработки
        if not auth_date and not skip_verify:
            raise ValueError("Отсутствует auth_date в initData")

        # hash не обязателен в режиме разработки
        if not hash_value and not skip_verify:
            raise ValueError("Отсутствует hash в initData")

        # Проверяем подпись
        # Формируем строку для проверки (без hash)
        data_check_string = []
        for key in sorted(parsed.keys()):
            if key != 'hash':
                value = parsed[key][0]
                data_check_string.append(f"{key}={value}")

        data_check_string = '\n'.join(data_check_string)

        # Вычисляем секретный ключ (аналогично Telegram)
        secret_key = hmac.new(
            "WebAppData".encode(),
            TOKEN.encode(),
            hashlib.sha256
        ).digest()

        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Проверяем hash
        if calculated_hash != hash_value:
            # В режиме разработки можем пропустить проверку подписи
            # В продакшене это обязательно!
            import os
            skip_verify = os.getenv('SKIP_INITDATA_VERIFY', 'true').lower() == 'true'
            if not skip_verify:
                raise ValueError("Неверная подпись initData")

        # Парсим user
        user_data = json.loads(unquote(user_str))

        return {
            'user_id': user_data.get('id'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'username': user_data.get('username'),
            'auth_date': int(auth_date) if auth_date else 0
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Ошибка проверки initData: {str(e)}")


def get_current_user(
        x_init_data: Optional[str] = Header(
            None, 
            alias="X-Init-Data",
            description="Данные инициализации от Max мессенджера. Содержит информацию о пользователе и подпись для проверки подлинности. Формат: hash=xxx&user=xxx&auth_date=xxx&..."
        ),
        x_selected_role: Optional[str] = Header(
            None, 
            alias="X-Selected-Role",
            description="Выбранная роль пользователя для переключения между ролями. Доступные значения: 'student', 'teacher', 'admin', 'support'. Если не указано, используется роль по умолчанию (приоритет: admin > support > teacher > student)"
        )
) -> Dict[str, Any]:
    """
    Получить текущего пользователя из initData
    
    Авторизация происходит через initData от Max мессенджера.
    Если указана роль в заголовке X-Selected-Role, возвращает пользователя с этой ролью.
    Это позволяет пользователям с несколькими ролями переключаться между ними.
    """
    # Временный обход авторизации для локального тестирования
    import os
    skip_auth = os.getenv('SKIP_AUTH', 'true').lower() == 'true'

    if skip_auth:
        # Получаем пользователя напрямую из БД без проверки initData
        # Можно указать DEV_USER_MAX_ID в переменных окружения для локальной разработки
        # Если не указан, пытаемся извлечь из initData (даже если это мок)
        dev_user_max_id = os.getenv('DEV_USER_MAX_ID')
        
        if dev_user_max_id:
            # Используем жестко заданный ID
            max_user_id = int(dev_user_max_id)
        elif x_init_data:
            # Пытаемся извлечь user_id из initData (даже без проверки подписи)
            try:
                parsed = parse_qs(x_init_data)
                user_str = parsed.get('user', [None])[0]
                if user_str:
                    user_data = json.loads(unquote(user_str))
                    max_user_id = user_data.get('id')
                else:
                    raise HTTPException(status_code=401, detail="Не удалось извлечь user_id из initData")
            except Exception as e:
                raise HTTPException(status_code=401, detail=f"Ошибка парсинга initData: {str(e)}")
        else:
            raise HTTPException(status_code=401, detail="Отсутствует initData и DEV_USER_MAX_ID не задан")
        
        if not max_user_id:
            raise HTTPException(status_code=401, detail="Не удалось определить user_id")
            
        if x_selected_role:
            # Если указана роль, получаем пользователя с этой ролью
            user = User.get_by_max_id(max_user_id, role=x_selected_role)
        else:
            user = User.get_by_max_id(max_user_id)

        if not user:
            raise HTTPException(status_code=403, detail="Пользователь не найден в БД")
        return user

    # Обычная авторизация через initData
    if not x_init_data:
        raise HTTPException(status_code=401, detail="Отсутствует initData")

    # Проверяем initData
    max_user_data = verify_init_data(x_init_data)
    max_user_id = max_user_data.get('user_id')

    if not max_user_id:
        raise HTTPException(status_code=401, detail="Неверный user_id в initData")

    # Получаем пользователя из БД
    if x_selected_role:
        # Если указана роль, получаем пользователя с этой ролью
        user = User.get_by_max_id(max_user_id, role=x_selected_role)
    else:
        user = User.get_by_max_id(max_user_id)

    if not user:
        raise HTTPException(status_code=403, detail="Пользователь не найден в системе")

    return user
