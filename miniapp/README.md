# Miniapp Docker Setup

## Структура

- **nginx** (порт 80) - основной прокси-сервер
- **frontend** (порт 3000) - React приложение
- **backend** (порт 8000) - FastAPI бэкенд
- **schedule** (порт 8001) - сервис расписания
- **db** (порт 5432) - PostgreSQL база данных

## Запуск

```bash
cd miniapp
docker-compose up -d
```

## Доступ

- Frontend: http://localhost
- Backend API: http://localhost/api
- Schedule API: http://localhost/api2
- Swagger: http://localhost/api/docs

## Переменные окружения

Создайте `.env` файл в директории `miniapp/`:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=maxbot
POSTGRES_PASSWORD=maxbot123
POSTGRES_DB=maxbot_db
SKIP_AUTH=false
SKIP_INITDATA_VERIFY=true
```

## Остановка

```bash
docker-compose down
```

## Пересборка

```bash
docker-compose build --no-cache
docker-compose up -d
```

