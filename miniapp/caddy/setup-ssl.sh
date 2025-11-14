#!/bin/bash
# Скрипт для генерации доверенных SSL-сертификатов для localhost

set -e

echo "Установка mkcert (если не установлен)..."
if ! command -v mkcert &> /dev/null; then
    echo "mkcert не найден. Установите его:"
    echo "Windows (choco): choco install mkcert"
    echo "Windows (scoop): scoop install mkcert"
    echo "Linux: sudo apt install mkcert или смотрите https://github.com/FiloSottile/mkcert"
    exit 1
fi

echo "Создание локального CA (если еще не создан)..."
mkcert -install

echo "Генерация сертификатов для localhost и 178.72.139.15..."
mkdir -p ./ssl
mkcert -key-file ./ssl/localhost-key.pem -cert-file ./ssl/localhost.pem localhost 127.0.0.1 ::1 178.72.139.15

echo "✅ Сертификаты созданы в ./miniapp/caddy/ssl/"
echo "Теперь перезапустите docker compose up -d"

