"""SQL схема для создания таблиц"""
import logging
from db.connection import get_connection, return_connection

logger = logging.getLogger(__name__)

# SQL для создания таблиц
CREATE_TABLES = """
-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    username VARCHAR(255),
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица состояний пользователей
CREATE TABLE IF NOT EXISTS user_states (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    state VARCHAR(100) DEFAULT 'idle',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица данных пользователей (JSON)
CREATE TABLE IF NOT EXISTS user_data (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    data JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица заявлений абитуриентов
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    application_id VARCHAR(100) UNIQUE NOT NULL,
    faculty VARCHAR(255),
    method VARCHAR(100),
    status VARCHAR(100) DEFAULT 'На проверке',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица заявок студентов
CREATE TABLE IF NOT EXISTS student_requests (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    request_id VARCHAR(100) UNIQUE NOT NULL,
    request_type VARCHAR(100),
    category VARCHAR(100),
    name VARCHAR(255),
    status VARCHAR(100) DEFAULT 'В обработке',
    processing_days INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица командировок сотрудников
CREATE TABLE IF NOT EXISTS business_trips (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    trip_id VARCHAR(100) UNIQUE NOT NULL,
    purpose TEXT,
    city VARCHAR(255),
    date_from DATE,
    date_to DATE,
    status VARCHAR(100) DEFAULT 'На согласовании',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для улучшения производительности
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_student_requests_user_id ON student_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_student_requests_status ON student_requests(status);
CREATE INDEX IF NOT EXISTS idx_business_trips_user_id ON business_trips(user_id);
CREATE INDEX IF NOT EXISTS idx_business_trips_status ON business_trips(status);
"""


def create_tables():
    """Создает все таблицы в БД"""
    conn = None
    try:
        conn = get_connection()
        if not conn:
            logger.error("Не удалось получить соединение с БД")
            return False
        
        cur = conn.cursor()
        cur.execute(CREATE_TABLES)
        conn.commit()
        cur.close()
        return_connection(conn)
        logger.info("✓ Таблицы БД созданы успешно")
        return True
    except Exception as e:
        logger.error(f"✗ Ошибка создания таблиц: {e}")
        if conn:
            return_connection(conn)
        return False

