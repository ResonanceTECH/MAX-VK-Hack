"""FastAPI backend для мини-приложения Max"""
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import sys
import os
import logging

# Добавляем путь к корневому проекту для импорта общих модулей
# В Docker контейнере используем /app/root, иначе относительный путь
if os.path.exists('/app/root'):
    project_root = '/app/root'
else:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

# Устанавливаем переменные окружения для PostgreSQL из env или значения по умолчанию
os.environ.setdefault('POSTGRES_HOST', os.getenv('POSTGRES_HOST', '178.72.139.15.nip.io'))
os.environ.setdefault('POSTGRES_PORT', os.getenv('POSTGRES_PORT', '5433'))
os.environ.setdefault('POSTGRES_USER', os.getenv('POSTGRES_USER', 'maxbot'))
os.environ.setdefault('POSTGRES_PASSWORD', os.getenv('POSTGRES_PASSWORD', 'maxbot123'))
os.environ.setdefault('POSTGRES_DB', os.getenv('POSTGRES_DB', 'maxbot_db'))

# Временный обход авторизации для локального тестирования (по умолчанию false в продакшене)
os.environ.setdefault('SKIP_AUTH', os.getenv('SKIP_AUTH', 'true'))
os.environ.setdefault('SKIP_INITDATA_VERIFY', os.getenv('SKIP_INITDATA_VERIFY', 'true'))

from db.models import User, Group, Teacher, Message
from db.connection import get_connection, init_db_pool, close_db_pool
from api.auth import verify_init_data, get_current_user
from api.routes import router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan события для инициализации и закрытия БД
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    if not init_db_pool():
        logger.error("Не удалось инициализировать БД")
    else:
        logger.info("Пул подключений к БД инициализирован")
    
    yield
    
    # Shutdown
    close_db_pool()

app = FastAPI(
    title="Max Bot Miniapp API",
    description="API для мини-приложения бота Max",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/api"  # Указываем префикс для работы за nginx прокси
)

# CORS для React приложения
# В продакшене можно ограничить origins для безопасности
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
if cors_origins == ['*']:
    cors_origins = ["*"]  # Разрешить все для простоты
else:
    cors_origins = [origin.strip() for origin in cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты (префикс /api добавляется nginx)
app.include_router(router, tags=["api"])

@app.get("/")
async def root():
    return {"message": "Max Bot Miniapp API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

