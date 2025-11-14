"""Скрипт для настройки миниприложения в боте"""
import os
import sys
from dotenv import load_dotenv
from api.max_api import MaxAPI

load_dotenv()

# URL миниприложения
MINIAPP_URL = os.getenv('MINIAPP_URL', 'https://178.72.139.15.nip.io')

def main():
    """Настраивает миниприложение для бота"""
    api = MaxAPI()
    
    print(f"Настройка миниприложения для бота...")
    print(f"URL: {MINIAPP_URL}")
    
    # Проверяем токен
    bot_info = api.get_me()
    if 'user_id' not in bot_info:
        print("Ошибка: невалидный токен бота")
        return False
    
    print(f"Бот: {bot_info.get('first_name', 'Unknown')} (@{bot_info.get('username', 'Unknown')})")
    
    # Настраиваем миниприложение
    success = api.set_webapp(MINIAPP_URL)
    
    if success:
        print(f"✓ Миниприложение успешно настроено: {MINIAPP_URL}")
        print("\nТеперь пользователи могут открыть миниприложение через бота")
        return True
    else:
        print("✗ Ошибка при настройке миниприложения")
        print("Проверьте токен и URL миниприложения")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

