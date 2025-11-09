"""Подключение к базе данных"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import logging
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Connection pool
connection_pool = None

def init_db_pool():
    """Инициализация пула подключений"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20, DATABASE_URL
        )
        logger.info("✓ Пул подключений к БД инициализирован")
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка инициализации БД: {e}")
        return False

def get_connection():
    """Получить подключение из пула"""
    if connection_pool:
        return connection_pool.getconn()
    return None

def return_connection(conn):
    """Вернуть подключение в пул"""
    if connection_pool:
        connection_pool.putconn(conn)

def close_db_pool():
    """Закрыть пул подключений"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        logger.info("Пул подключений закрыт")

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Выполнить запрос к БД"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch_one:
                return cur.fetchone()
            elif fetch_all:
                return cur.fetchall()
            else:
                conn.commit()
                return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Ошибка выполнения запроса: {e}")
        return None
    finally:
        return_connection(conn)

