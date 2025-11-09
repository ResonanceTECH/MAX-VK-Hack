-- Миграция для поддержки нескольких ролей у одного пользователя
-- Выполните этот скрипт, если у вас уже есть БД с данными

-- Удаляем старое ограничение UNIQUE на max_user_id
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_max_user_id_key;

-- Добавляем новое составное ограничение UNIQUE (max_user_id, role)
ALTER TABLE users ADD CONSTRAINT users_max_user_id_role_unique UNIQUE (max_user_id, role);

