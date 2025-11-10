-- Схема базы данных для бота Max

-- Пользователи системы
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    max_user_id BIGINT NOT NULL,  -- ID пользователя в Max
    fio VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,  -- 'student', 'teacher', 'admin', 'support'
    phone VARCHAR(20),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(max_user_id, role)  -- Один пользователь может иметь несколько ролей, но не дублировать одну роль
);

-- Группы
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,  -- например, "ИС-21"
    semester INTEGER,
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Участники групп (студенты)
CREATE TABLE IF NOT EXISTS group_members (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    is_headman BOOLEAN DEFAULT FALSE,  -- староста группы
    UNIQUE(user_id, group_id)
);

-- Преподаватели и их группы
CREATE TABLE IF NOT EXISTS teacher_groups (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    semester INTEGER,
    year INTEGER,
    UNIQUE(teacher_id, group_id, semester, year)
);

-- Сообщения (для истории общения)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    from_user_id INTEGER REFERENCES users(id),
    to_user_id INTEGER REFERENCES users(id),
    group_id INTEGER REFERENCES groups(id),  -- NULL для личных сообщений
    text TEXT NOT NULL,
    max_message_id VARCHAR(255),  -- ID сообщения в Max
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_max_id ON users(max_user_id);
CREATE INDEX IF NOT EXISTS idx_group_members_user ON group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_group_members_group ON group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_teacher_groups_teacher ON teacher_groups(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_groups_group ON teacher_groups(group_id);
CREATE INDEX IF NOT EXISTS idx_messages_from ON messages(from_user_id);
CREATE INDEX IF NOT EXISTS idx_messages_to ON messages(to_user_id);

