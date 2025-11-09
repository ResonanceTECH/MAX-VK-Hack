"""Главный файл бота"""
import time
import logging
from api.max_api import MaxAPI
from db.connection import init_db_pool, close_db_pool
from handlers.message import MessageHandler
from handlers.callback import CallbackHandler
from config import POLLING_TIMEOUT, POLLING_LIMIT

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Регистрация обработчиков
handlers = [
    MessageHandler(),
    CallbackHandler()
]

def main():
    """Основной цикл бота"""
    # Инициализация БД
    logger.info("Инициализация базы данных...")
    if not init_db_pool():
        logger.error("Не удалось инициализировать БД. Выход.")
        return
    
    # Инициализация API
    api = MaxAPI()
    
    # Проверка токена
    logger.info("Проверка токена...")
    bot_info = api.get_me()
    
    if 'user_id' in bot_info:
        logger.info("✓ Токен валиден!")
        logger.info(f"  Бот ID: {bot_info.get('user_id')}")
        logger.info(f"  Имя: {bot_info.get('first_name', 'Unknown')}")
        if bot_info.get('last_name'):
            logger.info(f"  Фамилия: {bot_info.get('last_name')}")
        logger.info(f"  Username: @{bot_info.get('username', 'Unknown')}")
    else:
        logger.error("✗ Токен невалиден или произошла ошибка")
        logger.error(f"  Ответ API: {bot_info}")
        return
    
    logger.info("\nБот запущен. Ожидание сообщений...")
    logger.info("Напишите боту в Max, чтобы проверить работоспособность\n")
    
    marker = None
    try:
        while True:
            try:
                updates_data = api.get_updates(
                    marker=marker, 
                    timeout=POLLING_TIMEOUT, 
                    limit=POLLING_LIMIT
                )
                
                if 'updates' in updates_data and updates_data['updates']:
                    for update in updates_data['updates']:
                        update_type = update.get('update_type')
                        logger.debug(f"Получено обновление: {update_type}")
                        
                        handled = False
                        for handler in handlers:
                            if handler.can_handle(update):
                                try:
                                    handler.handle(update, api)
                                    handled = True
                                    logger.debug(f"Обновление обработано: {handler.__class__.__name__}")
                                    break
                                except Exception as e:
                                    logger.error(f"Ошибка в обработчике {handler.__class__.__name__}: {e}", exc_info=True)
                        
                        if not handled:
                            logger.warning(f"Необработанное обновление: {update_type}")
                        
                        # Обновляем marker для следующего запроса
                        if 'marker' in updates_data:
                            marker = updates_data['marker']
                elif 'marker' in updates_data:
                    marker = updates_data['marker']
            
            except KeyboardInterrupt:
                logger.info("\nОстановка бота...")
                break
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}", exc_info=True)
                time.sleep(5)  # Пауза перед повтором
            
            time.sleep(0.1)
    finally:
        close_db_pool()


if __name__ == '__main__':
    main()
