"""Подключение к базе данных PostgreSQL"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import logging
from config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB
)

logger = logging.getLogger(__name__)

# Пул соединений
connection_pool = None


def init_db_pool(min_conn=1, max_conn=10):
    """Инициализирует пул соединений с БД"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            min_conn,
            max_conn,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        logger.info("✓ Пул соединений с БД инициализирован")
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка инициализации пула БД: {e}")
        return False


def get_connection():
    """Получает соединение из пула"""
    if connection_pool:
        return connection_pool.getconn()
    return None


def return_connection(conn):
    """Возвращает соединение в пул"""
    if connection_pool and conn:
        connection_pool.putconn(conn)


def close_db_pool():
    """Закрывает пул соединений"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        logger.info("✓ Пул соединений закрыт")


def test_connection():
    """Тестирует подключение к БД"""
    try:
        conn = get_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            cur.close()
            return_connection(conn)
            logger.info(f"✓ Подключение к БД успешно. PostgreSQL версия: {version[0]}")
            return True
        return False
    except Exception as e:
        logger.error(f"✗ Ошибка подключения к БД: {e}")
        return False

