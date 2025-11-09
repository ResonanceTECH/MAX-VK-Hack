-- Миграция: добавление поля status в таблицу messages
-- Выполните этот скрипт для добавления поддержки статусов сообщений

-- Добавляем поле status
ALTER TABLE messages ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'unread';

-- Обновляем существующие записи
UPDATE messages SET status = 'unread' WHERE status IS NULL;

-- Добавляем индекс для оптимизации запросов по статусу
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
CREATE INDEX IF NOT EXISTS idx_messages_to_status ON messages(to_user_id, status);

