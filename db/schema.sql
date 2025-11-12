-- Схема базы данных для бота Max

-- Пользователи системы
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    max_user_id BIGINT NOT NULL,  -- ID пользователя в Max
    first_name VARCHAR(100) NOT NULL,  -- Имя
    last_name VARCHAR(100) NOT NULL,  -- Фамилия
    middle_name VARCHAR(100),  -- Отчество (может быть NULL)
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
    status VARCHAR(20) DEFAULT 'unread',  -- Статус сообщения: 'unread', 'read'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Обращения в поддержку
CREATE TABLE IF NOT EXISTS support_tickets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'new',  -- 'new', 'in_progress', 'resolved'
    admin_id INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- Админ, который взял обращение в работу
    response_time INTEGER,  -- Время реакции в минутах (от создания до первого ответа)
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Новости
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    hashtags VARCHAR(500),  -- Хэштеги через запятую
    target_role VARCHAR(50),  -- 'student', 'teacher', 'all' или NULL для всех
    target_group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,  -- NULL для всех групп
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_max_id ON users(max_user_id);
CREATE INDEX IF NOT EXISTS idx_group_members_user ON group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_group_members_group ON group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_teacher_groups_teacher ON teacher_groups(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_groups_group ON teacher_groups(group_id);
CREATE INDEX IF NOT EXISTS idx_messages_from ON messages(from_user_id);
CREATE INDEX IF NOT EXISTS idx_messages_to ON messages(to_user_id);
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
CREATE INDEX IF NOT EXISTS idx_messages_to_status ON messages(to_user_id, status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_user ON support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_admin ON support_tickets(admin_id);
CREATE INDEX IF NOT EXISTS idx_news_role ON news(target_role);
CREATE INDEX IF NOT EXISTS idx_news_created_at ON news(created_at);

