"""Главный файл бота"""
import time
import logging
from api.max_api import MaxAPI
from handlers.commands import CommandsHandler
from handlers.callback import CallbackHandler
from handlers.admission import AdmissionHandler
from handlers.student import StudentHandler
from handlers.message import MessageHandler
from config import POLLING_TIMEOUT, POLLING_LIMIT

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Основной цикл бота"""
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
    
    # Инициализация обработчиков
    handlers = [
        CommandsHandler(),   # Обработка команд (должен быть первым)
        AdmissionHandler(),  # Обработка модуля Поступление (перед общим CallbackHandler)
        StudentHandler(),    # Обработка модуля Студенты (перед общим CallbackHandler)
        CallbackHandler(),   # Обработка нажатий кнопок (общие)
        MessageHandler(),    # Обработка обычных сообщений
    ]
    
    logger.info("\nБот запущен. Ожидание сообщений...")
    logger.info("Напишите боту в Max, чтобы проверить работоспособность\n")
    
    marker = None
    while True:
        try:
            updates_data = api.get_updates(marker=marker, timeout=POLLING_TIMEOUT, limit=POLLING_LIMIT)
            
            if 'updates' in updates_data and updates_data['updates']:
                for update in updates_data['updates']:
                    update_type = update.get('update_type')
                    logger.debug(f"Получено обновление: {update_type}")
                    
                    # Пробуем обработать обновление каждым обработчиком
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


if __name__ == '__main__':
    main()
