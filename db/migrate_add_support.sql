-- Миграция: Добавление таблиц для поддержки

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

-- FAQ (Часто задаваемые вопросы)
CREATE TABLE IF NOT EXISTS faq (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'general',  -- 'general', 'student', 'teacher', 'admin'
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- Кто создал FAQ
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Сообщения администрации (рассылки)
CREATE TABLE IF NOT EXISTS admin_messages (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    target_role VARCHAR(50),  -- 'student', 'teacher', 'all' или NULL для всех
    target_group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,  -- NULL для всех групп
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_support_tickets_user ON support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_admin ON support_tickets(admin_id);
CREATE INDEX IF NOT EXISTS idx_faq_category ON faq(category);
CREATE INDEX IF NOT EXISTS idx_admin_messages_role ON admin_messages(target_role);

