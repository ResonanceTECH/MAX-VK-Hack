"""Скрипт для инициализации базы данных"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DATABASE_URL, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Создать таблицы в базе данных"""
    try:
        # Подключаемся к БД
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Читаем и выполняем SQL схему
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Выполняем SQL по частям (psycopg2 не поддерживает множественные команды в одном execute)
        for statement in schema_sql.split(';'):
            statement = statement.strip()
            if statement:
                cur.execute(statement)
        
        cur.close()
        conn.close()
        
        logger.info("✓ База данных успешно инициализирована")
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка инициализации БД: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    init_database()

