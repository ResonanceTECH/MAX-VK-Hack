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
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

# Устанавливаем переменные окружения для PostgreSQL напрямую
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_USER'] = 'maxbot'
os.environ['POSTGRES_PASSWORD'] = 'maxbot123'
os.environ['POSTGRES_DB'] = 'maxbot_db'

# Временный обход авторизации для локального тестирования
os.environ['SKIP_AUTH'] = 'true'

from db.models import User, Group, Teacher, Message
from db.connection import get_connection, init_db_pool, close_db_pool
from miniapp.backend.api.auth import verify_init_data, get_current_user
from miniapp.backend.api.routes import router

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
    lifespan=lifespan
)

# CORS для React приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(router, prefix="/api", tags=["api"])

@app.get("/")
async def root():
    return {"message": "Max Bot Miniapp API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

