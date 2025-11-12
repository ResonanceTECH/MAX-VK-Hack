FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Создаем структуру для корня проекта
RUN mkdir -p /app/root

# Копируем необходимые модули из корня проекта
COPY db /app/root/db
COPY config.py /app/root/config.py
COPY utils /app/root/utils

# Копирование файлов зависимостей backend
COPY miniapp/backend/requirements.txt /app/requirements.txt

# Установка Python зависимостей
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копирование кода приложения backend (копируем содержимое, не перезаписывая /app/root)
COPY miniapp/backend/api /app/api
COPY miniapp/backend/main.py /app/main.py

# Переменные окружения по умолчанию
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

